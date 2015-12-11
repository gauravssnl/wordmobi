# Introduction #

Wordmobi has [multilingual](http://wiki.forum.nokia.com/index.php/Localization_Example_for_PyS60) support since version 0.4.4. At this moment, the following translations are available:

| **Language** | **File** | **Translator** | **Email** |
|:-------------|:---------|:---------------|:----------|
| English (EUA) | wmlocale\_en\_us.py | [Marcelo Barros](http://jedizone.wordpress.com) | marcelobarrosalmeida (at) gmail.com |
| Brazilian Portuguese | wmlocale\_pt\_br.py | [Marcelo Barros](http://jedizone.wordpress.com) | marcelobarrosalmeida (at) gmail.com |
| Spanish      | wmlocale\_es.py | [Pablo Poo](http://pablo.poo.cl/) | pablopoo (at) gmail.com |
| Turkish      | wmlocale\_tr.py | drAdeLante (Deniz Karaoglu) | drdeniz79 (at) gmail.com |
| Italian      | wmlocale\_it.py | Claudio Cherubino | claudiocherubino (at) gmail.com |
| Dutch        | wmlocale\_nl.py | Raymond Sneekes | raymond (at) sneek.es |
| German       | wmlocale\_de.py | [Steffen Fechner](http://diefechis.de/) | fechman (at) googlemail.com |
| Romanian     | wmlocale\_ro.py | [Adinel Giboi](http://reinventer.wordpress.com) |adinel.giboi (at) gmail.com |
| Simplified Chinese| wmlocale\_zh\_cn.py | 王钟寅 (bt4wang)  | bt4wang (at) gmail.com |
| French       | wmlocale\_fr.py | Yann Nave      |ynave (at) directinfoservice.com |
| Russian      | wmlocale\_ru.py | Cyrill Udartcev |http://cyrill.co.uk |
| Indonesian   | wmlocale\_id.py | Nikko Haendratnio  | http://nikko296.wordpress.com |

# Translating Wordmobi #

If you want to see your language supported, follow the steps below.

## Getting latest source code and Python for S60 ##

  1. Download the latest source code. You will see a zip file following the pattern "wordmobi-version-src.zip" in [download tab](http://code.google.com/p/wordmobi/downloads/list). Use the more recent one. If you are in doubt, please drop me an email (marcelobarrosalmeida at gmail.com).
  1. Inside this zip file you will see several **.py** files under a **src** directory. Just copy all python file into **e:\python\lib**, in our phone memory card. Create this path if it not exists.
  1. Move file **default.py** to **e:\python**.
  1. Check if you have [PythonForS60 1.4.5](http://sourceforge.net/project/showfiles.php?group_id=154155&package_id=171153&release_id=644640) installed and [PythonScriptShell 1.4.5](http://sourceforge.net/project/showfiles.php?group_id=154155&package_id=171153&release_id=644640) installed. If not, download and install them from [Sourceforge](http://sourceforge.net/project/showfiles.php?group_id=154155&package_id=171153&release_id=644640).

## Creating our locale file ##

You will need to choose one language for starting from. In source files (e:\python\lib), these translations are available as files that start with _wmlocale (see table in previous section)._

These file names follow the nomenclature wmlocale[\_<ISO 639-1 code>\_](http://pt.wikipedia.org/wiki/ISO_639-1)[<ISO 3166-1 code>](http://pt.wikipedia.org/wiki/ISO_3166-1). ISO 639-1 is a two letters code for representing language names and ISO 3166-1 is another two letters code for country names. Country name may be omitted if the language does not have any variation or Wordmobi does not have this variation yet.

Using this pattern, copy one translation available and rename it according to your language\country (if any). For instance, a UK user could create the file **wmlocale\_en\_uk.py**.

## Translating ##

Below, we have a snippet from locale file wmlocale\_en\_us.py.

```
# -*- coding: cp1252 -*-

# Wordmobi main menu
wm_menu_post = u"Posts"
wm_menu_comm = u"Comments"
wm_menu_tags = u"Tags"
wm_menu_cats = u"Categories"
# ...
wm_err_upd_page = u"Impossible to access update page %s"
wm_err_downld_fail = u"Impossible to download %s"
```

The rules are:

  1. Any line that starts with "#" is a comment. Do not translate or change it.
  1. Lines that need to be translated follows the pattern **variable** = **text to be displayed**. Just translated the second part (text to be displayed), preserving variable name and equal signal.
  1. Do not remove any **%s** or **%d** during translation. They are place holders for including additional information.

## Testing ##

### For non programmers ###

The simple way to test is just replacing some original locale file with yours. I mean, copy you translation contents **inside** wmlocale\_en\_us.py (**overwrite** original contents) and run **default.py**, via Python Shell. Select English\_EUA inside settings menu.

### For programmers ###

If you are comfortable for editing Python code, edit **settings.py** and find the following code snippet, at the end of file:

```
        langs = [ (LABELS.loc.st_menu_en_us, u"en_us"),
                  (LABELS.loc.st_menu_pt_br, u"pt_br"),
                  (LABELS.loc.st_menu_es, u"es"),
                  (LABELS.loc.st_menu_tr, u"tr")]
```

Just modify this array and copy your locale file to e:\python\lib.

For instance, copy **wmlocale\_en\_uk.py** to **e:\python\lib** and change langs as follow:

```
        langs = [ (LABELS.loc.st_menu_en_us, u"en_us"),
                  (LABELS.loc.st_menu_pt_br, u"pt_br"),
                  (LABELS.loc.st_menu_es, u"es"),
                  (LABELS.loc.st_menu_tr, u"tr")
                  (u"English (UK)", u"en_uk") ]
```

**u"English (UK)"** must be unicode and will be presented at language selection menu. u"en\_uk" must match with the end of your locale file name.

## Submitting ##

Just drop me an email with your translation (marcelobarrosalmeida at gmail.com).