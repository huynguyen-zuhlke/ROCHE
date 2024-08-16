from large_image.tilesource import base
from tifffile import TiffFile
import os
from PIL import Image


def to_jpeg(input_path):
    output_path = os.path.splitext(input_path)[0] + ".jpg"
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    bif = TiffFile(input_path)

    print(f"Number of pages = {len(bif.pages)}")


    baseline = None
    for s in bif.series:
        if s.name == "Baseline":
            baseline = s
    

    max_dimension = 65000
    print("baseline: ", baseline)
    if baseline is None:
        print(f"No baseline image.")
        return
    (width, height, depth) = baseline.shape
    if width >= max_dimension or height > max_dimension:
        print("Image dimension too big")
        return

    data = baseline.levels[0].asarray()
    # data =  bif.pages[0].asarray() if baseline is None else baseline.asarray()
    # data = baseline.asarray()

    img = Image.fromarray(data)
    img.save(output_path)
    print(f"Saved to {output_path}\n")



def dump_tiff_info(input_path):
    bif = TiffFile(input_path)

    print("=== Pages ===")
    for page in bif.pages:
        data = page.asarray()
        print(f"Shape = {data.shape}")
    
    print("=== Series ===")
    for s in bif.series:
        print(f"Name = {s.name}")
        print(f"is_pyramidal = {s.is_pyramidal}")
        pages_in_series = s.pages
        print(f"Number of pages = {len(pages_in_series)}")


source_image = "../samples/bif/FBCa01-Ki67.bif" 
# to_jpeg(source_image) 

source_dir = "../samples/bif/"
for file in os.listdir(source_dir):
    if file.endswith(".bif"):
        # print(os.path.join(source_dir, file))
        to_jpeg(os.path.join(source_dir, file))
        
