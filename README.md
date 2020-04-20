# card-assembler

Card Assembler is a free and open-source plug-in for Gimp. Assembles a card (gimp image) according to xml file blueprint. Meant for board game card creation. Supports templates.

## Features

* Create image, single-colour layer, textbox, layer group, import layers from predefined file.
* Load card layout information from a xml file blueprint.
* Supports command chaining, making templates possible.

## Installation

Copy `Card Assembler` folder into your Gimp plug-in folder: `<user>/AppData/Roaming/GIMP/<version>/plug-ins/`. Then you can find the addon in Gimp menu bar as `Card Assembler`.

Data folder `CardAssembler_Data` can be renamed and located anywhere. When you run the plug-in, Gimp will ask you for its location. In this folder, the main script will look for the suplemental script (CardAssembler_Definitions.py) and Blueprint.xml.



Feel free to comment, share ideas or report bugs.
