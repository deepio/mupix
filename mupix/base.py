import copy

import attr

from mupix.result_objects import Result


@attr.s
class MupixObject():
  notes = attr.ib(kw_only=True,)
  rests = attr.ib(kw_only=True,)
  timeSignatures = attr.ib(kw_only=True,)
  keySignatures = attr.ib(kw_only=True,)
  clefs = attr.ib(kw_only=True,)
  parts = attr.ib(kw_only=True, type=int, validator=[attr.validators.instance_of(int)])
  error_description = attr.ib(kw_only=True, type=dict, validator=[attr.validators.instance_of(dict)])

  @notes.validator
  @rests.validator
  @timeSignatures.validator
  @keySignatures.validator
  @clefs.validator
  def check(self, attribute, value):
    if not isinstance(value, list) and not isinstance(value, Result):
      raise ValueError(f"Must be a list or Results Object. {type(value)}")

  def ret(self):
    return self.notes, self.rests, self.timeSignatures, self.keySignatures, self.clefs, self.error_description


@attr.s
class Marking:
  _music21_object = attr.ib(eq=False)
  part = attr.ib(type=int)

  measure = attr.ib(init=False)
  @measure.default
  def _get_measure(self):
    return int(self._music21_object.measureNumber)

  onset = attr.ib(init=False, type=str)
  @onset.default
  def _get_onset(self):
    return str(self._music21_object.offset)

  def asdict(self):
    tmp = attr.asdict(self)
    del tmp["_music21_object"]
    return tmp

  def asname(self):
    string = str(self.__class__).split(".")[-1].replace("Object", "")
    return string[0].lower() + string[1:-2] + "s"


@attr.s
class MusicalEvent(Marking):
  duration = attr.ib(init=False, type=str, eq=False)
  @duration.default
  def _get_duration(self):
    return str(self._music21_object.quarterLength)

  voice = attr.ib(init=False, type=int)
  @voice.default
  def _get_voice(self):
    if isinstance(self._music21_object.activeSite.id, int):
      return 1
    else:
      return int(self._music21_object.activeSite.id)

  articulation = attr.ib(init=False, eq=False)
  @articulation.default
  def _get_articulation(self):
    return [item.name for item in self._music21_object.articulations]


@attr.s
class NoteObject(MusicalEvent):
  pitch = attr.ib(init=False, eq=False)
  @pitch.default
  def _get_pitch(self):
    return self._music21_object.step

  octave = attr.ib(init=False, eq=False)
  @octave.default
  def _get_octave(self):
    return self._music21_object.octave

  accidental = attr.ib(init=False, type=str, eq=False)
  @accidental.default
  def _get_accidental(self):
    note = self._music21_object
    if len(note.name) > 1:
      return note.name[1:]
    else:
      return ""

  stemdirection = attr.ib(init=False, eq=False)
  @stemdirection.default
  def _get_stem_direction(self):
    return self._music21_object.stemDirection

  beam = attr.ib(init=False, eq=False)
  @beam.default
  def _get_beam(self):
    note = self._music21_object
    note.beams.getTypes()
    # The number of "partial" elements that can appear in the beams is related to the note duration.
    # We do not want the errors be disproportionate if the duration is wrong too.
    return set([item for item in note.beams.getTypes()])


@attr.s
class RestObject(MusicalEvent):
  pass


@attr.s
class TimeSignatureObject(Marking):
  numerator = attr.ib(init=False, eq=False)
  @numerator.default
  def _get_numerator(self):
    return self._music21_object._getNumerator()

  denominator = attr.ib(init=False, eq=False)
  @denominator.default
  def _get_denominator(self):
    return self._music21_object._getDenominator()


@attr.s
class KeySignatureObject(Marking):
  step = attr.ib(init=False, eq=False)
  @step.default
  def _get_step(self):
    return self._music21_object.asKey().name.split(" ")[0]

  mode = attr.ib(init=False, eq=False)
  @mode.default
  def _get_mode(self):
    return self._music21_object.asKey().name.split(" ")[1]


@attr.s
class ClefObject(Marking):
  name = attr.ib(init=False, eq=False)
  @name.default
  def _get_name(self):
    return self._music21_object.sign

  line = attr.ib(init=False, eq=False)
  @line.default
  def _get_line(self):
    return self._music21_object.line

  octave = attr.ib(init=False, eq=False)
  @octave.default
  def _get_octave(self):
    return self._music21_object.octaveChange


def normalize_object_list(input_list, maximum):
  """
  Different software vendors encode time signatures, key signatures, and clefs in a peculiar way.
  Some repeat the previous object in every following measure:
    eg: Let's say this hypothetical score has 44 measures. When parsing a problematic musicXML file,
      you will notice there are 44 treble clefs in the same instrument part. Meaning the same,
      unchanging clef, was repeated once per measure in the file. The same can happen on a per-system
      basis. It is not a bad way to explain the music because each element implied, even if it is missing.
  To avoid any further complication, the clefs, time signatures, and key signatures have been
  "normalized" to always be repeated on every measure, because they are still "acting" on a measure when
  they are omitted.

  [TODO] Clean up the algorithm, maybe splitting it into an iter and a yielder or something with dequeue
  for better readability. This is just a PoC anyway.

  Args:
    input_list (list): A list of objects (KeySignatureObject, TimeSignatureObject or ClefObject).
    maximum (int): How many measures should the objects be expanded for.

  Returns:
    list: The expanded object list
  """

  measure = 1
  output_list = []
  # If there are no inputs given, skip everything.
  if len(input_list) == 0:
    return []

  while measure <= maximum:
    try:
      # Next element follows sequential number
      if input_list[0].measure == measure:
        output_list.append(input_list.pop(0))
        measure += 1
      # Missing element, create a new one and add it at the end of the list
      elif input_list[0].measure > measure:
        # If there is no information in the first measure, pick the information from the first element and duplicate
        if len(output_list) == 0:
          last_object = copy.deepcopy(input_list[0])
          last_object.measure = measure
          output_list.append(last_object)
          measure += 1
        else:
          last_object = copy.deepcopy(output_list[-1])
          last_object.measure += 1
          output_list.append(last_object)
          measure += 1
      # Next element has the same number as the previous one, but the other attributes are different.
      elif input_list[0].measure < measure:
        output_list.append(input_list.pop(0))
    # `input_list` last item's number was smaller than maximum.
    # Keep creating a duplicate of the last item until maximum is reached.
    except IndexError:
      try:
        tail_object = copy.deepcopy(output_list[-1])
      except IndexError:
        raise Exception(len(input_list), input_list, output_list)
      tail_object.measure += 1
      output_list.append(tail_object)
      measure += 1
  return output_list
