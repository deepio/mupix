import re

import mupix


def test_version():
  """
  Make sure the version in the TOML file and in the __init__.py file are the same.
  """
  with open("pyproject.toml") as f:
    pattern = f"(?<=version = \")(.*?)(?=\")"
    assert mupix.__version__ == re.findall(pattern, f.read(), re.DOTALL)[0]
