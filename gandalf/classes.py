from collections import defaultdict
from os import system

class Parser:
  def __init__(self, file_object):
    self.output = defaultdict()
    self.file_object = file_object

  def parse(self):
    return "Parsing..."

def main():
  system("clear")
  print("Hello")

if __name__ == "__main__": main()
