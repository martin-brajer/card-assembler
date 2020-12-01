# -*- coding: utf-8 -*-
"""
Supplemental script which handles data manipulation.

Introduces :class:`Blueprint` class which can read `xml` files and
produce layout list, which is used by the main script :mod:`cardassembler`.
"""
# ---IMPORTS---
import xml.etree.ElementTree as ET

# ---CONSTANTS---

# ---FUNCTIONS---


def main():
    import os.path
    blueprint = Blueprint('D:\Programming\Python\Gimp\cardassembler_data\Blueprint.xml')
    layout = blueprint.generate_layout("unique item example")
    palette = blueprint.generate_palette("color")
    pass


# ---CLASSES---


class Blueprint():
    """ Blueprint information handling class.

    Can read xml file, produce layout list and palettes.

    :param filePath: Blueprint xml folder
    :type filePath: str
    """
    
    def __init__(self, filePath):
        #: Tree structure (:class:`dict`) of card data
        self.data = self._load_data(filePath)

    def _load_data(self, filePath):
        """ Load blueprint (xml file) into dictionary tree.

        :param filePath: Path to the \*.xml file to load
        :type filePath: str
        :return: Tree structure of card data
        :rtype: dict
        """        
        root = ET.parse(filePath).getroot()
        return self._xml2dict(root)

    def _xml2dict(self, parent):
        """ Recursive translation from ElementTree to dictionary tree.

        :param parent: [description]
        :type parent: [type]
        :return: [description]
        :rtype: [type]
        """        
        newDict = {}
        for child in parent:
            key = child.tag
            text = child.text

            # If there is no text (just another child) tail
            # is still there ("         \n").
            # Second: "item.text" == None <=> "<item></item>".
            if (text is not None) and (text.strip().replace("\n", "")):
                # ElementTree unescapes newline so we're reverting back.
                text = text.replace('\\n', '\n')
                if key in newDict:
                    text = newDict[key] + ', ' + text
                if child.attrib:
                    if 'parse' in child.attrib:
                        text = self._parse(text, child.attrib['parse'])

                newDict[key] = text

            # Go down the level.
            else:
                newDict[key] = self._xml2dict(child)

        return newDict

    def _parse(self, text, method):
        """ ElementTree.element.text to various python types.

        :param text: [description]
        :type text: [type]
        :param method: [description]
        :type method: [type]
        :raises KeyError: [description]
        :return: [description]
        :rtype: [type]
        """        
        if method == 'int':
            return int(text)

        elif method == 'float':
            return float(text)

        elif method == 'tuple':
            new = []
            for txt in text.split(', '):
                new.append(self._parse(txt, 'int'))
            return tuple(new)

        raise KeyError('Method "{}" not found!'.format(method))

    def generate_layout(self, startBy):
        """ Generate card layout given starting position.

        Starting position children are sorted alphabetically (name them accordingly).

        :param startBy: Path through data tree, space separated
        :type startBy: str
        :return: Tree structure of chosen card data
        :rtype: dict
        """        
        return self._stepIn({}, startBy)

    def _stepIn(self, layout, thisStep):
        """ Browse data guided by 'next' tag.

        Does not overwrite (first in stays).

        :param layout: [description]
        :type layout: [type]
        :param thisStep: [description]
        :type thisStep: [type]
        :return: [description]
        :rtype: [type]
        """        
        nextSteps = []
        for key, value in self._nextDataset(thisStep).items():
            # Next is not written into layout.
            if key == 'next':
                for nextStep in value.split(', '):
                    nextSteps.append(nextStep)

            # If lower levels can be reached.
            elif isinstance(value, dict):
                if key not in layout:
                    layout[key] = {}
                self._stepIn(layout[key], thisStep + ' ' + key)

            # Keys having values from previous levels are NOT changed.
            elif key not in layout:
                layout[key] = value

        # Recursively browse all "next"-branches.
        while nextSteps:
            self._stepIn(layout, nextSteps.pop())

        return layout

    def _nextDataset(self, nextSteps):
        """ Browse ElementTree based on argument indicator.

        Individual node turns must be separated by space.

        :param nextSteps: [description]
        :type nextSteps: [type]
        :raises KeyError: [description]
        :return: [description]
        :rtype: [type]
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

        :param startBy: Path through data tree, space separated
        :type startBy: str
        :return: Pairs of name and color
        :rtype: list
        """        
        palette = self._harvest_leaves(self._nextDataset(startBy))
        palette.sort()
        palette.sort(key=lambda x: x[0].count(' '))
        return palette

    def _harvest_leaves(self, colorDict):
        """ Harvest leaves.

        :param colorDict: [description]
        :type colorDict: [type]
        :return: [description]
        :rtype: [type]
        """        
        palette = []
        for key, value in colorDict.items():
            if isinstance(value, dict):
                subpalette = self._harvest_leaves(value)
                for subKey, subValue in subpalette:
                    palette.append(
                        (key + (" " if subKey else "") + subKey, subValue))

            elif key == 'color':
                palette.append(("", value))

        return palette


# ---MAIN---
if __name__ == "__main__":
    main()
