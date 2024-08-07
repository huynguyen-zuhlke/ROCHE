import openslide
import numpy as np
import tifffile
from datetime import datetime
import time


def print_properties(slide):
    for(key, value) in slide.properties.items():
        print(key + " = ", value)

def mrxs_to_bif(input_path, output_path = None, debug = False ):
    start_time = time.time()
    
    if output_path == None: 
        # output_path = "mrxs-bif-" + datetime.now().strftime("%m-%d-%H-%M-%S") + ".bif"
        output_path = "../outputs/mrxs-bif-output.bif"

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    with openslide.OpenSlide(input_path) as slide:
        
        if debug: print_properties(slide)

        print(f"Number of levels: {slide.level_count}")

        with tifffile.TiffWriter(output_path, bigtiff=True ) as tif:
            base_level = 0
            levels_to_read = slide.level_count


            for level in range(base_level, (base_level + levels_to_read)):
                print(f"\n=== Converting level {level} ===" )

                extratags=[]

                # Has to set subifds to None, and sub_file_type to None for the base level too.
                sub_ifds = None
                sub_file_type = None if level == base_level else 1
                

                width, height = slide.level_dimensions[level]

                # bounds_x = int(slide.properties.get("openslide.bounds-x", 0))
                # bounds_y = int(slide.properties.get("openslide.bounds-y", 0))
                # bounds_width = int(slide.properties.get("openslide.bounds-width", 0))
                # bounds_height = int(slide.properties.get("openslide.bounds-height", 0))
                
                bounds_x = 0
                bounds_y = 0
                bounds_width = width
                bounds_height = height

                print(f"Bounds properties:")
                print((bounds_x, bounds_y, bounds_width, bounds_height))

                roi_x = bounds_x
                roi_y = bounds_y
                roi_width = bounds_width 
                roi_height = bounds_height

                resolution_unit = "centimeter"
                micrometer_pixel_x = float(slide.properties[f"mirax.LAYER_0_LEVEL_{level}_SECTION.MICROMETER_PER_PIXEL_X"])
                micrometer_pixel_y = float(slide.properties[f"mirax.LAYER_0_LEVEL_{level}_SECTION.MICROMETER_PER_PIXEL_Y"])

                # How many pixels per centimeter. Resolution unit is currently hardcoded to centimeter.
                resolution = (1e4 / micrometer_pixel_x, 1e4 / micrometer_pixel_x)
                print(f"Pixel size: {(micrometer_pixel_x, micrometer_pixel_y)}")
                print(f"Resolution: {resolution}")


                mdata = {}

                print(f"metadata:")
                print(mdata)

                tile_size = (256, 256)
                format = "rgb"
                compression = "zlib"

                print(f"Reading layer region {dict(x= roi_x, y= roi_y, width= roi_width, height= roi_height)}")
                image = slide.read_region((roi_x, roi_y), level, (roi_width, roi_height))
                #base_region.convert("RGB")

                print(f"creating numpy array")
                data = np.array(image)

                print(f"writing to output file")
                tif.write(
                    data,
                    dtype=data.dtype,
                    tile=tile_size,
                    photometric=format,
                    compression=compression,
                    resolution=resolution,
                    resolutionunit=resolution_unit,
                    subifds=sub_ifds,
                    subfiletype=sub_file_type,
                    metadata=mdata,
                    extratags=extratags,
                    maxworkers=6,
                )


            # associated_images
            thumbnail = slide.associated_images["thumbnail"]
            thumbnail_data = np.array(thumbnail)
            tif.write(
                thumbnail_data,
                dtype=thumbnail_data.dtype,
                metadata={
                    "Name": "thumbnail"
                }
            )
        
        end_time = time.time()
        print("Successfully saved to " + output_path + " in " + str(end_time - start_time) + " seconds")


source_path = "../samples/mrxs/CMU-1-Saved-1_16/CMU-1-Saved-1_16.mrxs"
mrxs_to_bif(source_path)
