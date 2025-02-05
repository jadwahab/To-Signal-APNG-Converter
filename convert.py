import os
import time
from apng import APNG
from PIL import Image

# Set up the conversion folder using the present working directory (pwd)
conversion_path = os.path.join(os.getcwd(), "conversion")

# Settings
jpegquality = 5
fps = "5"
delay = 10

def export():
    """
    Opens an APNG file (result.png in the pwd) and exports each frame
    as a PNG with a zero-padded filename (e.g. 000.png, 001.png, etc.).
    """
    result_path = os.path.join(os.getcwd(), "result.png")
    im = APNG.open(result_path)
    for i, (png, control) in enumerate(im.frames):
        filename = "{:03d}.png".format(i)
        png.save(os.path.join(os.getcwd(), filename))

def compressimages(image_file):
    """
    Opens an image from the conversion folder, resizes it,
    and saves a compressed version.
    The output filename is the input’s basename with "c.PNG" appended.
    For example, "000.png" becomes "000c.PNG".
    """
    filepath = os.path.join(conversion_path, image_file)
    maxwidth = 75
    image = Image.open(filepath)
    width, height = image.size
    aspectratio = width / height
    newheight = maxwidth / aspectratio
    image = image.resize((maxwidth, round(newheight)))
    
    # Remove the original extension and add "c.PNG"
    base, _ = os.path.splitext(image_file)
    filename = base + "c.PNG"
    image.save(os.path.join(conversion_path, filename), optimize=True)

def runconversion(convert):
    """
    Converts a given file from the conversion folder:
      - Uses ffmpeg to extract frames (with zero-padded filenames) from the input file.
      - Compresses each generated image.
      - Assembles the compressed images into an APNG.
    """
    input_path = os.path.join(conversion_path, convert)
    # ffmpeg output: filenames like "000.png", "001.png", etc.
    output_pattern = os.path.join(conversion_path, "%03d.png")
    ffmpeg_command = f'ffmpeg -i "{input_path}" -vf fps={fps} -compression_level 100 "{output_pattern}"'
    os.system(ffmpeg_command)
    time.sleep(1)
    
    # Gather the files output by ffmpeg.
    # We only want files that end in ".png" but not the ones that are already compressed.
    files = []
    for f in os.listdir(conversion_path):
        full_path = os.path.join(conversion_path, f)
        if os.path.isfile(full_path) and f.endswith(".png") and "c.PNG" not in f:
            files.append(f)
    
    # Compress each of the extracted PNGs.
    for f in files:
        compressimages(f)
    
    # Gather the compressed files (which now have names like "000c.PNG")
    compressedfiles = []
    for f in os.listdir(conversion_path):
        full_path = os.path.join(conversion_path, f)
        if os.path.isfile(full_path) and f.endswith("c.PNG"):
            compressedfiles.append(full_path)
    
    # If no compressed images were found, warn and exit the function.
    if not compressedfiles:
        print("No compressed files found. Check your ffmpeg output and file naming.")
        return

    # Create the final APNG file. The output filename is based on the input file.
    output_apng = os.path.join(os.getcwd(), convert + ".png")
    APNG.from_files(compressedfiles, delay=delay).save(output_apng)

def cleanup():
    """
    Deletes any PNG files (both .png and .PNG) in the conversion folder.
    """
    for f in os.listdir(conversion_path):
        full_path = os.path.join(conversion_path, f)
        if os.path.isfile(full_path) and (f.endswith(".png") or f.endswith(".PNG")):
            os.remove(full_path)
    time.sleep(0.1)

# First, clean up the conversion folder.
cleanup()

# Build a list of files to convert (e.g. any .webm files in the conversion folder)
toconvert = []
for f in os.listdir(conversion_path):
    full_path = os.path.join(conversion_path, f)
    if os.path.isfile(full_path) and f.endswith(".webm"):
        toconvert.append(f)

# Process each file in the list.
for f in toconvert:
    print("FILE BEING CONVERTED: " + f)
    runconversion(f)
    cleanup()
