import pytest

from mupix.application import BasicCompare
from mupix.extra import __return_root_path

# Test Files path
ROOT_DIR = __return_root_path() + "/tests/xml"
test_file = ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml"


@pytest.fixture
def load_single_voice_compare_resources():
  ROOT_DIR = __return_root_path() + "/tests/xml"
  return BasicCompare(
    true_filepath=ROOT_DIR + "/compare/ms_F_Lydian_quarter_true.xml",
    test_filepath=ROOT_DIR + "/compare/ms_F_Lydian_quarter_test.xml",
    do_not_count=[],
  )


def test_compare_basic_single_voice_notes_total(load_single_voice_compare_resources):
  # raise Exception(
  #   load_single_voice_compare_resources.error_description,
  #   load_single_voice_compare_resources.notes,
  #   load_single_voice_compare_resources.notes[-1].right,
  #   load_single_voice_compare_resources.notes[-1].wrong
  # )
  assert load_single_voice_compare_resources.notes[-1].right == 86
  assert load_single_voice_compare_resources.notes[-1].wrong == 2


def test_compare_basic_single_voice_notes_accidental(load_single_voice_compare_resources):
  # raise Exception(load_single_voice_compare_resources.notes[0])
  assert load_single_voice_compare_resources.notes[0].right == 7
  assert load_single_voice_compare_resources.notes[0].wrong == 1


def test_compare_basic_single_voice_notes_beam(load_single_voice_compare_resources):
  # raise Exception(load_single_voice_compare_resources.notes[1])
  assert load_single_voice_compare_resources.notes[1].right == 8
  assert load_single_voice_compare_resources.notes[1].wrong == 0


def test_compare_basic_single_voice_notes_duration(load_single_voice_compare_resources):
  # raise Exception(load_single_voice_compare_resources.notes[2])
  assert load_single_voice_compare_resources.notes[2].right == 8
  assert load_single_voice_compare_resources.notes[2].wrong == 0
