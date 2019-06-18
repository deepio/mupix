import attr


@attr.s
class Marking:
  music21_object = attr.ib()


@attr.s
class MusicalEvent(Marking):
  duration = attr.ib(init=False, type=int)
  @duration.default
  def _get_duration(self):
    return self.music21_object.quarterLength

  voice = attr.ib(init=False, type=int)
  @voice.default
  def _get_voice(self):
    if isinstance(self.music21_object.activeSite.id, int):
      return 1
    else:
      return int(self.music21_object.activeSite.id)

  onset = attr.ib(init=False,)
  @onset.default
  def _get_onset(self):
    return self.music21_object.offset

  articulation = attr.ib(init=False)
  @articulation.default
  def _get_articulation(self):
    return self.music21_object.articulations


@attr.s
class NoteObject(MusicalEvent):
  pitch = attr.ib(init=False)
  @pitch.default
  def _get_pitch(self):
    return self.music21_object.step

  octave = attr.ib(init=False)
  @octave.default
  def _get_octave(self):
    return self.music21_object.octave

  accidental = attr.ib(init=False, type=str)
  @accidental.default
  def _get_accidental(self):
    note = self.music21_object
    if len(note.name) > 1:
      return note.name[1:]
    else:
      return ""

  stem_direction = attr.ib(init=False)
  @stem_direction.default
  def _get_stem_direction(self):
    return self.music21_object.stemDirection

  beam = attr.ib(init=False)
  @beam.default
  def _get_beam(self):
    note = self.music21_object
    note.beams.getTypes()
    return [item for item in note.beams.getTypes()]


@attr.s
class RestObject(MusicalEvent):
  pass


@attr.s
class TimeSignature(Marking):
  numerator = attr.ib(init=False)
  @numerator.default
  def _get_numerator(self):
    return self.music21_object._getNumerator()

  denominator = attr.ib(init=False)
  @denominator.default
  def _get_denominator(self):
    return self.music21_object._getDenominator()


@attr.s
class KeySignature(Marking):
  step = attr.ib(init=False)
  @step.default
  def _get_step(self):
    return self.music21_object.asKey().name.split(" ")[0]

  mode = attr.ib(init=False)
  @mode.default
  def _get_mode(self):
    return self.music21_object.asKey().name.split(" ")[1]


@attr.s
class Result:
  right = attr.ib(type=int, default=0)
  wrong = attr.ib(type=int, default=0)
