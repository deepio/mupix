from gandalf.diff.szoch import SzochDiff
from gandalf.extra import __return_root_path


def test_note_skipping():
  TEST_DIR = __return_root_path() + "/tests/xml"
  note_offset_true = TEST_DIR + "/noteoffset-cmajor.xml"
  note_offset_test = TEST_DIR + "/noteoffset-cmajor-test.xml"

  true_c_step = 32
  true_w_step = 3
  true_e_step = 32
  true_data = true_c_step, true_w_step, true_e_step
  note_skip_test = SzochDiff(note_offset_true, note_offset_test).output
  test_c_step = note_skip_test.correct_step
  test_w_step = note_skip_test.wrong_step
  test_e_step = note_skip_test.expected_step
  test_data = test_c_step, test_w_step, test_e_step
  assert true_data == test_data
