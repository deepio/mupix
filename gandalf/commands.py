import click

from gandalf.application import xml_validator
from gandalf.application import xml_type_finder
from gandalf.application import Compare
from gandalf.application import ParseMusic21
from gandalf.extra import output_filter


@click.group()
@click.option("-p", "--pretty-print", is_flag=True, help="Print the output with and automatic indent.")
@click.option("-n", "--notes", is_flag=True, help="Show note objects")
@click.option("-r", "--rests", is_flag=True, help="Show rest objects")
@click.option("-t", "--time-signatures", is_flag=True, help="Show the time signatures")
@click.option("-k", "--key-signatures", is_flag=True, help="Show the key signatures")
@click.option("-c", "--clefs", is_flag=True, help="Show the clefs")
@click.option("-z", "--error-description", is_flag=True, help="What element matched with what")
@click.option("-T", "--total-only", is_flag=True, help="Show the total of each category")
@click.pass_context
def cli(ctx, pretty_print, notes, rests, time_signatures, key_signatures, clefs, error_description, total_only):
  """
  This tool helps parse MusicXML files and can list how many discrepancies there are, and what type they are.

  Feed it any musicXML file and it will list all of its contents, or compare a musicXML file with a "ground truth" musicXML file that you know to be correct. It will list how many mistakes there are, and what they are as well.
  """


@cli.command("compare", short_help="Compare two or more MusicXML files. You may also select the type of algorithm you want to use by specifying --sort=anw")  # noqa
@click.option("--sort", default="basic", help="Note alignment algorithm to use when aligning Gandalf objects.")
@click.argument("true_data")
@click.argument("test_data", nargs=-1)
@click.pass_context
def compare(ctx, sort, true_data, test_data):
  """
  Compares two MusicXML files.

  OPTIONS:

    --sort=basic    Uses a dumb alignment that does not look forward or backward in time.                                                

    --sort=anw      Uses a simplistic version of the Affine-Needleman-Wunsch based on a single element from the Gandalf Objects.

    --sort=anw-1    Uses the first version of the Affine-Needleman-Wunsch algorithm, based on multiple elements from each of the Gandalf Objects.

  TRUE_DATA:

    <file>                        A single file

  [TEST_DATA]:

    <file>                        A single file

    <file A> <file B> <file C>    A list of files delineated with a space
  """
  for f in test_data:
    output_filter(
      ctx.parent.params,
      Compare,
      true_filepath=true_data,
      test_filepath=f,
      sorting_algorithm=sort,
    )


@cli.command("read", short_help="Show the parsed Symbolic file as a list of elements")
@click.argument("file_path", nargs=-1)
@click.pass_context
def read(ctx, file_path):
  """
  Prints to screen the parsed symbolic file as a list of elements.

  [FILE_PATH]:

    <file>                        A single file

    <file A> <file B> <file C>    A list of files delineated with a space
  """
  for f in file_path:
    output_filter(ctx.parent.params, ParseMusic21.from_filepath, f)


@cli.command("validate", short_help="Check if MusicXML file is valid.")
@click.argument("file_path", nargs=-1)
def validate(file_path):
  """
  Checks if the given file is a valid musicXML file.

  [FILE_PATH]:

    <file>                        A single file

    <file A> <file B> <file C>    A list of files delineated with a space
  """
  for f in file_path:
    print(f"{f}: {xml_validator(f)}")


@cli.command("xml_type", short_help="Check the format of the musicxml.")
@click.argument("file_path", nargs=-1)
def xml_finder(file_path):
  """
  Checks if the given musicXML file is written in a part-wise or time-wise fashion.

  [FILE_PATH]:

    <file>                        A single file

    <file A> <file B> <file C>    A list of files delineated with a space
  """
  for f in file_path:
    print(f"{f}: {xml_type_finder(f)}")
