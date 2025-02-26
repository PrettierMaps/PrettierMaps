from qgis.core import QgsProject, QgsVectorLayer


def is_quick_osm_layer(layer):
    variable_names = layer.customProperty("variableNames")
    if variable_names is None:
        return False
    if "quickosm_query" not in variable_names:
        return False
    return True


def has_quick_osm_layers():
    for layer in QgsProject.instance().mapLayers().values():
        if isinstance(layer, QgsVectorLayer) and is_quick_osm_layer(layer):
            return True
    return False
