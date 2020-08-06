import hashlib

from mupix.typewise import MupixObject
from mupix.extra import __return_root_path

# Test Files path
ROOT_DIR = __return_root_path() + "/tests/xml"
test_file = ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml"


def test_basic_parse_xml():
	"""
	Using base64 is not ideal, because it will just get huge!
		mupix read ms_F_Lydian_quarter_true.xml | openssl base64 -e
			or
		mupix read ms_F_Lydian_quarter_true.xml | base64

	But maybe that's not such a bad idea...

	Result should be:
		MupixObject(notes=[NoteObject(_music21_object=<music21.note.Note F>, part=1, measure=1, onset='0.0', duration='1.0', voice=1, articulation=[], step=5, name='F', octave=4, accidental='', stemdirection='up', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note G>, part=1, measure=1, onset='1.0', duration='1.0', voice=1, articulation=[], step=7, name='G', octave=4, accidental='', stemdirection='up', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note A>, part=1, measure=1, onset='2.0', duration='1.0', voice=1, articulation=[], step=9, name='A', octave=4, accidental='', stemdirection='up', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note B>, part=1, measure=1, onset='3.0', duration='1.0', voice=1, articulation=[], step=11, name='B', octave=4, accidental='', stemdirection='down', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note C>, part=1, measure=2, onset='0.0', duration='1.0', voice=1, articulation=[], step=0, name='C', octave=5, accidental='', stemdirection='down', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note D>, part=1, measure=2, onset='1.0', duration='1.0', voice=1, articulation=[], step=2, name='D', octave=5, accidental='', stemdirection='down', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note E>, part=1, measure=2, onset='2.0', duration='1.0', voice=1, articulation=[], step=4, name='E', octave=5, accidental='', stemdirection='down', beam=set(), tiestyle=None, tietype=None, tieplacement=None), NoteObject(_music21_object=<music21.note.Note F>, part=1, measure=2, onset='3.0', duration='1.0', voice=1, articulation=[], step=5, name='F', octave=5, accidental='', stemdirection='down', beam=set(), tiestyle=None, tietype=None, tieplacement=None)], rests=[], timeSignatures=[TimeSignatureObject(_music21_object=<music21.meter.TimeSignature 4/4>, part=1, measure=1, onset='0.0', numerator=4, denominator=4)], keySignatures=[KeySignatureObject(_music21_object=<music21.key.KeySignature of no sharps or flats>, part=1, measure=1, onset='0.0', step='C', mode='major')], clefs=[ClefObject(_music21_object=<music21.clef.TrebleClef>, part=1, measure=1, onset='0.0', name='G', line=2, octave=0)], spanners=[], dynamics=[], parts=1, error_description={}, visualize='0xbadbad', software_vendor="['MuseScore', '2.1.0']")
	"""
	m = hashlib.sha512()
	output = MupixObject.from_filepath(ROOT_DIR + "/compare/ms_F_Lydian_quarter_true.xml")
	# Visualizer will always return with it's address in memory.
	# TODO: Create a test for the visualizer functionality
	setattr(output, "visualize", "0xbadbad")
	output = bytes(str(output), encoding="utf-8")
	m.update(output)
	# If you want to change the structure of how elements are stored, or add fields to the classes,
	# you will need to manually check to make sure there are no errors and generate a new hash for the structure.

	# You can get the new hash AFTER checking manually for errors by un-commenting this next line and running the test.
	# raise Exception(output.decode("utf-8"))
	# raise Exception(m.hexdigest())
	correct_hash = "eb93dceae0a8eda0bc101f7a7b194d3d4c1fdb8c5541b97253d030b8d7131c3c56e6477e49e6b2421a2c9a369c8c6d4f125a9446f6c25377b3d9762adac87ac4" # noqa
	assert m.hexdigest() == correct_hash


def test_key_signature_parse_xml():
	"""
	Music21 will assume all key signatures are in the major mode, it does not try to discern the mode.

	{
		"part": 1,
		"measure": 1,
		"onset": 0.0,
		"step": "A",
		"mode": "major"
	},
	{
		"part": 1,
		"measure": 2,
		"onset": 3.0,
		"step": "B",
		"mode": "major"
	},
	{
		"part": 1,
		"measure": 3,
		"onset": 1.0,
		"step": "B-",
		"mode": "major"
	},
	{
		"part": 1,
		"measure": 4,
		"onset": 0.0,
		"step": "C",
		"mode": "major"
	}
	"""
	key_signatures = MupixObject.from_filepath(ROOT_DIR + "/read/key_signature.xml").ret()[3]

	assert key_signatures[0].part == 1
	assert key_signatures[0].measure == 1
	assert key_signatures[0].onset == "0.0"
	assert key_signatures[0].step == "A"

	assert key_signatures[1].part == 1
	assert key_signatures[1].measure == 2
	assert key_signatures[1].onset == "3.0"
	assert key_signatures[1].step == "B"

	assert key_signatures[2].part == 1
	assert key_signatures[2].measure == 3
	assert key_signatures[2].onset == "1.0"
	assert key_signatures[2].step == "B-"

	assert key_signatures[3].part == 1
	assert key_signatures[3].measure == 4
	assert key_signatures[3].onset == "0.0"
	assert key_signatures[3].step == "C"


def test_beam_parse_xml():
	"""
	"""
	notes = MupixObject.from_filepath(ROOT_DIR + "/read/beam.xml").ret()[0]
	assert notes[0].beam == {'start'}
	assert notes[1].beam == {'continue', 'partial'}
	assert notes[2].beam == {'partial', 'stop'}


def test_time_signature_parse_xml():
	"""
	"""
	time_signatures = MupixObject.from_filepath(ROOT_DIR + "/read/time_signature.xml").ret()[2]

	assert time_signatures[0].measure == 1
	assert time_signatures[0].onset == "0.0"
	assert time_signatures[0].numerator == 4
	assert time_signatures[0].denominator == 4

	assert time_signatures[1].measure == 2
	assert time_signatures[1].onset == "0.0"
	assert time_signatures[1].numerator == 7
	assert time_signatures[1].denominator == 8

	assert time_signatures[2].measure == 3
	assert time_signatures[2].onset == "0.0"
	assert time_signatures[2].numerator == 25
	assert time_signatures[2].denominator == 16

	assert time_signatures[3].measure == 4
	assert time_signatures[3].onset == "0.0"
	assert time_signatures[3].numerator == 4
	assert time_signatures[3].denominator == 4

	assert time_signatures[4].measure == 5
	assert time_signatures[4].onset == "0.0"
	assert time_signatures[4].numerator == 2
	assert time_signatures[4].denominator == 2


def test_voice_parse_xml():
	"""
	"""
	voices = MupixObject.from_filepath(ROOT_DIR + "/read/voice.xml").ret()[0]

	assert voices[0].voice == 1
	assert voices[1].voice == 2
	assert voices[2].voice == 3
	assert voices[3].voice == 4
