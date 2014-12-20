##################################################
Single Russian-Ukrainian keyboard layout on Ubuntu
##################################################

:slug: ubuntu-ruu-kbd
:lang: en
:date: 2014-12-20
:tags: keyboard,ukraine,ubuntu
:category: work
:summary: Using single keyboard layout to input both Russian and Ukrainian in Ubuntu

My most used input language is English, with second used being Russian.
Occasionally though I have to input text (e.g. in search field) in German,
French or Ukrainian.
For Western languages Ubuntu comes with "English (international with AltGr dead keys)"
available as a choice of input layout.
It works out nicely as my default English layout,
and those extra accented letters are easy within reach
(plus some extra handy symbols are made available).
On the Cyrillic languages side things are a bit more complicated.
I could not find any suitable layout in Ubuntu enabled out of the box.

It turns out there is one layout included in Ubuntu, one just has to manually turn it on:

- open file ``/usr/share/X11/xkb/rules/evdev.extras.xml``, find the layout named ``ruu``

  .. code-block:: xml

     <variant>
       <configItem>
         <name>ruu</name>
         <shortDescription>ru</shortDescription>
         <description>Russian (with Ukrainian-Belorussian layout)</description>
         <languageList><iso639Id>rus</iso639Id>
                       <iso639Id>ukr</iso639Id>
                       <iso639Id>bel</iso639Id></languageList>
       </configItem>
     </variant>

- copy the whole enclosing ``<variant>`` tag as shown above
- open file ``/usr/share/X11/xkb/rules/evdev.xml``
- find Russian section

  .. code-block:: xml

    <layout>
      <configItem>
        <name>ru</name>

        <shortDescription>ru</shortDescription>
        <description>Russian</description>
        <languageList>
          <iso639Id>rus</iso639Id>
        </languageList>
      </configItem>
      <variantList>
        <variant>
          <configItem>
            <name>phonetic</name>
            <description>Russian (phonetic)</description>

- paste there copied ``ruu`` variant alongside other available variants

  .. code-block:: xml

    <layout>
      <configItem>
        <name>ru</name>

        <shortDescription>ru</shortDescription>
        <description>Russian</description>
        <languageList>
          <iso639Id>rus</iso639Id>
        </languageList>
      </configItem>
      <variantList>
        <variant>
          <configItem>
            <name>ruu</name>
            <shortDescription>ru</shortDescription>
            <description>Russian (with Ukrainian-Belorussian layout)</description>
            <languageList><iso639Id>rus</iso639Id>
                          <iso639Id>ukr</iso639Id>
                          <iso639Id>bel</iso639Id></languageList>
          </configItem>
        </variant>
        <variant>
          <configItem>
            <name>phonetic</name>
            <description>Russian (phonetic)</description>

- restart X server


Now you can choose a "Russian (with Ukrainian-Belorussian layout)" from available layouts.
It is a standard Russian layout, plus you can input Ukrainian- or Belorussian-specific
characters via AltGr (usually right Alt), plus some more extra symbols are available
via AltGr, like Ukrainian Hryvnia (₴) or some math symbols (e.g. ±).
Check out the "Keyboard Layout Chart" for this layout to see all available characters.
