# -*- coding: utf-8 -*-
"""
Gimp gimpfu plug-in for board game card creation.

Code not using gimpfu is imported from CardAssembler_Definitions.py,
which is located in data folder.
Written for Gimp 2.10.18, which uses python 2.7.17.
"""

# ---IMPORTS---
import gimpfu as GF
import os
import sys

# ---CONSTANTS---


# ---FUNCTIONS---
def default_data_folder():
    """ Gimp's folder in user folder. """
    dataFolder = os.path.expanduser('~')
    # Rest of the Gimp plug-in path contains gimp version
    # and therefore can change. Any folder can be chosen.
    dataFolder += '/AppData/Roaming/GIMP/'
    return dataFolder


def card_creator(dataFolder, xmlFile, cardIDs, save):
    """ Creates board-game cards.

    Registered function by GF.register. Main functionality.
    """
    toolbox = initialize_toolbox(dataFolder, xmlFile)

    if not cardIDs:
        raise ValueError('No card IDs inserted!')

    for cardID in cardIDs.split('\n'):
        toolbox.create_image(cardID)
        toolbox.display_image()
        if save:
            toolbox.save_image()


def palette_creator(dataFolder, xmlFile, paletteID, name):
    """ Creates palette.

    Registered function by GF.register. Supplemental functionality.
    """
    toolbox = initialize_toolbox(dataFolder, xmlFile)

    if not paletteID:
        raise ValueError('No palette ID inserted!')

    toolbox.create_palette(paletteID, name)


def initialize_toolbox(dataFolder, xmlFile):
    """ Common initialization used by all registered functions. """
    # This weird import is forced by Gimp running this script through
    # eval(...) function inside its installation folder and direct
    # import from different folder raises 'access denied' error.
    sys.path.append(dataFolder)
    import CardAssembler_Definitions

    toolbox = Toolbox(dataFolder)
    toolbox.load_blueprint(
        xmlFile,
        blueprintClass=CardAssembler_Definitions.Blueprint)

    return toolbox


# ---CLASSES---


class Toolbox(object):
    """ Blueprint-to-image manipulation tool.

    This class offers means for creating common card components
    (i.e. text, icons). Then completes the image and optionally
    saves it. Probably you'll want to fine-tune it manually.
    """

    def __init__(self, dataFolder):
        self.blueprint = None
        self.dataFolder = dataFolder + '/'

        self.gimpImage = None
        self.gimpImageImport = {}  # {name: Gimp image object}

        # Specifies how a command dict is interpreted.
        self.commandLib = {
            'image': self._command_image,
            'monochrome': self._command_monochrome,
            'import_layer_load': self._command_import_layer_load,
            'import_layer': self._command_import_layer,
            'group': self._command_group,
            'text': self._command_text,
        }

    def load_blueprint(self, xmlFile, blueprintClass):
        """ Initialize Blueprint class from supplemental file. """
        self.blueprint = blueprintClass(self.dataFolder + xmlFile)

    def create_image(self, cardID):
        """ Blueprint to image.

        Layout consists of commands, which are called alphabetically by name.
        """
        if self.blueprint is None:
            raise AttributeError('Blueprint must be initialized first!')

        layout = self.blueprint.generate_layout_dict(cardID)
        for commandName in sorted(layout.keys()):
            self._command_interpreter(layout[commandName], commandName)

    def _command_interpreter(self, command, commandName):
        """ Forward command to appropriate method. """
        if 'commandType' not in command:
            raise KeyError(
                'Command "{}" is missing commandType tag.'.format(
                    commandName))
        commandType = command['commandType']

        if commandType not in self.commandLib:
            raise KeyError(
                'Unknown commandType "{}" of command "{}"'.format(
                    commandType, commandName))

        self.commandLib[commandType](command)

    def _command_image(self, command):
        """ Create new image. Needed for layer creation.

        Parameters: size(tuple), [name(string)].
        """
        self.image = GF.pdb.gimp_image_new(
            command['size'][0], command['size'][1], GF.RGB)
        GF.pdb.gimp_image_set_filename(
            self.image, command.get('name', 'Card Assembler Image'))

    def _command_monochrome(self, command):
        """ One-colour-filled-layer.

        Parameters: size(tuple), color(string),
            [name(string)], [position(tuple)],
            [addToPosition(int)].
        """
        if self.image is None:
            raise AttributeError('Image to add the layer to not found.')

        layer = GF.pdb.gimp_layer_new(
            self.image,
            command['size'][0], command['size'][1],
            GF.RGB,
            command.get('name', 'Monochrome'),
            100,
            GF.LAYER_MODE_NORMAL)
        self.image.add_layer(layer, command.get('addToPosition', 0))
        if 'position' in command:
            GF.pdb.gimp_layer_set_offsets(layer, *command['position'])
        GF.pdb.gimp_context_set_foreground(command['color'])
        GF.pdb.gimp_drawable_edit_bucket_fill(layer, 0, 0, 0)

    def _command_import_layer_load(self, command):
        """ Load new data image.

        Must be in Data folder. Filename is specified in xml file.
        Name parameter is used in xml file to reference
        the imported file. That's why it's not optional parameter.

        Parameters: filename(string), name(string).
        """
        filepath = self.dataFolder + command['filename']
        self.gimpImageImport[command['name']] = GF.pdb.gimp_file_load(
            filepath, filepath)

    def _command_import_layer(self, command):
        """ Copy layer from a data image.

        Parameters: targetFile(string), targetLayer(string),
            [addToPosition(int)], [name(string)], [position(tuple)].
        """
        if self.image is None:
            raise AttributeError('Image to add the layer to not found.')

        oldLayer = GF.pdb.gimp_image_get_layer_by_name(
            self.gimpImageImport[command['targetFile']], command['targetLayer'])
        newLayer = GF.pdb.gimp_layer_new_from_drawable(
            oldLayer, self.image)
        self.image.add_layer(newLayer, command.get('addToPosition', 0))
        newLayer.name = command.get('name', command['targetLayer'])
        GF.pdb.gimp_layer_set_offsets(
            newLayer, *command.get('position', (0, 0)))

    def _command_group(self, command):
        """ Create new layer group.

        To fill next layers in, set its 'addToPosition' parameter to -1.

        Parameters: [addToPosition(int)], [name(string)].
        """
        if self.image is None:
            raise AttributeError('Image to add the layer to not found.')

        layerGroup = GF.pdb.gimp_layer_group_new(self.image)
        self.image.add_layer(layerGroup, command.get('addToPosition', 0))
        layerGroup.name = command.get('name', 'Group')

    def _command_text(self, command):
        """ Text layer.

        If Size is not filled in, 'dynamic' mode is used.
        Justification values: left(0), right(1), center(2), fill(3).

        Parameters: text(string), font(string), fontSize(int),
            [textScale(float)], [addToPosition(int)], [name(string)],
            [color(string)], [size(tuple)], [lineSpacing(float)],
            [letterSpacing(float)], [justification(int)], [position(tuple)].
        """
        if self.image is None:
            raise AttributeError('Image to add the layer to not found.')

        fontsize = command['fontSize'] * command.get('textScale', 1)
        textLayer = GF.pdb.gimp_text_layer_new(
            self.image,
            command['text'],
            command['font'],
            fontsize, 0)
        self.image.add_layer(textLayer, command.get('addToPosition', 0))
        textLayer.name = command.get('name', 'Text Layer')
        GF.pdb.gimp_text_layer_set_color(
            textLayer, command.get('color', '#000000'))
        if 'size' in command:
            GF.pdb.gimp_text_layer_resize(
                textLayer, *command['size'])
        GF.pdb.gimp_text_layer_set_line_spacing(
            textLayer, command.get('lineSpacing', 0))
        GF.pdb.gimp_text_layer_set_letter_spacing(
            textLayer, command.get('letterSpacing', 0))
        GF.pdb.gimp_text_layer_set_justification(
            textLayer, command.get('justification', 0))
        GF.pdb.gimp_layer_set_offsets(
            textLayer, *command.get('position', (0, 0)))

    def display_image(self):
        """ Display the created image. """
        display = GF.pdb.gimp_display_new(self.image)

    def save_image(self):
        """ Save the image as <image.name>.xcf into 'Saved images' subfolder. """
        directory = self.dataFolder + 'Saved images/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = directory + GF.pdb.gimp_image_get_name(self.image) + '.xcf'
        GF.pdb.gimp_xcf_save(0, self.image, None, filename, filename)

    def create_palette(self, paletteID, name):
        """Blueprint to palette.

        Colors are sorted by their branch hight and then alphabetically.
        """
        palette = GF.pdb.gimp_palette_new(name)
        GF.pdb.gimp_palette_set_columns(palette, 1)

        for name, color in self.blueprint.generate_palette(paletteID):
            GF.pdb.gimp_palette_add_entry(palette, name, color)


