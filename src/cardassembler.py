# -*- coding: utf-8 -*-
"""
Main script which handles communication with Gimp.

All code using `gimpfu <https://www.gimp.org/docs/python/index.html>`_
is here. The rest can be found in :mod:`blueprint` module.
Written for `Gimp 2.10.18 <https://www.gimp.org/>`_ which uses
`Python 2.7.18 <https://docs.python.org/release/2.7.18/>`_.

Probably: Gimp runs this script through :func:`eval()` function inside
its installation folder and direct import from different folder raises
*access denied error*. See :meth:`_run_code` function in 
:file:`{Gimp installation folder}/lib/python2.7/runpy.py`.
"""

# ---IMPORTS---
import gimpfu
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import blueprint  # Same folder as this script.

# ---CONSTANTS---
__version__ = blueprint.__version__

# ---FUNCTIONS---
def card_creator(dataFolder, xmlFile, cardIDs, save):
    """ Create board-game cards.
    
    Registered function by ``gimpfu.register()``. Main plugin functionality.
    Add "keepCmdOpen" among **cardIDs** to keep the cmd window open.
    
    :param dataFolder: Blueprints (XML) and data images (XCF) folder
    :type dataFolder: str
    :param xmlFile: Blueprint to be used (with extension)
    :type xmlFile: str
    :param cardIDs: Newline-separated paths to starting nodes.
    :type cardIDs: str
    :param save: Save the images after generation
    :type save: bool
    :raises ValueError: If cardIDs are empty.
    """
    if not cardIDs:
        raise ValueError('No card IDs inserted!')
    dataFolder = dataFolder.decode("utf-8")
    keepCmdOpen = False

    toolbox = Toolbox(dataFolder, xmlFile)
    for cardID in cardIDs.split('\n'):
        if cardID == 'keepCmdOpen':
            keepCmdOpen = True
            continue
        toolbox.create_image(cardID)
        if save:
            toolbox.save_image()
    
    if keepCmdOpen:
        raw_input('\nPress Enter to close this window!')



def palette_creator(dataFolder, xmlFile, paletteID, name):
    """ Create palette.

    Registered function by ``gimpfu.register()``. Supplemental plugin functionality.

    :param dataFolder: Blueprints (XML) folder
    :type dataFolder: str
    :param xmlFile: Blueprint to be used (with extension)
    :type xmlFile: str
    :param paletteID: Path to the starting node.
    :type paletteID: str
    :param name: Name of the created palette
    :type name: str
    :raises ValueError: If the paletteID is empty.
    """    
    if not paletteID:
        raise ValueError('No palette ID inserted!')
    dataFolder = dataFolder.decode("utf-8")
    
    toolbox = Toolbox(dataFolder, xmlFile)
    toolbox.create_palette(paletteID, name)


# ---CLASSES---


