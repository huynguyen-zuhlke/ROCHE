import os
from time import strftime
from tkinter import LabelFrame
from large_image.tilesource import base
from tifffile import TiffFile, TiffWriter
from PIL import Image

def convert(input_path):
    output_path = os.path.splitext(input_path)[0] + ".tif"
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    bif = TiffFile(input_path)

    print(f"Number of pages = {len(bif.pages)}")

    tif = TiffWriter(output_path, bigtiff=True)
    baseline = None
    label = None
    thumbnail = None

    for s in bif.series:
        print(f"Series = {s.name}")
        if s.name == "Label" or s.name == "Label_Image":
            label = s
        if s.name == "thumbnail" or s.name == "Thumbnail":
            thumbnail = s
        if s.name == "Baseline":
            baseline = s

    if(label != None):
        label_data = label.asarray()

        label_frame = label.keyframe
        label_xmp = label_frame.tags[700]
        label_xmp_bytes = label_xmp.value
    

        tif.write(
            label_data,
            dtype=label_data.dtype,
            # description="Label_Image",
            description=label_frame.description,
            photometric=label_frame.photometric,
            resolution=label_frame.resolution,
            subfiletype=0,
            subifds=None,
            subsampling=None,
            tile=None,
            extratags=[
                (700, 'B', label_xmp.count, label_xmp_bytes, True),
            ],
            metadata=None,
            # software (TIFFTag 305) must start with "ScanOutputManager" otherwise TIFFFILE won't recognize it as bif file
            software="ScanOutputManager 1.1.0.15854",
            datetime= label_frame.datetime.strftime("%Y:%m:%d %H:%M:%S") if label_frame.datetime is not None else None,
        )

    if(thumbnail != None):
        thumbnail_data = thumbnail.asarray()

        thumbnail_frame = thumbnail.keyframe
        thumbnail_xmp = thumbnail_frame.tags[700]
        thumbnail_xmp_bytes = thumbnail_xmp.value

        tif.write(
            thumbnail_data,
            dtype=thumbnail_data.dtype,
            photometric=thumbnail_frame.photometric,
            planarconfig=thumbnail_frame.planarconfig,
            resolution=thumbnail_frame.resolution,
            resolutionunit=thumbnail_frame.resolutionunit,
            # IMPORTANT - need to set ImageDescription (TIFFTag 270) to "Label_Image" according to the spec.
            description=thumbnail_frame.description,
            subfiletype=0,
            subifds=None,
            subsampling=thumbnail_frame.subsampling,
            tile=thumbnail_frame.tile,
            extratags=[
                (700, 'B', thumbnail_xmp.count, thumbnail_xmp_bytes, True),
            ],
            # metadata doesn't seem to be necessary
            metadata=None,
            datetime= thumbnail_frame.datetime.strftime("%Y:%m:%d %H:%M:%S") if thumbnail_frame.datetime is not None else None,
            software="ScanOutputManager 1.1.0.15854",
        )

    if baseline is not None:
        level_count = len(baseline.levels)
        base_level = 0
        for level in range(base_level, level_count):
            current_level = baseline.levels[level]

            level_frame = current_level.keyframe

            icc_bytes = baseline.levels[0].keyframe.tags[34675].value
            icc_bytes_count = baseline.levels[0].keyframe.tags[34675].valuebytecount
            extra_tags = [
                # (306, 's', len(date_time), date_time, True)
            ]
            if level == base_level:
                extra_tags.append((34675, 'B', icc_bytes_count, icc_bytes, True))

            data = current_level.keyframe.asarray()
            
            tif.write(
                data,
                dtype=data.dtype,
                tile=level_frame.tile,
                # photometric=level_frame.photometric,
                photometric="rgb",
                description=level_frame.description,
                compression=level_frame.compression,
                resolution=level_frame.resolution,
                resolutionunit=level_frame.resolutionunit,
                # subifds=None,
                # subfiletype=None if level == base_level else 1,
                subifds=level_frame.subifds,
                subfiletype=level_frame.subfiletype,
                subsampling=level_frame.subsampling,
                metadata=None,
                datetime= level_frame.datetime.strftime("%Y:%m:%d %H:%M:%S") if level_frame.datetime is not None else None,
                extratags=extra_tags,
                maxworkers=6,
                # software (TIFFTag 305) must start with "ScanOutputManager" otherwise TIFFFILE won't recognize it as bif file
                software="ScanOutputManager 1.1.0.15854"
            )
    
    print("Done")



input_files = [
    "../samples/bif/FBCa01-HE.bif",
    "../samples/bif/FBCa01-ER.bif",
    "../samples/bif/FBCa01-PR.bif",
    "../samples/bif/FBCa01-Ki67.bif",
    "../samples/bif/FBCa01-HER2 IHC.bif",
    "../samples/bif/DP600PE9_VT354156_PR.bif",
    "../samples/bif/DP600PE9_VT354163_ER.bif"
]

for input in input_files:
    convert(input)
    print()
