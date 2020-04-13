import os
import sys


def resource_dir():
    """Return the path to the resources directory."""
    root_dir = (getattr(sys, "_MEIPASS", os.path.abspath("."))
                if getattr(sys, "frozen", False) else os.path.abspath("."))
    return os.path.join(root_dir, "resources")


def background_image_file():
    """Return the path to the background image file."""
    return os.path.join(resource_dir(), "wood_texture.jpg")


def icon_file():
    """Return the path to the icon file."""
    return os.path.join(resource_dir(), "icon.ico")
