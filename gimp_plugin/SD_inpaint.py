#!/usr/bin/env python
from gimpfu import *
import os
import sys
import socket

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.stderr = open(os.path.join(working_dir, 'err.txt'), 'w')
sys.stdout = open(os.path.join(working_dir, 'log.txt'), 'w')

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# webui address
server_address = ('localhost', 7861)


debug_logs_enabled = True


def stable_diffusion_inpaint(image):
    if debug_logs_enabled:
        pdb.gimp_message('script is running')

    # get the mask of the layer as a pixel region
    dimensions = get_dimensions_of_layer(image.active_layer)
    mask_region = get_layer_mask(image.active_layer, dimensions)

    # get the image of the layer as a pixel region
    image_copy, layer_region = compute_image_region(image, dimensions)

    # send images to the webui
    image_packet = region_to_bytearray_packets(layer_region)
    if mask_region is not None:
        mask_packet = region_to_bytearray_packets(mask_region)
        send_to_webui('inpain2' + image_packet + mask_packet)
    else:
        send_to_webui('inpaint' + image_packet)

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

    # send the image to the webui
    image_packet = region_to_bytearray_packets(layer_region)
    send_to_webui('img2img' + image_packet)

    # delete the copy
    pdb.gimp_image_delete(image_copy)

    if debug_logs_enabled:
        pdb.gimp_message('script finished')


def region_to_bytearray_packets(region):
    image_size = region.w * region.h * region.bpp
    flat_image_data = bytearray(image_size)
    flat_image_data[:] = region[:, :]
    width_bytes = int_to_bytearray(region.w, 4, 'big')
    height_bytes = int_to_bytearray(region.h, 4, 'big')
    bpp_bytes = int_to_bytearray(region.bpp, 4, 'big')
    image_size_bytes = int_to_bytearray(image_size, 4, 'big')
    return str(width_bytes) + str(height_bytes) + str(bpp_bytes) + str(image_size_bytes) + str(flat_image_data)


def send_to_webui(data):
    connect_to_webui()

    # Prepare the packet
    amount_to_send = len(data)
    amount_to_send_bytes = int_to_bytearray(amount_to_send, 4, 'big')

    # Send the data
    sock.sendall(amount_to_send_bytes)
    sock.sendall(data)


def connect_to_webui():
    sock.connect(server_address)


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


def int_to_bytearray(x, amount, indian_type='big'):
    buff = []
    if indian_type == 'little':
        for i in range(amount):
            buff.append((x & (255 << (i * 8))) >> (i * 8))
    elif indian_type == 'big':
        for i in range(amount - 1, -1, -1):
            buff.append((x & (255 << (i * 8))) >> (i * 8))
    return bytearray(buff)


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
