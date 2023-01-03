#!/usr/bin/env python

from gimpfu import *
import gimpcolor
import os

import sys
sys.stderr = open(r'C:\Users\Plads\AppData\Roaming\GIMP\2.10\plug-ins\er.txt', 'w')
sys.stdout = open(r'C:\Users\Plads\AppData\Roaming\GIMP\2.10\plug-ins\log.txt', 'w')


debug_logs_enabled = True


def stable_diffusion_script(image, output_file=r""):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    w, h, = image.active_layer.width, image.active_layer.height
    x, y = image.active_layer.offsets

    try:
        mask_region = image.active_layer.mask.get_pixel_rgn(0, 0, w, h, dirty=False)
    except AttributeError:
        exception_message = 'error: no mask found on selected layer'
        pdb.gimp_message(exception_message)
        raise Exception(exception_message)
    image_copy = pdb.gimp_image_duplicate(image)
    consolidated = image_copy.flatten()
    consolidated_region = consolidated.get_pixel_rgn(x, y, w, h, dirty=False)

    send_image_data(consolidated_region, mask_region, output_file)

    pdb.gimp_image_delete(image_copy)
    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def send_image_data(image, mask, output_file):
    save_region_as_image(image, 0, 0, output_file + "\\image.png")
    save_region_as_image(mask, 1, 2, output_file + "\\mask.png")


def save_region_as_image(region, image_type, layer_type, path):
    # Create a new image with the same dimensions as the region
    image = gimp.Image(region.w, region.h, image_type)

    # Create a new layer to hold the image data
    layer = gimp.Layer(image, "layer", region.w, region.h, layer_type, 100, 0)
    image.add_layer(layer)

    # Copy the data from the region into the layer
    layer_region = layer.get_pixel_rgn(0, 0, region.w, region.h, True, False)
    layer_region[:, :] = region[:, :]

    # Save the image to the specified file path
    pdb.gimp_file_save(image, layer, path, path)

    # Clean up
    image.remove_layer(layer)
    gimp.delete(image)


register(
    "python-fu-SD-inpaint",
    "Send selected layer and mask to stable diffusion webui",
    "Send selected layer and mask to stable diffusion webui",
    "John-William Lebel", "John-William Lebel", "2023",
    "SD inpaint",
    "RGB*, GRAY*",  # valid layer color type
    [
        (PF_IMAGE, "image", "takes current image", None),
        (PF_DIRNAME, "output", "Output folder", '')
    ],
    [],
    stable_diffusion_script, menu="<Image>/Tools/Paint Tools")

main()
