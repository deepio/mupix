import hashlib
import json

import pytest

from gandalf.base import ValidateXML
from gandalf.base import MusicXML_Parser
from gandalf.extra import __return_root_path

ROOT_DIR = __return_root_path() + "/tests/xml"
test_file = ROOT_DIR + "/test.xml"
schema = ROOT_DIR + "/musicxml.xsd"


@pytest.mark.slow
def test_validate_xml():
  global test_file, schema
  assert ValidateXML(schema, test_file).isvalid()


  def test_parts(data):
    """
    Test if the entire part data is parsed correctly.
    """
    m = hashlib.sha512()
    m.update(bytes(json.dumps(data.get_parts()), "utf-8"))
    correct_hash = b"\xcc\xc4\xbbX\x89o\xe9+s\xebkkS\x1e\x7f\xa7\xc4\xacAZ\xae\x02\x08\x99\xfeD,\x12\x92t\x17\xbe\xcc"
    correct_hash += b"\x13\xa8\xe4\xb8\xc2(nP\xd0\xbcz@\xd9\xcd\xeb\xb4\x0f\xec?\xfb\xf9\xb9th32PX\xca\x02\x83"
    assert m.digest() == correct_hash

