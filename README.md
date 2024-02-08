# ruamel.yaml

`ruamel.yaml` is a YAML 1.2 loader/dumper package for Python.
<table class="docutils">
  <tr>    <td>version</td>
    <td>0.18.4</td>
  </tr>
  <tr>    <td>updated</td>
    <td>2023-11-01</td>
  </tr>
  <tr>    <td>documentation</td>
    <td><a href="https://yaml.readthedocs.io">https://yaml.readthedocs.io</a></td>
  </tr>
  <tr>    <td>repository</td>
    <td><a href="https://sourceforge.net/projects/ruamel-yaml">https://sourceforge.net/projects/ruamel-yaml</a></td>
  </tr>
  <tr>    <td>pypi</td>
    <td><a href="https://pypi.org/project/ruamel.yaml">https://pypi.org/project/ruamel.yaml</a></td>
  </tr>
</table>

As announced, in 0.18.0, the old PyYAML functions have been deprecated.
(`scan`, `parse`, `compose`, `load`, `emit`, `serialize`, `dump` and their variants
(`_all`, `safe_`, `round_trip_`, etc)). If you only read this after your program has 
stopped working: I am sorry to hear that, but that also means you, or the person 
developing your program, has not tested with warnings on (which is the recommendation 
in PEP 565, and e.g. defaultin when using `pytest`). If you have troubles, explicitly use
```
pip install "ruamel.yaml<0.18.0"
```
or put something to that effects in your requirments, to give yourself
some time to solve the issue.

