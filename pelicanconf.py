#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Pavlo Shchelokovskyy'
SITENAME = u'Bits and Pieces'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Kiev'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ('Python.org', 'http://python.org/'),
    ('OpenStack', 'http://www.openstack.org/'),
)

# Social widget
SOCIAL = (
    ('GitHub', 'https://github.com/pshchelo'),
    ('BitBucket', 'https://bitbucket.org/pshchelo'),
    ('Google+', 'https://plus.google.com/+PavloShchelokovskyy/about'),
    ('Twitter', 'https://twitter.com/pshchelo'),
    ('LinkedIn', 'https://www.linkedin.com/in/pshchelo'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

THEME = 'pelican-bootstrap3'
TYPOGRIFY = True


# Copied over from old config, do I need theese?
GITHUB_URL = 'https://github.com/pshchelo'
STATIC_PATHS = [
        'images',
        'extra/robots.txt',
        'extra/favicon.ico'
]
EXTRA_PATH_METADATA = {
        'extra/robots.txt': {'path': 'robots.txt'},
        'extra/favicon.ico': {'path': 'favicon.ico'}
}
