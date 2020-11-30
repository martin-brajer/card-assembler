# -*- coding: utf-8 -*-
"""
Supplemental script which handles data manipulation.

Introduces :class:`Blueprint` class which can read `xml` files and
produce layout list, which is used by the main script.
"""
# ---IMPORTS---
import xml.etree.ElementTree as ET
import operator

# ---CONSTANTS---

# ---FUNCTIONS---


def main():
    import os.path
    blueprint = Blueprint(os.path.dirname(__file__) + '/Blueprint.xml')
    layout = blueprint.generate_layout_dict("unique item example")
    palette = blueprint.generate_palette("color")
    pass


# ---CLASSES---


class Blueprint(object):
    """ Blueprint information handling class.

    Can read xml file and produce layout list,
    which is used by the main script.

    :param filePath: Blueprint xml folder
    :type filePath: str
    """

    def __init__(self, filePath):
        self.data = self._load_data(filePath)

    def _load_data(self, filePath):
        """ Load blueprint (xml file) into dictionary tree. """
        root = ET.parse(filePath).getroot()
        return self.xml2dict(root)

    def xml2dict(self, parent):
        """ Recursive translation from ElementTree to dictionary tree. """
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
                newDict[key] = self.xml2dict(child)

        return newDict

    def _parse(self, text, method):
        """ ElementTree.element.text to various python types. """
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

    def generate_layout_dict(self, startBy):
        """ Generate layout given starting position.

        Starting position children are sorted
        alphabetically (name them accordingly).
        """
        return self._stepIn({}, startBy)

    def _stepIn(self, layout, thisStep):
        """ Browse data guided by 'next' tag.

        Does not overwrite (first in stays).
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
        """ Make palette out of used colors.

        To be used in another mini plug-in to import palette into Gimp.
        """
        palette = self._harvest_leaves(self._nextDataset(startBy))
        palette.sort()
        palette.sort(key=lambda x: x[0].count(' '))
        return palette

    def _harvest_leaves(self, colorDict):
        """ X """
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