# ---REGISTER---

GF.register(
    "MB_palette_assembler",  # Name registered in Procedure Browser (blurb).
    # Widget title (proc_name).
    "Creates palette.\n\nGimp plug-in folder:\n<user>/AppData/Roaming/GIMP/<version>/plug-ins/",
    "Creates palette",  # Help.
    "Martin Brajer",  # Author.
    "Martin Brajer",  # Copyright holder.
    "May 2020",  # Date.
    "Palette Assembler",  # Menu Entry (label).
    "",  # Image Type - no image required (imagetypes).
    [  # (params).
        (GF.PF_DIRNAME, "dataFolder", "Data folder:", default_data_folder()),
        (GF.PF_STRING, "xmlFile", "XML file:", "Blueprint.xml"),
        (GF.PF_TEXT, "paletteID", "Palette ID:", "color"),
        (GF.PF_TEXT, "name", "Name:", "Card Assembler Palette"),
    ],
    [],  # (results).
    palette_creator,  # Matches to name of function being defined (function).
    menu="<Image>/Card Assembler"  # Menu item location.
)

GF.register(
    "MB_card_assembler",  # Name registered in Procedure Browser (blurb).
    # Widget title (proc_name).
    "Creates board-game cards.\n\nGimp plug-in folder:\n<user>/AppData/Roaming/GIMP/<version>/plug-ins/",
    "Creates board-game cards",  # Help.
    "Martin Brajer",  # Author.
    "Martin Brajer",  # Copyright holder.
    "April 2020",  # Date.
    "Card Assembler",  # Menu Entry (label).
    "",  # Image Type - no image required (imagetypes).
    [  # (params).
        (GF.PF_DIRNAME, "dataFolder", "Data folder:", default_data_folder()),
        (GF.PF_STRING, "xmlFile", "XML file:", "Blueprint.xml"),
        (GF.PF_TEXT, "cardIDs", "Card IDs:", ""),
        (GF.PF_BOOL, "save", "Save:", False),
    ],
    [],  # (results).
    card_creator,  # Matches to name of function being defined (function).
    menu="<Image>/Card Assembler"  # Menu item location.
)

GF.main()
