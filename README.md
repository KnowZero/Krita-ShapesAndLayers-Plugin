# Shapes and Layers Krita Plugin
This plugin includes a collection of tools to manipulate vector layers and shapes. (Requires Krita 5.0+) 

## Features
### Split Shapes Into Layers
```Usage: Layer->Split->Split Vector Shapes Into Layers...```

Finds all shapes inside a vector layer and splits each shape into its own layer. Group shapes will be made into group layers, and shapes will be made into either their own vector layer or their own paint/raster layer depending on the option chosen.
You can also choose the depth you wish it to traverse by changing the top-level group depth option. By default, the top-level group setting is set to be equal to the top most non-group shape it finds. 

### Adjust Font Sizes
```Usage: Tools->Shapes And Layers->Adjust Font Sizes...```

Finds all text shapes within a document and adjusts them according to the operation chosen. This will also adjust text within the group layers
The default 0.75 division is for restoring the font sizes to the Krita 4 sizes 
