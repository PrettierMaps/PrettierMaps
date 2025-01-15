from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer

# Define the output directory
output_directory = r"C:\Users\ap_va\OneDrive\Documents\Irene - UofG\Year 3\PrettierMap"

# Iterate through all layers in the QGIS project
for layer in QgsProject.instance().mapLayers().values():
    # Check if the layer is a vector layer and a temporary memory layer
    if isinstance(layer, QgsVectorLayer) and layer.isValid() and layer.dataProvider().name() == 'memory':
        # Define the output file path and layer name
        print(layer)
        layer_name = layer.name()
        output_file = f"{output_directory}\\{layer_name}.gpkg"
        
        # Save the temporary layer to a GeoPackage
        QgsVectorFileWriter.writeAsVectorFormat(layer, output_file, "UTF-8", layer.crs(), "GPKG", layerOptions=['GEOMETRY_NAME=geom', f'layerName={layer_name}'])
        
        # Add the permanent layer to the QGIS project
        permanent_layer = QgsVectorLayer(f'{output_file}|layername={layer_name}', layer_name, "ogr")
        QgsProject.instance().addMapLayer(permanent_layer)
        
        # Optionally, remove the temporary layer from the project
        QgsProject.instance().removeMapLayer(layer.id())

print("All temporary vector layers have been converted to permanent layers.")