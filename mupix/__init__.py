# import re
from .commands import cli # noqa F401

# # Read version from toml file?
# with open("../pyproject.toml") as f:
#   pattern = f"(?<=version = \")(.*?)(?=\")"
#   __version__ = re.findall(pattern, f.read(), re.DOTALL)[0]
__version__ = '0.2.1'
