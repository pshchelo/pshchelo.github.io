#################
Catchy Post Title
#################

.. |date| date::

:date: 2016-09-20
:modified: |date|
:tags: list,of,tags
:category: somecategory
:slug: file-slug
:lang: ru
:authors: pas-ha
:summary: short summary for index and feeds
:status: draft

Example of Asciinema embed
--------------------------

Asciinema is a terminal recording tool and sharing site.

https://asciinema.org

.. raw:: html

   <script type="text/javascript" src="https://asciinema.org/a/8bd6ang0cfrky0or7abwkaxcm.js" id="asciicast-8bd6ang0cfrky0or7abwkaxcm" async data-size="medium"></script>

This is how it can be emedded even into static site like Pelican

Example of GitHub Gist embed
----------------------------

Gist is a GitHub feature to store and share small scripts or code snippets
that seem not to be worthy their own place in a proper GitHub repo.

https://gist.github.com


Copy the **Embed** tag from your Gist and use it with ``.. raw: html``
RST directive:

.. raw:: html

  <script src="https://gist.github.com/pshchelo/952d247b4dec1bacc6e023a343e29ba8.js"></script>

To embed a specific file of a multi-file Gist, append ``?file=FILENAME`` query
to the gist URL.
