import pandas as pd
import numpy as np
from osgeo import gdal
import os
from PIL import Image
import json
import math

class Mosaic:


    def __init__(self, input_tiff = None):

        if input_tiff:
            self.dataset = gdal.Open(input_tiff)

            if self.dataset is None:
                print(f"Error opening file {input_tiff}")
                exit(1)

            self.image_width = self.dataset.RasterXSize
            self.image_height = self.dataset.RasterYSize

            self.geotransform = self.dataset.GetGeoTransform()
            self.gds_x, self.gds_y = self.get_pixel_cm()

    

    def get_pixel_cm(self):
        # Approximate conversion factor: 1 degree = 111,320 meters at the equator
        # Convert pixel size from degrees to centimeters
        #pixel_size_x_cm = abs(self.geotransform[1]) * 111320 * 100
        #pixel_size_y_cm = abs(self.geotransform[5]) * 111320 * 100
        return np.abs(self.geotransform[1] * 100), np.abs(self.geotransform[5]) * 100
        #return pixel_size_x_cm, pixel_size_y_cm

    def calculate_tile_size_px(self, tile_width_cm):
        tile_width = int(tile_width_cm / self.gds_x)
        tile_height = int(tile_width_cm / self.gds_y)
        return tile_width, tile_height

    def total_tiles(self, tile_width_cm, overlap_percentage,):
        tile_width, tile_height = self.calculate_tile_size_px(tile_width_cm)
        overlap_pixels = int(tile_width * overlap_percentage) 
        x_stride = tile_width - overlap_pixels
        y_stride = tile_height - overlap_pixels

        n_tiles_x = math.ceil((self.image_width - overlap_pixels) / x_stride)
        n_tiles_y = math.ceil((self.image_height - overlap_pixels) / y_stride)

        total_tiles = n_tiles_x * n_tiles_y
        return total_tiles


    def generate_tiles(self, tile_width_cm, overlap_percentage, blank_threshold, output_dir, output_tile_width):

        tile_width, tile_height = self.calculate_tile_size_px(tile_width_cm)
        print( tile_width, tile_height)

        overlap_pixels = int(tile_width * overlap_percentage) # overlap in pixels
        print(overlap_pixels)

        # Calculate the step size (stride) for the loop
        x_stride = tile_width - overlap_pixels
        y_stride = tile_height - overlap_pixels

        almost_empty_counter = 0
        tile_with_no_labels_counter = 0
        labels_per_tile = []
        tile_count = 0
        # Calculate the size of the dataset in hectares
        pixel_area_cm2 = self.gds_x * self.gds_y  # Area of one pixel in cm²
        pixel_area_m2 = pixel_area_cm2 / 10000  # Convert cm² to m²
        pixel_area_ha = pixel_area_m2 / 10000  # Convert m² to hectares

        total_area_ha = self.image_width * self.image_height * pixel_area_ha


        os.makedirs(output_dir + "/dataset/images", exist_ok=True)
        os.makedirs(output_dir + "/dataset/labels", exist_ok=True)
        all_metadata = {"tiles": [],
                        "mosaic": {
                            "width": self.image_width,
                            "height": self.image_height,
                            "geotransform": self.geotransform,
                            "gds_x": self.gds_x,
                            "gds_y": self.gds_y,
                            "pixel_width": self.geotransform[1],
                            "pixel_height": self.geotransform[5],
                            "output_tile_width": output_tile_width,
                            "output_tile_height": output_tile_width,
                            "overlap_percentage": overlap_percentage,
                            "overlap_pixels": overlap_pixels,
                            "tile_size_cm": tile_width_cm
                        } }
        

        # Loop over the image, generating tiles
        for x_offset in range(0, self.image_width, x_stride):
            for y_offset in range(0, self.image_height, y_stride):
                # Calculate width and height for the current tile (handle edge tiles)
                w = min(tile_width, self.image_width - x_offset)
                h = min(tile_height, self.image_height - y_offset)

                # Read the tile data using GDAL
                tile = self.dataset.ReadAsArray(x_offset, y_offset, w, h)
                tile = np.transpose(tile, (1, 2, 0))  # Rearrange to (height, width, bands)
                #print(tile.shape)

                # Check if the tile is completely white (255, 255, 255 for RGB)
                if np.all(tile == 255) or np.all(tile == 0):
                    #print(f"Skipping tile at ({x_offset}, {y_offset}) - completely empty")
                    continue  # Skip this tile
                
                # Check if the tile is mostly blank (90% or more)
                blank_pixels = np.sum(tile == 255) + np.sum(tile == 0)
                total_pixels = tile.size
                if blank_pixels / total_pixels >= blank_threshold:
                    tile_image = Image.fromarray(tile)
                    almost_empty_counter += 1
                    continue  # Skip this tile

                if tile_image.mode != "RGB":
                    tile_image = tile_image.convert("RGB")
                    
                # Convert the tile to a PNG format using PIL
                tile_image = Image.fromarray(tile)
                
                # resize tile image to fit the output pixel size for the model
                tile_resized = tile_image.resize((output_tile_width, output_tile_width))

                # Define the output paths
                output_tile = os.path.join(output_dir, f"dataset/images/tile_{x_offset}_{y_offset}.png")
                
                # Save the tile as a PNG image
                tile_resized.save(output_tile)
                print(f"Saved tile: {output_tile} ({w}x{h} pixels)")


                # Calculate the geospatial coordinates of the top-left corner of the tile
                # rembember the output tile width and height is just a resize, the coordinates are still the same
                x_min_tile = self.geotransform[0] + x_offset * self.geotransform[1]
                y_min_tile = self.geotransform[3] + y_offset * self.geotransform[5]
                x_max_tile = x_min_tile + w * self.geotransform[1]
                y_max_tile = y_min_tile + h * self.geotransform[5]

                # Store the geospatial metadata for this tile
                # This will help convert the bboxes for the tile back to geo format to display them un qgis
                metadata = {
                    "tile": f"tile_{x_offset}_{y_offset}.png",  # Name of the tile
                    "xmin": x_min_tile,
                    "ymin": y_min_tile,
                    "xmax": x_max_tile,
                    "ymax": y_max_tile,
                    "tile_width": w,
                    "tile_height": h,
                    "x_offset": x_offset,
                    "y_offset": y_offset
                }

                # Append this tile's metadata to the list
                all_metadata["tiles"].append(metadata)


        # Save all the metadata to a single JSON file
        metadata_file = os.path.join(output_dir, "tile_metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(all_metadata, f, indent=4)
            print(f"Metadata saved to {metadata_file}")


        total_tiles = len(labels_per_tile) + tile_with_no_labels_counter

        print(f"Area en hectareas: {total_area_ha}")
        print(f"Tiles discarded because they were almost all blank: {almost_empty_counter}")

        print(f"Total of saved tiles: {total_tiles}")

        # Save the statistics to a text file
        stats_output_path = os.path.join(output_dir, "tile_statistics.txt")
        with open(stats_output_path, 'w') as stats_file:
            stats_file.write(f"Area en hectareas: {total_area_ha}\n")
            stats_file.write(f"Tiles discarded because they were almost all blank: {almost_empty_counter}\n")
            stats_file.write(f"Total of saved tiles: {total_tiles}\n")

        print(f"Statistics saved to {stats_output_path}")



   