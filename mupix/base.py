"""
The properties of these objects are named in a specific way for a reason. Any
property that is not to be evaluated has an underscore in them
(eg: _music21_object). If the property requires more than a word to describe
it, then write it in camelCase style.
"""
import copy

import attr

from mupix.result_objects import Result


@attr.s
class MupixObject():
  """A MupixObject holds information for an entire score.
  It holds an ordered list of all the musical events in the score.

  :param [notes]: A list of objects related to notes
  :type [notes]: List or Result object

  :param [rests]: A list of objects related to rests
  :type [rests]: List or Result object

  :param [timeSignatures]: A list of objects related to time signatures
  :type [timeSignatures]: List or Result object

  :param [keySignatures]: A list of objects related to key signatures
  :type [keySignatures]: List or Result object

  :param [clefs]: A list of objects related to clefs
  :type [clefs]: List or Result object

  :param [parts]: A number representing the number of total staffs per system
  :type [parts]: Integer

  :param [error_description]: More detailed error information
  :type [error_description]: Dictionary
  """
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
    """
    Type-check for notes, rests, time signatures, key signatures, and, clefs.
    They should be either a list, or a Result object for eventual output.
    """
    if not isinstance(value, list) and not isinstance(value, Result):
      raise ValueError(f"Must be a list or Results Object. {type(value)}")

  def ret(self):
    """
    Return all information about the Mupix object as a tuple.
    """
    return self.notes, self.rests, self.timeSignatures, self.keySignatures, self.clefs, self.error_description


@attr.s
class Marking:
  """
  The base class for all the components of a Mupix object

  :property [_music21_object]: The original music21 object, in case it is needed.

  :property [part]: An integer representing the instrument (1 for the first instrument, etc.)

  :property [measure]: The measure in which this object can be found. It is
    inferred by the music21 object.

  :property [onset]: The time in the measure where this event occurs. It is
    inferred by the music21 object.
  """
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
    """
    Return the object as a JSON serializable python dictionary.
    """
    tmp = attr.asdict(self)
    del tmp["_music21_object"]
    return tmp

  def asname(self):
    """
    Returns the name of the current class (or subclass)
    """
    string = str(self.__class__).split(".")[-1].replace("Object", "")
    return string[0].lower() + string[1:-2] + "s"


@attr.s
class MusicalEvent(Marking):
  """
  A musical event is an **active** marking in a score, rather than **passive**
  marking like a key signature or a time signature. Active markings are
  effective when read and discarded when finished.

  :property [duration]: The amount of time the event will last.

  :property [voice]: In the case of multiple instruments within a staff, this
    is a numerical representation of which instrument it represents.

  :property [articulation]: A musical articulation (staccato, tenuto, accents, etc.)
  """
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
  """
  Same as :func:`mupix.base.MusicalEvent`
  """
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


def _populate_list(input_list, maximum):
  """
  Different music engraving software encode time signatures, key signatures,
    and clefs in a peculiar way. Some repeat the previous object in every
    following measure.

    Let's say this hypothetical score has 44 measures. When parsing a problematic musicXML file,
    you will notice there are 44 treble clefs in the same instrument part. Meaning the same,
    unchanging clef, was repeated once per measure in the file. The same can happen on a per-system
    basis. It is not a bad way to explain the music because each element implied, even if it is missing.

  To avoid any further complication, the clefs, time signatures, and key signatures have been
  "normalized" to always be repeated on every measure, because they are still "acting" on a measure when
  they are omitted.

  [TODO] Clean up the algorithm, maybe splitting it into an iter and a yielder or something with dequeue
  for better readability. This is just a PoC anyway.

  :param [input_list]: A list of objects (KeySignatureObject, TimeSignatureObject or ClefObject).
  :type [input_list]: List

  :param [maximum]: An integer that represents the maximum number of measures in the score. In other words, how many measures should the objects be expanded for.
  :type [maximum]: Integer

  :return: Returns a the original list with added objects if they are missing from each measure.
  :rtype: List
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
