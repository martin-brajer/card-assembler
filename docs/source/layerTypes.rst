Layer types
===========

All layer nodes can use ``next`` tag, see
:ref:`Creating blueprint > Nesting <Create a blueprint Nesting>`.
In the following list of layer types parameters are formatted as follows:

* **name** (:class:`type`, ``default if optional``) Description

.. _group:
.. note::
    Setting ``add_to_position = -1`` adds the layer to a recently defined
    group.

image
-----
   
Create new image. Needed for any layer creation.

* **size** (:class:`tuple`) Image dimensions in pixels note
* **name** (:class:`str`, ``Card Assembler Image``) Image name

monochrome
----------
   
Single color filled layer.

* **size** (:class:`tuple`) Layer dimensions in pixels
* **color** (:class:`str`) Layer color in hex code
* **name** (:class:`str`, ``Monochrome``): Layer name
* **position** (:class:`tuple`, ``0, 0``)
* **add_to_position** (:class:`int`, ``0``) Position among layers (``-1`` for group_)

import_layer_load
-----------------

Load new data image. The file has to be in the data folder. Filename is
specified in the XML file. Name parameter is used in the XML file to reference
the imported file. That’s why it’s not an optional parameter.

* **filename** (:class:`str`) See description
* **name** (:class:`str`) Name the data for future use by `import_layer`_

import_layer
------------
   
Copy layer from a data image.

* **target_file** (:class:`str`) Use **name** filled in `import_layer_load`_
* **target_layer** (:class:`str`) Name of the layer to be imported in the target file
* **add_to_position** (:class:`int`, ``0``) Position among layers (``-1`` for group_)
* **name** (:class:`str`, **target_layer**) Layer name
* **position** (:class:`tuple`, ``0, 0``)

group
-----

Create new layer group. To fill next layers in, set theirs **add_to_position**
parameter to ``-1``.

* **add_to_position** (:class:`int`, ``0``) Position among layers (``-1`` for group_)
* **name** (:class:`str`, ``Group``) Group name

text
----

Text layer.

* **text** (:class:`str`) Text
* **font** (:class:`str`) Font name
* **font_size** (:class:`int`) Font size
* **font_scale** (:class:`float`, ``1``) Multiply **font_size**
* **add_to_position** (:class:`int`, ``0``) Position among layers (``-1`` for group_)
* **name** (:class:`str`, Gimp default = ``Text Layer``) Layer name
* **color** (:class:`str`, ``#000000``) Text color in hex code
* **size** (:class:`tuple`, autosize) Layer dimensions in pixels
* **line_spacing** (:class:`float`, ``0``) Line separation change
* **letter_spacing** (:class:`float`, ``0``) Letters separation change
* **justification** (:class:`int`, ``0``) Either left (``0``), right (``1``),
  center (``2``) or fill (``3``)
* **position** (:class:`tuple`, ``0, 0``)

select
------

New selection by percentage of image size.

* **mode** (:class:`str`, ``select``) Either ``select``, ``select_invert`` or ``deselect``
* **left** (:class:`float`, ``0``) Left edge position in percentage of the image size
* **right** (:class:`float`, ``100``) Right edge position in percentage of the image size
* **top** (:class:`float`, ``0``) Top edge position in percentage of the image size
* **botton** (:class:`float`, ``100``) Bottom edge position in percentage of the image size

mask
----

Mask layer. Create a mask for the given layer from the given selection.

* **target_layer** (:class:`str`) Layer to be masked
* other parameters are passed to `select`_

hide
----

Ignore command. Used for overrides, i.e. hiding a predefined (template) layer.
