import os
import time
from apng import APNG
from PIL import Image
from os import listdir
from os.path import isfile, join

path = os.getcwd() + "\conversion"
jpegquality = 5
fps="5"
delay=10
toconvert = []
files = []
compressedfiles = []
delete = []

def fill(files, ends, addpath):
    for f in listdir(path):
        if isfile:
            if f.endswith(ends):
                files += [addpath + f]


def export():
    im = APNG.open("result.png")
    for i, (png, control) in enumerate(im.frames):
        png.save("{i}.png".format(i=i))

def compressimages(image_file):
    # accessing the image file
    filepath = os.path.join(os.getcwd(), "conversion/", image_file)
    # maximum pixel size
    maxwidth = 75
    # opening the file
    image = Image.open(filepath)
    # Calculating the width and height of the original photo
    width, height = image.size
    # calculating the aspect ratio of the image
    aspectratio = width / height
 
    # Calculating the new height of the compressed image
    newheight = maxwidth / aspectratio
 
    # Resizing the original image
    image = image.resize((maxwidth, round(newheight)))
 
    # Saving the image
    filename = image_file+"c.PNG"
    image.save(('conversion/' + filename), optimize=True)
    return


def runconversion(convert):
    os.system("ffmpeg -i conversion/"+convert+" -vf fps="+fps+" -compression_level 100 conversion/%02df.png")

    time.sleep(1)

    fill(files, "f.png", "")

    for f in files:
        compressimages(f)

    fill(compressedfiles, "c.PNG", "conversion/")

    for i in compressedfiles:
        i = "conversion/"+i
    APNG.from_files(compressedfiles, delay=delay).save((convert+".png"))

def cleanup():
    delete = []
    fill(delete, ".png", "")
    fill(delete, ".PNG", "")
    for f in delete:
        whatdo=path+"/"+f
        os.remove(whatdo)
    time.sleep(0.1)

cleanup()
fill(toconvert, ".webm", "")
for f in toconvert:
    files = []
    compressedfiles = []
    print("FILE BEING CONVERTED"+f)
    runconversion(f)
    cleanup()
