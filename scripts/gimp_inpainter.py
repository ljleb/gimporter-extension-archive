import os.path
import gradio as gr
import modules.scripts as scripts
import sys

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from modules.shared import opts
base_dir = scripts.basedir()
sys.path.append(base_dir)


config_path = os.path.join(base_dir, 'user-config.cfg')


# setting up the watchdogs
class ImageHandler(FileSystemEventHandler):
    file_path = os.path.join(base_dir, 'gimp_plugins', 'image.png')

    def on_any_event(self, event):
        print('image received!')


class MaskHandler(FileSystemEventHandler):
    file_path = os.path.join(base_dir, 'gimp_plugins', 'mask.png')

    def on_any_event(self, event):
        print('mask received!')


image_handler = ImageHandler()
mask_handler = MaskHandler()
observer = Observer()
observer.schedule(image_handler, ImageHandler.file_path)
observer.schedule(mask_handler, MaskHandler.file_path)
observer.start()


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
