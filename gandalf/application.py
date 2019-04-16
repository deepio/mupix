from gandalf.exceptions import FileIncompatible
from gandalf.engraver.sibelius import Sibelius
from gandalf.engraver.finale import Finale
from gandalf.engraver.guitarpro import Guitarpro
from gandalf.omr.audiveris import Audiveris
from gandalf.omr.photoscore import Photoscore
from gandalf.omr.scoremaker import Scoremaker
from gandalf.omr.smartscore import Smartscore
from gandalf.extra import boundary_search

def Parse(file_obj):
  handlers = {
    # Engravers
    "Sibelius": Sibelius,
    "Finale": Finale,
    "GuitarPro": Guitarpro,
    # OMRs
  }

  try:
    for software in handlers:
      if software in "".join(boundary_search("<software>", "</software>", file_obj)):
        return handlers.get(software)(file_obj)
  except Exception as err:
    raise FileIncompatible(f"""Either a parser was not created for that musicXML output, or you did not provide a valid musicXML file.\nTraceback:\n{err}""")

if __name__ == "__main__":
  with open("../tests/xml/test.xml") as f:
    data = f.read()
  print(
    Parse(data)
  )
