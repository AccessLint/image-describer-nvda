import sys
import os
module_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(module_path)

import pyscreeze
import api
import base64
import globalPluginHandler
import os
import requests
import tempfile
import threading
import tones
import ui


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def describe_image(self, file):
        base64_image = self.encode_image(file)
        headers = {
            "Content-Type": "application/json",
            "X-Image-Describer-Client": "NVDA",
        }
        payload = {"srcUrl": f"data:image/jpeg;base64,{base64_image}", "quick": False}
        response = requests.post(
            "https://describe.accesslint.com/api/v2/descriptions",
            headers=headers, json=payload, timeout=15)
        result = response.json()
        content = result["description"]
        ui.message(content)
        os.unlink(file)

    def script_describe_image(self, gesture):
        tones.beep(300, 200)
        ui.message("Getting description...")
        nav = api.getNavigatorObject()
        left, top, width, height = nav.location
        bounding_box = (left, top, width, height)
        image = pyscreeze.screenshot(region=bounding_box)
        file = tempfile.mktemp(suffix=".png")
        image.save(file)
        return threading.Thread(
            target=self.describe_image,
            kwargs={"file": file}).start()

    __gestures = {
        "kb:shift+NVDA+i": "describe_image",
    }
