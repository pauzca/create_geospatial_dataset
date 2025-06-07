# Convert predicted segmentation masks to a shapefile
import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape, MultiPolygon, Polygon
from affine import Affine
import pickle
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import argparse
import geopandas as gpd
from rasterio.mask import mask
from shapely.ops import unary_union


"""
Convertir mascaras binarias de segmentación a shape files para su visualización en QGIS
the segmentation output should be in a pkl file with the name "masks_dict.pkl". 
And should have two columns
"filename" for the tile image name
"mask" for one of the masks in that image
There should be as many rows as there were initially bounding boxes

Necesita parametros:

--folder: donde se encuentran las mascaras de segmentación binarias
--metadata: ruta al archivo de metadatos que contiene la información geográfica de las imágenes y mosaicos

"""

# convert segmentation masks stored in binary arrays to a shape file for display on qgis
def convert_masks_to_shapefile(args):

    masks_folder = args.folder
    metadata_file = args.metadata

    global image_folder
    global segmentation_dict

    shape_folder = os.path.join(masks_folder,"shapes")
    if not os.path.exists(shape_folder):
        os.makedirs(os.path.join(masks_folder,"shapes"))

    output_file = os.path.join(shape_folder,"mask_segmentation.shp")

    # read metadata file
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    tiles_geo = metadata["tiles"]
    geo_mosaic = metadata["mosaic"]
    tiles_geo_df = pd.DataFrame(tiles_geo)

    # Example geoinformation (replace with your data source)
    pixel_width = geo_mosaic["pixel_width"]
    pixel_height = geo_mosaic["pixel_height"]

    all_polygons = []
    count_masks = 0

    segmentation_masks = [f for f in os.listdir(masks_folder) if f.endswith(".png")]

    for i, mask_file in enumerate(segmentation_masks):
        # Example mask for the tile (replace with your actual masks)
        tile_info = tiles_geo_df[tiles_geo_df["tile"] == mask_file].iloc[0]
        mask = cv2.imread(os.path.join(masks_folder, mask_file), cv2.IMREAD_GRAYSCALE)
        plt.imshow(mask)
        plt.title(mask_file)
        plt.show()
        # convert mask to geo referenced format
        mask = cv2.resize(mask, (tile_info["tile_width"], tile_info["tile_height"]), interpolation=cv2.INTER_NEAREST)
        # Create affine transform for the tile
        transform = Affine(
            pixel_width, 0, tile_info['xmin'],
            0, pixel_height, tile_info['ymin']
        )

        count_masks += 1
        # Create a binary mask for this specific ID
        mask_geom = [
            shape(geom)
            for geom, value in shapes(mask, transform=transform)
            if value == 255
        ]

        # Combine multiple disconnected parts into a MultiPolygon if needed
        combined_geom = MultiPolygon(mask_geom) if len(mask_geom) > 1 else mask_geom[0]
        # Store the geometry and corresponding metadata
        all_polygons.append(combined_geom)
    
    print(f"Processed {count_masks} masks")
    
    # Create a single GeoDataFrame
    # Combine todas las geometrías en una sola
    merged_geometry = unary_union(all_polygons)
    # Crea el GeoDataFrame con una sola fila
    gdf = gpd.GeoDataFrame({'value': [1], 'geometry': [merged_geometry]}, crs="EPSG:3857")

    print(gdf)
    print(gdf.geometry.is_empty.sum(), "empty geometries")

    # Save to one shapefile
    gdf.to_file(output_file)
    print(f"✅ Shapefile saved at: {output_file}")

    area_m2 = gdf.geometry.area.iloc[0]
    print(f"Área cubierta total: {area_m2:.2f} m²")

    area_ha = area_m2 / 10_000
    print(f"Área en hectáreas: {area_ha:.2f} ha")






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # segmentation folder
    parser.add_argument('--folder', type=str, default='/home/paula/Documentos/PROYECTOS/segmentacion_vegetacion/segmentation', help='folder containing segmentation masks')
    parser.add_argument('--metadata', type=str, default='/home/paula/Documentos/PROYECTOS/segmentacion_vegetacion/tile_metadata.json', help='path to metadata file')

    args = parser.parse_args()

    convert_masks_to_shapefile(args)



