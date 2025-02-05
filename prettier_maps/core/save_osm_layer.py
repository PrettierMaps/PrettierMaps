from pathlib import Path

from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer


def has_layers() -> bool:
    """Returns whether or not the current Project has any layers

    :return: True if the current QGIS Project has one or more layers, False otherwise.
    """

    instance = QgsProject.instance()
    assert instance is not None
    layers = instance.mapLayers()

    # See if the map has any elements
    return bool(layers)


def save_quick_osm_layers(output_directory: str) -> None:
    """Saves the QuickOSM layers

    :param output_directory: Output directory to save the layers to
    """

    instance = QgsProject.instance()
    assert instance is not None

    for layer in instance.mapLayers().values():
        # Check if the layer is a vector layer and a temporary memory layer
        if (
            isinstance(layer, QgsVectorLayer)
            and layer.isValid()
            and layer.dataProvider().name() == "memory"
        ):
            geom_type = layer.geometryType()
            geom_type_str = ["point", "line", "polygon"][geom_type]

            # Define the output file path and layer name
            layer_name = layer.name()
            new_layer_name = f"{layer_name}_{geom_type_str}"
            layer.setName(new_layer_name)
            output_file = str(Path(output_directory) / f"{new_layer_name}.gpkg")

            # Save the temporary layer to a GeoPackage
            QgsVectorFileWriter.writeAsVectorFormat(
                layer,
                output_file,
                "UTF-8",
                layer.crs(),
                "GPKG",
                layerOptions=["GEOMETRY_NAME=geom", f"layerName={new_layer_name}"],
            )

            # Add the permanent layer to the QGIS project
            permanent_layer = QgsVectorLayer(
                f"{output_file}|layername={new_layer_name}", new_layer_name, "ogr"
            )
            QgsProject.instance().addMapLayer(permanent_layer)

            # Optionally, remove the temporary layer from the project
            QgsProject.instance().removeMapLayer(layer.id())
