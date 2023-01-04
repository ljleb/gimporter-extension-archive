import modules.scripts as scripts
import sys
base_dir = scripts.basedir()
sys.path.append(base_dir)

from modules import generation_parameters_copypaste
from lib.config_watchdog import start_config_watchdog
import os.path

import gradio as gr


def set_images_in_viewport(tab, image_path, mask_path=None):
    image = generation_parameters_copypaste.paste_fields[tab]['init_img']
    image.value = image_path
    return


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
