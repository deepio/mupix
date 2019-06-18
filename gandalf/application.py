from io import StringIO, BytesIO

from lxml import etree
import music21

from gandalf.base import TimeSignature
from gandalf.base import KeySignature
from gandalf.base import NoteObject
from gandalf.base import RestObject
from gandalf.base import Result

from gandalf.extra import __return_root_path


def parse_xml(filepath):
  """
  Returning all the music21 elements we could be interested in.
  """
  notes_and_rests = [item for item in music21.converter.parseFile(filepath).recurse().notesAndRests]
  time_signatures = [item for item in music21.converter.parseFile(filepath).recurse().getTimeSignatures()]
  key_signatures = [item for item in music21.converter.parseFile(filepath).recurse().getClefs()]
  return notes_and_rests, time_signatures, key_signatures


def validate_xml(musicxml_filepath):
  """
  Return if the provided musicxml file is valid against the current musicxml schema.

  Args:
    schema_filepath (string): a filepath to the musicxml schema.

    musicxml_filepath (string): a filepath to the musicxml file to be validated.

  Returns:
    bool
  """
  schema_filepath = __return_root_path() + "/tests/xml/musicxml.xsd"
  with open(schema_filepath, "r") as schema:
    schema = StringIO(schema.read())
  with open(musicxml_filepath, "rb") as xml_file:
    test = BytesIO(xml_file.read())

  xml_schema = etree.XMLSchema(etree.parse(schema_filepath))
  return xml_schema.validate(etree.parse(test))


class Compare:
  def __init__(self, true_data, test_data):
    self.true_data = parse_xml(true_data)
    self.test_data = parse_xml(test_data)
    self.compare()
    self.calculate_total()

  def __str__(self):
    return str(Result(self.total_right, self.total_wrong))

  def __repr__(self):
    return Result(self.total_right, self.total_wrong)

  def compare(self):
    self.pitch = Result()
    self.octave = Result()
    self.accidental = Result()
    self.stem_direction = Result()
