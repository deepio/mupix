class FileIncompatible(Exception):
  """
  Either a parser was not created for that musicXML output, or you did not
  provide a valid musicXML file.
  """
  pass


class CheckNextNoteException(Exception):
  """
  Exception raised when about to check the next note to see if one was
  incorrectly inserted into the omr output.
  """
  pass
