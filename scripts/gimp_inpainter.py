from modules import scripts
import sys
base_dir = scripts.basedir()
sys.path.append(base_dir)

from modules import generation_parameters_copypaste, shared
from lib.config_watchdog import start_config_watchdog
import os.path

from lib.hijacker import scripts_hijacker

import gradio as gr


image_args = {
    'img2img': None,
    'inpaint': None,
    'inpaint_plus_mask': None,
    'img2img_mask': None,
    'inpaint_mask': None,
}


def update_image(tab, image):
    print(f'{tab} demo.load: {image}')
    if image_args[tab] == image:
        return gr.update()

    return image_args[tab]


def update_image_args(tab, image):
    print(f'{tab} image.change: {image}')
    if type(image) is dict:
        image_args[tab] = image['image']
    else:
        image_args[tab] = image


@scripts_hijacker.hijack('create_ui')
def create_ui_hijack(*args, original_function, **kwargs):
    with original_function(*args, **kwargs) as demo:
        tab = 'img2img'
        image = generation_parameters_copypaste.paste_fields[tab]['init_img']
        image.change(fn=update_image_args, inputs=[gr.State(tab), image], outputs=[])
        demo.load(fn=update_image, inputs=[gr.State(tab), image], outputs=image, every=1)

        tab = 'inpaint_plus_mask'
        image_mask = generation_parameters_copypaste.paste_fields['inpaint']['init_img']
        # image_mask.change(fn=update_image_args, inputs=[gr.State(tab), image_mask], outputs=[])
        # demo.load(fn=update_image, inputs=[gr.State(tab), image_mask], outputs=image_mask, every=1)

        tab = 'inpaint'
        image, mask = image_mask.parent.children[2:4]
        image.change(fn=update_image_args, inputs=[gr.State(tab), image], outputs=[])
        demo.load(fn=update_image, inputs=[gr.State(tab), image], outputs=image, every=1)
        tab = 'inpaint_mask'
        image.change(fn=update_image_args, inputs=[gr.State(tab), mask], outputs=[])
        demo.load(fn=update_image, inputs=[gr.State(tab), mask], outputs=mask, every=1)
    demo_queue, demo.queue = demo.queue, lambda *_args, **_kwargs: demo_queue()
    return demo


def set_images_in_viewport(tab, image_path, mask_path=None):
    image_args[tab] = image_path
    image_args[f'{tab}_mask'] = mask_path
    if tab == 'inpaint':
        image_args['inpaint_plus_mask'] = image_path


gimp_plugin_path = os.path.join(base_dir, 'gimp_plugin')
observer = start_config_watchdog(gimp_plugin_path, set_images_in_viewport)


class GimpScript(scripts.Script):
    def title(self):
        return "Gimp-extension"

    def ui(self, is_img2img):
        pass

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def run(self, p, *args):
        pass

    def postprocess(self, p, res, *args):
        pass  # send images back to gimp


print('[gimp-inpaint] done init')
