Card Assembler overview
=======================

|Releases| |License| |Documentation Status|

.. |Documentation Status| image:: https://readthedocs.org/projects/card-assembler/badge/?version=latest
   :target: https://card-assembler.readthedocs.io/en/latest/?badge=latest
.. |License| image:: https://img.shields.io/github/license/martin-brajer/card-assembler
   :target: https://github.com/martin-brajer/card-assembler/blob/master/LICENSE
.. |Releases| image:: https://img.shields.io/github/v/release/martin-brajer/card-assembler
   :target: https://github.com/martin-brajer/card-assembler/releases

Card Assembler is a free and open-source plug-in for Gimp. Assembles an
image according to an XML file blueprint. Meant for board game card
creation.

Features
--------

* Gimp tools: single-colour layer, textbox, import layers from a given XCF
  file etc.
* Load card layout information from an XML file blueprint.
* Command chaining, making templates possible.
* Export colors used in blueprint to Gimp as a palette.

Installation
------------

Copy all PY files from :file:`src/` into :file:`card-assembler/`
in your Gimp plug-in folder:
:file:`{user}/AppData/Roaming/GIMP/{version}/plug-ins/`. Then **restart Gimp**.

How to use this plug in
-----------------------

There is a new item in the menu bar - :guilabel:`Card Assembler` containing:

1. :guilabel:`Card Assembler`: Create board-game cards.

   * :guilabel:`Data Folder`: Data files location. Mainly the following xml file.
   * :guilabel:`XML file`: Name of the blueprint (XML) you want to use.
   * :guilabel:`CardIDs`: Path to the starting node within the blueprint.

     * Omit the root node. Steps are separated by spaces.
     * Write each CardID entry on a separate line.

   * :guilabel:`Save`: Save the image into a data folder subfolder as
     :file:`{image name}.xcf`.

2. :guilabel:`Palette creator`: Export colors used in a blueprint to Gimp palette.

   * :guilabel:`Data Folder`, :guilabel:`XML file`: Same as above.
   * :guilabel:`PaletteID`: Path to the colors starting node (assuming there is
     a special color subtree).
   * :guilabel:`Name`: The new palette's name.

To keep Gimp's cmd open after the task is done, add **keepCmdOpen** file to the
plug-in folder.

License
-------

Card Assembler is licensed under the `MIT license`_.

.. _MIT license: https://github.com/martin-brajer/card-assembler/blob/master/LICENSE
