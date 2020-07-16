import copy
import json
import os
import re
import sys

from music21.interval import Interval
from music21.key import Key
from music21.note import Note


def __return_root_path() -> str:
	"""
	This is a simple function to get the root directory of the repository.

	Returns:
		(string): of the local filepath to this project.
	"""
	if os.name == "posix":
		return "/".join(os.path.abspath(__file__).split("/")[0:-2])
	else:
		return "\\".join(os.path.abspath(__file__).split("\\")[0:-2])


def return_char_except(value: int) -> str:
	"""
	Because we are already using the "_" to signal a skipped Mupix Object.
	"""
	if value >= 95:
		value += 1
	return chr(value)


def boundary_search(begin, end, string):
	"""
	Boundary Search
	This is the regex formula for finding everything between two specific strings.
	e.g. :
				this character =>[ (all of the stuff here, including newlines) ] <= this character
				(?<=[)(.*?)(?=])
	Args:
		begin (string): The character that signals the begins what you want to search for.
		end (string): The character that signals the end of what you are looking for.
		string (string): Multi-line data you wish to search through.
	Returns:
		output (list): A list of all instances of what was searched for.
	"""
	pattern = f"(?<={begin})(.*?)(?={end})"
	return re.findall(pattern, string, re.DOTALL)


def output_filter(ctx, func, *args, **kwargs):
	"""
	This is a helper function to filter the output of all commands into notes, rests, etc.
	"""
	output = func(*args, **kwargs)
	msg = {}

	# If no filtering options are defined, output all information
	if all(value == False for value in [ctx["notes"], ctx["rests"], ctx["time_signatures"], ctx["key_signatures"], ctx["clefs"], ctx["spanners"], ctx["dynamics"], ctx["error_description"]]):  # noqa
		# turn to json serializable.
		msg["Notes"] = [i.asdict() for i in output.notes]
		msg["Rests"] = [i.asdict() for i in output.rests]
		msg["TimeSignatures"] = [i.asdict() for i in output.timeSignatures]
		msg["KeySignatures"] = [i.asdict() for i in output.keySignatures]
		msg["Clefs"] = [i.asdict() for i in output.clefs]
		msg["Spanners"] = [i.asdict() for i in output.spanners]
		msg["Dynamics"] = [i.asdict() for i in output.dynamics]
		# Leave out of the regular output
		# msg["ErrorDescription"] = output.error_description
	else:
		# Not Pretty Print with a combination
		if ctx["notes"]:
			msg["Notes"] = [i.asdict() for i in output.notes]
		if ctx["rests"]:
			msg["Rests"] = [i.asdict() for i in output.rests]
		if ctx["time_signatures"]:
			msg["TimeSignatures"] = [i.asdict() for i in output.timeSignatures]
		if ctx["key_signatures"]:
			msg["KeySignatures"] = [i.asdict() for i in output.keySignatures]
		if ctx["clefs"]:
			msg["Clefs"] = [i.asdict() for i in output.clefs]
		if ctx["spanners"]:
			msg["Spanners"] = [i.asdict() for i in output.spanners]
		if ctx["dynamics"]:
			msg["Dynamics"] = [i.asdict() for i in output.dynamics]
		if ctx["error_description"]:
			msg["ErrorDescription"] = output.error_description

	if ctx["total_only"]:
		for category in msg:
			try:
				msg[category] = [item for item in msg[category] if 'Total' in item['name']]
			except KeyError:
				print(f"[{func}] - Does not have a Total output or something went wrong with it.")
				sys.exit(0)

	if not ctx["pretty_print"]:
		print(msg)
	else:
		print(json.dumps(msg, indent=2))


