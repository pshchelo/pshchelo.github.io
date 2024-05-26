from datetime import datetime

AUTHOR = "pshchelo"
SITEURL = ""
SITENAME = "Bits and Pieces"
SITETITLE = ""
SITESUBTITLE = ""
SITEDESCRIPTION = ""
SITELOGO = "/images/avatar.jpg"
ROBOTS = "index, follow"

PATH = "content"
TIMEZONE = "Europe/Kiev"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Python", "http://python.org/"),
    ("OpenStack", "http://www.openstack.org/"),
)

# Social widget
SOCIAL_WIDGET_NAME = "Contacts"
SOCIAL = (
    ("github", "https://github.com/pshchelo"),
    ("bitbucket", "https://bitbucket.org/pshchelo"),
    ("twitter", "https://twitter.com/pshchelo"),
    ("linkedin", "https://www.linkedin.com/in/pshchelo"),
    # ("rss", "/blog/feeds/all.atom.xml"),
)

# To enable "Fork Me" ribbon
#GITHUB_URL = "https://github.com/pshchelo/pshchelo.github.io"

# Enable "share on twitter link"
#TWITTER_USERNAME = "pshchelo"

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

STATIC_PATHS = [
    "images",
    "extra",
]

EXTRA_PATH_METADATA = {
    "images/favicon.ico": {"path": "favicon.ico"},
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/nojekyll": {"path": ".nojekyll"},
}

THEME = "Flex"
##########
MAIN_MENU = True
PYGMENTS_STYLE = "solarized-light"
USE_FOLDER_AS_CATEGORY = True
THEME_COLOR_AUTO_DETECT_BROWSER_PREFERENCE = True
THEME_COLOR_ENABLE_USER_OVERRIDE = True

MENUITEMS = (
    ("Archives", "/archives.html"),
    ("Categories", "/categories.html"),
    ("Tags", "/tags.html"),
)

GITHUB_CORNER_URL = "https://github.com/pshchelo/pshchelo.github.io"
COPYRIGHT_YEAR = datetime.now().year
# LINKS_IN_NEW_TAB = "external"
# USE_LESS = True
# HOME_HIDE_TAGS = True
# BROWSER_COLOR = "#123456"  # hex web color to set on the browser
