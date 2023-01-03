import os.path
import gradio as gr
import modules.scripts as scripts
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from modules.shared import opts
base_dir = scripts.basedir()
sys.path.append(base_dir)


# setting up watchdogs
class PngHandler(FileSystemEventHandler):
    file_path = os.path.join(base_dir, 'gimp_plugins')
    paths_to_check = [
        os.path.join(file_path, 'gimp_export_config.cfg'),
    ]

    def on_modified(self, event):
        if event.src_path not in PngHandler.paths_to_check:
            return

        with open(event.src_path, 'r') as config_file:
            print(config_file.readlines())
        print(event)


png_handler = PngHandler()
observer = Observer()
observer.schedule(png_handler, PngHandler.file_path)
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
