import json

import click

from gandalf.application import parse_xml
from gandalf.application import validate_xml
# from gandalf.application import Compare


def output_filter(ctx, func, *args, **kwargs):
  """
  This is a helper function to filter the output of all commands into notes, rests, etc.
  """

  # If no filtering options are defined, output all information
  if all(value == False for value in ctx.values()):  # noqa
    print(func(*args, **kwargs))
  else:
    if not ctx["p"]:
      if ctx["n"]:
        print(func(*args, **kwargs)[0])
      if ctx["r"]:
        print(func(*args, **kwargs)[1])
      if ctx["t"]:
        print(func(*args, **kwargs)[2])
      if ctx["k"]:
        print(func(*args, **kwargs)[3])
      if ctx["c"]:
        print(func(*args, **kwargs)[4])
    else:
      if ctx["n"]:
        print(json.dumps([item.asdict() for item in func(*args, **kwargs)[0]], indent=2))
      if ctx["r"]:
        print(json.dumps([item.asdict() for item in func(*args, **kwargs)[1]], indent=2))
      if ctx["t"]:
        print(json.dumps([item.asdict() for item in func(*args, **kwargs)[2]], indent=2))
      if ctx["k"]:
        print(json.dumps([item.asdict() for item in func(*args, **kwargs)[3]], indent=2))
      if ctx["c"]:
        print(json.dumps([item.asdict() for item in func(*args, **kwargs)[4]], indent=2))


@click.group()
@click.option("-p/--pretty-print", default=False)
@click.option("-n/--notes", default=False)
@click.option("-r/--rests", default=False)
@click.option("-t/--time-signatures", default=False)
@click.option("-k/--key-signatures", default=False)
@click.option("-c/--clefs", default=False)
@click.pass_context
def cli(ctx, p, n, r, t, k, c):
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


@cli.command("read", short_help="Show the parsed musicxml tree of a single file")
@click.argument("file_path", nargs=-1)
@click.pass_context
def read(ctx, file_path):
  """
  """
  for f in file_path:
    return output_filter(ctx.parent.params, parse_xml, f)


@cli.command("validate", short_help="Check if MusicXML file is valid.")
@click.argument("file_path", nargs=-1)
def validate(file_path):
  """
  """
  for f in file_path:
    print(f"{f}: {validate_xml(f)}")
