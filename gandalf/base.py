import attr


@attr.s
class GandalfObject():
  notes = attr.ib(kw_only=True,)
  rests = attr.ib(kw_only=True,)
  time_signatures = attr.ib(kw_only=True,)
  key_signatures = attr.ib(kw_only=True,)
  clefs = attr.ib(kw_only=True,)

  @notes.validator
  @rests.validator
  @time_signatures.validator
  @key_signatures.validator
  @clefs.validator
  def check(self, attribute, value):
    if not isinstance(value, list) and not isinstance(value, Result):
      raise ValueError(f"Must be a list or Results Object. {type(value)}")

  def ret(self):
    return self.notes, self.rests, self.time_signatures, self.key_signatures, self.clefs


@attr.s
class Marking:
  _music21_object = attr.ib(cmp=False)
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


@attr.s
class MusicalEvent(Marking):
  duration = attr.ib(init=False, type=str, cmp=False)
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

  articulation = attr.ib(init=False, cmp=False)
  @articulation.default
  def _get_articulation(self):
    return [item.name for item in self._music21_object.articulations]


@attr.s
class NoteObject(MusicalEvent):
  pitch = attr.ib(init=False, cmp=False)
  @pitch.default
  def _get_pitch(self):
    return self._music21_object.step

  octave = attr.ib(init=False, cmp=False)
  @octave.default
  def _get_octave(self):
    return self._music21_object.octave

  accidental = attr.ib(init=False, type=str, cmp=False)
  @accidental.default
  def _get_accidental(self):
    note = self._music21_object
    if len(note.name) > 1:
      return note.name[1:]
    else:
      return ""

  stemdirection = attr.ib(init=False, cmp=False)
  @stemdirection.default
  def _get_stem_direction(self):
    return self._music21_object.stemDirection

  beam = attr.ib(init=False, cmp=False)
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
class TimeSignature(Marking):
  numerator = attr.ib(init=False, cmp=False)
  @numerator.default
  def _get_numerator(self):
    return self._music21_object._getNumerator()

  denominator = attr.ib(init=False, cmp=False)
  @denominator.default
  def _get_denominator(self):
    return self._music21_object._getDenominator()


@attr.s
class KeySignature(Marking):
  step = attr.ib(init=False, cmp=False)
  @step.default
  def _get_step(self):
    return self._music21_object.asKey().name.split(" ")[0]

  mode = attr.ib(init=False, cmp=False)
  @mode.default
  def _get_mode(self):
    return self._music21_object.asKey().name.split(" ")[1]


@attr.s
class Clef(Marking):
  name = attr.ib(init=False, cmp=False)
  @name.default
  def _get_name(self):
    return self._music21_object.sign

  line = attr.ib(init=False, cmp=False)
  @line.default
  def _get_line(self):
    return self._music21_object.line

  octave = attr.ib(init=False, cmp=False)
  @octave.default
  def _get_octave(self):
    return self._music21_object.octaveChange


@attr.s
class Result:
  right = attr.ib(type=int, default=0)
  wrong = attr.ib(type=int, default=0)
