# -*- coding: utf-8 -*-
"""
Main script which handles Gimp addone interface.

This code uses `gimpfu <https://www.gimp.org/docs/python/index.html>`_.
Written for `Gimp 2.10.18 <https://www.gimp.org/>`_ which uses
`Python 2.7.18 <https://docs.python.org/release/2.7.18/>`_.

.. note::
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
import toolbox  # nopep8
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

    toolbox_ = toolbox.Toolbox(data_folder, xml_file)
    for card_ID in card_IDs.split('\n'):
        if card_ID == 'keepCmdOpen':
            keep_cmd_open = True
            continue
        toolbox_.create_image(card_ID)
        if save:
            toolbox_.save_image()

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

    toolbox_ = toolbox.Toolbox(data_folder, xml_file)
    toolbox_.create_palette(palette_ID, name)


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
