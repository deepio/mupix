import hashlib
import json
import os

import pytest

from gandalf.base import ValidateXML
from gandalf.base import MusicXML_Parser

ROOT_DIR = "/".join(os.path.abspath(__file__).split("/")[0:-1])
test_file = ROOT_DIR + "/xml/test.xml"
schema = ROOT_DIR + "/xml/musicxml.xsd"


@pytest.mark.slow
def test_validate_xml():
  global test_file, schema
  assert ValidateXML(schema, test_file).isvalid()


def test_musicxml_parser():
  global test_file

  with open(test_file) as f:
    data = MusicXML_Parser(f.read())

  def test_vendor(data):
    assert data.get_vendor() == "Sibelius 7.1.3"

  def test_instruments(data):
    assert data.get_instruments() == ['P1-I1', 'P2-I1', 'P3-I1', 'P4-I1', 'P5-I1', 'P6-I1', 'P7-I1']

  def test_parts(data):
    m = hashlib.sha512()
    m.update(bytes(json.dumps(data.get_parts()), "utf-8"))
    correct_hash = b"\xcc\xc4\xbbX\x89o\xe9+s\xebkkS\x1e\x7f\xa7\xc4\xacAZ\xae\x02\x08\x99\xfeD,\x12\x92t\x17\xbe\xcc"
    correct_hash += b"\x13\xa8\xe4\xb8\xc2(nP\xd0\xbcz@\xd9\xcd\xeb\xb4\x0f\xec?\xfb\xf9\xb9th32PX\xca\x02\x83"
    assert m.digest() == correct_hash

  test_vendor(data)
  test_instruments(data)
  test_parts(data)


if __name__ == "__main__":
  test_musicxml_parser()
