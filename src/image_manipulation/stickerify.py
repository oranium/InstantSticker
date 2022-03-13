from PIL import Image
import requests
import machine_learning


def sticker_from_rectangle(coordinates, url):
    # max size for stickers
    max_size = (512, 512)
    try:
        # url for picture on telegram server
        img = Image.open(requests.get(url, stream=True).raw)
    except Exception:
        img = Image.open("random.jpg")
    if coordinates:
        left = coordinates["left"]-150
        top = coordinates["top"] - 150
        right = coordinates["left"] + coordinates["width"] + 100
        bottom = coordinates["top"] + coordinates["height"] + 100
    else:
        left = 0
        top = 0
        right = img.width
        bottom = img.height
    print(left,top,right,bottom)
    crop = None
    # crop ACS face coordinates
    try:
        crop = img.crop((left, top, right, bottom))
    except Exception:
            left = coordinates["left"]
            top = coordinates["top"]
            right = coordinates["left"] + coordinates["width"]
            bottom = coordinates["top"] + coordinates["height"]
            crop = img.crop((left, top, right, bottom))
    # resize to sticker proportions if necessary (it generally is necessary)
    width, height = crop.size
    if height > width:
        factor = 1 if height==0 else (512/float(height))
    else:
        factor = 1 if width==0 else (512/float(width))
    
    crop = crop.resize((int(factor*width), 512)) if height > width else crop.resize((512, int(factor*height)))    
    crop.save("sticker.png", "PNG")
    machine_learning.run_visualization("sticker.png")
    create_sticker()
    return "sticker.png"

def create_sticker():
    or_img = Image.open("sticker.png")
    or_img = or_img.convert(mode="RGBA")
    mask_img = Image.open("cm.png")
    mask_img = mask_img.convert(mode="RGBA")
    mask_img = mask_img.resize((or_img.width, or_img.height))
    transparent_vals = pixels_to_access(mask_img, or_img)
    or_img.putdata(transparent_vals)
    # need emoji info --> dynamic image name
    or_img.save("sticker.png", "PNG")
    return "sticker.png"

def scale(image, factor):
    pass

def pixels_to_access(mask,or_img):
    data = mask.getdata()
    transparent = []
    i=0
    for item in data:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            transparent.append((0,0,0,0))
        else:
            transparent.append(or_img.getdata()[i])
        i+=1
    return transparent
