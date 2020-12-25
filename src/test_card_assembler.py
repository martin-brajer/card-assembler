# -*- coding: utf-8 -*-
"""
Testing of both scripts: :mod:`cardassembler` and :mod:`blueprint`.

.. note::
    Run this script directly to run a :mod:`unittest`.
"""


import os
import re
import sys
import unittest

import xml.etree.ElementTree as ET
import pycodestyle

import blueprint
# Bypass internal Gimp's python gimpfu package imported
# by :mod:`cardassembler`.
from MyMock import Gimpfu as Mock_Gimpfu
sys.modules['gimpfu'] = Mock_Gimpfu()
import cardassembler  # nopep8


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """ Test that we conform to PEP-8. """
        style = pycodestyle.StyleGuide()
        path = os.path.abspath(os.path.dirname(__file__))
        result = style.check_files([
            path + '\\blueprint.py',
            path + '\\cardassembler.py',
        ])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_version(self):
        """ Test whether :data:`__version__` follows
        `Semantic Versioning 2.0.0 <https://semver.org/>`_.
        """
        #: FAQ: Is there a suggested regular expression (RegEx) to
        # check a SemVer string?
        pattern = (
            r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0'
            r'|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-'
            r'9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*'
            r'))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)'
            r'*))?$'
        )
        self.assertTrue(re.search(pattern, blueprint.__version__))

    def test_version_equal(self):
        self.assertEqual(cardassembler.__version__, blueprint.__version__)

    def test_author_equal(self):
        self.assertEqual(cardassembler.__author__, blueprint.__author__)


class TestBlueprintMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.blueprint = blueprint.Blueprint(None)
        #: Beginning of example :file:`Minimal blueprint.xml`.
        XML = (
            '<data><card><command01_image><layer_type>image</layer_type>'
            '<size parse="tuple">800, 500</size></command01_image>'
            '</card></data>'
        )
        cls.element_tree = ET.fromstring(XML)
        #: Dict representation of :data:`XML`.
        cls.DICT = {'card': {'command01_image': {
            'layer_type': 'image',
            'size': (800, 500),
        }}}

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
        self.assertEqual(
            self.blueprint._ElementTree_to_dict(self.element_tree),
            self.DICT)

    def test_goto(self):
        self.blueprint.data = self.DICT
        self.assertEqual(
            self.blueprint._goto('card command01_image'),
            self.DICT['card']['command01_image'])


if __name__ == '__main__':
    unittest.main(exit=False)
