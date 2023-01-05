from modules import scripts, shared, script_callbacks
import sys
base_dir = scripts.basedir()
sys.path.append(base_dir)

from lib.config_watchdog import start_config_watchdog
import os.path
from PIL import Image
import gradio as gr


class StateChange:
    def __init__(self, new, old):
        self.new = new
        self.old = old


ui_images = dict()
image_states = dict()


def on_after_leaf_component(component, **kwargs):
    global ui_images

    if 'elem_id' in kwargs:
        elem_id = kwargs['elem_id']
        if elem_id in {'img2img_image', 'img2maskimg', 'img_inpaint_base', 'img_inpaint_mask'}:
            ui_images[elem_id] = component
            image_states[elem_id] = StateChange(None, None)
            register_load_callback(elem_id, component)


script_callbacks.on_after_component(on_after_leaf_component)


def register_load_callback(elem_id, ui_image):
    dummy_state = gr.State()
    gr.Button(visible=False, elem_id=f'gimp_refresh_{elem_id}').click(
        fn=get_image_update(elem_id, ui_image, dummy_state),
        inputs=[],
        outputs=[ui_image, dummy_state]
    )
    ui_image.change(
        fn=set_image_state(elem_id, ui_image),
        inputs=[ui_image],
        outputs=[]
    )


def get_image_update(elem_id, ui_image, dummy_state):
    def inner():
        state = image_states[elem_id]
        if state.old != state.new:
            state.old = state.new
            return {ui_image: gr.Image.update(state.new)}

        return {dummy_state: gr.update(value=None)}

    def inner_img2maskimg():
        res = inner()
        if ui_image in res:
            ui_image.tool = None
            res[ui_image]['value'] = res[ui_image]['value']['image']

        return res

    if elem_id == 'img2maskimg':
        return inner_img2maskimg

    return inner


def set_image_state(elem_id, ui_image):
    def inner(pil_image):
        if pil_image is not None:
            state = image_states[elem_id]
            state.old, state.new = pil_image, pil_image

    def inner_img2maskimg(pil_image):
        inner(pil_image)
        if ui_image.tool is None:
            ui_image.tool = shared.cmd_opts.gradio_inpaint_tool

    if elem_id == 'img2maskimg':
        return inner_img2maskimg

    return inner


def set_images_in_viewport(tab, image_path, mask_path=None):
    if tab == 'inpaint' and mask_path is None:
        image_states['img2maskimg'].new = {'image': Image.open(image_path)}
    elif tab == 'inpaint' and mask_path is not None:
        image_states['img_inpaint_base'].new = Image.open(image_path)
        image_states['img_inpaint_mask'].new = Image.open(mask_path)
    elif tab == 'img2img':
        image_states['img2img_image'].new = Image.open(image_path)


gimp_plugin_path = os.path.join(base_dir, 'gimp_plugin')
observer = start_config_watchdog(gimp_plugin_path, set_images_in_viewport)


class GimpScript(scripts.Script):
    def title(self):
        return "Gimp-extension"

    def show(self, is_img2img):
        return False


print('[gimp-inpaint] done init')
