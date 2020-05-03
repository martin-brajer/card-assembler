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
def data_folder():
    """ Find Data folder.

    It is set as default value
    in GF.register function.
    """
    dataFolder = os.path.expanduser('~')  # .replace("\\", "/")
    # Rest of the Gimp plug-in path contains gimp version
    # and therefore can change. Any folder can be chosen.
    dataFolder += '/AppData/Roaming/GIMP/'
    return dataFolder


def card_creator(dataFolder, xmlFile, cardIDs, save):
    """Registered function CardCreator, creates new card image
    from predefined values. Requires two arguments, the paths to
    the card definitions and chosen card ID.
    """
    # This weird import is forced by Gimp running this script through
    # eval(...) function inside its installation folder and direct
    # import from different folder raises 'access denied' error.
    dataFolder += '/'
    sys.path.append(dataFolder)
    try:
        import cardassembler_definitions
    except ImportError, err:
        raise ImportError('{} in folder {}'.format(str(err), dataFolder))

    toolbox = Toolbox(dataFolder)
    toolbox.blueprint = cardassembler_definitions.Blueprint(
        dataFolder + xmlFile)

    if not cardIDs:
        raise ValueError('No card IDs inserted!')

    for cardID in cardIDs.split('\n'):
        toolbox.create_image(cardID)
        toolbox.display_image()
        if save:
            toolbox.save_image()


