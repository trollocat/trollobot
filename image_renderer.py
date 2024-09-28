from PIL import Image


def create_beatmap_image(image_paths):
    images = [Image.open(img) for img in image_paths]

    # widths, heights = zip(*(i.size for i in images)) # useful but not used

    # Total width should be 1984px but discord crop makes 2016px prettier, this means a horizontal margin of 16px
    total_width = 2016
    max_height = 124

    map_image = Image.new('RGBA', (total_width, max_height))

    x_offset = 16
    for img in images:
        map_image.paste(img, (x_offset, 0), img)
        x_offset += img.size[0]

    return map_image
