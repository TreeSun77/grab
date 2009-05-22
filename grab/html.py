# -*- coding: utf-8 -*-
import re
from htmlentitydefs import name2codepoint
import logging

def decode_entities(text):
    """
    Convert HTML entities to their unicode analogs.
    """

    re_entity = re.compile(r'(&[a-z]+;)')
    re_num_entity = re.compile(r'(&#\d+;)')

    def process_entity(match):
        entity = match.group(1)
        name = entity[1:-1]
        if name in name2codepoint:
            return unichr(name2codepoint[name])
        else:
            return entity

    
    def process_num_entity(match):
        entity = match.group(1)
        num = entity[2:-1]
        try:
            return unichr(int(num))
        except ValueError:
            return entity

    text = re_num_entity.sub(process_num_entity, text)
    text = re_entity.sub(process_entity, text)
    return text


def make_unicode(html, guess_encodings):
    """
    Convert byte stream to unicode.
    """

    RE_CONTENT_TYPE_TAG = re.compile(r'<meta[^>]+http-equiv\s*=\s*.?Content-Type[^>]+', re.I)
    RE_CHARSET = re.compile(r'charset\s*=\s*([-_a-z0-9]+)', re.I)
  
    match = RE_CONTENT_TYPE_TAG.search(html)
    if match:
        match = RE_CHARSET.search(match.group(0))
        if match:
            guess_encodings = [match.group(1)] + list(guess_encodings)

    for encoding in guess_encodings:
        try:
            return html.decode(encoding)
        except UnicodeDecodeError:
            pass
    else:
        # Dirty hack
        logging.error('Converting document to UTF-8 in ingore mode!')
        return html.decode('utf-8', 'ignore')


def find_refresh_url(html):
    """
    Find value of redirect url from http-equiv refresh meta tag.
    """

    # We should decode quote values to correctly find
    # the url value
    html = html.replace('&#39;', '\'')
    html = html.replace('&#34;', '"').replace('&quot;', '"')

    RE_REFRESH_TAG = re.compile(r'<meta[^>]+http-equiv\s*=\s*["\']*Refresh[^>]+', re.I)
    RE_REFRESH_URL = re.compile(r'url=["\']*([^\'"> ]+)')

    match = RE_REFRESH_TAG.search(html)
    if match:
        match = RE_REFRESH_URL.search(match.group(0))
        if match:
            return match.group(1)
    return None
