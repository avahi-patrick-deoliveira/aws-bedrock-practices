"""Helpers to build draw.io architecture diagrams with native AWS4 stencils and render them to PNG.

Build: drawpyo writes diagrams/<name>.drawio.
Render: the draw.io viewer is opened with headless Microsoft Edge (from WSL) and cropped with
Pillow, so Docker is not needed. Rendering needs internet access (viewer.diagrams.net).
"""
import base64
import os
import shutil
import subprocess
import urllib.parse
import zlib

import drawpyo
from drawpyo.diagram import Edge, Object

OUTPUT_DIR = "diagrams"
EDGE_EXE = "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
TEMP_PNG = "/mnt/c/Users/Public/diagram_render.png"

ICON = ("sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor={fill};"
        "strokeColor=none;dashed={dashed};verticalLabelPosition=bottom;verticalAlign=top;"
        "align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;pointerEvents=1;"
        "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{name};")
LABEL = ("text;html=1;align=center;verticalAlign=top;whiteSpace=wrap;fontSize=11;"
         "fontColor=#232F3E;strokeColor=none;fillColor=none;")
NOTE = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;"
        "fontSize=10;fontColor=#7F6000;align=center;")
SCRIPT = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#666666;"
          "fontSize=11;fontColor=#333333;align=center;")
GROUP = ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.{icon};strokeColor={color};fillColor=none;"
         "verticalAlign=top;align=left;spacingLeft=30;fontColor={color};dashed={dashed};html=1;fontSize=12;")
LOCAL_GROUP = ("rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#7D8998;dashed=1;"
               "verticalAlign=top;align=left;spacingLeft=10;fontColor=#232F3E;fontSize=12;")

# AWS4 category colors
COMPUTE, STORAGE, AI, SECURITY, NEUTRAL = "#ED7100", "#7AA116", "#01A88D", "#DD344C", "#232F3E"


class Diagram:
    def __init__(self, name):
        self.name = name
        self.file = drawpyo.File()
        self.file.file_name = f"{name}.drawio"
        self.file.file_path = OUTPUT_DIR
        self.page = drawpyo.Page(file=self.file)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def box(self, value, x, y, w, h, style):
        obj = Object(page=self.page, value=value)
        obj.position = (x, y)
        obj.geometry.width = w
        obj.geometry.height = h
        obj.apply_style_string(style)
        return obj

    def local_group(self, title, x, y, w, h):
        return self.box(title, x, y, w, h, LOCAL_GROUP)

    def cloud_group(self, title, x, y, w, h):
        return self.box(title, x, y, w, h,
                        GROUP.format(icon="group_aws_cloud_alt", color="#232F3E", dashed=0))

    def region_group(self, title, x, y, w, h):
        return self.box(title, x, y, w, h,
                        GROUP.format(icon="group_region", color="#147EBA", dashed=1))

    def script(self, value, x, y, w=240, h=44):
        return self.box(value, x, y, w, h, SCRIPT)

    def note(self, value, x, y, w=240, h=44):
        return self.box(value, x, y, w, h, NOTE)

    def icon(self, label, x, y, name, fill, dashed=0, side="below"):
        """AWS icon (60x60) with its label in a separate text box.

        side: "below", "right" (next to the icon) or "upright" (above and to the right).
        """
        obj = self.box("", x, y, 60, 60, ICON.format(name=name, fill=fill, dashed=dashed))
        if side == "below":
            self.box(label, x + 30 - 100, y + 64, 200, 60, LABEL)
        elif side == "right":
            self.box(label, x + 68, y + 8, 250, 44, LABEL + "align=left;")
        else:
            self.box(label, x + 68, y - 46, 250, 40, LABEL + "align=left;")
        return obj

    def edge(self, source, target, label="", dashed=False, both=False):
        e = Edge(page=self.page, source=source, target=target, label=label)
        e.waypoints = "orthogonal"
        e.endArrow = "block"
        e.startArrow = "block" if both else "none"
        e.strokeColor = "#545B64"
        if dashed:
            e.pattern = "dashed_small"
        return e

    def save(self, window="1500,760"):
        self.file.write()
        render(f"{OUTPUT_DIR}/{self.name}.drawio", f"{OUTPUT_DIR}/{self.name}.png", window)


def render(source, output, window):
    from PIL import Image, ImageChops

    xml = open(source).read()
    packed = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = packed.compress(urllib.parse.quote(xml, safe="").encode()) + packed.flush()
    url = ("https://viewer.diagrams.net/?lightbox=0&nav=0&toolbar=0&border=20#R"
           + urllib.parse.quote(base64.b64encode(data).decode(), safe=""))

    if os.path.exists(TEMP_PNG):
        os.remove(TEMP_PNG)
    windows_path = subprocess.check_output(["wslpath", "-w", TEMP_PNG]).decode().strip()
    subprocess.run([EDGE_EXE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={window}", "--virtual-time-budget=20000",
                    f"--screenshot={windows_path}", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    shutil.move(TEMP_PNG, output)

    image = Image.open(output).convert("RGB")
    box = ImageChops.difference(image, Image.new("RGB", image.size, (255, 255, 255))).getbbox()
    if box:
        pad = 20
        image.crop((max(box[0] - pad, 0), max(box[1] - pad, 0),
                    min(box[2] + pad, image.width), min(box[3] + pad, image.height))).save(output)
    print("Saved", output)
