import json
import os


def __return_root_path():
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


def output_filter(ctx, func, *args, **kwargs):
  """
  This is a helper function to filter the output of all commands into notes, rests, etc.
  """
  output = func(*args, **kwargs)

  # If no filtering options are defined, output all information
  if all(value == False for value in ctx.values()):  # noqa
    print(output.ret())
  else:
    # Not Pretty Print with a combination
    if not ctx["p"]:
      if ctx["n"]:
        print(output.notes)
      if ctx["r"]:
        print(output.rests)
      if ctx["t"]:
        print(output.timeSignatures)
      if ctx["k"]:
        print(output.keySignatures)
      if ctx["c"]:
        print(output.clefs)
    else:
      # Just Pretty Print
      if all(value == False for value in list(ctx.values())[1:]):  # noqa
        print("NOTES:" + json.dumps([item.asdict() for item in output.notes], indent=2))
        print("RESTS:" + json.dumps([item.asdict() for item in output.rests], indent=2))
        print("TIMES:" + json.dumps([item.asdict() for item in output.timeSignatures], indent=2))
        print("KEYS :" + json.dumps([item.asdict() for item in output.keySignatures], indent=2))
        print("CLEFS:" + json.dumps([item.asdict() for item in output.clefs], indent=2))

      else:
        # Pretty Print with a combination
        if ctx["n"]:
          print("NOTES:" + json.dumps([item.asdict() for item in output.notes], indent=2))
        if ctx["r"]:
          print("RESTS:" + json.dumps([item.asdict() for item in output.rests], indent=2))
        if ctx["t"]:
          print("TIMES:" + json.dumps([item.asdict() for item in output.timeSignatures], indent=2))
        if ctx["k"]:
          print("KEYS :" + json.dumps([item.asdict() for item in output.keySignatures], indent=2))
        if ctx["c"]:
          print("CLEFS:" + json.dumps([item.asdict() for item in output.clefs], indent=2))
