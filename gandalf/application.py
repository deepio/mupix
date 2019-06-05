import music21

from gandalf.base import TimeSignature
from gandalf.base import KeySignature
from gandalf.base import NoteObject
from gandalf.base import Result

from gandalf.extra import extract_accidental


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
            pass
        elif note.isNote:
          note_data[
            f"{part_index}.{measure_index}.{note_index}"
          ] = NoteObject(
            "eighth",
            note.step,
            note.octave,
            extract_accidental(note),
            note.stemDirection,
          )

  return note_data, meter_data, key_data


