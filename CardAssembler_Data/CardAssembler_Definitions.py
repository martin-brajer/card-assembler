# -*- coding: utf-8 -*-
"""
Supplemental script to gimp plug-in CardCreator.

Introduces Card class which can read xml file and
return layout list, which is used by the main script.
"""
# ---IMPORTS---
import xml.etree.ElementTree as ET

# ---CONSTANTS---

# ---FUNCTIONS---


def main():
    """ Testing area. """
    card = Card(
        'C:/<path>/CardAssembler/CardAssembler_Data/Blueprint.xml')
    layout = card.generate_layout("unique item dragonPotion")
    input('STOPPED')


# ---CLASSES---


class Card(object):
    """ Card information handling class.

    Can read xml file and return layout list,
    which is used by the main script.
    """

    def __init__(self, filePath):
        self.data = self.load_data(filePath)

    def load_data(self, filePath):
        """ Load filepath -> xml file into dictionary tree. """
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
            # "item.text" == None <=> "<item></item>".
            if (text is not None) and (text.strip().replace("\n", "")):
                # ElementTree unescapes newline so I'm reverting back.
                text = text.replace('\\n', '\n')
                # Merge same-key entries.
                if key in newDict:
                    text = newDict[key] + ', ' + text
                # Parse if requested.
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
            newText = []
            for txt in text.split(', '):
                newText.append(self._parse(txt, 'int'))
            return tuple(newText)

        raise KeyError('Method "{}" not found!'.format(method))

    def generate_layout(self, startBy):
        """ Generate layout given starting position.

        Starting position keys are sorted alphabetically
        (name them accordingly).
        """
        layout = []
        keys = sorted(self.nextDataset(startBy).keys())
        for key in keys:
            layout.append(self.stepIn({}, startBy + ' ' + key))

        return layout

    def nextDataset(self, nextSteps):
        """ Browse ElementTree based on argument indicator.

        Individual node turns must be separated by space.
        """
        data = self.data
        if not isinstance(nextSteps, list):
            nextSteps = nextSteps.split(' ')

        # Down the rabbit hole!
        for nextStep in nextSteps:
            data = data[nextStep]

        return data

    def stepIn(self, item, thisStep):
        """ Browse layout guided by 'next' key
        and fill missing values. """
        nextSteps = []
        for key, value in self.nextDataset(thisStep).items():
            # Next is not written into layout.
            if key == 'next':
                nextSteps = value.split(', ')
            # Keys having values from higher levels are NOT changed.
            elif key not in item:
                item[key] = value

        # Recursively browse all branches.
        while nextSteps:
            item = self.stepIn(item, nextSteps.pop())

        return item

    # def generate_palette(self, name):
    #     """ Make palette out of used colors. Then import it into Gimp. """
    #     palette = []
    #     for item in self.data['color']:
    #         pass

    #     return


# ---MAIN---
if __name__ == "__main__":
    main()
