# card-assembler

Card Assembler is a free and open-source plug-in for Gimp. Assembles an image according to an xml file blueprint. Meant for board game card creation.

## Features

* Create image, single-colour layer, textbox, layer group, import layers from a file.
* Load card layout information from a xml file blueprint.
* Supports command chaining, making templates possible.

## Installation

Copy `CardAssembler.py` file into your Gimp plug-in folder: `<user>/AppData/Roaming/GIMP/<version>/plug-ins/`. Then you can find the plug-in in Gimp menu bar as `Card Assembler`.

Data folder `CardAssembler_Data` can be renamed and located anywhere. When you run the plug-in, Gimp will ask you for its location. In this folder, the main script will look for the suplemental script (CardAssembler_Definitions.py) and blueprints (*.xml).



Feel free to comment, share ideas or report bugs.