There will be at least one more potentially breaking change in the 0.18 series: `YAML(typ='unsafe')`
now has a pending deprecation warning and is going to be deprecated, probably before the end of 2023.
If you only use it to dump, please use the new `YAML(typ='full')`, the result of that can be *safely*
loaded with a default  instance `YAML()`, as that will get you inspectable, tagged, scalars, instead of
executed Python functions/classes. (You should probably add constructors for what you actually need, 
but I do consider adding a `ruamel.yaml.unsafe` package that will re-add the `typ='unsafe'` option.
*Please adjust/pin your dependencies accordingly if necessary.*


There seems to be a CVE on `ruamel.yaml`, stating that the `load()` function could be abused 
because of unchecked input. `load()` was never the default function (that was `round_trip_load()`
before the new API came into existence`. So the creator of that CVE was ill informed and
probably lazily assumed that since `ruamel.yaml` is a derivative of PyYAML (for which
a similar CVE exists), the same problem would still exist, without checking. 
So the CVE was always inappriate,  now just more so, as the call
to the function `load()` with any input will terminate your program with an error message. If you 
(have to) care about such things as this CVE, my recommendation is to stop using Python
completely, as `pickle.load()` can be abused in the same way as `load()` (and like unlike `load()` 
is only documented to be unsafe, without development-time warning. 

Version 0.17.21 was the last one tested to be working on Python 3.5 and 3.6<BR>
The 0.16.13 release was the last that was tested to be working on Python 2.7.


There are two extra plug-in packages
(`ruamel.yaml.bytes` and `ruamel.yaml.string`)
for those not wanting to do the streaming to a
`io.BytesIO/StringIO` buffer themselves.

If your package uses `ruamel.yaml` and is not listed on PyPI, drop me an
email, preferably with some information on how you use the package (or a
link to the repository) and I'll keep you informed when the status of
the API is stable enough to make the transition.

<pre>
    <a href="overview/#overview">Overview</a>

    <a href="install/#installing">Installing</a>
      <a href="install/#optional-requirements">Optional requirements</a>

    <a href="basicuse/#basic-usage">Basic Usage</a>
      <a href="basicuse/#load-and-dump">Load and dump  </a>
      <a href="basicuse/#more-examples">More examples</a>

    <a href="dumpcls/#working-with-python-classes">Working with Python classes</a>
      <a href="dumpcls/#dumping-python-classes">Dumping Python classes</a>
      <a href="dumpcls/#dataclass">Dataclass</a>

    <a href="detail/#details">Details</a>
      <a href="detail/#indentation-of-block-sequences">Indentation of block sequences</a>
        <a href="detail/#inconsistently-indented-yaml">Inconsistently indented YAML</a>
        <a href="detail/#indenting-using-typsafe">Indenting using `typ="safe"`</a>
      <a href="detail/#positioning-in-top-level-mappings-prefixing">Positioning ':' in top level mappings, prefixing ':'</a>
        <a href="detail/#document-version-support">Document version support</a>
        <a href="detail/#round-trip-including-comments">Round trip including comments</a>
    <a href="detail/#config-file-formats">Config file formats</a>
    <a href="detail/#extending">Extending</a>
    <a href="detail/#smartening">Smartening</a>

    <a href="example/#examples">Examples</a>
      <a href="example/#output-of-dump-as-a-string">Output of `dump()` as a string</a>

    <a href="api/#departure-from-previous-api">Departure from previous API</a>
      <a href="api/#loading">Loading</a>
        <a href="api/#duplicate-keys">Duplicate keys</a>
      <a href="api/#dumping-a-multi-document-yaml-stream">Dumping a multi-document YAML stream</a>
      <a href="api/#dumping">Dumping</a>
        <a href="api/#controls">Controls</a>
      <a href="api/#transparent-usage-of-new-and-old-api">Transparent usage of new and old API</a>
      <a href="api/#reason-for-api-change">Reason for API change</a>

    <a href="pyyaml/#differences-with-pyyaml">Differences with PyYAML</a>
      <a href="pyyaml/#defaulting-to-yaml-12-support">Defaulting to YAML 1.2 support</a>
      <a href="pyyaml/#py2py3-reintegration">PY2/PY3 reintegration</a>
      <a href="pyyaml/#fixes">Fixes</a>
      <a href="pyyaml/#testing">Testing</a>
      <a href="pyyaml/#api">API</a>

    <a href="contributing/#contributing">Contributing</a>
      <a href="contributing/#documentation">Documentation</a>
      <a href="contributing/#code">Code</a>
        <a href="contributing/#flake">Flake</a>
        <a href="contributing/#toxpytest">Tox/pytest</a>
        <a href="contributing/#typingmypy">Typing/mypy</a>
      <a href="contributing/#generated-files">Generated files</a>
      <a href="contributing/#vulnerabilities">Vulnerabilities</a>
</pre>


[![image](https://readthedocs.org/projects/yaml/badge/?version=latest)](https://yaml.readthedocs.org/en/latest?badge=latest)[![image](https://bestpractices.coreinfrastructure.org/projects/1128/badge)](https://bestpractices.coreinfrastructure.org/projects/1128)
[![image](https://sourceforge.net/p/ruamel-yaml/code/ci/default/tree/_doc/_static/license.svg?format=raw)](https://opensource.org/licenses/MIT)
[![image](https://sourceforge.net/p/ruamel-yaml/code/ci/default/tree/_doc/_static/pypi.svg?format=raw)](https://pypi.org/project/ruamel.yaml/)
[![image](https://sourceforge.net/p/oitnb/code/ci/default/tree/_doc/_static/oitnb.svg?format=raw)](https://pypi.org/project/oitnb/)
[![image](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# ChangeLog

0.18.4 (2023-11-01):

- YAML() instance has a `doc_infos` attribute which is a cumulative list of DocInfo instances (one for `load()`, one per document for `load_all()`). DocInfo instances contain version information (requested, directive) and tag directive information
- fix issue that the YAML instance tags attribute was not reset between documents, resulting in mixing of tag directives of multiple documents. Now only provides tag directive information on latest document after loading. This means tags for dumping must be set **again** after a document is loaded with the same instance. (because of this tags will be removed in a favour of a different mechanism in the future)
- fix issue with multiple document intermixing YAML 1.2 and YAML 1.1, the VersionedResolver now resets
- fix issue with disappearing comment when next token was Tag (still can't have both a comment before a tag and after a tag, before node)

0.18.3 (2023-10-29):

- fix issue with spurious newline on first item after comment + nested block sequence
- additional links in the metadata on PyPI (Reported, with pointers how to fix, by [Sorin](https://sourceforge.net/u/ssbarnea/profile/)).

0.18.2 (2023-10-24):

- calling the deprecated functions now raises an `AttributeError` with the, somewhat more informative, orginal warning message. Instead of calling `sys.exit(1)`

0.18.1 (2023-10-24):

- calling the deprecated functions now always displays the warning message. (reported by [Trend Lloyd](https://sourceforge.net/u/lathiat2/profile/))

0.18.0 (2023-10-23):

- the **functions** `scan`, `parse`, `compose`, `load`, `emit`, `serialize`, `dump` and their variants (`_all`, `safe_`, `round_trip_`, etc) have been deprecated (the same named **methods** on `YAML()` instances are, of course, still there.
- `YAML(typ='unsafe')` now issues a `PendingDeprecationWarning`. This will become deprecated in the 0.18 series
(probably before the end of 2023).
You can use `YAML(typ='full')` to dump unregistered Python classes/functions. 
For loading you'll have to register your classes/functions
if you want the old, unsafe, functionality. You can still load any tag, like `!!python/name:posix.system', **safely** 
with the (default) round-trip parser.
- fix for `bytes-like object is required not 'str' while dumping binary streams`. This was reported, analysed and a fix provided by [Vit Zikmund](https://sourceforge.net/u/tlwhitec/profile/)

0.17.40 (2023-10-20):

- flow style sets are now preserved ( `!!set {a, b, c} )`. Any values specified when loading are dropped, including `!!null ""`.
- potential workaround for issue 484: the long_description_content_type including the variant specification `CommonMark`
can result in problems on Azure. If you can install from `.tar.gz` using
`RUAMEL_NO_LONG_DESCRIPTION=1 pip install ruamel.yaml --no-binary :all:` then the long description, and its
offending type, are nog included (in the METADATA). 
(Reported by [Coury Ditch](https://sourceforge.net/u/cmditch/profile/))
- links in documentation update (reported by [David Hoese](https://sourceforge.net/u/daveydave400/profile/))
- Added some `__repr__` for internally used classes

0.17.39 (2023-10-19):

- update README generation, no code changes

0.17.36 (2023-10-19):

- fixed issue 480, dumping of a loaded empty flow-style mapping with comment failed (Reported by [Stéphane Brunner](https://sourceforge.net/u/stbrunner/profile/))
- fixed issue 482, caused by DEFAULT_MAPPING_TAG having changes to being a `Tag()` instance, not a string (reported by [yan12125](https://sourceforge.net/u/yan12125/profile/))
- updated documentation to use mkdocs

0.17.35 (2023-10-04):

- support for loading dataclasses with `InitVar` variables (some special coding was necessary to get the, unexecpected, default value in the corresponding instance attribute ( example of usage in [this question](https://stackoverflow.com/q/77228378/1307905))

0.17.34 (2023-10-03):

- Python 3.12 also loads C version when using `typ='safe'`
- initial support for loading invoking
`__post_init__()` on dataclasses that have that
method after loading a registered dataclass.
(Originally
[asked](https://stackoverflow.com/q/51529458/1307905) on
Stackoverflow by
[nyanpasu64](https://stackoverflow.com/users/2683842/nyanpasu64)
and as
[ticket](https://sourceforge.net/p/ruamel-yaml/tickets/355/) by
[Patrick Lehmann](https://sourceforge.net/u/paebbels/profile/))

```
@yaml.register_class
@dataclass
class ...
```

0.17.33 (2023-09-28):

- added `flow_seq_start`, `flow_seq_end`, `flow_seq_separator`, `flow_map_start`, `flow_map_end`, `flow_map_separator` **class** attributes to the `Emitter` class so flow style output can more easily be influenced (based on [this answer](https://stackoverflow.com/a/76547814/1307905) on a StackOverflow question by [Huw Walters](https://stackoverflow.com/users/291033/huw-walters)).

0.17.32 (2023-06-17):

- fix issue with scanner getting stuck in infinite loop

0.17.31 (2023-05-31):

- added tag.setter on `ScalarEvent` and on `Node`, that takes either a `Tag` instance, or a str (reported by [Sorin Sbarnea](https://sourceforge.net/u/ssbarnea/profile/))

0.17.30 (2023-05-30):

- fix issue 467, caused by Tag instances not being hashable (reported by [Douglas Raillard](https://bitbucket.org/%7Bcf052d92-a278-4339-9aa8-de41923bb556%7D/))

0.17.29 (2023-05-30):

- changed the internals of the tag property from a string to a class which allows for preservation of the original handle and suffix. This should result in better results using documents with %TAG directives, as well as preserving URI escapes in tag suffixes.

0.17.28 (2023-05-26):

- fix for issue 464: documents ending with document end marker
without final newline fail to load (reported by [Mariusz
Rusiniak](https://sourceforge.net/u/r2dan/profile/))

0.17.27 (2023-05-25):

- fix issue with inline mappings as value for merge keys (reported by Sirish on [StackOverflow](https://stackoverflow.com/q/76331049/1307905))
- fix for 468, error inserting after accessing merge attribute on `CommentedMap` (reported by [Bastien gerard](https://sourceforge.net/u/bagerard/))
- fix for issue 461 pop + insert on same `CommentedMap` key throwing error (reported by [John Thorvald Wodder II](https://sourceforge.net/u/jwodder/profile/))

0.17.26 (2023-05-09):

- fix for error on edge cage for issue 459

0.17.25 (2023-05-09):

- fix for regression while dumping wrapped strings with too many backslashes removed (issue 459, reported by [Lele Gaifax](https://sourceforge.net/u/lele/profile/))

0.17.24 (2023-05-06):

- rewrite of `CommentedMap.insert()`. If you have a merge key in the YAML document for the mapping you insert to, the position value should be the one as you look at the YAML input. This fixes issue 453 where other keys of a merged in mapping would show up after an insert (reported by [Alex Miller](https://sourceforge.net/u/millerdevel/profile/)). It also fixes a call to `.insert()` resulting into the merge key to move to be the first key if it wasn't already and it is also now possible to insert a key before a merge key (even if the fist key in the mapping).
- fix (in the pure Python implementation including default) for issue 447. (reported by [Jack Cherng](https://sourceforge.net/u/jfcherng/profile/), also brought up by brent on [StackOverflow](https://stackoverflow.com/q/40072485/1307905))

0.17.23 (2023-05-05):

- fix 458, error on plain scalars starting with word longer than width. (reported by [Kyle Larose](https://sourceforge.net/u/klarose/profile/))
- fix for `.update()` no longer correctly handling keyword arguments (reported by John Lin on [StackOverflow]( https://stackoverflow.com/q/76089100/1307905))
- fix issue 454: high Unicode (emojis) in quoted strings always
escaped (reported by [Michal
Čihař](https://sourceforge.net/u/nijel/profile/) based on a
question on StackOverflow).
- fix issue with emitter conservatively inserting extra backslashes in wrapped quoted strings (reported by thebenman on [StackOverflow](https://stackoverflow.com/q/75631454/1307905))

0.17.22 (2023-05-02):

- fix issue 449 where the second exclamation marks got URL encoded (reported and fixing PR provided by [John Stark](https://sourceforge.net/u/jods/profile/))
- fix issue with indent != 2 and literal scalars with empty first line (reported by wrdis on [StackOverflow](https://stackoverflow.com/q/75584262/1307905))
- updated `__repr__` of CommentedMap, now that Python's dict is ordered -> no more `ordereddict(list-of-tuples)`
- merge MR 4, handling OctalInt in YAML 1.1 (provided by [Jacob Floyd](https://sourceforge.net/u/cognifloyd/profile/))
- fix loading of `!!float 42` (reported by Eric on [Stack overflow](https://stackoverflow.com/a/71555107/1307905))
- line numbers are now set on `CommentedKeySeq` and `CommentedKeyMap` (which are created if you have a sequence resp. mapping as the key in a mapping)
- plain scalars: put single words longer than width on a line of
their own, instead of after the previous line (issue 427, reported
by [Antoine
Cotten](https://sourceforge.net/u/antoineco/profile/)). Caveat:
this currently results in a space ending the previous line.
- fix for folded scalar part of 421: comments after ">" on first
line of folded scalars are now preserved (as were those in the
same position on literal scalars). Issue reported by Jacob Floyd.
- added stacklevel to warnings
- typing changed from Py2 compatible comments to Py3, removed various Py2-isms

0.17.21 (2022-02-12):

- fix bug in calling `.compose()` method with `pathlib.Path` instance.

0.17.20 (2022-01-03):

- fix error in microseconds while rounding datetime fractions >= 9999995 (reported by [Luis Ferreira](https://sourceforge.net/u/ljmf00/))

0.17.19 (2021-12-26):

- fix mypy problems (reported by [Arun](https://sourceforge.net/u/arunppsg/profile/))

0.17.18 (2021-12-24):

- copy-paste error in folded scalar comment attachment (reported by [Stephan Geulette](https://sourceforge.net/u/sgeulette/profile/))
- fix 411, indent error comment between key empty seq value (reported by [Guillermo Julián](https://sourceforge.net/u/gjulianm/profile/))

0.17.17 (2021-10-31):

- extract timestamp matching/creation to util

0.17.16 (2021-08-28):

- 398 also handle issue 397 when comment is newline

0.17.15 (2021-08-28):

- fix issue 397, insert comment before key when a comment between key and value exists (reported by [Bastien gerard](https://sourceforge.net/u/bagerard/))

0.17.14 (2021-08-25):

- fix issue 396, inserting key/val in merged-in dictionary (reported by [Bastien gerard](https://sourceforge.net/u/bagerard/))

0.17.13 (2021-08-21):

- minor fix in attr handling

0.17.12 (2021-08-21):

- fix issue with anchor on registered class not preserved and those classes using package attrs with `@attr.s()` (both reported by [ssph](https://sourceforge.net/u/sph/))

0.17.11 (2021-08-19):

- fix error baseclass for `DuplicateKeyError` (reported by [Łukasz Rogalski](https://sourceforge.net/u/lrogalski/))
- fix typo in reader error message, causing `KeyError` during reader error (reported by [MTU](https://sourceforge.net/u/mtu/))

0.17.10 (2021-06-24):

- fix issue 388, token with old comment structure != two elements (reported by [Dimitrios Bariamis](https://sourceforge.net/u/dbdbc/))

0.17.9 (2021-06-10):

- fix issue with updating CommentedMap (reported by sri on [StackOverflow](https://stackoverflow.com/q/67911659/1307905))

0.17.8 (2021-06-09):

- fix for issue 387 where templated anchors on tagged object did get set resulting in potential id reuse. (reported by [Artem Ploujnikov](https://sourceforge.net/u/flexthink/))

0.17.7 (2021-05-31):

- issue 385 also affected other deprecated loaders (reported via email by Oren Watson)

0.17.6 (2021-05-31):

- merged type annotations update provided by [Jochen Sprickerhof](https://sourceforge.net/u/jspricke/)
- fix for issue 385: deprecated round_trip_loader function not
working (reported by [Mike
Gouline](https://sourceforge.net/u/gouline/))
- wasted a few hours getting rid of mypy warnings/errors

0.17.5 (2021-05-30):

- fix for issue 384 `!!set` with aliased entry resulting in broken YAML on rt reported by [William Kimball](https://sourceforge.net/u/william303/))

0.17.4 (2021-04-07):

- prevent (empty) comments from throwing assertion error (issue 351 reported by [William Kimball](https://sourceforge.net/u/william303/)) comments (or empty line) will be dropped

0.17.3 (2021-04-07):

- fix for issue 382 caused by an error in a format string (reported by [William Kimball](https://sourceforge.net/u/william303/))
- allow expansion of aliases by setting `yaml.composer.return_alias = lambda s: copy.deepcopy(s)`
(as per [Stackoverflow answer](https://stackoverflow.com/a/66983530/1307905))

0.17.2 (2021-03-29):

- change -py2.py3-none-any.whl to -py3-none-any.whl, and remove 0.17.1

0.17.1 (2021-03-29):

- added 'Programming Language :: Python :: 3 :: Only', and
removing 0.17.0 from PyPI (reported by [Alasdair
Nicol](https://sourceforge.net/u/alasdairnicol/))

0.17.0 (2021-03-26):

- removed because of incomplete classifiers
- this release no longer supports Python 2.7, most if not all Python 2 specific code is removed. The 0.17.x series is the last to support Python 3.5 (this also allowed for removal of the dependency on `ruamel.std.pathlib`)
- remove Python2 specific code branches and adaptations (u-strings)
- prepare % code for f-strings using `_F`
- allow PyOxidisation ([issue 324](https://sourceforge.net/p/ruamel-yaml/tickets/324/) resp. [issue 171](https://github.com/indygreg/PyOxidizer/issues/171))
- replaced Python 2 compatible enforcement of keyword arguments with '*'
- the old top level *functions* `load`, `safe_load`, `round_trip_load`, `dump`, `safe_dump`, `round_trip_dump`, `scan`, `parse`, `compose`, `emit`, `serialize` as well as their `_all` variants for multi-document streams, now issue a `PendingDeprecationning` (e.g. when run from pytest, but also Python is started with `-Wd`). Use the methods on `YAML()`, which have been extended.
- fix for issue 376: indentation changes could put literal/folded
scalar to start before the `#` column of a following comment.
Effectively making the comment part of the scalar in the output.
(reported by [Bence Nagy](https://sourceforge.net/u/underyx/))

------------------------------------------------------------------------

For older changes see the file
[CHANGES](https://sourceforge.net/p/ruamel-yaml/code/ci/default/tree/CHANGES)
