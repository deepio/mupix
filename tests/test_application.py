import hashlib

import pytest

from gandalf.application import Compare
from gandalf.application import parse_xml
from gandalf.application import validate_xml
from gandalf.extra import __return_root_path

# Test Files path
ROOT_DIR = __return_root_path() + "/tests/xml"
schema = ROOT_DIR + "/musicxml.xsd"
test_file = ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml"


def test_parse_xml():
  """
  Using base64 is not ideal, because it will just get huge!
  gandalf read ms_F_Lydian_quarter_true.xml | openssl base64 -e
  b'KHsnMC4wLjAnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRicsIG9jdGF2ZT00LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0ndXAnKSwgJzAuMC4xJzogTm90ZU9iamVjdChkdXJhdGlvbj0nZWlnaHRoJywgcGl0Y2g9J0cnLCBvY3RhdmU9NCwgYWNjaWRlbnRhbD0nJywgc3RlbV9kaXJlY3Rpb249J3VwJyksICcwLjAuMic6IE5vdGVPYmplY3QoZHVyYXRpb249J2VpZ2h0aCcsIHBpdGNoPSdBJywgb2N0YXZlPTQsIGFjY2lkZW50YWw9JycsIHN0ZW1fZGlyZWN0aW9uPSd1cCcpLCAnMC4wLjMnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nQicsIG9jdGF2ZT00LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjAnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nQycsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjEnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRCcsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjInOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRScsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpLCAnMC4xLjMnOiBOb3RlT2JqZWN0KGR1cmF0aW9uPSdlaWdodGgnLCBwaXRjaD0nRicsIG9jdGF2ZT01LCBhY2NpZGVudGFsPScnLCBzdGVtX2RpcmVjdGlvbj0nZG93bicpfSwgeycwLjAuMCc6IFRpbWVTaWduYXR1cmUobnVtZXJhdG9yPTQsIGRlbm9taW5hdG9yPTQpfSwgeycwLjAuMCc6IEtleVNpZ25hdHVyZShzdGVwPSdDJywgc2NhbGU9J21ham9yJyl9KQ=='

  Instead, using sha512! Could have used something smaller like sha256 but this is fine.
  b'f\t\x1b\x1e\xcd\xfc\xeb\xb6q\xab):\xda0\xbb\x02I\x1e\x80\x19Z\x95\xc5\xd3\xab\xa7E\xa8(\x15,a\xc3\xe2\x9dzc@#\xa6\xc7R0\xce\x97\xe2\x16\xb1\xf6&\xcc\x04r\xc1\x9c\xb8\x93\xb5\x14FH\x10\xb3\xe1'
  """
  m = hashlib.sha512()

  output = parse_xml(ROOT_DIR + "/compare/ms_F_Lydian_quarter_true.xml")
  output = bytes(str(output), encoding="utf-8")
  m.update(output)

  correct_hash = b"f\t\x1b\x1e\xcd\xfc\xeb\xb6q\xab):\xda0\xbb\x02I\x1e\x80\x19Z\x95\xc5\xd3\xab\xa7"
  correct_hash += b"E\xa8(\x15,a\xc3\xe2\x9dzc@#\xa6\xc7R0\xce\x97\xe2\x16\xb1\xf6&\xcc\x04r\xc1\x9c"
  correct_hash += b"\xb8\x93\xb5\x14FH\x10\xb3\xe1"

  assert m.digest() == correct_hash


@pytest.mark.slow
def test_validate_xml():
  assert validate_xml(test_file)


def test_Compare():
  output = Compare(
    ROOT_DIR + "/compare/ms_F_Lydian_quarter_true.xml",
    ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml",
  )
  assert output.total_right == 30 and output.total_wrong == 2
