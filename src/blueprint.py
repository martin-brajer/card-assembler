# -*- coding: utf-8 -*-
"""
Supplemental script which handles data manipulation.

Read an *xml* files and produce a layout list, which is then used
by the main script :mod:`cardassembler`.
"""
# ---IMPORTS---
import xml.etree.ElementTree as ET

# ---CONSTANTS---

# ---FUNCTIONS---


def main():
    blueprint = Blueprint(input('Blueprint path: '))
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
        """ Load blueprint (xml file) into a dictionary tree.

        :param filePath: Path to the \*.xml file to load
        :type filePath: str
        :return: Tree structure of a card data
        :rtype: dict
        """        
        root = ET.parse(filePath).getroot()
        return self._xml2dict(root)

    def _xml2dict(self, parent):
        """
        
        Recursive translation from ElementTree to :class:`dict` tree from
        the given node down.

        :param parent: A node of ElementTree
        :type parent: ElementTree.Element
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
                newDict[key] = self._xml2dict(child)

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
            return tuple(self._parse(item, 'int') for item in text.split(', '))

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
        """ Browse data guided by the 'next' tag.

        Do not overwrite (first in stays).

        :param layout: Input layout
        :type layout: dict
        :param thisStep: Where does this step leads
        :type thisStep: str
        :return: Filled layout
        :rtype: dict
        """        
        nextSteps = []
        for key, value in self._nextDataset(thisStep).items():
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

        # Recursively browse all "next"-branches.
        while nextSteps:
            layout = self._stepIn(layout, nextSteps.pop())

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
