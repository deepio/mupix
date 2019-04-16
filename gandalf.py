from argparse import ArgumentParser
from os import system

def __parse_args__():
  parser = ArgumentParser(
    prog="python main.py",
    description="""
    This tool helps parse MusicXML files and can list how many discrepancies there are, and what they are.
    Feed it any musicXML file and it will list all of its contents, or compare a musicXML file with a
    "ground truth" musicXML file that you know to be correct. It will list how many mistakes there are, and
    what they are aswell.
    """,
  )
  parser.add_argument(
    "-c",
    "--compare",
    type=str,
    default=False,
    help="Compare two MusicXML files. -c <ground truth file> <file to parse through>"
  )
  parser.add_argument(
    "-m",
    "--mass-compare",
    action="store_true",
    help="Mass compare all the files."
  )
  return parser.parse_args()

def main():
  system("clear")
  user_input = __parse_args__()

  if user_input.mass_compare:
    print("Mass Compare files!")
  elif user_input.compare:
    print("Compare only two files")

if __name__ == "__main__": main()
