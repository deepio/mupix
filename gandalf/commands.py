import click

from gandalf.application import parse_xml
from gandalf.application import validate_xml
from gandalf.application import Compare


@click.group()
def cli():
  """
  This tool helps parse MusicXML files and can list how many discrepancies there are, and what they are.
  Feed it any musicXML file and it will list all of its contents, or compare a musicXML file with a
  "ground truth" musicXML file that you know to be correct. It will list how many mistakes there are, and
  what they are aswell.
  """


@cli.command("compare", short_help="Compare two MusicXML files.")
@click.argument("true_data")
@click.argument("test_data")
def compare(true_data, test_data):
  """
  Compares two MusicXML files. -c <ground truth file> <file to parse through>
  """
  print(Compare(true_data, test_data))


@cli.command("compare-all", short_help="Mass compare all the files.")
def compare_all():
  """
  """
  print("Mass Compare files!")


@cli.command("read", short_help="Show the parsed musicxml tree of a single file")
@click.argument("file_path", nargs=-1)
def read(file_path):
  """
  """
  for f in file_path:
    print(f"{parse_xml(f)}\n")


@cli.command("validate", short_help="Check if MusicXML file is valid.")
@click.argument("file_path", nargs=-1)
def validate(file_path):
  """
  """
  for f in file_path:
    print(f"{f}: {validate_xml(f)}")
