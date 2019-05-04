import pytest

from gandalf.base import ValidateXML

test_file = "tests/xml/test.xml"
schema = "tests/xml/musicxml.xsd"


@pytest.mark.slow
def test_validate_xml():
  global test_file, schema
  assert ValidateXML(schema, test_file).isvalid()

