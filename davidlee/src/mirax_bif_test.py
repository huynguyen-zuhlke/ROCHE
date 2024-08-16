from numpy._core.multiarray import dtype
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

        # Need to set shaped to False so description is not set to the shape of the image 
        with tifffile.TiffWriter(output_path, bigtiff=True, shaped=False ) as tif:
            ################ associated_images #######################
            label = slide.associated_images["label"]
            label_data = np.array(label)

            # IMPORTANT - xmp tag should be set according to the bif spec.
            label_xmp = r'''<?xml version='1.0' encoding='utf-8' ?>
            <Metadata>
                <iScan Mode="brightfield" Magnification="20" ScanRes="0.465"
                    UnitNumber="QIA00039" ScannerModel="VENTANA DP 600" Z-layers="1"
                    Z-spacing="1" UserName="Roche Service" BuildVersion="1.0.0.972-8f4bc6c"
                    BuildDate="2/18/2022 0:6:59 PM" SlideAnnotation="" ShowLabel="1"
                    LabelBoundary="0" Barcode1D="" Barcode2D="" FocusMode="0" FocusQuality="1"
                    ScanMode="1" ScanWhitePoint="235" Anonymization="0">
                    <AOI0 Left="206" Top="1888" Right="959" Bottom="1073"/>
                </iScan>
                <ProcessingParameters>
                    <Registration Method="None" UseLinearEncoder="1" Radius="0"
                        OverlapMinMicrons="" OverlapMaxMicrons="" ShiftMaxMicrons="" OverlapMin=""
                        OverlapMax="" ShiftMax=""/>
                    <Color TwistRGB="1,0,0,0,1,0,0,0,1" Applied="0"/>
                </ProcessingParameters>
            </Metadata>'''

            label_xmp_bytes = label_xmp.encode("utf-8")

            tif.write(
                label_data,
                dtype=label_data.dtype,
                # IMPORTANT - need to set ImageDescription (TIFFTag 270) to "Label_Image" according to the spec.
                description="Label_Image",
                extratags=[
                    (700, 'B', len(label_xmp_bytes), label_xmp_bytes, True)
                ],
                # metadata doesn't seem to be necessary
                metadata=None,
                # software (TIFFTag 305) must start with "ScanOutputManager" otherwise TIFFFILE won't recognize it as bif file
                software="ScanOutputManager",
            )

            thumbnail = slide.associated_images["thumbnail"]
            thumbnail_data = np.array(thumbnail)
            tif.write(
                thumbnail_data,
                dtype=thumbnail_data.dtype,
                # IMPORTANT - not sure if it's required by the spec but ImageDescription needs to be set to "Thumbnail" for a
                # page to be recognized as thumbnail_by TIFFFILE
                # description="Thumbnail",
                description="Probability_Image",
                # metadata doesn't seem to be necessary
                metadata=None,
                # software (TIFFTag 305) must start with "ScanOutputManager" otherwise TIFFFILE won't recognize it as bif file
                software="ScanOutputManager 1.0.0.972-8f4bc6c",
            )

            base_level = 0
            # levels_to_read = slide.level_count - base_level
            levels_to_read = 1


            for level in range(base_level, (base_level + levels_to_read)):
                print(f"\n=== Converting level {level} ===")

                # Has to set subifds to None, and sub_file_type to None for the base level too.
                sub_ifds = None
                sub_file_type = None if level == base_level else 1
                

                # width, height = slide.level_dimensions[level]
                width, height = (512, 1536)

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

                # IMPORTANT - xmp tag needs to be set
                # 1. so that TIFFFILE can recognize it as bif format
                # 2. so that it follows the BIF spec
                #
                # The root xml node must be <EncodedInfo>
                xmp = r'''<?xml version='1.0' encoding='utf-8' ?>
<EncodeInfo Ver="2">
    <SlideInfo Rack="0" Slot="3" BaseName="00000000-ffe1-0000-0000-deadbeef0000" OutputFileName="/raid/HER2 IHC 2019-2 Core2 Ki67.bif">
        <ServerDirectory Path="" Copy="false"/>
        <LabelImage Path="" ShowLabel="1" LabelBoundary="0"/>
        <iScan Mode="brightfield" Magnification="20" ScanRes="0.465"
            UnitNumber="QIA00039" ScannerModel="VENTANA DP 600" Z-layers="1"
            Z-spacing="1" UserName="Roche Service" BuildVersion="1.0.0.972-8f4bc6c"
            BuildDate="2/18/2022 0:6:59 PM" SlideAnnotation="" ShowLabel="1"
            LabelBoundary="0" Barcode1D="" Barcode2D="" FocusMode="0" FocusQuality="1"
            ScanMode="1" ScanWhitePoint="235" Anonymization="0">
            <AOI0 Left="0" Top="1536" Right="512" Bottom="0" AOIScanned="1"/>
        </iScan>
        <AoiInfo XIMAGESIZE="512" YIMAGESIZE="512" NumRows="3" NumCols="1"
            Pos-X="0" Pos-Y="1536" DirPath=""/>
    </SlideInfo>
    <SlideStitchInfo Left="-1" Top="-1" Right="-1" Bottom="-1">
        <ImageInfo AOIScanned="1" AOIIndex="0" NumRows="3" NumCols="1"
            Width="512" Height="512" Pos-X="0" Pos-Y="1536">
            <TileJointInfo FlagJoined="1" Confidence="100" Direction="UP" Tile1="1" 
                Tile2="2" OverlapX="0" OverlapY="0"/>
            <TileJointInfo FlagJoined="1" Confidence="100" Direction="UP" Tile1="2" 
                Tile2="3" OverlapX="0" OverlapY="0"/>
        </ImageInfo>
    </SlideStitchInfo>
    <AoiOrigin>
        <AOI0 OriginX="0" OriginY="0"/>
    </AoiOrigin>
</EncodeInfo>'''

                xmp_bytes = xmp.encode("utf-8")
                extratags = [] if level > base_level else [
                    (700, 'B', len(xmp_bytes), xmp_bytes, True)
                ] 


                tile_size = (512, 512)
                format = "rgb"
                # compression = "jpeg"
                compression = "zlib"

                print(f"Reading layer region {dict(x= roi_x, y= roi_y, width= roi_width, height= roi_height)}")
                image = slide.read_region((roi_x, roi_y), level, (roi_width, roi_height))
                #base_region.convert("RGB")

                print(f"creating numpy array")
                # data = np.array(image, dtype="uint8")
                # data = np.random.randint(0, 255, (1024, 512, 4), 'uint8')
                data = np.full((1536, 512, 4), [255, 165, 0, 1], 'uint8')
                data = data[..., :-1]
                print(data.shape)

                mag = 20

                tif.write(
                    data,
                    dtype=data.dtype,
                    tile=tile_size,
                    photometric=format,
                    # IMPORTANT - ImageDescription (TIFFTag 270) needs to be in the format "level=<level> mag=<magnification> quality=<quality>".
                    # For example: "leve=0 mag=40 quality=95".
                    # TIFFFILE requires at least "level=" to be included.
                    description=f"level={level} mag={20 / (2 ** level)} quality=95",
                    compression=compression,
                    resolution=resolution,
                    resolutionunit=resolution_unit,
                    subifds=sub_ifds,
                    subfiletype=sub_file_type,
                    metadata=None,
                    extratags=extratags,
                    maxworkers=6,
                    # software (TIFFTag 305) must start with "ScanOutputManager" otherwise TIFFFILE won't recognize it as bif file
                    software="ScanOutputManager 1.0.0.972-8f4bc6c"
                )


        
        end_time = time.time()
        print("Successfully saved to " + output_path + " in " + str(end_time - start_time) + " seconds")



# source_path = "../samples/mrxs/CMU-1-Saved-1_16/CMU-1-Saved-1_16.mrxs"
source_path = "../samples/mrxs/Mirax2-Fluorescence-1/Mirax2-Fluorescence-1.mrxs"
#foo(source_path)
mrxs_to_bif(source_path)

temp = r'''
<TileJointInfo FlagJoined="1" Confidence="100" Direction="RIGHT" Tile1="1" 
                Tile2="2" OverlapX="0" OverlapY="0"/>
'''