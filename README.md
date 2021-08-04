 
# Shapes and Layers Krita Plugin
## v.0.04
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