class Toolbox():
    """ Blueprint-to-image manipulation tool.

    This class offers means for creating common card components
    (i.e. text, icons). Then completes the image and optionally
    saves it. Probably you'll want to fine-tune the image manually.

    :param dataFolder: Blueprints (XML) and data images (XCF) folder
    :type dataFolder: str
    :param xmlFile: Blueprint to be used (with extension)
    :type xmlFile: str
    """

    def __init__(self, dataFolder, xmlFile):
        self.dataFolder = dataFolder + '\\'
        self.blueprint = blueprint.Blueprint(self.dataFolder + xmlFile)
        print('Blueprint loaded.')
        print('-' * 20)

        self.gimpImage = None
        self.gimpImageImported = {}  # dict{ name: <Gimp image object> }

        #: Directory used in :meth:`save_image`. Relative to
        # :attr:`dataFolder` directory.
        #: 
        #: Defaults to "Saved images".
        self.saveDirectory = 'Saved images/'

        # Specifies how a layer type is interpreted.
        self.addLayer = {
            'image': self._layer_image,
            'monochrome': self._layer_monochrome,
            'import_layer_load': self._layer_import_layer_load,
            'import_layer': self._layer_import_layer,
            'group': self._layer_group,
            'text': self._layer_text,
            'select': self._layer_select,
            'mask': self._layer_mask,
            'hide': self._layer_hide,
        }

    def create_image(self, cardID):
        """Blueprint to image.

        Layout consists of commands which are called alphabetically by name.

        :param cardID: Path to the starting node.
        :type cardID: str
        :raises RuntimeError: If there is no blueprint
        :raises KeyError: If any of the layers has no type
        :raises ValueError: If any of the layers has unknown type
        """        
        if self.blueprint is None:
            raise RuntimeError('Blueprint must be initialized first!')
        
        print('Assembling "{}"'.format(cardID))
        layout = self.blueprint.generate_layout(cardID)
        for layerName in sorted(layout.keys()):
            layer = layout[layerName]
            
            LAYERTYPE = 'layerType'
            if LAYERTYPE not in layer:
                raise KeyError('Layer "{0}" is missing {1} tag.'.format(layerName, LAYERTYPE))

            layerType = layer[LAYERTYPE]
            if layerType not in self.addLayer:
                raise ValueError('Unknown layer type "{0}" in "{1}"'.format(layerType, layerName))

            self.addLayer[layerType](**layer)
            print('Layer "{0}" of type "{1}" done.'.format(layerName, layerType))

        display = gimpfu.pdb.gimp_display_new(self.image)
        print('-' * 20)

    def _layer_image(self, size, name='Card Assembler Image', **kwargs):
        """ Create new image. Needed for layer creation.

        :param size: Image dimensions in pixels
        :type size: tuple
        :param name: Image name, defaults to "Card Assembler Image"
        :type name: str
        """
        self.image = gimpfu.pdb.gimp_image_new(size[0], size[1], gimpfu.RGB)
        gimpfu.pdb.gimp_image_set_filename(self.image, name)
    
    def _layer_monochrome(self, size, color, name='Monochrome', position=(0, 0),
            addToPosition=0, **kwargs):
        """ Single color filled layer.

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
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        newLayer = gimpfu.pdb.gimp_layer_new(
            self.image,
            size[0], size[1],
            gimpfu.RGB,
            name,
            100,
            gimpfu.LAYER_MODE_NORMAL)
        self.image.add_layer(newLayer, addToPosition)
        gimpfu.pdb.gimp_layer_set_offsets(newLayer, *position)
        gimpfu.pdb.gimp_context_set_foreground(color)
        gimpfu.pdb.gimp_drawable_edit_bucket_fill(newLayer, 0, 0, 0)

    def _layer_import_layer_load(self, filename, name, **kwargs):
        """ Load new data image.

        The file has to be in the data folder. Filename is specified in the
        XML file. Name parameter is used in the XML file to reference the
        imported file. That's why it's not an optional parameter.

        :param filename: See description
        :type filename: str
        :param name: Name the data for future use by ``import_layer``
        :type name: str
        
        :raises RuntimeError: If there is no image
        """
        filepath = self.dataFolder + filename
        self.gimpImageImported[name] = gimpfu.pdb.gimp_file_load(
            filepath, filepath)

    def _layer_import_layer(self, targetFile, targetLayer, addToPosition=0,
            name=None, position=(0, 0), **kwargs):
        """ Copy layer from a data image.

        :param targetFile: Use **name** filled in ``import_layer_load``
        :type targetFile: str
        :param targetLayer: Name of the layer to be imported in the target file
        :type targetLayer: str
        :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
        :type addToPosition: int, optional
        :param name: Layer name, defaults to **targetLayer**
        :type name: str or None, optional
        :param position: Defaults to (0, 0)
        :type position: tuple, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')
        if name is None:
            name = targetLayer

        oldLayer = gimpfu.pdb.gimp_image_get_layer_by_name(
            self.gimpImageImported[targetFile], targetLayer)
        newLayer = gimpfu.pdb.gimp_layer_new_from_drawable(oldLayer, self.image)
        self.image.add_layer(newLayer, addToPosition)
        newLayer.name = name
        gimpfu.pdb.gimp_layer_set_offsets(newLayer, *position)

    def _layer_group(self, addToPosition=0, name='Group', **kwargs):
        """ Create new layer group.

        To fill next layers in, set theirs **addToPosition** parameter to -1.

        :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
        :type addToPosition: int, optional
        :param name: Group name, defaults to "Group"
        :type name: str, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        layerGroup = gimpfu.pdb.gimp_layer_group_new(self.image)
        self.image.add_layer(layerGroup, addToPosition)
        layerGroup.name = name

    def _layer_text(self, text, font, fontSize, fontScale=1, addToPosition=0,
            name=None, color='#000000', size=None, lineSpacing=0,
            letterSpacing=0, justification=0, position=(0, 0), **kwargs):
        """ Text layer.

        :param text: Text
        :type text: str
        :param font: Font name
        :type font: str
        :param fontSize: Font size
        :type fontSize: int
        :param fontScale: Multiply **fontSize**, defaults to 1
        :type fontScale: float, optional
        :param addToPosition: Layering (-1 adds the layer to a recently defined group), defaults to 0
        :type addToPosition: int, optional
        :param name: Layer name, defaults to None (Gimp default)
        :type name: str or None, optional
        :param color: Text color in hex code, defaults to “#000000” (black)
        :type color: str, optional
        :param size: Layer dimensions in pixels, defaults to None (autosize)
        :type size: tuple or None
        :param lineSpacing: Line separation change, defaults to 0
        :type lineSpacing: float, optional
        :param letterSpacing: Letters separation change, defaults to 0
        :type letterSpacing: float, optional
        :param justification: Either left(0), right(1), center(2) or fill(3), defaults to 0
        :type justification: int, optional
        :param position: Defaults to (0, 0)
        :type position: tuple, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        fontsize = fontSize * fontScale
        textLayer = gimpfu.pdb.gimp_text_layer_new(
            self.image,
            text,
            font,
            fontsize, 0)
        self.image.add_layer(textLayer, addToPosition)
        if name is not None:
            textLayer.name = name
        gimpfu.pdb.gimp_text_layer_set_color(textLayer, color)
        if size is not None:
            gimpfu.pdb.gimp_text_layer_resize(textLayer, *size)
        gimpfu.pdb.gimp_text_layer_set_line_spacing(textLayer, lineSpacing)
        gimpfu.pdb.gimp_text_layer_set_letter_spacing(textLayer, letterSpacing)
        gimpfu.pdb.gimp_text_layer_set_justification(textLayer, justification)
        gimpfu.pdb.gimp_layer_set_offsets(textLayer, *position)

    def _layer_select(self, mode='select', left=0, right=100, top=0, bottom=100, **kwargs):
        """ New selection by percentage of image size.

        :param mode: Either "select", "selectInvert", or "deselect", defaults to "select"
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
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        if mode == 'select' or mode == 'selectInvert':
            x = round(gimpfu.pdb.gimp_image_width(self.image) * left / 100)
            y = round(gimpfu.pdb.gimp_image_height(self.image) * top / 100)

            width = round(gimpfu.pdb.gimp_image_width(self.image) * right / 100) - x
            height = round(gimpfu.pdb.gimp_image_height(self.image) * bottom / 100) - y

            if width <= 0:
                raise ArithmeticError(
                    'Select: parameter "left" must be lesser than "right".')
            if height <= 0:
                raise ArithmeticError(
                    'Select: parameter "top" must be lesser than "bottom".')

            gimpfu.pdb.gimp_image_select_rectangle(
                self.image,
                0,  # GIMP_CHANNEL_OP_ADD
                x, y, width, height)
            
            # Be aware of possible interference with _layer_mask() deselect part.
            if mode == 'selectInvert':
                gimpfu.pdb.gimp_selection_invert(self.image)
        
        elif mode == 'deselect':
            gimpfu.pdb.gimp_selection_none(self.image)

        else:
            raise ValueError('Select: unknown mode: "{}".'.format(mode))

    def _layer_mask(self, targetLayer, **kwargs):
        """ Mask layer.

        Create mask for given layer from given selection.

        :param targetLayer: Target layer to be masked
        :type targetLayer: str
        :param kwargs: Additional named arguments are passed to ``select``
        :type kwargs: various, optional
        """
        self._layer_select(**kwargs)

        newLayer = gimpfu.pdb.gimp_image_get_layer_by_name(self.image, targetLayer)
        mask = gimpfu.pdb.gimp_layer_create_mask(newLayer, 4)  # GIMP_ADD_SELECTION_MASK
        gimpfu.pdb.gimp_layer_add_mask(newLayer, mask)

        kwargs['mode'] = 'deselect'
        self._layer_select(**kwargs)

    def _layer_hide(self, **kwargs):
        """ Ignore command.

        Meant for overrides, i.e. hiding a predefined (template) layer.
        """
        pass

    def save_image(self):
        """ Save the image as **image.name**.xcf into :attr:`saveDirectory` subfolder. """
        directory = self.dataFolder + self.saveDirectory
        if not os.path.exists(directory):
            os.makedirs(directory)
            print('Directory created: {0}'.format(directory))
        filename = directory + gimpfu.pdb.gimp_image_get_name(self.image) + '.xcf'
        gimpfu.pdb.gimp_xcf_save(0, self.image, None, filename, filename)

    def create_palette(self, paletteID, name):
        """ Blueprint to palette.

        Colors are sorted by their branch hight and then alphabetically.

        :param paletteID: Path to the starting node.
        :type paletteID: str
        :param name: Created palette name
        :type name: str
        """        
        palette = gimpfu.pdb.gimp_palette_new(name)
        gimpfu.pdb.gimp_palette_set_columns(palette, 1)

        for name, color in self.blueprint.generate_palette(paletteID):
            gimpfu.pdb.gimp_palette_add_entry(palette, name, color)


# ---REGISTER---

gimpfu.register(
    "CA_palette_assembler",  # Name registered in Procedure Browser (blurb).
    "Create palette." + " " * 50,  # Widget title (proc_name).
    "Create palette.",  # Help.
    "Martin Brajer",  # Author.
    "Martin Brajer",  # Copyright holder.
    "May 2020",  # Date.
    "Palette Assembler",  # Menu Entry (label).
    "",  # Image Type - no image required (imagetypes).
    [  # (params).
        (gimpfu.PF_DIRNAME, "dataFolder", "Data folder:", os.path.expanduser('~')),
        (gimpfu.PF_STRING, "xmlFile", "XML file:", "Blueprint.xml"),
        (gimpfu.PF_TEXT, "paletteID", "Palette ID:", "color"),
        (gimpfu.PF_TEXT, "name", "Name:", "Card Assembler Palette"),
    ],
    [],  # (results).
    palette_creator,  # Matches to name of function being defined (function).
    menu="<Image>/Card Assembler"  # Menu item location.
)

gimpfu.register(
    "CA_card_assembler",  # Name registered in Procedure Browser (blurb).
    "Create board-game cards." + " " * 40,  # Widget title (proc_name).
    "Create board-game cards.",  # Help.
    "Martin Brajer",  # Author.
    "Martin Brajer",  # Copyright holder.
    "April 2020",  # Date.
    "Card Assembler",  # Menu Entry (label).
    "",  # Image Type - no image required (imagetypes).
    [  # (params).
        (gimpfu.PF_DIRNAME, "dataFolder", "Data folder:", os.path.expanduser('~')),
        (gimpfu.PF_STRING, "xmlFile", "XML file:", "Blueprint.xml"),
        (gimpfu.PF_TEXT, "cardIDs", "Card IDs:", ""),
        (gimpfu.PF_BOOL, "save", "Save:", False),
    ],
    [],  # (results).
    card_creator,  # Matches to name of function being defined (function).
    menu="<Image>/Card Assembler"  # Menu item location.
)

gimpfu.main()
