#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Pavlo Shchelokovskyy'
SITENAME = u'Bits and Pieces'
SITEURL = ''

TIMEZONE = 'Europe/Kiev'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('Python.org', 'http://python.org/'),
          ('OpenStack', 'http://www.openstack.org/'),
          )

# Social widget
SOCIAL = (('GitHub', 'https://github.com/pshchelo'),
          ('BitBucket', 'https://bitbucket.org/pshchelo'),
          ('Google+', 'https://plus.google.com/+PavloShchelokovskyy/about'),
          ('Twitter', 'https://twitter.com/pshchelo'),
          ('LinkedIn', 'http://ua.linkedin.com/pub/pavlo-shchelokovskyy/38/676/124/'),
          )

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

THEME = 'pelican-bootstrap3'
#TYPOGRIFY = True
