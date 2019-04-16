import click

@click.group()
def cli():
  """
  This tool helps parse MusicXML files and can list how many discrepancies there are, and what they are.
  Feed it any musicXML file and it will list all of its contents, or compare a musicXML file with a
  "ground truth" musicXML file that you know to be correct. It will list how many mistakes there are, and
  what they are aswell.
  """

@cli.command("compare", short_help="Compare two MusicXML files.")
def compare():
  """
   Compare two MusicXML files. -c <ground truth file> <file to parse through>
  """
  print("Compare only two files")

@cli.command("compare-all", short_help="Mass compare all the files.")
def compare_all():
  """
  """
  print("Mass Compare files!")
