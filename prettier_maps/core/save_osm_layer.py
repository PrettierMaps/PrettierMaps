from pathlib import Path

from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer


def has_layers() -> bool:
    return bool(QgsProject.instance().mapLayers())


def save_quick_osm_layers(output_directory: str):
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

            # Export the layer's style to a QML file
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

            # Add the permanent layer to the QGIS project
            permanent_layer = QgsVectorLayer(
                f"{output_file}|layername={new_layer_name}", new_layer_name, "ogr"
            )
            QgsProject.instance().addMapLayer(permanent_layer)

            # Load the style from the QML file into the new layer
            permanent_layer.loadNamedStyle(str(qml_file))

            # Optionally, remove the temporary layer from the project
            QgsProject.instance().removeMapLayer(layer.id())

            # Delete the QML file to save storage space
            qml_file.unlink()
