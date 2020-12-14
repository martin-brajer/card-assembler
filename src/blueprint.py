# -*- coding: utf-8 -*-
"""
Supplemental script which handles data manipulation.

Read an XML file and produce a layout list, which is then used
by the main script :mod:`cardassembler`.

.. note::
    Run this script directly to run a :mod:`unittest`.
"""


__all__ = ['Blueprint']
__version__ = '1.5.0'
__author__ = 'Martin Brajer'


import unittest

import xml.etree.ElementTree as ET


def main(path):
    blueprint = Blueprint((path + '\\Blueprint.xml').decode('utf-8'))
    layout = blueprint.generate_layout('unique item example')
    palette = blueprint.generate_palette('color')
    pass


class Blueprint():
    """ Blueprint information handling class.

    Can read XML file, produce layout list and palette.

    :param file_path: Folder containing XML blueprint
    :type file_path: str or None
    """

    #: Those tags are always stored in a :class:`list` & have extra treatment
    # in :meth:`_step_in`.
    SPECIAL_TAGS = ['next', 'text']

    def __init__(self, file_path):
        # Dict tree representation of the given XML file.
        self.data = self._load(file_path) if file_path is not None else None

    def _load(self, file_path):
        """ Load XML file blueprint into a dictionary tree.

        :param file_path: Path to the XML file to load
        :type file_path: str
        :return: Tree structure of cards data
        :rtype: dict
        """
        root = ET.parse(file_path).getroot()
        return self._ElementTree_to_dict(root)

    def _ElementTree_to_dict(self, parent):
        """ Translation from :mod:`xml.etree.ElementTree` to
        :class:`dict` tree from the given node down.

        Tags in :data:`SPECIAL_TAGS` are stored in a :class:`list`.

        :param parent: A node of ElementTree
        :type parent: :class:`ElementTree.Element`
        :return: Dictionary representation of the given tree
        :rtype: dict
        """
        node = {}
        for child in parent:
            tag = child.tag
            text = child.text
            # First condition: "item.text" is None <=> "<item></item>".
            # Second condition: is there actual information? Symbols
            # other than space and newline. If there is no text (just
            # another child), tail is still there (e.g. "         \n").
            if (text is not None) and (text.strip().replace('\n', '')):
                # ElementTree unescapes newline so we're reverting back.
                text = text.replace('\\n', '\n')
                if child.attrib and 'parse' in child.attrib:
                    text = self._parse(text, child.attrib['parse'])

                if tag in node:
                    node[tag].append(text)
                else:
                    node[tag] = [text] if tag in self.SPECIAL_TAGS else text

            # No text, go down the level.
            else:
                node[tag] = self._ElementTree_to_dict(child)
        return node

    def _parse(self, text, target_type):
        """ ElementTree.element.text to various python types.

        Input parsed as tuple can have any length. Its elements will be
        parsed as :class:`int`

        :param text: Text to be parsed
        :type text: str
        :param target_type: Either "int", "float" or "tuple"
        :type target_type: str
        :raises ValueError: If target type is not known
        :return: Parsed value
        :rtype: int or float or tuple
        """
        if target_type == 'int':
            return int(text)

        elif target_type == 'float':
            return float(text)

        elif target_type == 'tuple':
            return tuple(self._parse(item, 'int') for item in
                         text.replace(' ', '').split(','))

        raise ValueError('Unknown "{}" target type!'.format(target_type))

    def generate_layout(self, start_by):
        """ Generate card layout given starting position.

        Starting position children are sorted alphabetically (name them
        accordingly).

        :param start_by: Space separated path through data tree leading
            to the starting node
        :type start_by: str
        :return: Layout of the chosen card
        :rtype: list
        """
        layers = self._step_in({}, start_by)
        return [(name, layers[name]) for name in sorted(layers.keys())]

    def _step_in(self, layout, this_step):
        """ Browse data guided by the ``next`` tag.

        Do not overwrite (first in stays). Further ``next`` tags are served
        successively in the order according to the XML file. If there are
        multiple ``text`` tags, join them by ``\\n``

        :param layout: Input layout
        :type layout: dict
        :param this_step: Where does this step leads
        :type this_step: str
        :return: Filled layout
        :rtype: dict
        """
        next_steps = []
        for key, value in self._goto(this_step).items():
            # Next is not written into layout. It stores further direction.
            if key == 'next':
                next_steps.extend(value)

            # If lower levels can be reached.
            elif isinstance(value, dict):
                if key not in layout:
                    layout[key] = {}
                layout[key] = self._step_in(
                    layout[key], ' '.join((this_step, key)))
            # Keys having values from previous levels are NOT changed.
            elif key not in layout:
                if key == 'text':
                    value = '\n'.join(value)
                layout[key] = value

        # Recursively browse all "next" branches.
        for next_step in next_steps:
            layout = self._step_in(layout, next_step)
        return layout

    def _goto(self, next_steps):
        """ Find target dict tree node and return its sub tree.

        Analogous to successive application of :meth:`dict.get`.

        :param next_steps: Space separated key sequence.
        :type next_steps: str
        :raises KeyError: If one of the given keys doesn't exist.
        :return: Sub-tree of the :data:`self.data` dict tree.
        :rtype: dict
        """
        data = self.data
        # Down the rabbit hole!
        for next_step in next_steps.split(' '):
            if next_step in data:
                data = data[next_step]
            else:
                raise KeyError(
                    'While browsing the data tree by "{}", keyword "{}"'
                    'was not found.'.format(next_steps, next_step))
        return data

    def generate_palette(self, start_by):
        """ Make palette out of colors used by cards.

        To be used in another mini plug-in to import palette into Gimp.

        :param start_by: Path through the data tree (space separated)
        :type start_by: str
        :return: Pairs of name and color
        :rtype: list
        """
        palette = self._harvest_leaves(self._goto(start_by))
        palette.sort()  # Alphabetically first.
        palette.sort(key=lambda x: x[0].count(' '))
        return palette

    def _harvest_leaves(self, color_tree):
        """ Find the path to the leaves of the given tree, whose tag
        is ``color``.

        Kinda inverse to :meth:`_goto`.

        :param color_tree: Part of the data (dict tree) to look for
            colors in
        :type color_tree: dict
        :return: List colors as :class:`tuple` of space delimited
            path and color code
        :rtype: list
        """
        palette = []
        for key, value in color_tree.items():
            if isinstance(value, dict):
                subpalette = self._harvest_leaves(value)
                for subKey, subValue in subpalette:
                    palette.append(
                        (' '.join((key, subKey)) if subKey else key, subValue))

            elif key == 'color':
                palette.append(('', value))
        return palette


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        import pycodestyle
        style = pycodestyle.StyleGuide()  # (quiet=True)
        result = style.check_files([
            'src\\blueprint.py',
            'src\\cardassembler.py'
            ])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_version(self):
        """ Test whether :data:`__version__` follows
        `Semantic Versioning 2.0.0 <https://semver.org/>`_.
        """
        import re
        #: FAQ: Is there a suggested regular expression (RegEx) to
        # check a SemVer string?
        pattern = (
            r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0'
            r'|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-'
            r'9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*'
            r'))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)'
            r'*))?$'
            )
        self.assertTrue(re.search(pattern, __version__))


class TestBlueprintMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.blueprint = Blueprint(None)
        #: Beginning of example :file:`Minimal blueprint.xml`.
        XML = (
            '<data><card><command01_image><layer_type>image</layer_type>'
            '<size parse="tuple">800, 500</size></command01_image>'
            '</card></data>'
            )
        cls.element_tree = ET.fromstring(XML)
        #: Dict representation of :data:`XML`.
        cls.DICT = {'card': {'command01_image': {'layer_type': 'image',
                    'size': (800, 500)}}}

    def test_parse_int(self):
        self.assertEqual(self.blueprint._parse('5', 'int'), 5)

    def test_parse_float(self):
        self.assertAlmostEqual(self.blueprint._parse('1.3', 'float'), 1.3)

    def test_parse_tuple_spaces(self):
        self.assertEqual(
            self.blueprint._parse('3, 5', 'tuple'),
            self.blueprint._parse('3,5', 'tuple'))

    def test_parse_unknown(self):
        with self.assertRaises(ValueError):
            self.blueprint._parse('test', 'foo')

    def test_ElementTree_to_dict(self):
        self.assertEqual(self.blueprint._ElementTree_to_dict(
            self.element_tree), self.DICT)

    def test_goto(self):
        self.blueprint.data = self.DICT
        self.assertEqual(
            self.blueprint._goto('card command01_image'),
            self.DICT['card']['command01_image'])


if __name__ == '__main__':
    unittest.main(exit=False)
    # main('')
