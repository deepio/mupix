import itertools
import operator

import attr
import music21

from mupix.core import (
	NoteObject,
	RestObject,
	TimeSignatureObject,
	KeySignatureObject,
	ClefObject,
	Marking,
)
from mupix.extra import (
	add_step_information,
	normalize_object_list,
)
from mupix.typewise import BaseCompareClass


@attr.s
class MupixPartwiseObject():
	parts = attr.ib(
		kw_only=True,
		type=list,
		validator=attr.validators.deep_iterable(
			member_validator=attr.validators.instance_of(list),
			iterable_validator=attr.validators.instance_of(list),
		)

		# validator=attr.validators.deep_iterable(
		# 	member_validator=attr.validators.deep_iterable(
		# 		member_validator=Marking,
		# 		iterable_validator=attr.validators.instance_of(list)
		# 	),
		# 	iterable_validator=attr.validators.instance_of(list)
		# ),
	)

	def __iter__(self):
		return iter(self.parts)

	@classmethod
	def from_filepath(cls, filepath):
		"""

		Music notation software will sometimes repeat time signature, key signature
		or clef information arbitrarily. To combat this, we repeat the key, time
		and clef information in all measures because it always acts on the
		information inside of the measure anyway.

		Sometimes key signature information gets deleted in music21 objects, to
		combat this we force the key signature to be reintroduced to specify a note
		step.
		"""

		notes, rests, timeSignatures, keySignatures, clefs = [], [], [], [], []
		# Creates lists of lists notes[part][index]
		for parts_index, parts in enumerate(music21.converter.parseFile(filepath).recurse().getElementsByClass("Part"), 1):  # noqa
			notes.append([NoteObject(item, parts_index) for item in parts.recurse().notes if not item.isChord])
			rests.append([RestObject(item, parts_index) for item in parts.recurse().notesAndRests if not item.isNote])
			timeSignatures.append([TimeSignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("TimeSignature")])  # noqa
			keySignatures.append([KeySignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")])  # noqa
			clefs.append([ClefObject(item, parts_index) for item in parts.recurse().getElementsByClass("Clef")])

		try:
			measuresInScore = max(notes[0] + rests[0], key=operator.attrgetter('measure')).measure
		except ValueError:
			measuresInScore = 0
			parts_index = 0

		# Make sure the correct key and measure information is in every measure.
		# Sometimes
		for part in range(parts_index):
			timeSignatures[part] = normalize_object_list(
				object_list=timeSignatures[part],
				total_measures=measuresInScore,
				total_parts=parts_index
			)
			keySignatures[part] = normalize_object_list(
				object_list=keySignatures[part],
				total_measures=measuresInScore,
				total_parts=parts_index
			)
			clefs[part] = normalize_object_list(
				object_list=clefs[part],
				total_measures=measuresInScore,
				total_parts=parts_index
			)

		# Make sure the key signature information is in the note objects
		for part in range(parts_index):
			# only once keySignatures are normalized can we add the step information.
			notes[part] = add_step_information(notes[part], keySignatures[part])

		# Finally sort all elements in the correct musical stream
		out = []
		for part in range(parts_index):
			# Get notes and rests together first
			notes_and_rests = sorted(
				itertools.chain(notes[part], rests[part]),
				key=operator.attrgetter("measure", "onset")
			)
			# Make sure clefs, time sigs, and key sigs come first.
			out.append(
				sorted(
					itertools.chain(
						clefs[part],
						timeSignatures[part],
						keySignatures[part],
						notes_and_rests,
					),
					key=operator.attrgetter("measure", "onset")
				)
			)
		return cls(parts=out)


class PartiwiseCompareClass(BaseCompareClass):
	"""
	"""
	def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
		self.true_data = MupixPartwiseObject.from_filepath(true_filepath)
		self.test_data = MupixPartwiseObject.from_filepath(test_filepath)

	def sequence_alignment(self, func):

		for part in self.true_data:
			true_part = part
			break
		for part in self.test_data:
			test_part = part
			break

		# print(true_part)
		a = func(true_part, test_part)
		print(a)
		import sys
		sys.exit(0)
