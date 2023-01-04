#!/usr/bin/env python

from gimpfu import *
import os

working_dir = os.path.dirname(os.path.realpath(__file__))
image_path = os.path.join(working_dir, 'image.png')
mask_path = os.path.join(working_dir, 'mask.png')
export_config_file = os.path.join(working_dir, 'send_to_webui.cfg')

import sys
sys.stderr = open(os.path.join(working_dir, 'err.txt'), 'w')
sys.stdout = open(os.path.join(working_dir, 'log.txt'), 'w')


debug_logs_enabled = True


def stable_diffusion_inpaint(image):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    # get the mask of the layer as a pixel region
    rect = get_rect_of_layer(image.active_layer)
    mask_region = get_layer_mask(image.active_layer, rect[2:])

    # get the image of the layer as a pixel region
    image_copy, consolidated_region = compute_image_region(image, rect, is_inpaint=True)

    # save the images
    send_image_data(consolidated_region, mask_region)
    export_config('inpaint' + '|' + image_path + '|' + mask_path)

    # delete the copy
    pdb.gimp_image_delete(image_copy)

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def stable_diffusion_img2img(image):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    # get the image of the layer as a pixel region
    rect = get_rect_of_layer(image.active_layer)
    image_copy, consolidated_region = compute_image_region(image, rect)

    # save the images
    save_region_as_image(consolidated_region, 0, 0, image_path)
    export_config('img2img' + '|' + image_path)

    # delete the copy
    pdb.gimp_image_delete(image_copy)

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def export_config(content):
    config_file = open(export_config_file, 'w')
    config_file.write(content)
    config_file.close()


def compute_image_region(image, rect, is_inpaint=False):
    image_copy = pdb.gimp_image_duplicate(image)
    if is_inpaint:
        pdb.gimp_layer_remove_mask(image_copy.active_layer, 1)
    consolidated_image = image_copy.flatten()
    consolidated_region = consolidated_image.get_pixel_rgn(*rect, dirty=False)
    return image_copy, consolidated_region


def get_rect_of_layer(layer):
    w, h, = layer.width, layer.height
    x, y = layer.offsets
    return x, y, w, h


def get_layer_mask(layer, dimensions):
    try:
        return layer.mask.get_pixel_rgn(0, 0, *dimensions, dirty=False)
    except AttributeError:
        exception_message = 'error: no mask found on selected layer'
        pdb.gimp_message(exception_message)
        raise Exception(exception_message)


def send_image_data(image, mask):
    save_region_as_image(image, 0, 0, image_path)
    save_region_as_image(mask, 1, 2, mask_path)


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
