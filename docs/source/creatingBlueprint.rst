Create a blueprint
====================

Card Assembler works with tree structure. When calling the plug-in in Gimp,
you specify which node to start at. Its children are then alphabetically
called to formulate respective layer builders. Each layer must include
``commandType`` tag! Accepted values are listed in section :doc:`layerTypes`.

.. _Create a blueprint Nesting:

Nesting
-------

Any node can contain any number of ``next`` tags. Each points to another
node in the tree whose children are appended to the initial node.
This tag can only add new tags, not rewrite the ones already in place.
Intentional usage is inserting card specific tags first and then let
``next`` point to some more general version (i.e. template).

It is useful to create separate color dedicated subtree. Those can then be
exported into Gimp as a palette.

Parsing
-------

If a parameter :class:`type` is not :class:`str`, add attribute ``parse`` to
the parameter's tag with value :class:`int`, :class:`float` or :class:`tuple`
as needed. For example:

.. code:: xml

   <position parse="tuple">100, 125</position>

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

* :file:`Blueprint using a template`
   
   To assemble the this card, use "unique spell example" as **CardIDs**.
   
   The first tag (under the mentioned path) refers to the template for all
   spell cards, where universal details (such as title position) are specified.
   The main part continues by adding card specific details to the
   template-defined layers. Try to follow all ``next`` tags to discover its
   full structure.

   Take notice of the last part tagged ``color``. Using this definition, colors
   can be exported by filling "color" into **PaletteID**.
   
.. _examples: https://github.com/martin-brajer/card-assembler/tree/master/examples
