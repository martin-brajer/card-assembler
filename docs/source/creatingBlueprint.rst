Create a blueprint
====================

Card Assembler works with an XML tree structure. When calling the plug-in
in Gimp, you specify which node to start at. Its children are then
alphabetically called to formulate respective layer builders.

.. warning::
   Each layer must include ``layer_type`` tag! Accepted values are listed in
   section :doc:`layerTypes`.

.. note::
   Term *"layer"* is used a bit vaguely here. Among real layers
   (e.g. background, imported image) are also other commands: selection,
   load a file etc.

.. _Create a blueprint Nesting:

Parsing
-------

If a parameter :class:`type` is not :class:`str`, add attribute ``parse`` to
the parameter's tag with value :class:`int`, :class:`float` or :class:`tuple`
as needed. For example:

.. code:: xml

   <position parse="tuple">100, 125</position>

Concatenation
-------------

If a node have multiple tags with the same name, their contents are
joined by "\\n". The two following pieces of code are equivalent:

.. code:: xml

   <text>Hello,\nWord</text>

.. code:: xml

   <text>Hello,</text>
   <text>Word<text>

Nesting
-------

Any node can contain any number of ``next`` tags.
Intentional usage is inserting card specific tags first and then let
``next`` point to some more general version (i.e. template).

Properties of ``next`` tag:

* points to another node in the data tree whose children are appended to the
  initial node
* can only add new tags, not rewrite the ones already in place
* is executed at the end of a layer definition regardless o its position
* relative order to other ``next`` tags is retained in the execution

It's recommended to place the tag at the beginning of a layer definition for
easier readability.

It is useful to create separate color dedicated subtree. It can be later
exported into Gimp as a palette.

.. code:: xml

    <card>
        <command02_background>
            <next>color black</next>
            <layer_type>monochrome</layer_type>
            <size parse="tuple">800, 500</size>
        </command02_background>
    </card>
    ...
    <color>
        <black>#ffffff</black>
    </color>

Examples
--------

There are two example blueprints in `examples`_ folder. The first one provides
a minimal blueprint to start with. The second one shows intended use.

* :file:`Minimal blueprint.xml`

   To assemble the this card, use "example" as **CardIDs**. There are three
   commands in the file:
   
   #. Blank canvas.
   #. White background.
   #. Text "Example 1" in the middle.

* :file:`Blueprint using a template.xml` + :file:`Data image.xcf`
   
   To assemble the this card, use "unique spell example" as **CardIDs**.
   
   The first tag (under the mentioned path) refers to the template for all
   spell cards, where universal details (such as title position) are specified.
   The main part continues by adding card specific details to the
   template-defined layers. Try to follow all ``next`` tags to discover its
   full structure.

   Take notice of the last part tagged ``color``. Using this definition, colors
   can be exported by filling "color" into **PaletteID**.
   
.. _examples: https://github.com/martin-brajer/card-assembler/tree/master/examples
