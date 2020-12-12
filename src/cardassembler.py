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


__all__ = []
# Needs :class:`blueprint`. See below.
__version__ = None
__author__ = None


import os
import sys

import gimpfu

# Same folder as this script.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import blueprint  # nopep8


__version__ = blueprint.__version__
__author__ = blueprint.__author__


def card_creator(data_folder, xml_file, card_IDs, save):
    """ Create board-game cards.

    Registered function by ``gimpfu.register()``. Main plugin
    functionality. Add "keepCmdOpen" among **cardIDs** to keep
    the cmd window open.

    :param data_folder: Blueprints (XML) and data images (XCF) folder
    :type data_folder: str
    :param xml_file: Blueprint to be used (with extension)
    :type xml_file: str
    :param card_IDs: Newline-separated paths to starting nodes.
    :type card_IDs: str
    :param save: Save the images after generation
    :type save: bool
    :raises ValueError: If cardIDs are empty.
    """
    if not card_IDs:
        raise ValueError('No card IDs inserted!')
    data_folder = data_folder.decode('utf-8')
    keep_cmd_open = False

    toolbox = Toolbox(data_folder, xml_file)
    for card_ID in card_IDs.split('\n'):
        if card_ID == 'keepCmdOpen':
            keep_cmd_open = True
            continue
        toolbox.create_image(card_ID)
        if save:
            toolbox.save_image()

    if keep_cmd_open:
        raw_input('\nPress Enter to close this window!')


def palette_creator(data_folder, xml_file, palette_ID, name):
    """ Create palette.

    Registered function by ``gimpfu.register()``. Supplemental
    plugin functionality.

    :param data_folder: Blueprints (XML) folder
    :type data_folder: str
    :param xml_file: Blueprint to be used (with extension)
    :type xml_file: str
    :param palette_ID: Path to the starting node.
    :type palette_ID: str
    :param name: Name of the created palette
    :type name: str
    :raises ValueError: If the paletteID is empty.
    """
    if not palette_ID:
        raise ValueError('No palette ID inserted!')
    data_folder = data_folder.decode('utf-8')

    toolbox = Toolbox(data_folder, xml_file)
    toolbox.create_palette(palette_ID, name)


