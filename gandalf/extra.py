import json
import os
import re


def __return_root_path() -> str:
  """
  This is a simple function to get the root directory of the repository.

  Returns:
    (string): of the local filepath to this project.
  """
  if os.name == "posix":
    return "/".join(os.path.abspath(__file__).split("/")[0:-2])
  else:
    return "\\".join(os.path.abspath(__file__).split("\\")[0:-2])


def return_char_except(value: int) -> str:
  """
  Because we are already using the "_" to signal a skipped Gandalf Object.
  """
  if value >= 95:
    value += 1
  return chr(value)


def boundary_search(begin, end, string):
  """
  Boundary Search
  This is the regex formula for finding everything between two specific strings.
  e.g. :
        this character =>[ (all of the stuff here, including newlines) ] <= this character
        (?<=[)(.*?)(?=])
  Args:
    begin (string): The character that signals the begins what you want to search for.
    end (string): The character that signals the end of what you are looking for.
    string (string): Multi-line data you wish to search through.
  Returns:
    output (list): A list of all instances of what was searched for.
  """
  pattern = f"(?<={begin})(.*?)(?={end})"
  return re.findall(pattern, string, re.DOTALL)


def output_filter(ctx, func, *args, **kwargs):
  """
  This is a helper function to filter the output of all commands into notes, rests, etc.
  """
  output = func(*args, **kwargs)

  msg = {}
  # If no filtering options are defined, output all information
  if all(value == False for value in ctx.values()) or ctx["p"]:  # noqa
    # turn to json serializable.
    msg["Notes"] = [i.asdict() for i in output.notes]
    msg["Rests"] = [i.asdict() for i in output.rests]
    msg["TimeSignatures"] = [i.asdict() for i in output.timeSignatures]
    msg["KeySignatures"] = [i.asdict() for i in output.keySignatures]
    msg["Clefs"] = [i.asdict() for i in output.clefs]
  else:
    # Not Pretty Print with a combination
    if ctx["n"]:
      msg["Notes"] = [i.asdict() for i in output.notes]
    if ctx["r"]:
      msg["Rests"] = [i.asdict() for i in output.rests]
    if ctx["t"]:
      msg["TimeSignatures"] = [i.asdict() for i in output.timeSignatures]
    if ctx["k"]:
      msg["KeySignatures"] = [i.asdict() for i in output.keySignatures]
    if ctx["c"]:
      msg["Clefs"] = [i.asdict() for i in output.clefs]

  if not ctx["p"]:
    print(msg)
  else:
    print(json.dumps(msg, indent=2))
