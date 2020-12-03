Creating Blueprint.xml
======================

Card Assembler works with tree structure. When calling the plug-in in Gimp,
you specify the node where to start. Its children are then alphabetically
called to formulate respective layer builders. Each layer must have
``commandType`` tag! Accepted values are listed with details in section
:doc:`layerTypes`

Nesting
-------

Command can contain any number of ``next`` tags. Each points to another
node in the tree whose children are appended to the initial command.
This tag can only add new tags, not rewrite the old ones. Intentional
usage is inserting card specific tags first and then let ``next`` point
to some more general version (i.e. template).

It is useful to create separate color dedicated subtree. See `Palette
Creator parameters <README.md#palette-creator-parameters>`__.

Parsing
-------

If a parameter type is not *string*, add attribute ``parse`` to the
parameter's tag with value ``int``, ``float`` or ``tuple`` as needed.

For example: ``<position parse="tuple">100, 125</position>``.

Command types
-------------

* image
  * size (tuple)
  * name (string)
* monochrome
  * size (tuple)
  * color (string) - hex code
  * *name (string) = "Monochrome"*
  * *position (tuple) = (0, 0)*
  * *addToPosition (int) = 0* - ``-1`` adds to just defined group
* import\_layer\_load
  * filename (string)
  * name (string)
* import\_layer
  * targetFile (string) - use ``name`` filled in import\_layer\_load
  * targetLayer (string)
  * *name (string) = targetLayer*
  * *position (tuple) = (0, 0)*
  * *addToPosition (int) = 0*
* group
  * *name (string) = "Group"*
  * *addToPosition (int) = 0*
* text
  * text (string)
  * font (string)
  * fontSize (int)
  * *fontScale (float) = 1*
  * *name (string) = "Text Layer"*
  * *color (string) = "#000000"*
  * *size (tuple) = autosize*
  * *lineSpacing (float) = 0*
  * *letterSpacing (float) = 0*
  * *justification (int) = 0* - left: ``0``, right: ``1``, center: ``2``, fill: ``3``
  * *position (tuple) = (0, 0)*
  * *addToPosition (int) = 0*
* select
  * *mode(string) = "select"* - possible values: ``select``, ``deselect``, any other
  * *left(float) = 0* - dimensions in percentage of image size
  * *right(float) = 100*
  * *top(float) = 0*
  * *bottom(float) = 100*
* mask
  * layer(string)
  * *<``select`` commands>*
* hide
  * *no parameters*

Additionally, **all commands** can use ```next``
tag `<README.md#nesting>`__.

Examples
========

There are two example blueprints in
```cardassembler_data`` `<../../tree/master/CardAssembler_Data>`__
folder. One shows very simple blueprint to start with. The second one
shows intended use.

Simple
------

``Blueprint_Example_Simple.xml`` shows very simple blueprint to make
sense of how this plug-in works.

The only card there can be created by filling ``example`` into CardIDs
field.

Full
----

``Blueprint_Example_Full.xml`` shows intended usage including structure
to make adding more similar items easier and clearer.

The only card there can be created by filling ``unique spell example``
into CardIDs field. Colors can be exported by filling ``color`` into
`PaletteID field <README.md#palette-creator-parameters>`__.
