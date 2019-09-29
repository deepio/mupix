import pytest

from gandalf.application import xml_validator
from gandalf.extra import __return_root_path

ROOT_DIR = __return_root_path() + "/tests/xml"
test_file = ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml"


@pytest.mark.slow
def test_xml_validator():
  assert xml_validator(test_file)
