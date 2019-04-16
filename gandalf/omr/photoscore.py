import json
import os

from gandalf.base import MusicXML_Parser

class Photoscore(MusicXML_Parser):
  """
  Parser for the Photoscore OMR Software.
  """
  def __init__(self, file_obj):
    super().__init__(file_obj)

def main():
  os.system("clear")

  # Check if parsing works
  test_file = "../../tests/xml/test.xml"
  with open(test_file) as f:
    data = f.read()
  print(Photoscore(data))

if __name__ == "__main__": main()
