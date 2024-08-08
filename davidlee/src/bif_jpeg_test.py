from tifffile import TiffFile
from PIL import Image


def to_jpeg(input_path, output_path= "bif-jpeg-outcome.jpg"):
    print(f"Input: {input_path}")

    bif = TiffFile(input_path)

    print(f"Number of pages = {len(bif.pages)}")


    baseline = None
    for s in bif.series:
        if s.name == "Baseline":
            baseline = s
    

    print("baseline: ", baseline)
    data = bif.pages[4].asarray() if baseline is None else baseline.asarray()
    # data = baseline.asarray()

    img = Image.fromarray(data)
    img.save(output_path)



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


# dump_tiff_info("samples/bif/FBCa01-Ki67.bif")
to_jpeg("samples/bif/FBCa01-Ki67.bif") 
