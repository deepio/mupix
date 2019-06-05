import os


def __return_root_path():
  """
  This is a simple function to get the root directory of the repository.

  Returns:
    (string): of the local filepath to this project.
  """
  return "/".join(os.path.abspath(__file__).split("/")[0:-2])


def extract_accidental(note):
  if len(note.name) > 1:
    accidental = note.name[1:]
  else:
    accidental = ""
  return accidental

