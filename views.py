#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import wiki

from functools import wraps
from flask import Flask, flash, redirect, session, url_for, request, render_template, abort
from app import app

app.secret_key = app.config['SECRET_KEY']

if app.debug is not True:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('/srv/wikitranslate/log/error.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


@app.route('/')
def index():
    input_lang = request.args.get('input-lang')
    input_text = request.args.get('input-text')
    output_lang = request.args.get('output-lang')
    output_languages = wiki.get_all_languages()
    translation = None
    input_wiki_link = None
    output_wiki_link = None

    try:
        if input_lang and input_text and output_lang:
	    input_wiki_link = wiki._get_wiki_link(input_text, input_lang)
            output_languages = wiki.get_available_languages(input_text, input_lang)
            translation = wiki.translate(input_text, input_lang, output_lang)
            output_wiki_link = wiki._get_wiki_link(translation, output_lang)
    except wiki.OriginalPageNotFound:
        flash('Could not find <b>%s</b> Wikipedia article for <b>%s</b>.' % (wiki._get_lang_by_code(input_lang), input_text))
    except wiki.TranslationNotFound:
	flash('Could not find translation in <b>%s</b>.<br>The second dropdown list is now updated with <b>%s</b> languages in which the translation is available.' % (wiki._get_lang_by_code(output_lang), len(output_languages)))
    except Exception as e:
        flash(e)
    
    return render_template(
            'index.html',
            all_languages=wiki.get_all_languages(),
            output_languages=output_languages,
            translation=translation,
            input_lang=input_lang,
            output_lang=output_lang,
            input_text=input_text,
            input_wiki_link=input_wiki_link,
            output_wiki_link=output_wiki_link)

if __name__ == '__main__':
    app.run(debug=True)
