Layer types
===========

Parameters here show tags of xml blueprint relevant for given layer types.

Additionally, all commands can use ``next`` tag. See `creatingBlueprints`.

.. method:: image()
   
   Create new image. Needed for layer creation.

   :param size: Image dimensions in pixels
   :type size: tuple
   :param name: Image name, defaults to "Card Assembler Image"
   :type name: str

.. method:: monochrome()
   
   Single colour filled layer.

   :param size: Layer dimensions in pixels
   :type size: tuple
   :param color: Hex code
   :type color: str
   :param name: Layer name, defaults to "Monochrome"
   :type name: str, optional
   :param position: Defaults to (0, 0)
   :type position: tuple, optional
   :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
   :type addToPosition: int, optional
   :raises RuntimeError: If there is no image

.. method:: import_layer_load()

   Load new data image.

   The file has to be in the data folder. Filename is specified in the
   xml file. Name parameter is used in xml file to reference the imported
   file. That's why it's not optional parameter.

   :param filename: See description
   :type filename: str
   :param name: Name the data for future use by ``import_layer``
   :type name: str
   
   :raises RuntimeError: If there is no image

.. method:: import_layer()
   
   Copy layer from a data image.

   :param targetFile: Use **name** filled in ``import_layer_load``
   :type targetFile: str
   :param targetLayer: Name of the layer to be imported in the target file
   :type targetLayer: str
   :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
   :type addToPosition: int, optional
   :param name: Layer name, defaults to **targetLayer**
   :type name: str, optional
   :param position: Defaults to (0, 0)
   :type position: tuple, optional
   :raises RuntimeError: If there is no image

.. method:: group()

   Create new layer group.

   To fill next layers in, set theirs **addToPosition** parameter to -1.

   :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
   :type addToPosition: int, optional
   :param name: Group name, defaults to "Group"
   :type name: str, optional
   :raises RuntimeError: If there is no image

.. method:: text()
   
   Text layer.

   :param text: Text
   :type size: str
   :param font: Font name
   :type font: str
   :param fontSize: Font size
   :type fontSize: int
   :param fontScale: Multiply **fontSize**, defaults to 1
   :type fontScale: float, optional
   :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
   :type addToPosition: int, optional
   :param name: Layer name, defaults to "Text Layer" (Gimp default)
   :type name: str, optional
   :param color: Text color in hex code, defaults to “#000000” (black)
   :type color: str, optional
   :param size: Layer dimensions in pixels, defaults to *autosize*
   :type size: tuple
   :param lineSpacing: Line separation change, defaults to 0
   :type lineSpacing: float, optional
   :param letterSpacing: Letters separation change, defaults to 0
   :type letterSpacing: float, optional
   :param justification: Either left(0), right(1), center(2) or fill(3), defaults to 0
   :type justification: int, optional
   :param position: Defaults to (0, 0)
   :type position: tuple, optional
   :raises RuntimeError: If there is no image

.. method:: select()
   
   New selection by percentage of image size.

   :param mode: Either "select" or "deselect", defaults to the former one
   :type mode: str
   :param left: Left edge position in percentage of the image size, defaults to 0
   :type left: float, optional
   :param right: Right edge position in percentage of the image size, defaults to 100
   :type right: float, optional
   :param top: Top edge position in percentage of the image size, defaults to 0
   :type top: float, optional
   :param botton: Bottom edge position in percentage of the image size, defaults to 100
   :type bottom: float, optional
   :raises RuntimeError: If there is no image
   :raises ArithmeticError: If width is not positive
   :raises ArithmeticError: If height is not positive
   :raises ValueError: If mode is unknown

.. method:: mask()

   Mask layer.

   Create mask for given layer from given selection.

   :param layer: Target layer to select from
   :type layer: str
   :param parameters: Other parameters to be passed to ``select``
   :type parameters: ``select``

.. method:: hide()
   
   Ignore command.

   Meant for overrides, i.e. hiding a predefined (template) layer.
