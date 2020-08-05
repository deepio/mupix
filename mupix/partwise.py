# import itertools
import operator
from typing import (
	Union,
	# Callable,
)

import attr
import music21

from mupix.core import (
	NoteObject,
	RestObject,
	TimeSignatureObject,
	KeySignatureObject,
	ClefObject,
	# Marking,
)
from mupix.extra import (
	add_step_information,
	normalize_object_list,
)
from mupix.typewise import (
	BaseCompareClass,
	MupixObject
)


@attr.s
class MupixPartwiseObject():
	parts = attr.ib(
		kw_only=True,
		type=dict,
		# type=list,
		# validator=attr.validators.deep_iterable(
		# 	member_validator=attr.validators.instance_of(list),
		# 	iterable_validator=attr.validators.instance_of(list),
		# )

		# validator=attr.validators.deep_iterable(
		# 	member_validator=attr.validators.deep_iterable(
		# 		member_validator=Marking,
		# 		iterable_validator=attr.validators.instance_of(list)
		# 	),
		# 	iterable_validator=attr.validators.instance_of(list)
		# ),
	)
	visualize = attr.ib(kw_only=True)

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
		_keySignatures = []
		# Creates lists of lists notes[part][index]
		file_ = music21.converter.parseFile(filepath, forceSource=True)
		for parts_index, parts in enumerate(file_.recurse().getElementsByClass("Part"), 1):  # noqa
			notes.append([NoteObject(item, parts_index) for item in parts.recurse().notes if not item.isChord])
			rests.append([RestObject(item, parts_index) for item in parts.recurse().notesAndRests if not item.isNote])
			timeSignatures.append([TimeSignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("TimeSignature")])  # noqa
			keySignatures.append([KeySignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")])  # noqa
			clefs.append([ClefObject(item, parts_index) for item in parts.recurse().getElementsByClass("Clef")])

		########################################################
		# Expand keys
			_keySignatures.append([KeySignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")])  # noqa

		try:
			# This is fine because both rests and notes have a .measure property
			measuresInScore = max(notes[0] + rests[0], key=operator.attrgetter('measure')).measure
		except ValueError:
			measuresInScore = 0
			parts_index = 0

		# Make sure the correct key and measure information is in every measure.
		# Sometimes
		for part in range(parts_index):
			# timeSignatures[part] = normalize_object_list(
			# 	object_list=timeSignatures[part],
			# 	total_measures=measuresInScore,
			# 	total_parts=parts_index
			# )
			_keySignatures[part] = normalize_object_list(
				object_list=_keySignatures[part],
				total_measures=measuresInScore,
				total_parts=parts_index
			)
			# clefs[part] = normalize_object_list(
			# 	object_list=clefs[part],
			# 	total_measures=measuresInScore,
			# 	total_parts=parts_index
			# )

		# Make sure the key signature information is in the note objects
		for part in range(parts_index):
			# only once keySignatures are normalized can we add the step information.
			notes[part] = add_step_information(notes[part], _keySignatures[part])

		# Finally sort all elements in the correct musical stream
		# out = []
		# for part in range(parts_index):
		# 	# Get notes and rests together first
		# 	notes_and_rests = sorted(
		# 		itertools.chain(notes[part], rests[part]),
		# 		key=operator.attrgetter("measure", "onset")
		# 	)
		# 	# Make sure clefs, time sigs, and key sigs come first.
		# 	out.append(
		# 		sorted(
		# 			itertools.chain(
		# 				clefs[part],
		# 				timeSignatures[part],
		# 				keySignatures[part],
		# 				notes_and_rests,
		# 			),
		# 			key=operator.attrgetter("measure", "onset")
		# 		)
		# 	)
		# return cls(parts=out)
		from mupix.typewise import MupixObject
		from mupix.extra import get_software_vendor
		software_vendor = get_software_vendor(filepath)

		# spanners = [item for item in spanners[i]],
		# dynamics = [item for item in dynamics[i]],
		mupix_data = {i: MupixObject(
				notes = [item for item in notes[i]],
				rests = [item for item in rests[i]],
				timeSignatures = [item for item in timeSignatures[i]],
				keySignatures = [item for item in keySignatures[i]],
				clefs = [item for item in clefs[i]],
				spanners = [],
				dynamics = [],
				parts = 1,
				error_description = {},
				visualize = {},
				software_vendor = software_vendor,
			) for i in range(parts_index)
		}
		return cls(parts=mupix_data, visualize=file_)


class PartiwiseCompareClass(BaseCompareClass):
	"""
	Will iterate through each part of each score and align each part with the sequence alignment algorithm.
	"""
	def __init__(self, true_filepath: Union[str, MupixObject], test_filepath: Union[str, MupixObject], do_not_count: list = []):

		if isinstance(true_filepath, str):
			self.true_filepath = MupixPartwiseObject.from_filepath(true_filepath)
			self.test_filepath = MupixPartwiseObject.from_filepath(test_filepath)

		super().__init__(self.true_filepath, self.test_filepath, do_not_count)

	def sequence_alignment(self, func):
		# print(self.test_data)
		# raise Exception("\n")
		# raise Exception(self.dynamics_onset)
		test_length = len(self.test_data.parts)
		true_length = len(self.true_data.parts)

		if true_length != test_length:
			print(
				"[-] WARNING: Both files do not have an equal number of parts. \n"
				"\tThis may lead to additional inflated errors.\n"
				"\tYou have been warned. \n"
				f"\n\tGround Truth: {true_length} Test File: {test_length}"
			)

		from mupix.application import WeightedNeedlemanWunsch
		matrix = {}
		already_found_keys = []
		self.compiled_list = {}

		for true_parts in reversed(range(true_length)):
			matrix[true_parts] = {}
			smallest = 1_000_000
			smallest_group = None

			for test_parts in reversed(range(test_length)):
				if len(already_found_keys) == test_length:
					# need to compare against Null objects instead.
					continue

				aligned_part = WeightedNeedlemanWunsch(self.true_data.parts[true_parts], self.test_data.parts[test_parts], )

				errors = sum([len(x) for x in aligned_part.error_description])
				matrix[true_parts][test_parts] = errors

				if errors < smallest and test_parts not in already_found_keys:
					smallest = errors
					smallest_group = aligned_part

			self.compiled_list[true_parts] = smallest_group
			already_found_keys.append(test_parts)

	def _total(self, ):
		"""
		"""
		try:
			self.compiled_list
		except NameError:
			raise Exception(
				"[-] A partwise list has not been created yet.\n"
				"\tCreate one by running the sequence alignment method."
			)

		objects = self._return_object_names()

		# Create Result objects
		for object_ in objects:
			for parameter in self._return_parameter_names(object_):
				self.__getattribute__(object_).append(self.__getattribute__(parameter))
			self.__getattribute__(object_).append(self.__getattribute__(f"{object_}_total"))

		# Items common to both the ground truth and test sheets
		for i, item in self.compiled_list.items():
			# For each object (notes, rests, clefs, spanners, time sigs, keys)
			for object_ in objects:

				# Get Individual Parameters
				for parameter in self._return_parameter_names(object_):
					try:
						self.__getattribute__(parameter).right += item.__getattribute__(parameter).right
						self.__getattribute__(parameter).wrong += item.__getattribute__(parameter).wrong
					except AttributeError:
						# All none types are from unaligned objects. These must be counted as errors.
						self.__getattribute__(parameter).wrong += 1

				# Get Totals
				try:
					self.__getattribute__(f"{object_}_total").right += item.__getattribute__(f"{object_}_total").right
					self.__getattribute__(f"{object_}_total").wrong += item.__getattribute__(f"{object_}_total").wrong
				except AttributeError:
					# All none types are from unaligned objects. These must be counted as errors.
					self.__getattribute__(f"{object_}_total").wrong += 1

		# Add the visualize file after the alignment
		# TODO: Color all properties as they are found. {Working somewhat}
		# TODO: Test what is shown to work and what isn't.
		self.visualize = self.test_data.visualize

		# import sys
		# sys.exit(0)
