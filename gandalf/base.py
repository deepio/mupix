from collections import defaultdict, namedtuple
from io import StringIO, BytesIO
import json
from os import system

import attr
from lxml import etree

from gandalf.extra import boundary_search


@attr.s
class MusicalEvent:
  duration = attr.ib(type=int)
  voice = attr.ib(type=int)


@attr.s
class NoteObject(MusicalEvent):
  pitch = attr.ib(type=str)
  octave = attr.ib(type=int)


@attr.s
class RestObject(MusicalEvent):
  pass 


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


class MusicXML_Parser:
  def __init__(self, file_obj):
    self.output = defaultdict()
    self.file_obj = file_obj

    self.parse()

  def __str__(self):
    self.output = self.parse()
    return json.dumps(self.output, default=lambda o: o.__dict__, sort_keys=True, indent=2)

  def get_vendor(self,):
    return boundary_search("<software>", "</software>", self.file_obj)[0]

  def get_instruments(self,):
    return boundary_search("<score-instrument id=\"", "\"", self.file_obj)

  def get_parts(self,):
    output = defaultdict()
    for measure_number, instrument in enumerate(self.get_instruments()):
      output[instrument] = boundary_search("<part id=\"", "</part>", self.file_obj)[measure_number]
    return output

  def get_clefs(self, measure_obj,):
    return boundary_search("<sign>", "</sign>", measure_obj)

  def get_times(self, measure_obj):
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

  def get_key_fifths(self, measure_obj):
    fifths = []
    for item in self.get_keys(measure_obj):
      fifths.append("".join(boundary_search("<fifths>", "</fifths>", item)))
    return fifths

  def get_key_modes(self, measure_obj):
    modes = []
    for item in self.get_keys(measure_obj):
      modes.append("".join(boundary_search("<mode>", "</mode>", item)))
    return modes

  def get_step(self, note_obj):
    note = "".join(boundary_search("<pitch>", "</pitch>", note_obj))
    step = "".join(boundary_search("<step>", "</step>", note))
    octave = "".join(boundary_search("<octave>", "</octave>", note))
    note = f"{step}{octave}"
    if note == "":
      note = "rest"
    return note

  def get_accidental(self, note_obj):
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

  def get_duration(self, note_obj):
    duration = "".join(boundary_search("<type>", "</type>", note_obj))
    tuplet = "".join(boundary_search("<actual-notes>", "</actual-notes>", note_obj))
    if tuplet == "":
      return duration
    else:
      return f"{duration}-tuplet({tuplet})"

  def get_stem_direction(self, note_obj):
    return "".join(boundary_search("<stem>", "</stem>", note_obj))

  def get_articulations(self, note_obj):
    articulation = "".join(boundary_search("<articulations", "</articulations>", note_obj))
    return [art for art in boundary_search("<", " />", articulation)]

  def get_note_object(self, ):
    pass

  def parse(self):
    output = defaultdict()
    parts_obj = self.get_parts()
    for part_number, (instrument, part_data) in enumerate(parts_obj.items()):
      for measure_number, measure_data in enumerate(boundary_search("<measure", "</measure", part_data)):
        output[f"part_{part_number}.measure_{measure_number}.clef"] = self.get_clefs(measure_data)
        output[f"part_{part_number}.measure_{measure_number}.time_signature"] = self.get_times(measure_data)
        output[f"part_{part_number}.measure_{measure_number}.key_signature_fifth"] = self.get_key_fifths(measure_data)
        output[f"part_{part_number}.measure_{measure_number}.key_signature_mode"] = self.get_key_modes(measure_data)
        note_number = 0
        for note_data in boundary_search("<note", "</note", measure_data):
          if "vertical-alignment" not in note_data:
            note_number += 1
          output[f"part_{part_number}.measure_{measure_number}.note_{note_number}.step.{self.get_step(note_data)}"] = {
            "accidental": self.get_accidental(note_data),
            "duration": self.get_duration(note_data),
            "stem_direction": self.get_stem_direction(note_data),
            "articulation": self.get_articulations(note_data)
          }

    return output


def main():
  system("clear")

  test_file = "../tests/xml/test.xml"
  schema = "../tests/xml/musicxml.xsd"

  # Check if parsing works
  with open(test_file) as f:
    data = f.read()
  print(MusicXML_Parser(data))

  # Validation Check
  print(ValidateXML(schema, test_file).isvalid())


if __name__ == "__main__":
  main()
