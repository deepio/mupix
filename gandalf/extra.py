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

