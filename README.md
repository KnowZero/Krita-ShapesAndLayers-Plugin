 
# Shapes and Layers Krita Plugin
## v.0.10
This plugin includes a collection of tools to manipulate vector layers and shapes. (Requires Krita 5.0+) 

## Features
### Split Shapes Into Layers
```Usage: Layer->Split->Split Vector Shapes Into Layers...```

Finds all shapes inside a vector layer and splits each shape into its own layer. Group shapes will be made into group layers, and shapes will be made into either their own vector layer or their own paint/raster layer depending on the option chosen.
You can also choose the depth you wish it to traverse by changing the top-level group depth option. By default, the top-level group setting is set to be equal to the top most non-group shape it finds. 

### Adjust Font Sizes
```Usage: Tools->Scripts->Shapes And Layers->Adjust Font Sizes...```

Finds all text shapes within a document and adjusts them according to the operation chosen. This will also adjust text sizes within group shapes
The default 0.75 division is for restoring the font sizes to the Krita 4 sizes

### Visibility Helper
```Usage: Tools->Scripts->Shapes And Layers->Layer Visibility Helper...```

<p>Provides convenience features for handling invisible layers.</p>
<p><strong>Auto-select layer on making layer visible:</strong> When layer is made visible, select that layer</p>
<p><strong>Block invisible layers:</strong> Make invisible layers more noticable for those who get tunnel visioned</p>
<p><strong>Toggle visibility drag:</strong> Drag down or up to make multiple layers visible or invisible</p>

### Layer Styles Clipboard
```Usage: Layer->Layer Styles Clipboard```

Provides ability to copy, cut, paste and clear layer styles.
Shortcuts Available for configuration in Krita's shortcut manager


### Hide Dock Window Titlebars
```Usage: Tools->Scripts->Shapes And Layers->Hide Dock Window Titlebars```

Provides the ability to toggle the titlebars of Dock Windows on and off.
Holding Ctrl + Right mouse click will toggle individual dock windows. (If you click on child object of the window like a listbox, you may have to doubleclick)


### Font Manager Helper
```Usage: Tools->Scripts->Shapes And Layers->Font Manager Helper...```
<p>Provides the ability to add and remove temporary fonts without restarting Krita.</p>
<p><strong>Manual:</strong> You can add 1 or more fonts that will be added temporarily. Fonts are automatically removed when Krita is restarted.</p>
<p><strong>Auto:</strong> Monitor a temporary directory for new fonts and add/remove the fonts in realtime. If left running, it will resume next time Krita is opened and add all the fonts in the directory. Subdirectories are <strong>not</strong> supported. This is not intended for monitoring system font folders.</p>


### Show Eraser
```Usage: Tools->Scripts->Shapes And Layers->Show Eraser Cursor```

Changes the cursor into a visible eraser when the eraser is selected.
You can configure custom cursor SVG/PNG and set size with 4 different modes accross 3 different zoom levels.

<p>You can configure custom cursor SVG/PNG and set size with 4 different modes accross 3 different zoom levels.</p>
<p><strong>Default Size:</strong> Use default cursor.</p>
<p><strong>Static:</strong> Size of cursor will be exactly the number set.</p>
<p><strong>Adjust:</strong> Cursor will adjust based on zoom level.</p>
<p><strong>Hide:</strong> Cursor will be hidden.</p>


### Selection Arrange Docker ###
```Usage: Settings->Dockers->Selection Arrange Docker```

A docker that allows you to position paint layer nodes relative to rectangle selection
Note: Changes will not be added to undo history, a convenience undo has been added as a workaround, but it is suggested to save prior to use

### Shapes As Layers</u></h4>
```Usage: Settings->Dockers->Shapes As Layers```

A docker that allows you to see and select shapes on a vector layer as though each shape is its own layer. You can also view the SVG of said shape by pressing the Edit button.
Note: Shapes will only show when the Shape Select Tool is used.

### Selection Arrange Docker ###
```Usage: Settings->Dockers->Selection Arrange Docker```

A docker that allows you to position paint layer nodes relative to rectangle selection
Note: Changes will not be added to undo history, a convenience undo has been added as a workaround, but it is suggested to save prior to use
