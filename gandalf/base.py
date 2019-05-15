from collections import defaultdict, namedtuple
from io import StringIO, BytesIO
import json
import os

import attr
from lxml import etree

from gandalf.extra import boundary_search
from gandalf.extra import compare_list_items
from gandalf.extra import compare_dict_items
from gandalf.extra import __return_root_path


@attr.s
class MusicalEvent:
  duration = attr.ib(type=int)
  tuplet = attr.ib(type=int)
  voice = attr.ib(type=int)


@attr.s
class NoteObject(MusicalEvent):
  pitch = attr.ib(type=str)
  octave = attr.ib(type=int)
  accidental = attr.ib(type=str, validator=attr.validators.in_(["natural", "#", "b", ""]))


@attr.s
class RestObject(MusicalEvent):
  voice = attr.ib(type=list)


@attr.s
class MusicalMarker:
  part = attr.ib(type=int)
  measure = attr.ib(type=int)
  beat = attr.ib(type=int)


@attr.s
class ClefObject(MusicalMarker):
  # percussion clef not implemented.
  name = attr.ib(type=str, default="G-clef", validator=attr.validators.in_(["G-clef", "C-clef", "F-clef"]))
  step = attr.ib(type=str, default="g", validator=attr.validators.in_(["a", "b", "c", "d", "e", "f", "g"]))
  octave = attr.ib(type=int, default=4, validator=attr.validators.in_([3, 4]))


@attr.s
class TimeSignatureObject(MusicalMarker):
  numerator = attr.ib(type=int, default=4, validator=attr.validators.in_([x for x in range(1, 30, 1)]))
  denominator = attr.ib(type=int, default=4, validator=attr.validators.in_([1, 2, 4, 8, 16]))


@attr.s
class TempoObject(MusicalMarker):
  metronome_mark = attr.ib(init=False, type=int)
  metronome_step = attr.ib(init=False, type=int, validator=attr.validators.in_([1, 2, 4, 8, 16]))


@attr.s
class PageMarkers:
  marker_type = attr.ib(type=str)
  content = attr.ib(type=str)


@attr.s
class MeasureNumber(PageMarkers):
  measure_number = attr.ib(type=int)


def MusicXMLValidator(schema_filepath, musicxml_filepath):
  """
  Return if the provided musicxml file is valid against the current musicxml schema.

  Args:
    schema_filepath (string): a filepath to the musicxml schema.

    musicxml_filepath (string): a filepath to the musicxml file to be validated.

  Returns:
    bool
  """
  with open(schema_filepath, "r") as schema:
      schema = StringIO(schema.read())
  with open(musicxml_filepath, "rb") as xml_file:
    test = BytesIO(xml_file.read())

  xml_schema = etree.XMLSchema(etree.parse(schema_filepath))
  return xml_schema.validate(etree.parse(test))


class ValidateXML:
  def __init__(self, schema_filepath, testxml_filepath):
    self.schema_filepath = schema_filepath
    self.testxml_filepath = testxml_filepath
    self.output = namedtuple("ValidateXML", ["status", "schema_file", "test_file"])

    with open(self.schema_filepath, "r") as schema:
      self.schema = StringIO(schema.read())
    with open(self.testxml_filepath, "rb") as test_file:
      self.test = BytesIO(test_file.read())

    self.xmlschema_doc = etree.parse(self.schema_filepath)
    self.xml_schema = etree.XMLSchema(self.xmlschema_doc)

  def isvalid(self):
    status = self.xml_schema.validate(etree.parse(self.test))
    return self.output(status, self.schema_filepath, self.testxml_filepath)


class BasicDiff:
  def __init__(self, ground_truth, omr_data):
    print("Welcome to the mega parser :)")

    with open(ground_truth,) as f:
      self.true_data = MusicXML_Parser(f.read()).parse()
    with open(omr_data,) as f:
      self.test_data = MusicXML_Parser(f.read()).parse()
    self.c, self.w, self.e = 0, 0, 0
    self.compare()

  def compare(self):
    for key, value in self.true_data.items():
      if isinstance(value, list):
        temp = compare_list_items(self.true_data[key], self.test_data[key])
        self.c += temp[0]
        self.w += temp[1]
        self.e += temp[2]
      elif isinstance(value, dict):
        temp = compare_dict_items(self.true_data[key], self.test_data[key])
        self.c += temp[0]
        self.w += temp[1]
        self.e += temp[2]
      else:
        raise Exception(f"Something went very wrong, check the value: {value} and key: {key}")

  def __str__(self):
    message = f"Correct: {self.c}\nWrong: {self.w}\nTotal: {self.e}"
    return message


