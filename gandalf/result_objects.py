import attr


@attr.s
class Result:
  right = attr.ib(init=False, type=int, default=0)
  wrong = attr.ib(init=False, type=int, default=0)

  name = attr.ib(type=str)
  @name.default
  def _get_name(self):
    return str(self.__class__.__name__)

  def asdict(self):
    return attr.asdict(self)


@attr.s
class NotePitchResult(Result):
  pass


@attr.s
class NoteDurationResult(Result):
  pass


@attr.s
class NoteOctaveResult(Result):
  pass


@attr.s
class NoteAccidentalResult(Result):
  pass


@attr.s
class NoteStemDirectionResult(Result):
  pass


@attr.s
class NoteBeamResult(Result):
  pass


@attr.s
class NoteTotalResult(Result):
  pass


@attr.s
class RestAccidentalResult(Result):
  pass


@attr.s
class RestDurationResult(Result):
  pass


@attr.s
class RestTotalResult(Result):
  pass


@attr.s
class TimeSignatureNumeratorResult(Result):
  pass


@attr.s
class TimeSignatureDenominatorResult(Result):
  pass


@attr.s
class TimeSignatureTotalResult(Result):
  pass


@attr.s
class KeySignatureStepResult(Result):
  pass


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
