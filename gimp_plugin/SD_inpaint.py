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
    dimensions = get_dimensions_of_layer(image.active_layer)
    mask_region = get_layer_mask(image.active_layer, dimensions)

    # get the image of the layer as a pixel region
    image_copy, layer_region = compute_image_region(image, dimensions)

    # save the images
    if mask_region is not None:
        send_image_data(layer_region, mask_region)
        export_config('inpaint' + '|' + image_path + '|' + mask_path)
    else:
        save_region_as_image(layer_region, 0, 0, image_path)
        export_config('inpaint' + '|' + image_path)

    # delete the copy
    pdb.gimp_image_delete(image_copy)

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def stable_diffusion_img2img(image):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    # get the image of the layer as a pixel region
    dimensions = get_dimensions_of_layer(image.active_layer)
    image_copy, layer_region = compute_image_region(image, dimensions)

    # save the images
    save_region_as_image(layer_region, 0, 0, image_path)
    export_config('img2img' + '|' + image_path)

    # delete the copy
    pdb.gimp_image_delete(image_copy)

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def export_config(content):
    try:
        config_file = open(export_config_file, 'r')
        previous_file_content = config_file.read().split('|')
        config_file.close()
        export_id = int(previous_file_content[0]) + 1
    except (IOError, ValueError):
        export_id = 0
    export_id = export_id % 2
    config_file = open(export_config_file, 'w')
    config_file.write(str(export_id) + '|' + content)
    config_file.close()


def compute_image_region(image, dimensions):
    image_copy = pdb.gimp_image_duplicate(image)
    if image_copy.active_layer.mask is not None:
        pdb.gimp_layer_remove_mask(image_copy.active_layer, 1)
    layer_region = image_copy.active_layer.get_pixel_rgn(0, 0, *dimensions, dirty=False)
    return image_copy, layer_region


def get_dimensions_of_layer(layer):
    w, h, = layer.width, layer.height
    return w, h


def get_layer_mask(layer, dimensions):
    try:
        return layer.mask.get_pixel_rgn(0, 0, *dimensions, dirty=False)
    except AttributeError:
        return None


def send_image_data(image, mask):
    save_region_as_image(image, 0, 0, image_path)
    save_region_as_image(mask, 1, 2, mask_path)


def save_region_as_image(region, image_type, layer_type, path):
    # Create a new image with the same dimensions as the region
    image = gimp.Image(region.w, region.h, image_type)

    # Create a new layer to hold the image data
    layer = gimp.Layer(image, "layer", region.w, region.h, layer_type, 100, 0)
    if region.bpp == 4:
        layer.add_alpha()
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
