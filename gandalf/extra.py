import os
import re


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


def handle_backups(file_path):
  """
  Handle Backups

  In MusicXML, one way to write multiple notes on the same beat in a measure is by adding a `<backup>`
  tag. This tag will literally "backup the placement" by a defined duration (also called duration). To avoid this,
  i'm renaming the duration tag and placing the backup with it's associated note prior to parsing.

  Args:
    file_path (string): A string representation of the filename path.

  Returns:
    (string): Corrected contents of the file as a long string.
  """
  with open(file_path) as f:
    data = f.readlines()

  # This assumes the backup tag is always 3 lines long.
  note_back_ups = [index for index, x in enumerate(data) if x == "<backup>\n"]
  for note_back_up in note_back_ups:
    # Shuffle all important lines forward
    data[note_back_up + 2], data[note_back_up - 1], data[note_back_up], data[note_back_up + 1] = data[note_back_up - 1], data[note_back_up], data[note_back_up + 1].replace("duration", "vertical-alignment"), data[note_back_up + 2] # noqa E501

  return "".join(data)


def note_and_measure_offset(path: str, measure_offset: int, note_offset: int):
  """
  Note and Measure Offset Alignment

  Takes the current key, and returns the same key with a note/measure offset combination, this is required
  for looking at measures and notes ahead of the note currently in scope.

  Args:
    path (string): The dictionary key that describes what is at the current element in the list

    measure_offset (int): How many measures to look ahead, could also work for previous measures
                          but this is not tested.

    note_offset (int): How many notes to look ahead, could also work for previous notes but this
                          is not tested.

  Returns:
    (string): Describing the new altered path.
  """
  path_list = path.split(".")
  try:
    current_measure = int(path_list[1].split("_")[-1])
    path = path.replace(f"measure_{current_measure}", f"measure_{current_measure + measure_offset}")

    if "note" in path_list[2]:
      current_note = int(path_list[2].split("_")[-1])
      path = path.replace(f"note_{current_note}", f"note_{current_note + note_offset}")

  except IndexError:
    pass
  return path


def track_moved_notes(path: str) -> str:
  path_list = path.split(".")
  return f"{path_list[0]}.{path_list[1]}.{path_list[2]}"


def track_moved_measures(path: str) -> str:
  path_list = path.split(".")
  return f"{path_list[0]}.{path_list[1]}"


def __return_root_path():
  """
  This is a simple function to get the root directory of the repository.

  Returns:
    (string): of the local filepath to this project.
  """
  return "/".join(os.path.abspath(__file__).split("/")[0:-2])


if __name__ == "__main__":
  os.system("clear")