class Toolbox():
    """ Blueprint-to-image manipulation tool.

    This class offers means for creating common card components
    (i.e. text, icons). Then completes the image and optionally
    saves it. Probably you'll want to fine-tune the image manually.

    :param data_folder: Blueprints (XML) and data images (XCF) folder
    :type data_folder: str
    :param xml_file: Blueprint to be used (with extension)
    :type xml_file: str
    """

    def __init__(self, data_folder, xml_file):
        self.data_folder = data_folder + '\\'
        self.blueprint = blueprint.Blueprint(self.data_folder + xml_file)
        print('Blueprint loaded.')
        print('-' * 20)
        self.gimp_image = None
        self.gimp_image_imported = {}  # dict { name: <Gimp image object> }
        self.save_directory = 'Saved images/'
        self.add_layer = {
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

    def create_image(self, card_ID):
        """Blueprint to image.

        Layout consists of commands which are called alphabetically by
        name.

        :param card_ID: Path to the starting node.
        :type card_ID: str
        :raises RuntimeError: If there is no blueprint
        :raises KeyError: If any of the layers has no type
        :raises ValueError: If any of the layers has unknown type
        """
        if self.blueprint is None:
            raise RuntimeError('Blueprint must be initialized first!')
        print('Assembling "{}"'.format(card_ID))

        layout = self.blueprint.generate_layout(card_ID)
        for layer_name in sorted(layout.keys()):
            layer = layout[layer_name]

            LAYER_TYPE = 'layer_type'
            if LAYER_TYPE not in layer:
                raise KeyError('Layer "{}" is missing {} tag.'.format(
                    layer_name, LAYER_TYPE))

            layer_type = layer[LAYER_TYPE]
            if layer_type not in self.add_layer:
                raise ValueError('Unknown layer type "{}" in "{}"'.format(
                    layer_type, layer_name))

            self.add_layer[layer_type](**layer)
            print('Layer "{}" of type "{}" done.'.format(
                layer_name, layer_type))

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

    def _layer_monochrome(self, size, color, name='Monochrome',
                          position=(0, 0), add_to_position=0, **kwargs):
        """ Single color filled layer.

        :param size: Layer dimensions in pixels
        :type size: tuple
        :param color: Layer color in hex code
        :type color: str
        :param name: Layer name, defaults to "Monochrome"
        :type name: str, optional
        :param position: Defaults to (0, 0)
        :type position: tuple, optional
        :param add_to_position: Position among layers (-1 adds the layer to
            a recently defined group), defaults to 0
        :type add_to_position: int, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        new_layer = gimpfu.pdb.gimp_layer_new(
            self.image, size[0], size[1], gimpfu.RGB,
            name, 100, gimpfu.LAYER_MODE_NORMAL)
        self.image.add_layer(new_layer, add_to_position)
        gimpfu.pdb.gimp_layer_set_offsets(new_layer, *position)
        gimpfu.pdb.gimp_context_set_foreground(color)
        gimpfu.pdb.gimp_drawable_edit_bucket_fill(new_layer, 0, 0, 0)

    def _layer_import_layer_load(self, filename, name, **kwargs):
        """ Load new data image.

        The file has to be in the data folder. Filename is specified in
        the XML file. Name parameter is used in the XML file to
        reference the imported file. That's why it's not an optional
        parameter.

        :param filename: See description
        :type filename: str
        :param name: Name the data for future use by ``import_layer``
        :type name: str

        :raises RuntimeError: If there is no image
        """
        filepath = self.data_folder + filename
        self.gimp_image_imported[name] = gimpfu.pdb.gimp_file_load(
            filepath, filepath)

    def _layer_import_layer(self, target_file, target_layer, add_to_position=0,
                            name=None, position=(0, 0), **kwargs):
        """ Copy layer from a data image.

        :param target_file: Use **name** filled in ``import_layer_load``
        :type target_file: str
        :param target_layer: Name of the layer to be imported in the
            target file
        :type target_layer: str
        :param add_to_position: Position among layers (-1 adds the layer to
            a recently defined group), defaults to 0
        :type add_to_position: int, optional
        :param name: Layer name, defaults to **target_layer**
        :type name: str or None, optional
        :param position: Defaults to (0, 0)
        :type position: tuple, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')
        if name is None:
            name = target_layer

        old_layer = gimpfu.pdb.gimp_image_get_layer_by_name(
            self.gimp_image_imported[target_file], target_layer)
        new_layer = gimpfu.pdb.gimp_layer_new_from_drawable(
            old_layer, self.image)
        self.image.add_layer(new_layer, add_to_position)
        new_layer.name = name
        gimpfu.pdb.gimp_layer_set_offsets(new_layer, *position)

    def _layer_group(self, add_to_position=0, name='Group', **kwargs):
        """ Create new layer group.

        To fill next layers in, set theirs **add_to_position** parameter
        to ``-1``.

        :param add_to_position: Position among layers (-1 adds the layer to
            a recently defined group), defaults to 0
        :type add_to_position: int, optional
        :param name: Group name, defaults to "Group"
        :type name: str, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        layer_group = gimpfu.pdb.gimp_layer_group_new(self.image)
        self.image.add_layer(layer_group, add_to_position)
        layer_group.name = name

    def _layer_text(self, text, font, font_size, font_scale=1,
                    add_to_position=0, name=None, color='#000000', size=None,
                    line_spacing=0, letter_spacing=0, justification=0,
                    position=(0, 0), **kwargs):
        """ Text layer.

        :param text: Text
        :type text: str
        :param font: Font name
        :type font: str
        :param font_size: Font size
        :type font_size: int
        :param font_scale: Multiply **font_size**, defaults to 1
        :type font_scale: float, optional
        :param add_to_position: Position among layers (-1 adds the layer to
            a recently defined group), defaults to 0
        :type add_to_position: int, optional
        :param name: Layer name, defaults to None (Gimp default)
        :type name: str or None, optional
        :param color: Text color in hex code, defaults to “#000000”
        :type color: str, optional
        :param size: Layer dimensions in pixels, defaults to
            None (autosize)
        :type size: tuple or None
        :param line_spacing: Line separation change, defaults to 0
        :type line_spacing: float, optional
        :param letter_spacing: Letters separation change, defaults to 0
        :type letter_spacing: float, optional
        :param justification: Either left(0), right(1), center(2) or
            fill(3), defaults to 0
        :type justification: int, optional
        :param position: Defaults to (0, 0)
        :type position: tuple, optional
        :raises RuntimeError: If there is no image
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        font_size_final = font_size * font_scale
        textLayer = gimpfu.pdb.gimp_text_layer_new(
            self.image, text, font, font_size_final, 0)
        self.image.add_layer(textLayer, add_to_position)
        if name is not None:
            textLayer.name = name
        gimpfu.pdb.gimp_text_layer_set_color(textLayer, color)
        if size is not None:
            gimpfu.pdb.gimp_text_layer_resize(textLayer, *size)
        gimpfu.pdb.gimp_text_layer_set_line_spacing(textLayer, line_spacing)
        gimpfu.pdb.gimp_text_layer_set_letter_spacing(
            textLayer, letter_spacing)
        gimpfu.pdb.gimp_text_layer_set_justification(textLayer, justification)
        gimpfu.pdb.gimp_layer_set_offsets(textLayer, *position)

    def _layer_select(self, mode='select', left=0, right=100,
                      top=0, bottom=100, **kwargs):
        """ New selection by percentage of image size.

        :param mode: Either "select", "select_invert" or "deselect",
            defaults to "select"
        :type mode: str
        :param left: Left edge position in percentage of the image size,
            defaults to 0
        :type left: float, optional
        :param right: Right edge position in percentage of the image
            size, defaults to 100
        :type right: float, optional
        :param top: Top edge position in percentage of the image size,
            defaults to 0
        :type top: float, optional
        :param botton: Bottom edge position in percentage of the image
            size, defaults to 100
        :type bottom: float, optional
        :raises RuntimeError: If there is no image
        :raises ArithmeticError: If width is not positive
        :raises ArithmeticError: If height is not positive
        :raises ValueError: If mode is unknown
        """
        if self.image is None:
            raise RuntimeError('Image to add the layer to not found.')

        if mode.startswith('select'):
            x = round(gimpfu.pdb.gimp_image_width(self.image) * left / 100)
            y = round(gimpfu.pdb.gimp_image_height(self.image) * top / 100)
            width = round(
                gimpfu.pdb.gimp_image_width(self.image) * right / 100) - x
            height = round(
                gimpfu.pdb.gimp_image_height(self.image) * bottom / 100) - y
            if width <= 0:
                raise ArithmeticError(
                    'Select: parameter "left" must be lesser than "right".')
            if height <= 0:
                raise ArithmeticError(
                    'Select: parameter "top" must be lesser than "bottom".')

            gimpfu.pdb.gimp_image_select_rectangle(
                self.image, 0,  # GIMP_CHANNEL_OP_ADD
                x, y, width, height)
            # Be aware of possible interference with _layer_mask() deselect.
            if mode == 'select_invert':
                gimpfu.pdb.gimp_selection_invert(self.image)

        elif mode == 'deselect':
            gimpfu.pdb.gimp_selection_none(self.image)

        else:
            raise ValueError('Select: unknown mode: "{}".'.format(mode))

    def _layer_mask(self, target_layer, **kwargs):
        """ Mask layer.

        Create a mask for the given layer from the given selection.

        :param target_layer: Layer to be masked
        :type target_layer: str
        :param kwargs: Additional named arguments are passed to
            ``select``
        :type kwargs: various, optional
        """
        self._layer_select(**kwargs)

        layer = gimpfu.pdb.gimp_image_get_layer_by_name(
            self.image, target_layer)
        mask = gimpfu.pdb.gimp_layer_create_mask(layer, 4)
        gimpfu.pdb.gimp_layer_add_mask(layer, mask)

        kwargs['mode'] = 'deselect'
        self._layer_select(**kwargs)

    def _layer_hide(self, **kwargs):
        """ Ignore command.

        Used for overrides, i.e. hiding a predefined (template) layer.
        """
        pass

    def save_image(self):
        """ Save the image.

        Filemane: **image.name**.xcf into folder :attr:`saveDirectory`
        (subfolder of :attr:`dataFolder`).
        """
        directory = self.data_folder + self.save_directory
        if not os.path.exists(directory):
            os.makedirs(directory)
            print('Directory created: {}'.format(directory))
        filename = '{directory}{name}.xcf'.format(
            directory=directory,
            name=gimpfu.pdb.gimp_image_get_name(self.image))
        gimpfu.pdb.gimp_xcf_save(0, self.image, None, filename, filename)

    def create_palette(self, palette_ID, name):
        """ Blueprint to palette.

        Colors are sorted by their branch hight and then alphabetically.

        :param palette_ID: Path to the starting node.
        :type palette_ID: str
        :param name: Created palette name
        :type name: str
        """
        palette = gimpfu.pdb.gimp_palette_new(name)
        gimpfu.pdb.gimp_palette_set_columns(palette, 1)
        for name, color in self.blueprint.generate_palette(palette_ID):
            gimpfu.pdb.gimp_palette_add_entry(palette, name, color)


gimpfu.register(
    proc_name='CA_palette_assembler',  # Used in Procedure browser.
    blurb='Create palette.' + ' ' * 50,  # Widget title.
    help='Create palette.',
    author='Martin Brajer',
    copyright='Martin Brajer',
    date='May 2020',  # Copyright date.
    label='Palette Assembler',  # Menu entry.
    imagetypes='',  # No image required (imagetypes).
    params=[
        (gimpfu.PF_DIRNAME, 'dataFolder', 'Data folder:',
            os.path.expanduser('~')),
        (gimpfu.PF_STRING, 'xmlFile', 'XML file:', 'Blueprint.xml'),
        (gimpfu.PF_TEXT, 'paletteID', 'Palette ID:', 'color'),
        (gimpfu.PF_TEXT, 'name', 'Name:', 'Card Assembler Palette'),
        ],
    results=[],
    function=palette_creator,
    menu='<Image>/Card Assembler'
    )

gimpfu.register(
    proc_name='CA_card_assembler',  # Used in Procedure browser.
    blurb='Create board-game cards.' + ' ' * 40,  # Widget title.
    help='Create board-game cards.',
    author='Martin Brajer',
    copyright='Martin Brajer',
    date='April 2020',  # Copyright date.
    label='Card Assembler',  # Menu entry.
    imagetypes='',  # No image required (imagetypes).
    params=[
        (gimpfu.PF_DIRNAME, 'dataFolder', 'Data folder:',
            os.path.expanduser('~')),
        (gimpfu.PF_STRING, 'xmlFile', 'XML file:', 'Blueprint.xml'),
        (gimpfu.PF_TEXT, 'cardIDs', 'Card IDs:', ''),
        (gimpfu.PF_BOOL, 'save', 'Save:', False),
        ],
    results=[],
    function=card_creator,
    menu='<Image>/Card Assembler'
    )

gimpfu.main()
