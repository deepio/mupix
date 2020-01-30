"""
The properties of these objects are named in a specific way for a reason. Any
property that is not to be evaluated has an underscore in them
(eg: _music21_object). If the property requires more than a word to describe
it, then write it in camelCase style.
"""
import copy

import attr
from music21.interval import Interval
from music21.key import Key
from music21.note import Note

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
  """
  A NoteObject holds information useful to Mupix for symbolic music
  file differentiation.

  :property [step]: I believe the step in Music21 should be renamed to a
    `note.name`. A step should be similar to the concept of a scale degree,
    except that all the distances are counted in semitones relative to the key
    signature. Also note that octave differences are also removed, much like
    scale degrees.

    .. note:: For example
      In the key of C Major, if the octave information is removed

        C2 -> C8  = 0 (C, C)

        C2 -> C#8 = 1 (C, C#) that's one semitone

        C8 -> C#2 = 1 (C, C#) Still one semitone

        C2 -> G4  = 7 (C, C#, D, D#, E, F, F#, G) still 7 semitones

  :property [pitch]:
    This is what Music21 defines as a step (C, D, E, F, G, etc.)
    For continued use, grab the pitch by referencing the music21 object.

    .. warning:: This property will be deprecated in **version 0.2.0**. Use **noteObject._music21_object.step** instead.

  :property [octave]: The octave of the note (middle C is C4)

  :property [accidental]: Any note alterations of pitch (#, ##, b, bb, natural)

  :property [stemdirection]: The direction (up or down) of the note stem (if present).

  :property [beam]: How note beams are connected between adjacent notes.

  """
  step = attr.ib(kw_only=True, eq=False, default=None)

  # noteName = attr.ib(init=False, eq=False)
  # @noteName.default
  # def _get_noteName(self):
  #   return self._music21_object.step

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


def normalize_object_list(object_list, total_measures, total_parts):
  """
  Without changing the order of the objects, iterate through each instrumental
  part and populate missing information in place.
  """
  obj = []
  for part in range(1, total_parts + 1):
    obj += _populate_list([x for x in object_list if x.part == part], total_measures)
  return obj


def add_step_information(notes, keySignatures):
  """
  This function will populate the step information into Mupix note objects, it
  is required because music21 will not keep key signature information in
  measure other than the measure the key is defined in when reading musicXML.
  The maintainers of music21 don't believe this is an issue and won't fix it,
  so this and others must exist.

  :param [notes]: A list of Mupix NoteObjects.
  :type [notes]: List

  :param [keySignatures]: A list of Mupix KeySignatureObjects.
  :type [keySignatures]: List

  :return [List]: The original list of Mupix NoteObjects (in order) with step information included.
  :rtype: List
  """
  for key in keySignatures:
    key_name = key.step.upper() if key.mode == "major" else key.step.lower()

    for note in notes:
      if note.part == key.part and note.measure == key.measure:
        note.step = Interval(noteStart=Note(Key(key_name).asKey().tonic), noteEnd=note._music21_object).semitones % 12

  return notes


if __name__ == "__main__":
  """
  How to create Mupix Objects.
  """
  from music21.stream import Score, Part, Measure
  from music21.key import KeySignature
  from music21.note import Note  # noqa

  s = Score()
  p1 = Part(id="part1")
  m1 = Measure(number=1)
  m1.append(KeySignature(3))
  m1.append(Note("C4", type="eighth"))
  m2 = Measure(number=2)
  m2.append(KeySignature(0))
  m2.append(Note("G4", type="eighth"))
  p1.append([m1, m2])
  s.append([p1])

  notes = [NoteObject(item, 1) for item in s.recurse().notes if not item.isChord]
  print(notes)
