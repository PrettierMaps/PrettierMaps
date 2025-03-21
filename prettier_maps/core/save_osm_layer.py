from pathlib import Path
from typing import Tuple

from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer

from prettier_maps.core.layers import is_quick_osm_layer


def is_to_be_saved(layer: QgsVectorLayer) -> bool:
    """
    Simple filter for selecting which layers will be saved.
    """
    return (
        isinstance(layer, QgsVectorLayer)
        and layer.isValid()
        and layer.dataProvider().name() == "memory"
    )


def get_file_paths(directory: str, name: str) -> Tuple[str, Path]:
    """
    Generates file path information given a directory and file name.

    :param directory: Location of file.
    :param name: File name.
    """

    output_file_str = str(Path(directory) / f"{name}.gpkg")
    qml_file = Path(directory) / f"{name}.qml"

    return output_file_str, qml_file


def add_permanent_layer(
    instance: QgsProject, qml: Path, output_file: str, name: str
) -> None:
    """
    Creates a permanent version of a layer and loads this into the current project.

    :param instance: Current project.
    :param qml: Path of the style file.
    :param output_file: Path of hte output file.
    :param name: Name of the permanent layer.
    """
    permanent_layer = QgsVectorLayer(f"{output_file}|layername={name}", name, "ogr")
    instance.addMapLayer(permanent_layer)
    permanent_layer.loadNamedStyle(str(qml))


def save_quick_osm_layers(output_directory: str) -> None:
    """
    Saves all layers which are outputs of QuickOSM queries.
    """

    instance = QgsProject.instance()
    assert instance is not None

    quick_osm_geoms = ("point", "line", "polygon")

    for layer in instance.mapLayers().values():
        if is_to_be_saved(layer):
            print(f"found layer {layer.name}")
            geom_type = layer.geometryType()
            geom_type_str = quick_osm_geoms[geom_type]

            new_layer_name = f"{layer.name()}_{geom_type_str}"
            layer.setName(new_layer_name)

            output_file_str, qml_file = get_file_paths(output_directory, new_layer_name)
            layer.saveNamedStyle(str(qml_file))

            # Save the temporary layer to a GeoPackage
            QgsVectorFileWriter.writeAsVectorFormat(
                layer,
                output_file_str,
                "UTF-8",
                layer.crs(),
                "GPKG",
                layerOptions=["GEOMETRY_NAME=geom", f"layerName={new_layer_name}"],
            )

            add_permanent_layer(instance, qml_file, output_file_str, new_layer_name)
            instance.removeMapLayer(layer.id())
