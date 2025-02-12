from pathlib import Path

from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer


def has_layers() -> bool:
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
        if (
            isinstance(layer, QgsVectorLayer)
            and layer.isValid()
            and layer.dataProvider().name() == "memory"
        ):
            geom_type = layer.geometryType()
            geom_type_str = ["point", "line", "polygon"][geom_type]

            new_layer_name = f"{layer.name()}_{geom_type_str}"
            layer.setName(new_layer_name)
            output_file = str(Path(output_directory) / f"{new_layer_name}.gpkg")

            qml_file = Path(output_directory) / f"{new_layer_name}.qml"
            layer.saveNamedStyle(str(qml_file))

            # Save the temporary layer to a GeoPackage
            QgsVectorFileWriter.writeAsVectorFormat(
                layer,
                output_file,
                "UTF-8",
                layer.crs(),
                "GPKG",
                layerOptions=["GEOMETRY_NAME=geom", f"layerName={new_layer_name}"],
            )

            permanent_layer = QgsVectorLayer(
                f"{output_file}|layername={new_layer_name}", new_layer_name, "ogr"
            )
            QgsProject.instance().addMapLayer(permanent_layer)

            permanent_layer.loadNamedStyle(str(qml_file))

            # Delete the QML file to save storage space and remove the temporary layer
            # from the project
            QgsProject.instance().removeMapLayer(layer.id())
            qml_file.unlink()
