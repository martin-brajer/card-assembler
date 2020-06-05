# Card Assembler

Card Assembler is a free and open-source plug-in for Gimp. Assembles an image according to an xml file blueprint. Meant for board game card creation.

## Features

* Gimp tools: single-colour layer, textbox, import layers from given \*.xcf file etc.
* Load card layout information from an xml file blueprint.
* Command chaining, making templates possible.
* Export colors used in blueprint to Gimp palette.

# Installation
Copy `card-assembler.py` file into your Gimp plug-in folder: `<user>/AppData/Roaming/GIMP/<version>/plug-ins/`. You can optionally add it to a folder named `card-assembler`. Then **restart Gimp**.

Then you can find the plug-in in the menu bar as `Card Assembler`.

## Data folder
Data folder `cardassembler_data` can be renamed and located anywhere. When you run the plug-in, Gimp will ask you for its location. In this folder, the main script will look for the supplemental script `cardassembler_definitions.py`, blueprints `*.xml` and data files containing layers to be imported.

# How to use this plug in
There is a new item in the *Menu bar* - `Card Assembler`. It contains this plug-in functions:
1. Card Assembler - main script,
2. Palette creator - exports colors used in blueprint to Gimp palette.

## Card Assembler parameters
* Data Folder - supplemental script and data files location. See [Installation > Data folder](README.md#data-folder) for details.
* XML file - name of the blueprint (*.xml) you want to use. Must be located in `Data folder`.
* CardIDs - path to the starting node within the blueprint.
  * Omit root node. Branches are separated by space.
  * Write each CardID entry on a separate line.
  * See [examples](README.md#examples) for details.
* Save - if so, the image will be saved to `Saved images/` subfolder to data folder as `<image name>.xcf`.

## Palette creator parameters
* Data Folder, XML file - same as above.
* PaletteID - path to colors starting node (assuming there is special color subtree).
* Name - new palette name.

# Creating Blueprint.xml
Card Assembler works with tree structure. When calling the plug-in in Gimp, you specify node, where to start. Its children are then alphabetically called to formulate respective commands. Each command must have `commandType` tag with one of the values [shown below](README.md#command-types). For each of them respective parameters are listed. Optional parameters include default values.

## Nesting
Command can contain any number of `next` tags. Each points to another node in the tree whose children are appended to the initial command. This tag can only add new tags, not rewrite the old ones. Intentional usage is inserting card specific tags first and then let `next` point to some more general version (i.e. template).

It is useful to create separate color dedicated subtree. See [Palette Creator parameters](README.md#palette-creator-parameters).

## Parsing
If a parameter type is not *string*, add attribute `parse` to the parameter's tag with value `int`, `float` or `tuple` as needed.

For example: `<position parse="tuple">100, 125</position>`.

## Command types
- image
  - size (tuple)
  - name (string)
- monochrome
  - size (tuple)
  - color (string) - hex code
  - *name (string) = "Monochrome"*
  - *position (tuple) = (0, 0)*
  - *addToPosition (int) = 0* - `-1` adds to just defined group
- import_layer_load
  - filename (string)
  - name (string)
- import_layer
  - targetFile (string) - use `name` filled in import_layer_load
  - targetLayer (string)
  - *name (string) = targetLayer*
  - *position (tuple) = (0, 0)*
  - *addToPosition (int) = 0*
- group
  - *name (string) = "Group"*
  - *addToPosition (int) = 0*
- text
  - text (string)
  - font (string)
  - fontSize (int)
  - *fontScale (float) = 1*
  - *name (string) = "Text Layer"*
  - *color (string) = "#000000"*
  - *size (tuple) = autosize*
  - *lineSpacing (float) = 0*
  - *letterSpacing (float) = 0*
  - *justification (int) = 0* - left: `0`, right: `1`, center: `2`, fill: `3`
  - *position (tuple) = (0, 0)*
  - *addToPosition (int) = 0*
- select
  - *mode(string) = "select"* - possible values: `select`, `deselect`, any other
  - *left(float) = 0* - dimensions in percentage of image size
  - *right(float) = 100*
  - *top(float) = 0*
  - *bottom(float) = 100*
- mask
  - layer(string)
  - *<`select` commands>*
- hide
  - *no parameters*

Additionally, **all commands** can use [`next` tag](README.md#nesting).

# Examples
There are two example blueprints in [`cardassembler_data`](../../tree/master/CardAssembler_Data) folder. One shows very simple blueprint to start with. The second one shows intended use.

## Simple
`Blueprint_Example_Simple.xml` shows very simple blueprint to make sense of how this plug-in works.

The only card there can be created by filling `example` into CardIDs field.

## Full
`Blueprint_Example_Full.xml` shows intended usage including structure to make adding more similar items easier and clearer.

The only card there can be created by filling `unique spell example` into CardIDs field. Colors can be exported by filling `color` into [PaletteID field](README.md#palette-creator-parameters).

# License
Card Assembler is licensed under the [MIT license](LICENSE).

Feel free to comment, share ideas or report bugs.