# ---CLASSES---
class Toolbox(object):
    """ Blueprint to image manipulation tool.

    Image build information is saved in an xml file.

    This class offers means for creating common card components
    (i.e. text, icons). Then completes the image and optionally
    saves it. Probably you'll want to fine-tune it manually.
    """

    def __init__(self, dataFolder):
        """ Init.

        Parameter 'dataFolder' is a location of the xml files.
        """
        self.blueprint = None
        self.dataFolder = dataFolder

        # Gimp image objects
        self.image = None  # Code output will be here.
        self.data_images = {}  # {name: Gimp image object}

        # Image components this script can handle.
        self.component_type = {
            'image': self._component_image,
            'monochrome': self._component_monochrome,
            'import_layer_load': self._component_import_layer_load,
            'import_layer': self._component_import_layer,
            'group': self._component_group,
            'text': self._component_text,
        }

    def create_image(self, cardID):
        """ Blueprint > layout information si utilized here. """
        if self.blueprint is None:
            raise Exception('Blueprint must be initialized first!')

        layout = self.blueprint.generate_layout_dict(cardID)
        for layerName in sorted(layout.keys()):
            layerLayout = layout[layerName]
            if 'componentType' in layerLayout:
                componentType = layerLayout['componentType']
                if componentType in self.component_type:
                    self.component_type[componentType](layerLayout)
                else:
                    raise KeyError(
                        'Unknown componentType "{}" of layer "{}"'.format(
                            componentType, layerName))
            else:
                raise KeyError(
                    'Layer "{}" is missing componentType tag.'.format(layerName))

    def _component_image(self, layout):
        """ Create new image. This is the first call in a layout sequence.

        Parameters: size(tuple), [name(string)].
        """
        self.image = GF.pdb.gimp_image_new(
            layout['size'][0], layout['size'][1], GF.RGB)
        GF.pdb.gimp_image_set_filename(
            self.image, layout.get('name', 'Card Assembler Image'))

    def _component_monochrome(self, layout):
        """ One-colour-filled-layer. Allows masks.

        Parameters: size(tuple), color(string),
            [name(string)], [position(tuple)],
            [addToPosition(int)].
        """
        layer = GF.pdb.gimp_layer_new(self.image,
                                      layout['size'][0], layout['size'][1],
                                      GF.RGB, layout.get(
                                          'name', 'Monochrome'),
                                      100, GF.LAYER_MODE_NORMAL)
        self.image.add_layer(layer, layout.get('addToPosition', 0))
        if 'position' in layout:
            GF.pdb.gimp_layer_set_offsets(layer, *layout['position'])
        GF.pdb.gimp_context_set_foreground(layout['color'])
        GF.pdb.gimp_drawable_edit_bucket_fill(layer, 0, 0, 0)

    def _component_import_layer_load(self, layout):
        """ Load new data image.

        Must be in Data folder. Filename is specified in xml file.
        Name parameter is used in xml file to reference
        the imported file. That's why it's not optional parameter.
        Parameters: filename(string), name(string).
        """
        filepath = self.dataFolder + layout['filename']
        self.data_images[layout['name']] = GF.pdb.gimp_file_load(
            filepath, filepath)

    def _component_import_layer(self, layout):
        """ Copy layer from a data image.

        Parameters: targetFile(string), targetLayer(string),
            [addToPosition(int)], [name(string)], [position(tuple)].
        """
        oldLayer = GF.pdb.gimp_image_get_layer_by_name(
            self.data_images[layout['targetFile']], layout['targetLayer'])
        newLayer = GF.pdb.gimp_layer_new_from_drawable(
            oldLayer, self.image)
        self.image.add_layer(newLayer, layout.get('addToPosition', 0))
        newLayer.name = layout.get('name', layout['targetLayer'])
        GF.pdb.gimp_layer_set_offsets(
            newLayer, *layout.get('position', (0, 0)))

    def _component_group(self, layout):
        """ Create new layer group.

        To fill next layers in, their 'addToPosition'
        parameter must be set to -1.
        Parameters: [addToPosition(int)], [name(string)].
        """
        layerGroup = GF.pdb.gimp_layer_group_new(self.image)
        self.image.add_layer(layerGroup, layout.get('addToPosition', 0))
        layerGroup.name = layout.get('name', 'Group')

    def _component_text(self, layout):
        """ Text layer.

        If Size is not filled in, 'dynamic' mode is used.
        Justification values: left(0), right(1), center(2), fill(3).
        Parameters: text(string), font(string), fontSize(int),
            [textScale(float)], [addToPosition(int)], [name(string)],
            [color(string)], [size(tuple)], [lineSpacing(float)],
            [letterSpacing(float)], [justification(int)], [position(tuple)].
        """
        fontsize = layout['fontSize'] * layout.get('textScale', 1)
        textLayer = GF.pdb.gimp_text_layer_new(
            self.image, layout['text'],
            layout['font'], fontsize, 0)
        self.image.add_layer(textLayer, layout.get('addToPosition', 0))
        textLayer.name = layout.get('name', 'Text Layer')
        GF.pdb.gimp_text_layer_set_color(
            textLayer, layout.get('color', '#000000'))
        if 'size' in layout:
            GF.pdb.gimp_text_layer_resize(
                textLayer, *layout['size'])
        GF.pdb.gimp_text_layer_set_line_spacing(
            textLayer, layout.get('lineSpacing', 0))
        GF.pdb.gimp_text_layer_set_letter_spacing(
            textLayer, layout.get('letterSpacing', 0))
        GF.pdb.gimp_text_layer_set_justification(
            textLayer, layout.get('justification', 0))
        GF.pdb.gimp_layer_set_offsets(
            textLayer, *layout.get('position', (0, 0)))

    def display_image(self):
        """ Display the created image. """
        display = GF.pdb.gimp_display_new(self.image)

    def save_image(self):
        """ X """
        directory = self.dataFolder + 'Saved images/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = directory + GF.pdb.gimp_image_get_name(self.image) + '.xcf'
        GF.pdb.gimp_xcf_save(0, self.image, None, filename, filename)


# ---REGISTER---
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
        (GF.PF_DIRNAME, "dataFolder", "Data folder:", data_folder()),
        (GF.PF_STRING, "xmlFile", "XML file:", "Blueprint.xml"),
        (GF.PF_TEXT, "cardIDs", "Card IDs:", ""),
        (GF.PF_BOOL, "save", "Save:", False),
    ],
    [],  # (results).
    card_creator,  # Matches to name of function being defined (function).
    menu="<Image>/Card Assembler"  # Menu item location.
)   # End register.

GF.main()
