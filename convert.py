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
      - Uses ImageMagick to extract frames (with zero-padded filenames) from the input file.
      - Compresses each generated image.
      - Assembles the compressed images into an APNG, preserving frame delays.
    """
    input_path = os.path.join(conversion_path, convert)
    output_pattern = os.path.join(conversion_path, "%03d.png")
    
    # Step 1: Extract all frames with ImageMagick
    # -coalesce ensures all frames are fully expanded (important for GIFs/WebPs)
    magick_command = f'magick "{input_path}" -coalesce "{output_pattern}"'
    os.system(magick_command)
    time.sleep(1)
    
    # Step 2: Gather the files output by ImageMagick
    files = []
    for f in sorted(os.listdir(conversion_path)):
        full_path = os.path.join(conversion_path, f)
        if os.path.isfile(full_path) and f.endswith(".png") and "c.PNG" not in f:
            files.append(f)
    
    # Step 3: Compress each frame and collect frame delays as integers
    compressed_files = []
    frame_delays = []
    for f in files:
        compressimages(f)
        compressed_file = os.path.join(conversion_path, f.replace(".png", "c.PNG"))
        compressed_files.append(compressed_file)
        
        # Read the original frame delay in 1/100 sec units
        delay_output = os.popen(f'magick identify -format "%T\n" "{os.path.join(conversion_path, f)}"').read()
        delay_100th = int(delay_output.splitlines()[0]) if delay_output else delay
        # Convert to milliseconds and ensure integer
        frame_delays.append(int(delay_100th * 10))

    # Step 4: Check that we have frames
    if not compressed_files:
        print("No compressed files found. Check your ImageMagick output and file naming.")
        return

    # Step 5: Create the APNG using the compressed frames and integer delays
    output_apng = os.path.join(os.getcwd(), convert + ".png")
    APNG.from_files(compressed_files, delay=delay).save(output_apng)
    print(f"Conversion complete: {output_apng}")

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
    if os.path.isfile(full_path) and f.endswith(".webp"):
        toconvert.append(f)

# Process each file in the list.
for f in toconvert:
    print("FILE BEING CONVERTED: " + f)
    runconversion(f)
    cleanup()
