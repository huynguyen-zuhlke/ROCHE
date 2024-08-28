from large_image.tilesource import base
from tifffile import TiffFile
from numpy import ndarray
import os
from PIL import Image

def bif_read(path: str):
    file = TiffFile(path)
    return file

def jpeg_write(file: TiffFile, path: str):
    baseline = get_bif_baseline(file) 
    if(baseline is None):
        raise ValueError("No Baseline IFD found.")

    max_dimension = 65000
    level_count = len(baseline.levels)
    
    # There's a size limit for PIL Image so we are writing the first
    # level with dimensions that are within that limit
    l = 0
    while l < level_count and (baseline.levels[l].shape[0] > max_dimension or baseline.levels[l].shape[1] > max_dimension):
        l += 1

    if l == level_count:
        raise ValueError(f"Image too large")

    level = baseline.levels[l]
    img = Image.fromarray(level.asarray())
    img.save(path, "JPEG")


def get_bif_baseline(bif: TiffFile):
    baseline = None
    for s in bif.series:
        if s.name.lower() == "baseline" or s.name.lower() == "baseline_image":
            baseline = s

    return baseline



def bif_to_jpeg(input_path, output_path=None):
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".jpg"
        print(f"Input: {input_path}")
        print(f"Output: {output_path}")

    bif = bif_read(input_path)
    jpeg_write(bif, output_path)

    # baseline = get_bif_baseline(bif)
    # if(baseline is None):
    #     raise ValueError("No Baseline IFD found.")
    #
    # max_dimension = 65000
    # l = 0
    # level_count = len(baseline.levels)
    #
    # while l < level_count and (baseline.levels[l].shape[0] > max_dimension or baseline.levels[l].shape[1] > max_dimension):
    #     l += 1
    #
    # if l == level_count:
    #     raise ValueError(f"Image too large")


    # output_1 = os.path.splitext(input_path)[0] + "-1.jpg"
    # output_2 = os.path.splitext(input_path)[0] + "-2.jpg"
    # data1 = baseline.asarray()
    # Image.fromarray(data1).save(output_1, "JPEG")
    #
    # data2 = baseline.keyframe.asarray()
    # Image.fromarray(data2).save(output_2, "JPEG")

    # level = baseline.levels[l]
    # print(f"Saving level {l} as the output jpeg.")
    # 
    # img = Image.fromarray(level.asarray())
    # img.save(output_path, "JPEG")

    print(f"Saved to {output_path}\n")


source_image = "../samples/bif/FBCa01-Ki67.bif" 
# to_jpeg(source_image) 

source_dir = "../samples/bif/"
for file in os.listdir(source_dir):
    if file.endswith(".bif"):
        # source_image = os.path.join(source_dir, file)
        # bif_to_jpeg(source_image)
        try:
            source_image = os.path.join(source_dir, file)
            bif_to_jpeg(source_image)
        except ValueError:
            print("Conversion from {file} failed")
        
