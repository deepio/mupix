from mupix.application import xml_type_finder
from mupix.extra import __return_root_path

ROOT_DIR = __return_root_path() + "/tests/xml"
test_file = ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml"


def test_xml_type_identification():
  assert xml_type_finder(test_file) == "Partwise"