class MusicXML_Parser:
  def __init__(self, file_obj):
    self.output = defaultdict()
    self.file_obj = file_obj

    self.parse()

  def __str__(self):
    self.output = self.parse()
    return json.dumps(self.output, default=lambda o: o.__dict__, sort_keys=True, indent=2)

  def __getitem__(self, item):
    return self.output[item]

  def get_vendor(self,):
    return boundary_search("<software>", "</software>", self.file_obj)[0]

  def get_instruments(self,):
    return boundary_search("<score-instrument id=\"", "\"", self.file_obj)

  def get_parts(self,):
    output = defaultdict()
    for measure_number, instrument in enumerate(self.get_instruments()):
      output[instrument] = boundary_search("<part id=\"", "</part>", self.file_obj)[measure_number]
    return output

  def get_clefs(self, measure_obj,) -> list:
    return boundary_search("<sign>", "</sign>", measure_obj)

  def get_times(self, measure_obj) -> list:
    time = []
    numerator = boundary_search("<beats>", "</beats>", measure_obj)
    denominator = boundary_search("<beat-type>", "</beat-type>", measure_obj)
    if numerator == []:
      return []
    else:
      for item in range(len(numerator)):
        time.append(f"{numerator[item]}/{denominator[item]}")
      return time

  def get_keys(self, measure_obj):
    return boundary_search("<key", "</key>", measure_obj)

  def get_key_fifths(self, measure_obj) -> list:
    fifths = []
    for item in self.get_keys(measure_obj):
      fifths.append("".join(boundary_search("<fifths>", "</fifths>", item)))
    return fifths

  def get_key_modes(self, measure_obj) -> list:
    modes = []
    for item in self.get_keys(measure_obj):
      modes.append("".join(boundary_search("<mode>", "</mode>", item)))
    return modes

  def get_step(self, note_obj) -> str:
    note = "".join(boundary_search("<pitch>", "</pitch>", note_obj))
    step = "".join(boundary_search("<step>", "</step>", note))
    octave = "".join(boundary_search("<octave>", "</octave>", note))
    note = f"{step}{octave}"
    if note == "":
      note = "rest"
    return note

  def get_accidental(self, note_obj) -> str:
    accidental = "".join(boundary_search("<alter>", "</alter>", note_obj))
    if accidental == "0":
      return "natural"
    elif accidental == "1":
      return "#"
    elif accidental == "-1":
      return "b"
    elif accidental == "":
      return ""
    else:
      return "unexpected"

  def get_duration(self, note_obj) -> str:
    duration = "".join(boundary_search("<type>", "</type>", note_obj))
    tuplet = "".join(boundary_search("<actual-notes>", "</actual-notes>", note_obj))
    if tuplet == "":
      return duration
    else:
      return f"{duration}-tuplet({tuplet})"

  def get_stem_direction(self, note_obj) -> str:
    return "".join(boundary_search("<stem>", "</stem>", note_obj))

  def get_articulations(self, note_obj) -> list:
    articulation = "".join(boundary_search("<articulations", "</articulations>", note_obj))
    return [art for art in boundary_search("<", " />", articulation)]

  def get_note_object(self, ):
    pass

  def parse(self):
    output = {}
    parts_obj = self.get_parts()
    for part_number, (instrument, part_data) in enumerate(parts_obj.items()):
      for measure_number, measure_data in enumerate(boundary_search("<measure", "</measure", part_data)):
        if self.get_clefs(measure_data) != []:
          output[f"part_{part_number}.measure_{measure_number}.clef"] = self.get_clefs(measure_data)
        if self.get_times(measure_data) != []:
          output[f"part_{part_number}.measure_{measure_number}.time_signature"] = self.get_times(measure_data)
        if self.get_key_fifths(measure_data) != []:
          output[f"part_{part_number}.measure_{measure_number}.key_signature_fifth"] = self.get_key_fifths(measure_data)
        if self.get_key_modes(measure_data) != []:
          output[f"part_{part_number}.measure_{measure_number}.key_signature_mode"] = self.get_key_modes(measure_data)
        note_number = 0
        for note_data in boundary_search("<note", "</note", measure_data):
          if "vertical-alignment" not in note_data:
            note_number += 1

          output[f"part_{part_number}.measure_{measure_number}.note_{note_number}.step.{self.get_step(note_data)}"] = {}
          if self.get_duration(note_data):
            output[f"part_{part_number}.measure_{measure_number}.note_{note_number}.step.{self.get_step(note_data)}"]["duration"] = self.get_duration(note_data) # noqa E501
          if self.get_accidental(note_data):
            output[f"part_{part_number}.measure_{measure_number}.note_{note_number}.step.{self.get_step(note_data)}"]["accidental"] = self.get_accidental(note_data) # noqa E501
          if self.get_stem_direction(note_data):
            output[f"part_{part_number}.measure_{measure_number}.note_{note_number}.step.{self.get_step(note_data)}"]["stem_direction"] = self.get_stem_direction(note_data) # noqa E501
          if self.get_articulations(note_data) != []:
            output[f"part_{part_number}.measure_{measure_number}.note_{note_number}.step.{self.get_step(note_data)}"]["articulation"] = self.get_articulations(note_data) # noqa E501

    return output


def main():
  os.system("clear")

  ROOT_DIR = __return_root_path() + "/tests/xml"
  test_file = ROOT_DIR + "/test.xml"
  schema = ROOT_DIR + "/musicxml.xsd" # noqa F841

  # Examine Parsing
  # Check if parsing works
  # with open(test_file) as f:
  #   data = f.read()
  # print(MusicXML_Parser(data))

  # Validation Check
  # print(ValidateXML(schema, test_file).isvalid())

  # Diff Check
  print(BasicDiff(test_file, test_file))


if __name__ == "__main__":
  main()
