"""
The properties of these objects are named in a specific way for a reason. Any
property that is not to be evaluated has an underscore in them
(eg: _music21_object). If the property requires more than a word to describe
it, then write it in camelCase style.
"""
import attr


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

	tiestyle = attr.ib(init=False, eq=False)
	@tiestyle.default
	def _get_tie_style(self):
		"""
		"normal" or "dotted" or "dashed" or "hidden"
		"""
		try:
			return self._music21_object.tie.style
		except AttributeError:
			return None

	tietype = attr.ib(init=False, eq=False)
	@tietype.default
	def _get_tie_type(self):
		"""
		"start", "stop", "continue", "let-ring", "continue-let-ring"
		"""
		try:
			return self._music21_object.tie.type
		except AttributeError:
			return None

	tieplacement = attr.ib(init=False, eq=False)
	@tieplacement.default
	def _get_tie_placement(self):
		"""
		None, above, below
		"""
		try:
			return self._music21_object.tie.placement
		except AttributeError:
			return None


@attr.s
class RestObject(MusicalEvent):
	"""
	Same as :func:`mupix.core.MusicalEvent`
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


@attr.s
class SpannerObject(Marking):
	"""
	This is an object that holds information related to musical objects which can span multiple
	measures like crescendos.
	"""
	name = attr.ib(init=False, eq=False)
	@name.default
	def _get_name(self):
		return self._music21_object.type

	# This is empty in Music21, need to repopulate this data.
	measure = attr.ib(init=False)
	@measure.default
	def _get_measure(self):
		return self._music21_object.getFirst().measureNumber

	placement = attr.ib(init=False, eq=False)
	@placement.default
	def _get_placement(self):
		return self._music21_object.placement

	length = attr.ib(init=False, eq=False)
	@length.default
	def _get_length(self):
		return self._music21_object.spread


@attr.s
class DynamicObject(Marking):
	"""
	This is an object that holds information related to dynamics
	"""
	name = attr.ib(init=False, eq=False)
	@name.default
	def _get_name(self):
		return self._music21_object.longName


if __name__ == "__main__":
	"""
	How to create Mupix Objects.
	"""
	from music21.stream import Score, Part, Measure
	from music21.key import KeySignature
	from music21.note import Note  # noqa

	from mupix.extra import add_step_information

	s = Score()

	p1 = Part(id="part1")
	m1 = Measure(number=1)
	m1.append(KeySignature(0))
	m1.append(Note("C4", type="eighth"))
	m2 = Measure(number=2)
	m2.append(KeySignature(1))
	m2.append(Note("G4", type="eighth"))
	p1.append([m1, m2])

	p2 = Part(id="part2")
	m1_ = Measure(number=1)
	m1_.append(KeySignature(0))
	m1_.append(Note("C4", type="eighth"))
	m2_ = Measure(number=2)
	m2_.append(KeySignature(1))
	m2_.append(Note("G4", type="eighth"))
	p2.append([m1_, m2_])

	s.append([p1, p2])

	notes = [NoteObject(item, 1) for item in s.recurse().notes if not item.isChord]
	keySignatures = [KeySignatureObject(item, 1) for item in s.recurse().getElementsByClass("KeySignature")]  # noqa

	print(notes)
	notes = add_step_information(notes, keySignatures)
	print(notes)
