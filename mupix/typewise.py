"""
//FIXME: Move from RE to lxml library only when the following three conditions are met
	//TODO: Get all major commercial music notation software (Missing one)
	//TODO: Create testing sheets using all notation software
	//TODO: Create an automated method for testing multiple versions of Notation software (Almost done)
"""

import re
import operator

import attr
import music21

from mupix.core import (
	NoteObject,
	RestObject,
	TimeSignatureObject,
	KeySignatureObject,
	ClefObject,
	SpannerObject,
	DynamicObject,
)
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
	NoteTieStyle,
	NoteTieType,
	NoteTiePlacement,
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
	KeySignatureOnsetResult,
	KeySignatureTotalResult,
	ClefNameResult,
	ClefLineResult,
	ClefOctaveResult,
	ClefOnsetResult,
	ClefTotalResult,
	SpannerNameResult,
	SpannerPlacementResult,
	SpannerLengthResult,
	SpannerTotalResult,
	DynamicOnsetResult,
	DynamicNameResult,
	DynamicTotalResult,
)
from mupix.extra import (
	add_step_information,
	normalize_object_list,
	return_char_except,
	boundary_search,
)


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
	spanners = attr.ib(kw_only=True,)
	dynamics = attr.ib(kw_only=True,)
	parts = attr.ib(kw_only=True, type=int, validator=[attr.validators.instance_of(int)])
	error_description = attr.ib(kw_only=True, type=dict, validator=[attr.validators.instance_of(dict)])
	software_vendor = attr.ib(kw_only=True, type=list, default=[], validator=[attr.validators.instance_of(list)])

	@notes.validator
	@rests.validator
	@timeSignatures.validator
	@keySignatures.validator
	@clefs.validator
	@spanners.validator
	@dynamics.validator
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
		# return self.notes, self.rests, self.timeSignatures, self.keySignatures, self.clefs, self.error_description
		return self.notes, self.rests, self.timeSignatures, self.keySignatures, self.clefs, self.spanners, self.dynamics, self.error_description

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

		with open(filepath, "r") as f:
			data = f.read()

		software_vendor = re.finditer(r"(?<=<software>).+(?=<\/software>)", data).__next__().group().split(" ")

		notes, rests, timeSignatures, keySignatures, clefs, spanners, dynamics = [], [], [], [], [], [], []
		_keySignatures = []
		# _clefs = []
		for parts_index, parts in enumerate(music21.converter.parseFile(filepath, forceSource=True).recurse().getElementsByClass("Part"), 1):  # noqa
			notes += [NoteObject(item, parts_index) for item in parts.recurse().notes if not item.isChord]
			rests += [RestObject(item, parts_index) for item in parts.recurse().notesAndRests if not item.isNote]
			timeSignatures += [TimeSignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("TimeSignature")]  # noqa
			keySignatures += [KeySignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")]  # noqa
			clefs += [ClefObject(item, parts_index) for item in parts.recurse().getElementsByClass("Clef")]
			dynamics += [DynamicObject(item, parts_index) for item in parts.recurse().getElementsByClass("Dynamic")]

			for measure in parts.recurse().getElementsByClass("Measure"):
				spanners += [SpannerObject(item, parts_index) for item in measure.activeSite.spanners]

		########################################################
		# Expand keys
		#
		# Because even with activeState, note objects can't find 
		# the key for some reason?
			_keySignatures += [KeySignatureObject(item, parts_index) for item in parts.recurse().getElementsByClass("KeySignature")]  # noqa
			# _clefs += [ClefObject(item, parts_index) for item in parts.recurse().getElementsByClass("Clef")]

		try:
			measuresInScore = max(notes + rests, key=operator.attrgetter('measure')).measure
		except ValueError:
			measuresInScore = 0
			parts_index = 0

		_keySignatures = normalize_object_list(object_list=_keySignatures, total_measures=measuresInScore, total_parts=parts_index)
		# _clefs = normalize_object_list(object_list=_clefs, total_measures=measuresInScore, total_parts=parts_index)

		# only once _keySignatures are normalized can we add the step information.
		notes = add_step_information(notes, _keySignatures)
		########################################################

		return cls(
			notes=notes,
			rests=rests,
			timeSignatures=timeSignatures,
			keySignatures=keySignatures,
			clefs=clefs,
			parts=parts_index,
			spanners=spanners,
			dynamics=dynamics,
			error_description={},
			software_vendor=software_vendor,
		)


class BaseCompareClass(MupixObject):
	"""
	The base comparison class for Mupix Objects.
	"""
	def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
		# for result_to_exclude in do_not_count:
		#   del self.__getattribute__(result_to_exclude)

		# Notes
		self.notes = []
		self.notes_step = NoteStepResult()
		self.notes_name = NoteNameResult()
		self.notes_duration = NoteDurationResult()
		self.notes_octave = NoteOctaveResult()
		self.notes_accidental = NoteAccidentalResult()
		self.notes_articulation = NoteArticulationResult()
		self.notes_stemdirection = NoteStemDirectionResult()
		self.notes_beam = NoteBeamResult()
		self.notes_voice = NoteVoiceResult()
		self.notes_tiestyle = NoteTieStyle()
		self.notes_tietype = NoteTieType()
		self.notes_tieplacement = NoteTiePlacement()
		self.notes_total = NoteTotalResult()

		# Rests
		self.rests = []
		self.rests_articulation = RestArticulationResult()
		self.rests_duration = RestDurationResult()
		self.rests_voice = RestVoiceResult()
		self.rests_total = RestTotalResult()

		# Time Signatures
		self.timeSignatures = []
		self.timeSignatures_numerator = TimeSignatureNumeratorResult()
		self.timeSignatures_denominator = TimeSignatureDenominatorResult()
		self.timeSignatures_total = TimeSignatureTotalResult()

		# Key Signatures
		self.keySignatures = []
		self.keySignatures_step = KeySignatureStepResult()
		self.keySignatures_mode = KeySignatureModeResult()
		self.keySignatures_onset = KeySignatureOnsetResult()
		self.keySignatures_total = KeySignatureTotalResult()

		# Clefs
		self.clefs = []
		self.clefs_name = ClefNameResult()
		self.clefs_line = ClefLineResult()
		self.clefs_octave = ClefOctaveResult()
		self.clefs_onset = ClefOnsetResult()
		self.clefs_total = ClefTotalResult()

		# Spanners
		self.spanners = []
		self.spanners_name = SpannerNameResult()
		self.spanners_placement = SpannerPlacementResult()
		self.spanners_length = SpannerLengthResult()
		self.spanners_total = SpannerTotalResult()

		# Dynamics
		self.dynamics = []
		self.dynamics_onset = DynamicOnsetResult()
		self.dynamics_name = DynamicNameResult()
		self.dynamics_total = DynamicTotalResult()


		self.error_description = {}

		# Parse both files
		self.true_data = MupixObject.from_filepath(true_filepath)
		self.test_data = MupixObject.from_filepath(test_filepath)

	def _return_object_names(self):
		"""
		Returns all the objects

		For example:
			['clefs', 'keySignatures', 'notes', 'rests', 'timeSignatures', 'spanners']
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
		"""
		Compare the properties of two same objects for any property that may be incorrect.
		"""
		for result_parameter in self._return_parameter_names(object_):
			property_ = result_parameter.split("_")[-1]
			try:
				if true_object.__getattribute__(property_) == test_object.__getattribute__(property_):
					self.__getattribute__(result_parameter).right += 1
				else:
					out = (
						f"{true_object.part}-{true_object.measure}-{true_object.onset}=>{test_object.part}-"
						f"{test_object.measure}-{test_object.onset}__{true_object.__getattribute__(property_)}"
						f"_{test_object.__getattribute__(property_)}"
					)
					try:
						self.error_description[result_parameter].append(out)
					except KeyError:
						self.error_description[result_parameter] = [out]
					self.__getattribute__(result_parameter).wrong += 1
			except AttributeError:
				raise Exception(type(true_object), type(test_object), "What happened here???")

	def _compare_expand_objects_different(self, true_object, test_object, object_):
		for parameter in self._return_parameter_names(object_):

			if isinstance(test_object, str):
				out = (
					f"{true_object.part}-{true_object.measure}-{true_object.onset}=>"
					"skip adjustment"
				)
			elif isinstance(true_object, str):
				out = (
					f"skip adjustment=>{test_object.part}"
					f"-{test_object.measure}-{test_object.onset}__{parameter}"
				)
			else:
				out = (
					f"{true_object.part}-{true_object.measure}-{true_object.onset}=>{test_object.part}"
					f"-{test_object.measure}-{test_object.onset}__{parameter}"
				)
			try:
				self.error_description[parameter].append(out)
			except KeyError:
				self.error_description[parameter] = [out]

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
					out = (
						f"{true_object.part}-{true_object.measure}-{true_object.onset}=>{test_object.part}"
						f"-{test_object.measure}-{test_object.onset}"
					)
					try:
						self.error_description["note_articulation"].append(out)
					except KeyError:
						self.error_description["note_articulation"] = [out]
					self.notes_articulation.wrong += 1

		elif (isinstance(true_object, NoteObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, NoteObject)):
			self._compare_expand_objects_different(true_object, test_object, "notes")

		elif isinstance(true_object, RestObject) and isinstance(test_object, RestObject):
			self._compare_expand_objects_same(true_object, test_object, "rests")

			for i in true_object.articulation:
				if i in test_object.articulation:
					self.rests_articulation.right += 1
				else:
					out = (
						f"{true_object.part}-{true_object.measure}-{true_object.onset}=>{test_object.part}-"
						f"{test_object.measure}-{test_object.onset}"
					)
					try:
						self.error_description["rest_articulation"].append(out)
					except KeyError:
						self.error_description["rest_articulation"] = [out]
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

		elif isinstance(true_object, SpannerObject) and isinstance(test_object, SpannerObject):
			self._compare_expand_objects_same(true_object, test_object, "spanners")

		elif (isinstance(true_object, SpannerObject) and isinstance(test_object, str)) or (isinstance(true_object, str) and isinstance(test_object, SpannerObject)):
			self._compare_expand_objects_different(true_object, test_object, "spanners")

	def _object_split(self):
		"""
		Align Objects together by comparing voice, measure and onset.
		"""
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

			- Spanners 				are aligned by spanner names

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

		# Spanners
		true_spanners = [item.name for item in self.true_data.spanners]
		test_spanners = [item.name for item in self.test_data.spanners]
		spanner_anw = func(true_spanners, test_spanners)

		true_spanner_objects = self._rebuild(spanner_anw.aligned_true_data, self.true_data.spanners)
		test_spanner_objects = self._rebuild(spanner_anw.aligned_test_data, self.true_data.spanners)
		for index, objects in enumerate(true_spanner_objects):
			self._compare(objects, test_spanner_objects[index])

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
		true_rests = [item for item in self.true_data.rests]
		test_rests = [item for item in self.test_data.rests]
		rests_anw = func(true_rests, test_rests)

		true_rest_objects = self._rebuild(rests_anw.aligned_true_data, self.true_data.rests)
		test_rest_objects = self._rebuild(rests_anw.aligned_test_data, self.test_data.rests)
		for index, objects in enumerate(true_rest_objects):
			self._compare(objects, test_rest_objects[index])

		# Time Signature
		true_timeSignatures = [item for item in self.true_data.timeSignatures]
		test_timeSignatures = [item for item in self.test_data.timeSignatures]
		timeSignatures_anw = func(true_timeSignatures, test_timeSignatures)

		true_timeSignature_objects = self._rebuild(timeSignatures_anw.aligned_true_data, self.true_data.timeSignatures)
		test_timeSignature_objects = self._rebuild(timeSignatures_anw.aligned_test_data, self.test_data.timeSignatures)
		for index, objects in enumerate(true_timeSignature_objects):
			self._compare(objects, test_timeSignature_objects[index])

		# Key Signature
		true_keySignatures = [item for item in self.true_data.keySignatures]
		test_keySignatures = [item for item in self.test_data.keySignatures]
		keySignatures_anw = func(true_keySignatures, test_keySignatures)

		true_keySignature_objects = self._rebuild(keySignatures_anw.aligned_true_data, self.true_data.keySignatures)
		test_keySignature_objects = self._rebuild(keySignatures_anw.aligned_test_data, self.test_data.keySignatures)
		for index, objects in enumerate(true_keySignature_objects):
			self._compare(objects, test_keySignature_objects[index])

		# Clefs
		true_clefs = [item for item in self.true_data.clefs]
		test_clefs = [item for item in self.test_data.clefs]
		clef_anw = func(true_clefs, test_clefs)

		true_clef_objects = self._rebuild(clef_anw.aligned_true_data, self.true_data.clefs)
		test_clef_objects = self._rebuild(clef_anw.aligned_test_data, self.test_data.clefs)
		for index, objects in enumerate(true_clef_objects):
			self._compare(objects, test_clef_objects[index])
