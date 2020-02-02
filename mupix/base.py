"""
The properties of these objects are named in a specific way for a reason. Any
property that is not to be evaluated has an underscore in them
(eg: _music21_object). If the property requires more than a word to describe
it, then write it in camelCase style.
"""
import copy
import operator

import attr
import music21
from music21.interval import Interval
from music21.key import Key
from music21.note import Note

from mupix.result_objects import (
  Result,
  NoteNameResult,
  NoteStepResult,
  NoteDurationResult,
  NoteOctaveResult,
  NoteAccidentalResult,
  NoteArticulationResult,
  NoteStemDirectionResult,
  NoteBeamResult,
  NoteVoiceResult,
  NoteTotalResult,
  RestArticulationResult,
  RestDurationResult,
  RestVoiceResult,
  RestTotalResult,
  TimeSignatureNumeratorResult,
  TimeSignatureDenominatorResult,
  TimeSignatureTotalResult,
  KeySignatureStepResult,
  KeySignatureModeResult,
  KeySignatureTotalResult,
  ClefNameResult,
  ClefLineResult,
  ClefOctaveResult,
  ClefTotalResult,
)
from mupix.extra import return_char_except


@attr.s
class MupixObject():
  """A MupixObject holds information for an entire score.
  A Mupix Object contains multiple lists of the contents within a symbolic music-file.

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

  def __iter__(self):
    return iter(self.ret())

  @classmethod
  def from_filepath(cls, filepath):
    """
    .. note::

      Using activesite from music21 won't work because the key 
      signature would be in measure one, and in measure two there is no
      information about key anymore. So :func:`mupix.base.add_step_information`
      was written.

      .. code-block:: python

        notes += [NoteObject(
          item,           # Music21 Object
          parts_index,    # Part number
          step=Interval(  # A step defined in the NoteObjects from mupix/base.py
            noteStart=item._getActiveSite().keySignature.asKey().tonic,
            noteEnd=item).semitones % 12) for item in parts.recurse().notes if not item.isChord]


    :param [filepath]: A character string that represents the filepath and filename of the file to open.
    :type [filepath]: String

    :return: A fully populated Mupix Object, with all the components of the symbolic music file analysized and sorted in their sections.
    :rtype: Mupix Object
    """
    notes, rests, timeSignatures, keySignatures, clefs = [], [], [], [], []
    for parts_index, parts in enumerate(music21.converter.parseFile(filepath).recurse().getElementsByClass("Part"), 1):  # noqa
      notes += [NoteObject(item, parts_index) for item in parts.recurse().notes if not item.isChord]
      rests += [RestObject(item, parts_index) for item in parts.recurse().notesAndRests if not item.isNote]
      timeSignatures += [TimeSignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("TimeSignature")]  # noqa
      keySignatures += [KeySignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")]  # noqa
      clefs += [ClefObject(item, parts_index) for item in parts.recurse().getElementsByClass("Clef")]

    try:
      measuresInScore = max(notes + rests, key=operator.attrgetter('measure')).measure
    except ValueError:
      measuresInScore = 0
      parts_index = 0

    timeSignatures = normalize_object_list(object_list=timeSignatures, total_measures=measuresInScore, total_parts=parts_index)
    keySignatures = normalize_object_list(object_list=keySignatures, total_measures=measuresInScore, total_parts=parts_index)
    clefs = normalize_object_list(object_list=clefs, total_measures=measuresInScore, total_parts=parts_index)

    notes = add_step_information(notes, keySignatures)  # only once keySignatures are normalized can we add the step information.

    return cls(
      notes=notes,
      rests=rests,
      timeSignatures=timeSignatures,
      keySignatures=keySignatures,
      clefs=clefs,
      parts=parts_index,
      error_description={},
    )


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

  name = attr.ib(init=False, eq=False)
  @name.default
  def _get_name(self):
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
  """
  This is an object that holds information related to all time signatures.
  """
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
  """
  This is an object that holds information related to all key signatures.
  """
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
  """
  This is an object that holds information related to all clefs.
  """
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
  part and populate missing information in place. This small function just
  makes sure :func:`mupix.base._populate_list` occurs on every part.
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
    # key_name = key.step.upper()  # Treat it all like major

    for note in notes:
      if note.part == key.part and note.measure == key.measure:
        # note.step = Interval(noteStart=Note(Key(key_name).asKey().tonic), noteEnd=note._music21_object).semitones % 12
        note.step = Interval(noteStart=Note(Key(key_name).asKey().tonic), noteEnd=Note(note._music21_object.step)).semitones % 12

  return notes


class BaseCompareClass(MupixObject):
  """
  The base comparison class for Mupix Objects.
  """
  # Notes
  notes = []
  notes_step = NoteStepResult()
  notes_name = NoteNameResult()
  notes_duration = NoteDurationResult()
  notes_octave = NoteOctaveResult()
  notes_accidental = NoteAccidentalResult()
  notes_articulation = NoteArticulationResult()
  notes_stemdirection = NoteStemDirectionResult()
  notes_beam = NoteBeamResult()
  notes_voice = NoteVoiceResult()
  notes_total = NoteTotalResult()

  # Rests
  rests = []
  rests_articulation = RestArticulationResult()
  rests_duration = RestDurationResult()
  rests_voice = RestVoiceResult()
  rests_total = RestTotalResult()

  # Time Signatures
  timeSignatures = []
  timeSignatures_numerator = TimeSignatureNumeratorResult()
  timeSignatures_denominator = TimeSignatureDenominatorResult()
  timeSignatures_total = TimeSignatureTotalResult()

  # Key Signatures
  keySignatures = []
  keySignatures_step = KeySignatureStepResult()
  keySignatures_mode = KeySignatureModeResult()
  keySignatures_total = KeySignatureTotalResult()

  # Clefs
  clefs = []
  clefs_name = ClefNameResult()
  clefs_line = ClefLineResult()
  clefs_octave = ClefOctaveResult()
  clefs_total = ClefTotalResult()

  error_description = {}

  def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
    # for result_to_exclude in do_not_count:
    #   del self.__getattribute__(result_to_exclude)

    # Parse both files
    self.true_data = MupixObject.from_filepath(true_filepath)
    self.test_data = MupixObject.from_filepath(test_filepath)

  def _return_object_names(self):
    """
    Returns all the objects

    For example:
      ['clefs', 'keySignatures', 'notes', 'rests', 'timeSignatures']
    """
    return [item for item in dir(self) if "_" not in item and item not in ["check", "ret"]]

  def _return_parameter_names(self, field):
    """
    For a specific object, return all items

    For notes:
      ['notes_accidental', 'notes_articulation', 'notes_beam', 'notes_duration', 'notes_octave', 'notes_step', 'notes_stemdirection']
    """
    return [item for item in dir(self) if field in item and "_" in item and "total" not in item]

  def _compare_expand_objects_same(self, true_object, test_object, object_):
    for result_parameter in self._return_parameter_names(object_):
      property_ = result_parameter.split("_")[-1]
      try:
        if true_object.__getattribute__(property_) == test_object.__getattribute__(property_):
          self.__getattribute__(result_parameter).right += 1
        else:
          self.error_description[f"part{self.true_part}_onset{self.true_onset}_{property_}_{self.true_mu21_obj}"] = f"part{self.test_part}_onset{self.test_onset}_{test_object}"  # noqa
          self.__getattribute__(result_parameter).wrong += 1
      except AttributeError:
        raise Exception(type(true_object), type(test_object), "What happened here???")

  def _compare_expand_objects_different(self, true_object, test_object, object_):
    for parameter in self._return_parameter_names("notes"):
      try:
        self.error_description[f"part{self.true_part}_onset{self.true_onset}_{parameter}_{self.true_mu21_obj}"] = "_"  # noqa
      except AttributeError:
        self.error_description[str(uuid.uuid4())] = f"part{self.test_part}_onset{self.test_onset}_{test_object}"  # noqa
        self.__getattribute__(parameter).wrong += 1

  def _compare(self, true_object, test_object):
    """
    Compare two Mupix Objects.

      - If the sequence alignment believes there is an extra note in the OMR output, simply deleting the extra note
        should be the solution. Removing each wrong element individually and finally removing the note is not how a
        human would fix this type of error.

      - Then check for each parameter available in the type of marking, count an error for each wrong element and a
        right for every correct. This function should works for all Mupix objects.
    """
    # If object is misaligned
    try:
      self.true_part = true_object.part
      self.true_onset = true_object.onset
      self.true_mu21_obj = true_object._music21_object
    except AttributeError:
      self.true_part = "_"
      self.true_onset = ""
      self.true_mu21_obj = ""

    # If object is missaligned
    try:
      self.test_part = test_object.part
      self.test_onset = test_object.onset
      self.test_mu21_obj = test_object._music21_object
    except AttributeError:
      self.test_part = "_"
      self.test_onset = ""
      self.test_mu21_obj = ""

    # As much as I liked how small and compact this was vs writing them out,
    # it became hard to find out where the real problem was...
    # 
    # # If there is an extra object in the test data, it's better to just delete
    # # it and note it as wrong for being additional incorrect data.
    # if true_object == "_":
    #   self.__getattribute__(f"{test_object.asname()}_total").wrong += 1
    #   self.error_description[f"part{self.true_part}_onset{self.true_onset}_not_aligned_{self.true_mu21_obj}"] = f"part{self.test_part}_onset{self.test_onset}_{self.test_mu21_obj}"  # noqa
    # else:
    #   for param in self._return_parameter_names(true_object.asname()):
    #     try:
    #       if true_object.__getattribute__(param.split("_")[-1]) == test_object.__getattribute__(param.split("_")[-1]):
    #         self.__getattribute__(param).right += 1
    #       else:
    #         self.__getattribute__(param).wrong += 1
    #         self.error_description[f"part{self.true_part}_onset{self.true_onset}_{param}_{self.true_mu21_obj}"] = f"part{self.test_part}_onset{self.test_onset}_{self.test_mu21_obj}"  # noqa
    #     except AttributeError:
    #       # If the object needs to be created, each parameter needs to be added individually, +1 error each.
    #       self.__getattribute__(param).wrong += 1
    #       self.error_description[f"part{self.true_part}_onset{self.true_onset}_{param}_{self.true_mu21_obj}"] = f"part{self.test_part}_onset{self.test_onset}_{self.test_mu21_obj}"  # noqa

    if isinstance(true_object, NoteObject) and isinstance(test_object, NoteObject):
      self._compare_expand_objects_same(true_object, test_object, "notes")

      for i in true_object.articulation:
        if i in test_object.articulation:
          self.notes_articulation.right += 1
        else:
          self.error_description[f"part{self.true_part}_onset{self.true_onset}_{i}_{self.true_mu21_obj}"] = f"part{self.test_part}_onset{self.test_onset}_{test_object}"  # noqa
          self.notes_articulation.wrong += 1

    elif (isinstance(true_object, NoteObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, NoteObject)):
      self._compare_expand_objects_different(true_object, test_object, "notes")

    elif isinstance(true_object, RestObject) and isinstance(test_object, RestObject):
      self._compare_expand_objects_same(true_object, test_object, "rests")

      for i in true_object.articulation:
        if i in test_object.articulation:
          self.rests_articulation.right += 1
        else:
          self.error_description[f"part{self.true_part}_onset{self.true_onset}_{i}_{self.true_mu21_obj}"] = f"part{self.test_part}_onset{self.test_onset}_{test_object}"  # noqa
          self.rests_articulation.wrong += 1

    elif (isinstance(true_object, RestObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, RestObject)):
      self._compare_expand_objects_different(true_object, test_object, "rests")

    elif isinstance(true_object, TimeSignatureObject) and isinstance(test_object, TimeSignatureObject):
      self._compare_expand_objects_same(true_object, test_object, "timeSignatures")

    elif (isinstance(true_object, TimeSignatureObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, TimeSignatureObject)):
      self._compare_expand_objects_different(true_object, test_object, "timeSignatures")

    elif isinstance(true_object, KeySignatureObject) and isinstance(test_object, KeySignatureObject):
      self._compare_expand_objects_same(true_object, test_object, "keySignatures")

    elif (isinstance(true_object, KeySignatureObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, KeySignatureObject)):
      self._compare_expand_objects_different(true_object, test_object, "keySignatures")

    elif isinstance(true_object, ClefObject) and isinstance(test_object, ClefObject):
      self._compare_expand_objects_same(true_object, test_object, "clefs")

    elif (isinstance(true_object, ClefObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, ClefObject)):
      self._compare_expand_objects_different(true_object, test_object, "clefs")

  def _object_split(self):
    """
    Align Objects together by comparing voice, measure and onset.
    """
    # print(self._return_object_names())
    for obj in self._return_object_names():
      for true_object in self.true_data.__getattribute__(obj):
        for test_object in self.test_data.__getattribute__(obj):
          if true_object == test_object:
            self._compare(true_object, test_object)

  def _total(self):
    """
    Automatically add the number of right/wrong attributes to the total of each
    param (notes, rests).

    This function also checks if there are less errors by fixing the key with
    all the pitches, or most the pitches are correct. But it is not smart,
    it takes a global average of all the instruments together and not based on
    the part.
    """

    try:
      if self.notes_step.wrong > self.notes_name.wrong:
        del self.notes_step
      else:
        del self.notes_name
    except AttributeError:
      self.error_description["Error"] = "Could not remove note_step or note_name"

    for obj in self._return_object_names():
      for params in self._return_parameter_names(obj):
        # Add the detailed results to the list of objects
        self.__getattribute__(obj).append(self.__getattribute__(params))
        self.__getattribute__(f"{obj}_total").right += self.__getattribute__(params).right
        self.__getattribute__(f"{obj}_total").wrong += self.__getattribute__(params).wrong

      self.__getattribute__(obj).append(self.__getattribute__(f"{obj}_total"))

  def _rebuild(self, aligned_data, unaligned_data):
    """
    Rebuild the list of items according to how the AffineNeedlemanWunsch aligned them.
    """
    output = []
    track = 0
    for entry in aligned_data:
      if entry != "_" and entry != " ":
        output.append(unaligned_data[track])
        track += 1
      else:
        output.append("_")

    return output

  def basic_sequence_alignment(self, func):
    """
    This will align all the objects based on the sequence alignment class that
    is inserted as the function argument. The problem is that it uses specific
    parameters of each object to align them. It would be much better to align
    using values for each parameter.

    .. note:: Align each note object with each other. Understandably this is not
      the best, but it serves more as a proof-of-concept or a placeholder to be
      built later.

      - Notes           are aligned by step names

      - Restes          are aligned by measure number as a single char

      - TimeSignatures  are aligned by measure number as a single char

      - KeySignatures   are aligned by measure number as a single char

      - Clefs           are aligned by measure number as a single char

    :param [func]: A class that inherited from the SequenceAlignment class 
      which is defined in the sequence_alignment.py file.
    :type [func]: SequenceAlignment
    """

    # Notes
    true_notes = [item.step for item in self.true_data.notes]
    test_notes = [item.step for item in self.test_data.notes]
    notes_anw = func(true_notes, test_notes)

    true_note_objects = self._rebuild(notes_anw.aligned_true_data, self.true_data.notes)
    test_note_objects = self._rebuild(notes_anw.aligned_test_data, self.test_data.notes)
    for index, objects in enumerate(true_note_objects):
      self._compare(objects, test_note_objects[index])

    # Rests
    true_rests = [return_char_except(item.measure) for item in self.true_data.rests]
    test_rests = [return_char_except(item.measure) for item in self.test_data.rests]
    rests_anw = func(true_rests, test_rests)

    true_rest_objects = self._rebuild(rests_anw.aligned_true_data, self.true_data.rests)
    test_rest_objects = self._rebuild(rests_anw.aligned_test_data, self.test_data.rests)
    for index, objects in enumerate(true_rest_objects):
      self._compare(objects, test_rest_objects[index])

    # Time Signature
    true_timeSignatures = [return_char_except(item.measure) for item in self.true_data.timeSignatures]
    test_timeSignatures = [return_char_except(item.measure) for item in self.test_data.timeSignatures]
    timeSignatures_anw = func(true_timeSignatures, test_timeSignatures)

    true_timeSignature_objects = self._rebuild(timeSignatures_anw.aligned_true_data, self.true_data.timeSignatures)
    test_timeSignature_objects = self._rebuild(timeSignatures_anw.aligned_test_data, self.test_data.timeSignatures)
    for index, objects in enumerate(true_timeSignature_objects):
      self._compare(objects, test_timeSignature_objects[index])

    # Key Signature
    true_keySignatures = [return_char_except(item.measure) for item in self.true_data.keySignatures]
    test_keySignatures = [return_char_except(item.measure) for item in self.test_data.keySignatures]
    keySignatures_anw = func(true_keySignatures, test_keySignatures)

    true_keySignature_objects = self._rebuild(keySignatures_anw.aligned_true_data, self.true_data.keySignatures)
    test_keySignature_objects = self._rebuild(keySignatures_anw.aligned_test_data, self.test_data.keySignatures)
    for index, objects in enumerate(true_keySignature_objects):
      self._compare(objects, test_keySignature_objects[index])

    # Clefs
    true_clefs = [return_char_except(item.measure) for item in self.true_data.clefs]
    test_clefs = [return_char_except(item.measure) for item in self.test_data.clefs]
    clef_anw = func(true_clefs, test_clefs)

    true_clef_objects = self._rebuild(clef_anw.aligned_true_data, self.true_data.clefs)
    test_clef_objects = self._rebuild(clef_anw.aligned_test_data, self.test_data.clefs)
    for index, objects in enumerate(true_clef_objects):
      self._compare(objects, test_clef_objects[index])

  def sequence_alignment(self, func):
    """
    Align each note object with each other based on a scoring method. It
    serves more as a proof-of-concept or a placeholder to be built later.

    .. note:: Align each note object with each other based on the parameters of each.
      These are defined in the scoring_method, for an example look 

    :param [func]: Takes a function to be used in the alignment process
    :type [func]: SequenceAlignment
    """

    # Notes
    true_notes = [item for item in self.true_data.notes]
    test_notes = [item for item in self.test_data.notes]
    notes_anw = func(true_notes, test_notes)

    true_note_objects = self._rebuild(notes_anw.aligned_true_data, self.true_data.notes)
    test_note_objects = self._rebuild(notes_anw.aligned_test_data, self.test_data.notes)
    for index, objects in enumerate(true_note_objects):
      self._compare(objects, test_note_objects[index])

    # Rests
    true_rests = [item.measure for item in self.true_data.rests]
    test_rests = [item.measure for item in self.test_data.rests]
    rests_anw = func(true_rests, test_rests)

    true_rest_objects = self._rebuild(rests_anw.aligned_true_data, self.true_data.rests)
    test_rest_objects = self._rebuild(rests_anw.aligned_test_data, self.test_data.rests)
    for index, objects in enumerate(true_rest_objects):
      self._compare(objects, test_rest_objects[index])

    # Time Signature
    true_timeSignatures = [return_char_except(item.measure) for item in self.true_data.timeSignatures]
    test_timeSignatures = [return_char_except(item.measure) for item in self.test_data.timeSignatures]
    timeSignatures_anw = func(true_timeSignatures, test_timeSignatures)

    true_timeSignature_objects = self._rebuild(timeSignatures_anw.aligned_true_data, self.true_data.timeSignatures)
    test_timeSignature_objects = self._rebuild(timeSignatures_anw.aligned_test_data, self.test_data.timeSignatures)
    for index, objects in enumerate(true_timeSignature_objects):
      self._compare(objects, test_timeSignature_objects[index])

    # Key Signature
    true_keySignatures = [return_char_except(item.measure) for item in self.true_data.keySignatures]
    test_keySignatures = [return_char_except(item.measure) for item in self.test_data.keySignatures]
    keySignatures_anw = func(true_keySignatures, test_keySignatures)

    true_keySignature_objects = self._rebuild(keySignatures_anw.aligned_true_data, self.true_data.keySignatures)
    test_keySignature_objects = self._rebuild(keySignatures_anw.aligned_test_data, self.test_data.keySignatures)
    for index, objects in enumerate(true_keySignature_objects):
      self._compare(objects, test_keySignature_objects[index])

    # Clefs
    true_clefs = [return_char_except(item.measure) for item in self.true_data.clefs]
    test_clefs = [return_char_except(item.measure) for item in self.test_data.clefs]
    clef_anw = func(true_clefs, test_clefs)

    true_clef_objects = self._rebuild(clef_anw.aligned_true_data, self.true_data.clefs)
    test_clef_objects = self._rebuild(clef_anw.aligned_test_data, self.test_data.clefs)
    for index, objects in enumerate(true_clef_objects):
      self._compare(objects, test_clef_objects[index])


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
  m1.append(KeySignature(0))
  m1.append(Note("C4", type="eighth"))
  m2 = Measure(number=2)
  m2.append(KeySignature(1))
  m2.append(Note("G4", type="eighth"))
  p1.append([m1, m2])
  s.append([p1])

  notes = [NoteObject(item, 1) for item in s.recurse().notes if not item.isChord]
  keySignatures = [KeySignatureObject(item, 1) for item in s.recurse().getElementsByClass("KeySignature")]  # noqa

  print(notes)
  notes = add_step_information(notes, keySignatures)
  print(notes)