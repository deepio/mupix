from gandalf.exceptions import FileIncompatible
from gandalf.engraver.sibelius import Sibelius
from gandalf.engraver.finale import Finale
from gandalf.engraver.guitarpro import Guitarpro
from gandalf.omr.audiveris import Audiveris
from gandalf.omr.photoscore import Photoscore
from gandalf.omr.scoremaker import Scoremaker
from gandalf.omr.smartscore import Smartscore
from gandalf.extra import boundary_search
from gandalf.extra import handle_backups


def Parse(file_obj):
  """
  The Parse function will select the appropriate parser for the given musicxml file.

  Args:
    file_obj (string): A Filepath to the musicxml file to parse.

  Returns:
    (dict) of all the elements within.
  """

  # Rewrite musicxml files to have backup tags inside the note objects, the way it should be.
  # This function returns the file as a corrected string.
  file_obj = handle_backups(file_obj)

  handlers = {
    # Engravers
    "Sibelius": Sibelius,
    "Finale": Finale,
    "GuitarPro": Guitarpro,
    # OMRs
    "Audiveris": Audiveris,
    "PhotoScore": Photoscore,
    "ScoreMaker": Scoremaker,
    "SmartScore": Smartscore,
  }

  try:
    for software in handlers:
      if software in "".join(boundary_search("<software>", "</software>", file_obj)):
        return handlers.get(software)(file_obj)
  except Exception as err:
    raise FileIncompatible("Either a parser was not created for that musicXML output" +
                            ", you found a significant bug, or you did not provide a" +
                            f"valid musicXML file.\nTraceback:\n{err}") # noqa E127


if __name__ == "__main__":
  data = "../tests/xml/test.xml"
  print(Parse(data))