def _populate_list(input_list, maximum):
	"""
	Different music engraving software encode time signatures, key signatures,
	and clefs in a peculiar way. Some repeat the previous object in every
	following measure.

	Let's say this hypothetical score has 44 measures. When parsing a problematic musicXML file,
	you will notice there are 44 treble clefs in the same instrument part. Meaning the same,
	unchanging clef, was repeated once per measure in the file. The same can happen on a per-system
	basis. It is not a bad way to explain the music because each element implied, even if it is missing.

	To avoid any further complication, the clefs, time signatures, and key signatures have been
	"normalized" to always be repeated on every measure, because they are still "acting" on a measure when
	they are omitted.

	[TODO] Clean up the algorithm, maybe splitting it into an iter and a yielder or something with dequeue
	for better readability. This is just a PoC anyway.

	:param [input_list]: A list of objects (KeySignatureObject, TimeSignatureObject or ClefObject).
	:type [input_list]: List

	:param [maximum]: An integer that represents the maximum number of measures in the score. In other words, how many measures should the objects be expanded for.
	:type [maximum]: Integer

	:return: Returns a the original list with added objects if they are missing from each measure.
	:rtype: List
	"""

	measure = 1
	output_list = []
	# If there are no inputs given, skip everything.
	if len(input_list) == 0:
		return []

	while measure <= maximum:
		try:
			# Next element follows sequential number
			if input_list[0].measure == measure:
				output_list.append(input_list.pop(0))
				measure += 1
			# Missing element, create a new one and add it at the end of the list
			elif input_list[0].measure > measure:
				# If there is no information in the first measure, pick the information from the first element and duplicate
				if len(output_list) == 0:
					last_object = copy.deepcopy(input_list[0])
					last_object.measure = measure
					output_list.append(last_object)
					measure += 1
				else:
					last_object = copy.deepcopy(output_list[-1])
					last_object.measure += 1
					output_list.append(last_object)
					measure += 1
			# Next element has the same number as the previous one, but the other attributes are different.
			elif input_list[0].measure < measure:
				output_list.append(input_list.pop(0))
		# `input_list` last item's number was smaller than maximum.
		# Keep creating a duplicate of the last item until maximum is reached.
		except IndexError:
			try:
				tail_object = copy.deepcopy(output_list[-1])
			except IndexError:
					raise Exception(len(input_list), input_list, output_list)
			tail_object.measure += 1
			output_list.append(tail_object)
			measure += 1
	return output_list


def normalize_object_list(object_list, total_measures, total_parts):
	"""
	Without changing the order of the objects, iterate through each instrumental
	part and populate missing information in place. This small function just
	makes sure :func:`mupix.base._populate_list` occurs on every part.
	"""
	obj = []
	for part in range(1, total_parts + 1):
		obj += _populate_list([x for x in object_list if x.part == part], total_measures)
	return obj


def add_step_information(notes: list, keySignatures: list):
	"""
	This function will populate the step information into Mupix note objects, it
	is required because music21 will not keep key signature information in
	measure other than the measure the key is defined in when reading musicXML.
	The maintainers of music21 don't believe this is an issue and won't fix it,
	so this and others must exist.

	:param [notes]: A list of Mupix NoteObjects.
	:type [notes]: List

	:param [keySignatures]: A list of Mupix KeySignatureObjects.
	:type [keySignatures]: List

	:return [List]: The original list of Mupix NoteObjects (in order) with step information included.
	:rtype: List
	"""
	for key in keySignatures:  # min 1 keySignatures per measure

		key_name = key.step.upper() if key.mode == "major" else key.step.lower()
		for note in notes:
			if note.part == key.part and note.measure == key.measure:
				note.step = Interval(noteStart=Note(Key(key_name).asKey().tonic), noteEnd=Note(note._music21_object.step)).semitones % 12

	return notes


def _temp_fix_spanners(spanner: list, tmp_list: list) -> list:
	"""
	"""
	if len(spanner) != len(tmp_list):
		raise Exception("Spanner measure addition error.")

	for index, item in enumerate(spanner):
		spanner[index].measure = tmp_list[index]["measure"]

	return spanner
