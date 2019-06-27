import hashlib

from gandalf.application import ParseMusic21
from gandalf.extra import __return_root_path

# Test Files path
ROOT_DIR = __return_root_path() + "/tests/xml"
test_file = ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml"


def test_basic_parse_xml():
  """
  Using base64 is not ideal, because it will just get huge!
  gandalf read ms_F_Lydian_quarter_true.xml | openssl base64 -e
  b'KHsnMC4wLjAnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRicsIG9jdGF2ZT00LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0ndXAnKSwgJzAuMC4xJzogTm90ZU9iamVjdChkdXJhdGlvbj0nZWlnaHRoJywgcGl0Y2g9J0cnLCBvY3RhdmU9NCwgYWNjaWRlbnRhbD0nJywgc3RlbV9kaXJlY3Rpb249J3VwJyksICcwLjAuMic6IE5vdGVPYmplY3QoZHVyYXRpb249J2VpZ2h0aCcsIHBpdGNoPSdBJywgb2N0YXZlPTQsIGFjY2lkZW50YWw9JycsIHN0ZW1fZGlyZWN0aW9uPSd1cCcpLCAnMC4wLjMnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nQicsIG9jdGF2ZT00LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjAnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nQycsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjEnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRCcsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjInOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRScsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjMnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRicsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpfSwgeycwLjAuMCc6IFRpbWVTaWduYXR1cmUobnVtZXJhdG9yPTQsIGRlbm9taW5hdG9yPTQpfSwgeycwLjAuMCc6IEtleVNpZ25hdHVyZShzdGVwPSdDJywgc2NhbGU9J21ham9yJyl9KQ=='
  """
  m = hashlib.sha512()
  output = ParseMusic21.from_filepath(ROOT_DIR + "/compare/ms_F_Lydian_quarter_true.xml")
  output = bytes(str(output), encoding="utf-8")
  m.update(output)
  # If you want to change the structure of how elements are stored, or add fields to the classes,
  # you will need to manually check to make sure there are no errors and generate a new hash for the structure.

  # You can get the new hash AFTER checking manually for errors by un-commenting this next line and running the test.
  # raise Exception(m.hexdigest())
  # raise Exception(output)
  correct_hash = "1dd7e4eba9a911e3499bbb856104f8855cf38f4fa8e7e27579ad69f003106aedcdbd523b8c56f3fcfe0985264869ef8d210d4bc54e4f4b5db6ab0c32826ffb5c" # noqa
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
  key_signatures = ParseMusic21.from_filepath(ROOT_DIR + "/read/key_signature.xml").ret()[3]

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
  notes = ParseMusic21.from_filepath(ROOT_DIR + "/read/beam.xml").ret()[0]
  assert notes[0].beam == {'start'}
  assert notes[1].beam == {'continue', 'partial'}
  assert notes[2].beam == {'partial', 'stop'}


def test_time_signature_parse_xml():
  """
  """
  time_signatures = ParseMusic21.from_filepath(ROOT_DIR + "/read/time_signature.xml").ret()[2]

  assert time_signatures[0].measure == 1
  assert time_signatures[0].onset == "0.0"
  assert time_signatures[0].numerator == 4
  assert time_signatures[0].denominator == 4

  assert time_signatures[1].measure == 2
  assert time_signatures[1].onset == "4.0"
  assert time_signatures[1].numerator == 7
  assert time_signatures[1].denominator == 8

  assert time_signatures[2].measure == 3
  assert time_signatures[2].onset == "7.5"
  assert time_signatures[2].numerator == 25
  assert time_signatures[2].denominator == 16

  assert time_signatures[3].measure == 4
  assert time_signatures[3].onset == "13.75"
  assert time_signatures[3].numerator == 4
  assert time_signatures[3].denominator == 4

  assert time_signatures[4].measure == 5
  assert time_signatures[4].onset == "17.75"
  assert time_signatures[4].numerator == 2
  assert time_signatures[4].denominator == 2


def test_voice_parse_xml():
  """
  """
  voices = ParseMusic21.from_filepath(ROOT_DIR + "/read/voice.xml").ret()[0]

  assert voices[0].voice == 1
  assert voices[1].voice == 2
  assert voices[2].voice == 3
  assert voices[3].voice == 4
