# -*- coding: utf-8 -*-
"""
Supplemental script which handles data manipulation.

Read an XML file and produce a layout list, which is then used
by the main script :mod:`cardassembler`.

Special variable :data:`__version__` is defined here.

.. note::
    Run this script directly to run a :mod:`unittest`.
"""
#: Versioning follows `Semantic Versioning 2.0.0 <https://semver.org/>`_.
__version__ = '1.4.0'

import unittest
import xml.etree.ElementTree as ET


def main():
    blueprint = Blueprint("")
    layout = blueprint.generate_layout("unique item example")
    palette = blueprint.generate_palette("color")
    pass


class Blueprint():
    """ Blueprint information handling class.

    Can read XML file, produce layout list and palette.

    :param filePath: Folder containing XML blueprint
    :type filePath: str or None
    """
    
    def __init__(self, filePath):
        #: Tree structure (:class:`dict`) representation of an XML file.
        self.data = self._load(filePath) if filePath is not None else None

    def _load(self, filePath):
        """ Load XML file blueprint into a dictionary tree.

        :param filePath: Path to the XML file to load
        :type filePath: str
        :return: Tree structure of cards data
        :rtype: dict
        """        
        root = ET.parse(filePath).getroot()
        return self._ElementTree2dict(root)

    def _ElementTree2dict(self, parent):
        """ Translation from :mod:`xml.etree.ElementTree` to :class:`dict`
        tree from the given node down (recursive).

        :param parent: A node of ElementTree
        :type parent: :class:`ElementTree.Element`
        :return: Dictionary representation of the given tree
        :rtype: dict
        """        
        newDict = {}
        for child in parent:
            key = child.tag
            text = child.text
            
            # First condition: "item.text" is None <=> "<item></item>".
            # Second condition: is there actual information? Symbols other
            # than space and newline. If there is no text (just another
            # child), tail is still there (e.g. "         \n").
            if (text is not None) and (text.strip().replace('\n', '')):
                # ElementTree unescapes newline so we're reverting back.
                text = text.replace('\\n', '\n')
                if child.attrib and 'parse' in child.attrib:
                    text = self._parse(text, child.attrib['parse'])
                
                newDict[key] = newDict[key] + ', ' + text if key in newDict else text
                
            # Go down the level.
            else:
                newDict[key] = self._ElementTree2dict(child)

        return newDict

    def _parse(self, text, targetType):
        """ ElementTree.element.text to various python types.

        Input parsed as tuple can have any length. Its elements will be
        parsed as :class:`int`

        :param text: Text to be parsed
        :type text: str
        :param targetType: Either "int", "float" or "tuple"
        :type targetType: str
        :raises ValueError: If target type is not known
        :return: Parsed value
        :rtype: int or float or tuple
        """        
        if targetType == 'int':
            return int(text)

        elif targetType == 'float':
            return float(text)

        elif targetType == 'tuple':
            return tuple(self._parse(item, 'int') for item in
                text.replace(' ', '').split(','))

        raise ValueError('Unknown "{0}" target type!'.format(targetType))

    def generate_layout(self, startBy):
        """ Generate card layout given starting position.

        Starting position children are sorted alphabetically (name them accordingly).

        :param startBy: Space separated path through data tree leading to the starting node
        :type startBy: str
        :return: Layout of the chosen card
        :rtype: dict
        """        
        return self._stepIn({}, startBy)

    def _stepIn(self, layout, thisStep):
        """ Browse data guided by the ``next`` tag.

        Do not overwrite (first in stays).

        :param layout: Input layout
        :type layout: dict
        :param thisStep: Where does this step leads
        :type thisStep: str
        :return: Filled layout
        :rtype: dict
        """        
        nextSteps = []
        for key, value in self._goto(thisStep).items():
            # Next is not written into layout. It stores further direction.
            if key == 'next':
                for nextStep in value.split(', '):
                    nextSteps.append(nextStep)

            # If lower levels can be reached.
            elif isinstance(value, dict):
                if key not in layout:
                    layout[key] = {}
                layout[key] = self._stepIn(layout[key], thisStep + ' ' + key)

            # Keys having values from previous levels are NOT changed.
            elif key not in layout:
                layout[key] = value

        # Recursively browse all "next" branches.
        while nextSteps:
            layout = self._stepIn(layout, nextSteps.pop())

        return layout

    def _goto(self, nextSteps):
        """ Find target dict tree node and return its sub tree.

        Analogous to successive application of :meth:`dict.get`.

        :param nextSteps: Space separated key sequence.
        :type nextSteps: str
        :raises KeyError: If one of the given keys doesn't exist.
        :return: Sub-tree of the :data:`self.data` dict tree.
        :rtype: dict
        """        
        data = self.data
        # Down the rabbit hole!
        for nextStep in nextSteps.split(' '):
            if nextStep in data:
                data = data[nextStep]
            else:
                raise KeyError(
                    'While browsing the data tree by "{}", keyword "{}" was not found.'.format(
                        nextSteps, nextStep))
        return data

    def generate_palette(self, startBy):
        """ Make palette out of colors used by cards.

        To be used in another mini plug-in to import palette into Gimp.

        :param startBy: Path through the data tree (space separated)
        :type startBy: str
        :return: Pairs of name and color
        :rtype: list
        """        
        palette = self._harvest_leaves(self._goto(startBy))
        palette.sort()  # Alphabetically first.
        palette.sort(key=lambda x: x[0].count(' '))
        return palette

    def _harvest_leaves(self, colorTree):
        """ Find the path to the leaves of the given tree, whose tag is ``color``.

        Kinda inverse to :meth:`_goto`.

        :param colorTree: Part of the data (dict tree) to look for colors in
        :type colorTree: dict
        :return: List colors as :class:`tuple` of space delimited path and color code
        :rtype: list
        """        
        palette = []
        for key, value in colorTree.items():
            if isinstance(value, dict):
                subpalette = self._harvest_leaves(value)
                for subKey, subValue in subpalette:
                    palette.append(
                        ('{} {}'.format(key, subKey) if subKey else key, subValue))

            elif key == 'color':
                palette.append(("", value))

        return palette


class TestBlueprintModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        cls.blueprint = Blueprint(None)
        #: Beginning of example :file:`Minimal blueprint.xml`.
        XML = '<data><card><command01_image><layerType>image</layerType><size parse="tuple">800, 500</size></command01_image></card></data>'
        cls.elementTree = ET.fromstring(XML)
        #: Dict representation of :data:`XML`.
        cls.DICT = {'card': {'command01_image':
            {'layerType': 'image', 'size': (800, 500)}}}
    
    def test_version(self):
        """ Test whether :data:`__version__` follows `Semantic Versioning 2.0.0
        <https://semver.org/>`_.
        """
        import re
        #: FAQ: Is there a suggested regular expression (RegEx) to check a SemVer string?
        pattern = '^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        self.assertTrue(re.search(pattern, __version__))

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
    
    def test_ElementTree2dict(self):
        self.assertEqual(self.blueprint._ElementTree2dict(self.elementTree), self.DICT)
    
    def test_goto(self):
        self.blueprint.data = self.DICT
        self.assertEqual(
            self.blueprint._goto('card command01_image'),
            self.DICT['card']['command01_image'])
    

if __name__ == "__main__":
    unittest.main(exit=False)
    # main()
