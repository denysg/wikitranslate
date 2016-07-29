import sys
import BeautifulSoup as bs
import requests
import urllib
import argparse

WIKI_BASE_URL = 'https://%s.wikipedia.org/wiki/'

class RequestError(Exception):
    pass

class OriginalPageNotFound(Exception):
    pass

class TranslationNotFound(Exception):
    pass

def translate(text_in, lang_in, lang_out):
    url_in = WIKI_BASE_URL % lang_in + text_in
    try:
        response = send_request(url_in)
        url_out = find_translated_article_url(response.text, lang_out)
        translated_text = _extract_text_from_url(url_out)
        get_available_languages(response.text)
    except Exception as e:
        print 'Error: %s' % e
        sys.exit(1)

    return translated_text

def _extract_text_from_url(url):
    return url.split('wiki/')[1].replace('_', ' ')

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

def get_available_languages(original_article_body):
    languages = []
    soup = bs.BeautifulSoup(original_article_body)
    language_links = soup.findAll('a', attrs={'lang': True})
    for link in language_links:
        languages.append(link['lang'])

    print 'Available in %s languages:' % len(languages)
    for lang_code in languages:
        print _get_lang_by_code(lang_code)

    return languages

def _get_lang_by_code(lang_code):
    with open('languages.txt', 'r') as languages:
        for line in languages.readlines():
            code = line.split(':')[0].strip()
            lang = line.split(':')[1].strip()

            if lang_code == code:
                return lang

def _is_disimbiguation(url):
    if '(disimbiguation)' in url:
        return True
    else:
        return False

def send_request(url):
    r = requests.get(url)
    if r.history:
        for resp in r.history:
            print resp.status_code
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



