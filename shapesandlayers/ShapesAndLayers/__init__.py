from . import qt_compat
from krita import DockWidgetFactory, DockWidgetFactoryBase

from .ShapesAndLayers import *
from .ShapesAndLayersShapesAsLayers import shapesAndLayersShapesAsLayers
from .ShapesAndLayersSelectionArrangeDocker import shapesAndLayersSelectionArrangeDocker

Application.addDockWidgetFactory(
    DockWidgetFactory(
        "shapesAndLayersShapesAsLayers",
        DockWidgetFactoryBase.DockPosition.DockRight,
        shapesAndLayersShapesAsLayers,
    )
)

Application.addDockWidgetFactory(
    DockWidgetFactory(
        "shapesAndLayersSelectionArrangeDocker",
        DockWidgetFactoryBase.DockPosition.DockRight,
        shapesAndLayersSelectionArrangeDocker,
    )
)
