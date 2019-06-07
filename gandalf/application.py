from io import StringIO, BytesIO

from lxml import etree
import music21

from gandalf.base import TimeSignature
from gandalf.base import KeySignature
from gandalf.base import NoteObject
from gandalf.base import RestObject
from gandalf.base import Result

from gandalf.extra import __return_root_path
from gandalf.extra import extract_accidental
from gandalf.extra import extract_beam


def parse_xml(filepath):
  """
  Output dictionary key's are structured in the following way.
    part_number.measure_number.musical_event_number

  The reason we enumerate this way is because we want the notes in a measure to be
  incremental to the measure, not based on the beat. If we base it off the beat, our
  comparison will break.
  """
  note_data = {}
  meter_data = {}
  key_data = {}
  file_object = music21.converter.parseFile(filepath)

  # For all parts in the score
  for part_index, part in enumerate(file_object.recurse().getElementsByClass("Part")):
    # And all measures in the part
    for measure_index, measure in enumerate(part.recurse().getElementsByClass("Measure")):

      for meter_index, meter in enumerate(measure.recurse().getElementsByClass("TimeSignature")):
        meter_data[f"{part_index}.{measure_index}.{meter_index}"] = TimeSignature(meter._getNumerator(), meter._getDenominator())  # noqa

      for key_index, key in enumerate(measure.recurse().getElementsByClass("KeySignature")):
        key = str(key.asKey()).split(" ")
        key_data[f"{part_index}.{measure_index}.{key_index}"] = KeySignature(key[0], key[1])

      # Grab all Musical events
      for note_index, note in enumerate(measure.recurse().getElementsByClass(["Note", "Rest"])):
        if note.isRest:
          # note_data[f"{part_index}.{measure_index}.{note_index}"] = \
          note_data[f"{part_index}.{measure_index}.{note_index}"] = RestObject(note.quarterLength)
        elif note.isNote:
          note_data[f"{part_index}.{measure_index}.{note_index}"] = \
          NoteObject(
            note.quarterLength,
            note.step,
            note.octave,
            extract_accidental(note),
            note.stemDirection,
            extract_beam(note),
          )

  return note_data, meter_data, key_data


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
    self.note_parameter_list = ["pitch", "octave", "accidental", "stem_direction"]

    for self.key, self.value in self.true_data[0].items():
      self.compare_dicts()

  def compare_dicts(self):
    true_object = self.value
    test_object = self.test_data[0][self.key]

    # Fancy way of doing the exact same comparison for all parameters. It just saves from doing the
    # same things for every parameter in the list.
    # Why? Its to avoid code duplication, but it has the expense of being a little to read at first sight.
    #   if pitch,
    #   elif pitch,

    #   if octave,
    #   elif octave,

    #   if accidental,
    #   elif accidental,

    #   if stem_direction
    #   elif stem_direction
    for parameter in self.note_parameter_list:
      if true_object.__getattribute__(parameter) == test_object.__getattribute__(parameter):
        self.__setattr__(parameter, Result(self.__getattribute__(parameter).right + 1, self.__getattribute__(parameter).wrong))  # noqa
      elif true_object.__getattribute__(parameter) != test_object.__getattribute__(parameter):
        self.__setattr__(parameter, Result(self.__getattribute__(parameter).right, self.__getattribute__(parameter).wrong + 1))  # noqa

  def calculate_total(self):
    """
    Fancy way to cycle through parameters instead of explicitly going through each
    """
    self.total_right, self.total_wrong = 0, 0
    for parameter in self.note_parameter_list:
      self.total_right += self.__getattribute__(parameter).right
      self.total_wrong += self.__getattribute__(parameter).wrong
