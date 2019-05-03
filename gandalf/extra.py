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
