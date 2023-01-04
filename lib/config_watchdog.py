from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os.path


class ConfigEventHandler(FileSystemEventHandler):
    def __init__(self, watchdog_path, callback):
        self.config_path = os.path.join(watchdog_path, 'send_to_webui.cfg')
        self.callback = callback
        self.last_receive_id = -1

    def on_modified(self, event):
        if event.src_path != self.config_path:
            return

        with open(event.src_path, 'r') as config_file:
            content = config_file.read().split('|')
            receive_id = int(content[0])
            if self.last_receive_id == receive_id:
                return
            self.last_receive_id = receive_id
            self.callback(*content[1:])


def start_config_watchdog(gimp_plugin_path, callback):
    config_event_handler = ConfigEventHandler(gimp_plugin_path, callback)
    observer = Observer()
    observer.schedule(config_event_handler, gimp_plugin_path)
    observer.start()
    return observer
