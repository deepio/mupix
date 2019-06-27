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


def output_filter(ctx, func, *args, **kwargs):
  """
  This is a helper function to filter the output of all commands into notes, rests, etc.
  """

  # If no filtering options are defined, output all information
  if all(value == False for value in ctx.values()):  # noqa
    print(func(*args, **kwargs).ret())
  else:
    # Not Pretty Print with a combination
    if not ctx["p"]:
      if ctx["n"]:
        print(func(*args, **kwargs).ret()[0])
      if ctx["r"]:
        print(func(*args, **kwargs).ret()[1])
      if ctx["t"]:
        print(func(*args, **kwargs).ret()[2])
      if ctx["k"]:
        print(func(*args, **kwargs).ret()[3])
      if ctx["c"]:
        print(func(*args, **kwargs).ret()[4])
    else:
      # Just Pretty Print
      if all(value == False for value in list(ctx.values())[1:]):  # noqa
        print("NOTES:" + json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[0]], indent=2))
        print("RESTS:" + json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[1]], indent=2))
        print("TIMES:" + json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[2]], indent=2))
        print("KEYS :" + json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[3]], indent=2))
        print("CLEFS:" + json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[4]], indent=2))
      else:
        # Pretty Print with a combination
        if ctx["n"]:
          print(json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[0]], indent=2))
        if ctx["r"]:
          print(json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[1]], indent=2))
        if ctx["t"]:
          print(json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[2]], indent=2))
        if ctx["k"]:
          print(json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[3]], indent=2))
        if ctx["c"]:
          print(json.dumps([item.asdict() for item in func(*args, **kwargs).ret()[4]], indent=2))
