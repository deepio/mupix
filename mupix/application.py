# -*- coding: utf-8 -*-
"""
This project wraps around `Music21` and `lxml` to make certain tasks easier and
provide code for lining up and evaluating multiple symbolic music-files. I
do not agree with certain design decisions `Music21` has taken regarding the
handling of the MusicXML format. Issues which become observable to me when
examining the output of multiple music engraving software.

*************
Documentation
*************
"""

from io import BytesIO

from lxml import etree

from mupix.extra import __return_root_path
from mupix.sequence_alignment import (
	AffineNeedlemanWunsch,
	AdvancedAffineNeedlemanWunsch
)
from mupix.typewise import BaseCompareClass
from mupix.partwise import PartiwiseCompareClass


class BasicCompare(BaseCompareClass):
	"""
	Using 1-to-1 comparisons based on the index of each element.
	Obviously not ideal, but can be an interesting comparison.
	"""
	def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
		super().__init__(true_filepath, test_filepath, do_not_count)
		self._object_split()
		self._total()


class SimpleNeedlemanWunsch(BaseCompareClass):
	"""
	This version aligns notes based on the note names, and the measures + offsets
	of other elements.

	.. note:: Align each note object with each other. Understandably this is not
		the best, but it serves more as a proof-of-concept or a placeholder to be
		built later.

		- Notes           are aligned by step names

		- Restes          are aligned by measure number as a single char

		- TimeSignatures  are aligned by measure number as a single char

		- KeySignatures   are aligned by measure number as a single char

		- Clefs           are aligned by measure number as a single char
	"""
	def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
		super().__init__(true_filepath, test_filepath, do_not_count)
		self.basic_sequence_alignment(func=AffineNeedlemanWunsch)
		self._total()


class WeightedNeedlemanWunsch(BaseCompareClass):
	"""
	Using a weighted version of Affine Needleman-Wunsch, the way it should be
	used.
	"""
	def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
		super().__init__(true_filepath, test_filepath, do_not_count)
		self.sequence_alignment(func=AdvancedAffineNeedlemanWunsch)
		self._total()


class PartwiseWeightedNeedlemanWunsch(PartiwiseCompareClass):
	"""
	"""
	def __init__(self, true_filepath: str, test_filepath: str, do_not_count: list = []):
		super().__init__(true_filepath, test_filepath, do_not_count)
		self.sequence_alignment(func=AdvancedAffineNeedlemanWunsch)

	# 	# Parse both files
	# 	self.true_data = MupixObject.partwise_from_filepath(true_filepath)
	# 	self.test_data = MupixObject.partwise_from_filepath(test_filepath)
	# 	self.partwise_sequence_alignment(func=AdvancedAffineNeedlemanWunsch)

	# def partwise_sequence_alignment(self, func):
	# 	for part, _ in enumerate(self.true_data.notes):

	# 		true_notes_part_x = [item for item in self.true_data.notes[part]]
	# 		test_notes_part_x = [item for item in self.test_data.notes[part]]
	# 		notes_x = func(true_notes_part_x, test_notes_part_x)  # noqa

	# 		try:
	# 			true_notes_part_y = [item for item in self.true_data.notes[part]]
	# 			test_notes_part_y = [item for item in self.test_data.notes[part + 1]]
	# 			notes_y = func(true_notes_part_y, test_notes_part_y)
	# 		except IndexError:
	# 			notes_y = float("inf")  # noqa


def xml_validator(musicxml_filepath, schema_filepath=__return_root_path() + "/tests/xml/musicxml.xsd"):
	"""Return if the provided musicxml file is valid against the current musicxml schema.

	:param [musicxml_filepath]: A character string that represents the filepath and filename of the file to open.
	:type [musicxml_filepath]: String

	:param [schema_filepath](optional): A character string that represents the filepath and filename of the schema to use.
	:type [schema_filepath]: String

	:return: Returns a boolean value, either it is a valid MusicXML file or it is not.
	:rtype: Bool
	"""
	with open(musicxml_filepath, "rb") as xml_file:
		test = BytesIO(xml_file.read())

	try:
		xml_schema = etree.XMLSchema(etree.parse(schema_filepath))
	except etree.XMLSyntaxError:
		xml_schema = etree.DTD(schema_filepath)

	return xml_schema.validate(etree.parse(test))


def xml_type_finder(musicxml_filepath):
	"""
	Check if the xml file is written in a partwise or timewise fashion. This is just the fastest way
	to check.

	:param [filepath]: A character string that represents the filepath and filename of the file to open.
	:type [filepath]: String

	:return: Either a Partwise or a Timewise string will return.
	:rtype: String
	"""
	with open(musicxml_filepath, "r") as xml_file:
		for line in xml_file:
			if "score-partwise" in line.lower():
				return "Partwise"
			elif "score-timewise" in line.lower():
				return "Timewise"
			else:
				pass  # Leave room 
		raise Exception("File has neither time-wise or part-wise tags")
