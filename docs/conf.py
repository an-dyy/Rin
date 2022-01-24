import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Rin"
copyright = "2022, Andy"
author = "Andy"
release = "0.1.0-alpha"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.extlinks",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/latest/", None),
}

rst_prolog = """
.. |cacheable| replace:: This class is `cache-able`.
"""

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_class_signature = "separated"
autodoc_default_options = {"exclude-members": "__init__"}

add_module_names = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

templates_path = ["_templates"]
html_static_path = ["_static"]
html_theme = "furo"

html_theme_options = {
    "dark_css_variables": {
        "color-api-name": "#f0f0f0",
        "color-api-pre-name": "#f0f0f0",
    },
}

pygments_style = "default"
pygments_dark_style = "native"
