import os
import sys
import BeautifulSoup as bs
import requests
import urllib
import argparse

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LANG_FILE = os.path.join(BASE_PATH, 'languages.txt')
WIKI_BASE_URL = 'https://%s.wikipedia.org/wiki/'


def translate(text_in, lang_in, lang_out):
    url_in = _get_wiki_link(text_in, lang_in)
    try:
        response = send_request(url_in)
        url_out = find_translated_article_url(response.text, lang_out)
        translated_text = _extract_text_from_url(url_out)
    except Exception as e:
        raise e

    return translated_text.decode('utf-8')

def _extract_text_from_url(url):
    text = url.split('wiki/')[1].replace('_', ' ')
    if '#' in text:
        # This is in case a translated article is a chapter
        # in another article.
        text = text.split('#')[-1]
    return text

def find_translated_article_url(original_article_body, lang_out):
    soup = bs.BeautifulSoup(original_article_body)
    url = soup.findAll('a', attrs={'lang': lang_out})

    if not url:
        raise TranslationNotFound('Could not find translation.')
    elif len(url) > 1:
        raise Exception
    elif not url[0]['href']:
        raise Exception

    return _decode_url(url[0]['href'].encode('utf-8'))

def get_available_languages(text_in, lang_in):
    languages = []
    response = send_request(_get_wiki_link(text_in, lang_in))
    soup = bs.BeautifulSoup(response.text)
    language_links = soup.findAll('a', attrs={'lang': True})

    for link in language_links:
        code = link['lang'].decode('utf-8')
        lang = _get_lang_by_code(code) or code
        languages.append((code, lang.decode('utf-8')))

    return _sort_lang(languages)

def get_all_languages():
    languages = []
    with open(LANG_FILE, 'r') as f:
        for line in f.readlines():
            lang_code = line.split(':')[0].strip().decode('utf-8')
            lang = line.split(':')[1].strip().decode('utf-8')
            languages.append((lang_code, lang))

    return _sort_lang(languages)

def _get_lang_by_code(lang_code):
    with open(LANG_FILE, 'r') as languages:
        for line in languages.readlines():
            code = line.split(':')[0].strip()
            lang = line.split(':')[1].strip()

            if lang_code == code:
                return lang

def _sort_lang(lang_tuple):
    lang_tuple.sort(key=lambda x: x[1])
    return lang_tuple

def _get_wiki_link(text, lang):
    return WIKI_BASE_URL % lang + text

def send_request(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r
    elif r.status_code == 404:
        raise OriginalPageNotFound('Could not find a Wikipedia article for the word you were trying to translate.')
    else:
        raise RequestError('Error sending the request.')

def _decode_url(encoded_url):
    return urllib.unquote(encoded_url)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text',
        help='Text to translate')
    parser.add_argument('lang_in',
        help='Language to translate from.')
    parser.add_argument('lang_out',
        help='Language to translate to.')
    args = parser.parse_args()

    translated_text = translate(args.text, args.lang_in, args.lang_out)
    print '[%s] %s > [%s] %s' % (
        args.lang_in,
        args.text,
        args.lang_out,
        translated_text)

if __name__ == '__main__':
    main()

class RequestError(Exception):
    pass

class OriginalPageNotFound(Exception):
    pass

class TranslationNotFound(Exception):
    pass
