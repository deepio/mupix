import click

from gandalf.application import Parse
from gandalf.base import BasicDiff


@click.group()
def cli():
  """
  This tool helps parse MusicXML files and can list how many discrepancies there are, and what they are.
  Feed it any musicXML file and it will list all of its contents, or compare a musicXML file with a
  "ground truth" musicXML file that you know to be correct. It will list how many mistakes there are, and
  what they are aswell.
  """


@cli.command("compare", short_help="Compare two MusicXML files.")
@click.argument("correct_data")
@click.argument("test_data")
def compare(correct_data, test_data):
  """
   Compare two MusicXML files. -c <ground truth file> <file to parse through>
  """
  print(BasicDiff(correct_data, test_data))


@cli.command("compare-all", short_help="Mass compare all the files.")
def compare_all():
  """
  """
  print("Mass Compare files!")


@cli.command("read", short_help="Show the parsed musicxml tree of a single file")
@click.argument("filename")
def read(filename):
  """
  """
  print(Parse(filename))


if __name__ == "__main__":
  test_file = "../tests/xml/test.xml"
  print(BasicDiff(test_file, test_file))
