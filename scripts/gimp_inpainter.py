from modules import scripts, shared, script_callbacks
import sys
base_dir = scripts.basedir()
sys.path.append(base_dir)

from lib.config_watchdog import start_config_watchdog
import os.path
from PIL import Image
import gradio as gr

import lib.websockets_server

ui_images = dict()
image_states = dict()


def on_after_leaf_component(component, **kwargs):
    global ui_images

    if 'elem_id' in kwargs:
        elem_id = kwargs['elem_id']
        if elem_id in {'img2img_image', 'img2maskimg', 'img_inpaint_base', 'img_inpaint_mask'}:
            ui_images[elem_id] = component
            image_states[elem_id] = None
            register_load_callback(elem_id, component)


script_callbacks.on_after_component(on_after_leaf_component)


def register_load_callback(elem_id, ui_image):
    gr.Button(visible=False, elem_id=f'gimp_refresh_{elem_id}').click(
        fn=get_image_update(elem_id, ui_image),
        inputs=[],
        outputs=[ui_image]
    )
    ui_image.change(
        fn=set_image_state(elem_id, ui_image),
        inputs=[ui_image],
        outputs=[]
    )


def get_image_update(elem_id, ui_image):
    def inner():
        return gr.Image.update(image_states[elem_id])

    def inner_img2maskimg():
        res = inner()
        ui_image.tool = None
        res['value'] = res['value']['image']
        return res

    if elem_id == 'img2maskimg':
        return inner_img2maskimg

    return inner


def set_image_state(elem_id, ui_image):
    def inner(pil_image):
        if pil_image is not None:
            image_states[elem_id] = pil_image

    def inner_img2maskimg(pil_image):
        inner(pil_image)
        if ui_image.tool is None:
            ui_image.tool = shared.cmd_opts.gradio_inpaint_tool

    if elem_id == 'img2maskimg':
        return inner_img2maskimg

    return inner


def set_images_in_viewport(tab, image_path, mask_path=None):
    to_enqueue = []

    if tab == 'inpaint' and mask_path is None:
        image_states['img2maskimg'] = {'image': Image.open(image_path)}
        to_enqueue.append('img2maskimg')

    elif tab == 'inpaint' and mask_path is not None:
        image_states['img_inpaint_base'] = Image.open(image_path)
        image_states['img_inpaint_mask'] = Image.open(mask_path)
        to_enqueue.extend(['img_inpaint_base', 'img_inpaint_mask'])

    elif tab == 'img2img':
        image_states['img2img_image'] = Image.open(image_path)
        to_enqueue.append('img2img_image')

    if to_enqueue:
        lib.websockets_server.elem_ids_queue.put(to_enqueue)


class GimpScript(scripts.Script):
    def title(self):
        return "Gimp-extension"

    def show(self, is_img2img):
        return False


gimp_plugin_path = os.path.join(base_dir, 'gimp_plugin')
watchdog_thread = start_config_watchdog(gimp_plugin_path, set_images_in_viewport)
lib.websockets_server.start_server()
print('[gimporter] done init')
