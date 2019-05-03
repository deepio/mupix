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


