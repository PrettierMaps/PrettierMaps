def is_quick_osm_layer(layer):
    variable_names = layer.customProperty("variableNames")
    if variable_names is None:
        return False
    if "quickosm_query" not in variable_names:
        return False
    return True


def has_quick_osm_layers():
    pass
