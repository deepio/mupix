from io import StringIO, BytesIO

import attr
from lxml import etree
import music21

from gandalf.base import GandalfObject
from gandalf.base import NoteObject
from gandalf.base import RestObject
from gandalf.base import TimeSignature
from gandalf.base import KeySignature
from gandalf.base import Clef
from gandalf.base import Result
from gandalf.extra import __return_root_path


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


@attr.s
class ParseMusic21(GandalfObject):
  """
  This is just a simplifying wrapper around Music21, so it can import anything Music21 can.
  """
  @classmethod
  def from_filepath(cls, filepath):
    notes, rests, time_signatures, key_signatures, clefs = [], [], [], [], []
    for parts_index, parts in enumerate(music21.converter.parseFile(filepath).recurse().getElementsByClass("Part"), 1):  # noqa
      notes += [NoteObject(item, parts_index) for item in parts.recurse().notes if not item.isChord]
      rests += [RestObject(item, parts_index) for item in parts.recurse().notesAndRests if not item.isNote]
      time_signatures += [TimeSignature(item, parts_index) for item in parts.recurse().getTimeSignatures()]
      key_signatures += [KeySignature(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")]  # noqa
      clefs += [Clef(item, parts_index) for item in parts.recurse().getElementsByClass("Clef")]
    return cls(
      notes=notes,
      rests=rests,
      time_signatures=time_signatures,
      key_signatures=key_signatures,
      clefs=clefs
    )

