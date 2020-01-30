import attr


@attr.s
class Result:
  """
  Base results object that holds the number of right and wrong notes.

  Arg
    right (int): The number of correct Mupix Object Elements
    wrong (int): The number of wrong Mupix Object Elements
    name (str): The name this results object
  """
  right = attr.ib(init=False, type=int, default=0)
  wrong = attr.ib(init=False, type=int, default=0)

  name = attr.ib(type=str)
  @name.default
  def _get_name(self):
    """
    Get the name of this Results object, even when it's inherited so its still available
    when calling an attrs as a dictionary.
    """
    return str(self.__class__.__name__)

  def asdict(self):
    """
    This is a just a method to unify. I'd rather have a method to turn a class object
    into a dictionary, instead of how attrs works like this.
    """
    return attr.asdict(self)


@attr.s
class NoteStepResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Pitches.
  """


@attr.s
class NoteDurationResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Durations.
  """


@attr.s
class NoteOctaveResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Octaves.
  """


@attr.s
class NoteAccidentalResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Accidentals
  """


@attr.s
class NoteArticulationResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Articulations
  """


@attr.s
class NoteStemDirectionResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Stem Directions
  """


@attr.s
class NoteBeamResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Beams
  """


@attr.s
class NoteVoiceResult(Result):
  """
  Results Object that holds the number of correct and incorrect Note Voices
  """


@attr.s
class NoteTotalResult(Result):
  """
  The accumulated total of all the Note related Results Objects
  """


@attr.s
class RestAccidentalResult(Result):
  """
  It sounds weird, but rests are note objects in musicxml. In the event one is added erroneously,
  we should count it.
  """


@attr.s
class RestArticulationResult(Result):
  """
  Articulations can not exist by themselves in an empty measure. They must be attached to a note
  or a rest.
  """


@attr.s
class RestDurationResult(Result):
  """
  Results Object that holds the number of correct and incorrect Rest Durations
  """


@attr.s
class RestVoiceResult(Result):
  """
  Results Object that holds the number of correct and incorrect Rest Voices
  """


@attr.s
class RestTotalResult(Result):
  """
  The accumulated total of all the Rest related Results Objects
  """


@attr.s
class TimeSignatureNumeratorResult(Result):
  """
  Results Object that holds the number of correct and incorrect Time Signature Numerator values
  """


@attr.s
class TimeSignatureDenominatorResult(Result):
  """
  Results Object that holds the number of correct and incorrect Time Signature Denominator values
  """


@attr.s
class TimeSignatureTotalResult(Result):
  """
  The accumulated total of all the Time Signature related Results Objects
  """


@attr.s
class KeySignatureStepResult(Result):
  """
  """


@attr.s
class KeySignatureModeResult(Result):
  pass


@attr.s
class KeySignatureTotalResult(Result):
  pass


@attr.s
class ClefNameResult(Result):
  pass


@attr.s
class ClefLineResult(Result):
  pass


@attr.s
class ClefOctaveResult(Result):
  pass


@attr.s
class ClefTotalResult(Result):
  pass
