# Card Assembler

Card Assembler is a free and open-source plug-in for Gimp. Assembles an image according to an xml file blueprint. Meant for board game card creation.

## Features

* Create image, single-colour layer, textbox, layer group, import layers from an xcf (Gimp) file.
* Load card layout information from a xml file blueprint.
* Supports command chaining, making templates possible.

## Installation

Copy `card-assembler.py` file into your Gimp plug-in folder: `<user>/AppData/Roaming/GIMP/<version>/plug-ins/`. Then you can find the plug-in in Gimp menu bar as `Card Assembler`.

Data folder `cardassembler_data` can be renamed and located anywhere. When you run the plug-in, Gimp will ask you for its location. In this folder, the main script will look for the supplemental script `cardassembler_definitions.py` and blueprints `*.xml`.

## Examples

There are two example blueprints in `cardassembler_data` folder.

The first one (`Blueprint_Example_Simple.xml`) shows very simple blueprint to make sense of how this plug-in works. 

The second one (`Blueprint_Example_Full.xml`) shows intended usage, including structure for easier (and clearer) adding of another similar items.

Feel free to comment, share ideas or report bugs.
