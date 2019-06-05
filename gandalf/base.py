import attr


@attr.s
class MusicalEvent:
  duration = attr.ib(type=int)


@attr.s
class NoteObject(MusicalEvent):
  pitch = attr.ib(type=str)
  octave = attr.ib(type=int)
  accidental = attr.ib(
    type=str,
    validator=attr.validators.in_(["-", "--", "#", "##", ""])
  )
  stem_direction = attr.ib(
    type=str,
    validator=attr.validators.in_(["up", "down", "noStem"])
  )


@attr.s
class RestObject(MusicalEvent):
  voice = attr.ib(type=list)


@attr.s
class TimeSignature:
  numerator = attr.ib(type=int)
  denominator = attr.ib(type=int)


@attr.s
class KeySignature:
  step = attr.ib(type=str)
  scale = attr.ib(type=str)


@attr.s
class Result:
  right = attr.ib(type=int, default=0)
  wrong = attr.ib(type=int, default=0)
