###########################################
Единая русско-украинская раскладка в Ubuntu
###########################################

:slug: ubuntu-ruu-kbd
:lang: ru
:date: 2014-12-20
:tags: keyboard,ukraine,ubuntu
:category: work
:summary: Using single keyboard layout to input both Russian and Ukrainian in Ubuntu

Так получилось, что моим основным языком ввода является английский,
вторым по частоте использования русский.
Тем не менее, иногда мне надо вводить текст на немецком, франзузском и украинском языках.
Для западноевропейских языков в Ubuntu есть удобная раскладка
"English (international with AltGr dead keys)".
Пользоваться ей как основной довольно удобно,
поскольку все акценты/умляуты доступны через AltGr,
плюс к ним несколько других символов.
Для кириллических языков ситуация несколько более сложная.
Я не смог найти подходящую раскладку в Ubuntu "из коробки".

Как оказалось, раскладка-то есть, но ее надо специально руками включить:

- открыть файл ``/usr/share/X11/xkb/rules/evdev.extras.xml``, найти вариант раскладки с именем ``ruu``

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

- скопировать всю часть между тэгами ``<variant>`` как показано выше
- открыть файл ``/usr/share/X11/xkb/rules/evdev.xml``
- найти секцию описывающую Русский язык

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

- вставить ранее скопированный вариант раскладки ``ruu`` рядом с другими доступными вариантами

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

- перезапустить X server

Теперь в списке доступных раскладок появляется "Russian (with Ukrainian-Belorussian layout)".
В основном это стандартная русская раскладка (главное отличие - расплолжение буквы ё),
но все специфично украинские и белорусские буквы доступны через AltGr,
и кроме них несколько других плюшек вроде валютного значка
украинской гривны (₴) или всяких математических знаков (например ±).
Чтобы увидеть все доступные символы, проверьте "Keyboard Layout Chart" для этой раскладки.
