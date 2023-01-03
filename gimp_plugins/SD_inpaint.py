#!/usr/bin/env python

from gimpfu import *
import gimpcolor
import os

working_dir = os.path.dirname(os.path.realpath(__file__))

import sys
sys.stderr = open(working_dir + r'\er.txt', 'w')
sys.stdout = open(working_dir + r'\log.txt', 'w')


debug_logs_enabled = True


def stable_diffusion_inpaint(image, output_file=working_dir):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    # get the mask of the layer as a pixel region
    x, y, w, h = get_rect_of_layer(image.active_layer)
    mask_region = get_layer_mask(image.active_layer, 0, 0, w, h)

    # get the image of the layer as a pixel region
    image_copy = pdb.gimp_image_duplicate(image)
    consolidated_image = image_copy.flatten()
    consolidated_region = consolidated_image.get_pixel_rgn(x, y, w, h, dirty=False)

    # save the images
    send_image_data(consolidated_region, mask_region, output_file)

    # delete the copy
    pdb.gimp_image_delete(image_copy)

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def stable_diffusion_img2img(image, output_file=working_dir):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    # code

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def get_rect_of_layer(layer):
    w, h, = layer.width, layer.height
    x, y = layer.offsets
    return x, y, w, h


def get_layer_mask(layer, x, y, w, h):
    try:
        return layer.mask.get_pixel_rgn(x, y, w, h, dirty=False)
    except AttributeError:
        exception_message = 'error: no mask found on selected layer'
        pdb.gimp_message(exception_message)
        raise Exception(exception_message)


def send_image_data(image, mask, output_file):
    save_region_as_image(mask, 1, 2, output_file + r"\mask.png")
    save_region_as_image(image, 0, 0, output_file + r"\image.png")


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
        (PF_IMAGE, "image", "takes current image", None)
    ],
    [],
    stable_diffusion_inpaint, menu="<Image>/Tools/Paint Tools")

register(
    "python-fu-SD-img2img",
    "Send selected layer to stable diffusion webui",
    "Send selected layer to stable diffusion webui",
    "John-William Lebel", "John-William Lebel", "2023",
    "SD img2img",
    "RGB*, GRAY*",  # valid layer color type
    [
        (PF_IMAGE, "image", "takes current image", None)
    ],
    [],
    stable_diffusion_img2img, menu="<Image>/Tools/Paint Tools")

main()
