import attr

from gandalf.extra import note_and_measure_offset
from gandalf.extra import track_moved_notes
# from gandalf.extra import track_moved_measures


@attr.s
class SzochResults:
  All_Symbols = attr.ib(init=False, default=0, type=int,)
  Symbol_Classes = attr.ib(init=False, default=0, type=int,)
  Weights = attr.ib(type=list,)

  Correctly_Identified = attr.ib(init=False, default=0, type=int,)
  Wrongly_Identified = attr.ib(init=False, default=0, type=int,)

  correct_step = attr.ib(init=False, default=0, type=int,)
  wrong_step = attr.ib(init=False, default=0, type=int,)
  expected_step = attr.ib(init=False, default=0, type=int,)

  correct_duration = attr.ib(init=False, default=0, type=int,)
  wrong_duration = attr.ib(init=False, default=0, type=int,)
  expected_duration = attr.ib(init=False, default=0, type=int,)

  correct_stem_dir = attr.ib(init=False, default=0, type=int,)
  wrong_stem_dir = attr.ib(init=False, default=0, type=int,)
  expected_stem_dir = attr.ib(init=False, default=0, type=int,)

  correct_accidental = attr.ib(init=False, default=0, type=int,)
  wrong_accidental = attr.ib(init=False, default=0, type=int,)
  expected_accidental = attr.ib(init=False, default=0, type=int,)

  correct_clef = attr.ib(init=False, default=0, type=int,)
  wrong_clef = attr.ib(init=False, default=0, type=int,)
  expected_clef = attr.ib(init=False, default=0, type=int,)

  correct_articulation = attr.ib(init=False, default=0, type=int,)
  wrong_articulation = attr.ib(init=False, default=0, type=int,)
  expected_articulation = attr.ib(init=False, default=0, type=int,)

  correct_time_signature = attr.ib(init=False, default=0, type=int,)
  wrong_time_signature = attr.ib(init=False, default=0, type=int,)
  expected_time_signature = attr.ib(init=False, default=0, type=int,)

  correct_key_signature = attr.ib(init=False, default=0, type=int,)
  wrong_key_signature = attr.ib(init=False, default=0, type=int,)
  expected_key_signature = attr.ib(init=False, default=0, type=int,)


def compare_list_items(ground_truth_list: list, omr_data_list: list) -> tuple:
  """
  Count and compare two list for items.
    - All items from the ground truths that are in the omr data list.
    - All extra items that are in the omr data, but not in the ground truth.

  Args:
    ground_truth_list (list): List of values from the ground truth MusicXML dict
                              taken at a specific key in the dictionary.

    omr_data_list (list): List of values from the omr data MusicXML dict taken
                          at a specific key in the dictionary.

  Returns (tuple): correct, wrong, expected
  """
  correct, wrong, expected = (0, 0, 0)

  if isinstance(ground_truth_list, list) and isinstance(omr_data_list, list):
    if ground_truth_list == [] and omr_data_list == []:
      return 0, 0, 0

    for item in ground_truth_list:
      if item in omr_data_list:
        correct += 1
        expected += 1
        omr_data_list.remove(item)
      else:
        wrong += 1
        expected += 1

    return correct, wrong, expected
  else:
    raise Exception(f"Something went wrong\nGroundTruth type: {type(ground_truth_list)}\nOMRData type: {type(omr_data_list)}") # noqa E501


def diff(ground_truth, omr_output):
  """
  Szwoch Diff Tool

  This is an implementation of szoch's proposed diff method, evaluating
  correct, extra, and, expected symbols.

  Args:
    ground_truth (dict): A dictionary of a manually or "known-correct" MusicXML
                        file that was parsed by the parser.

    test_dictionary (dict): A dictionary of a musicXML file we wish to evaluate that
                        was parsed by the parser.

  Returns:
    szwoch (attrs): Returns a mutable named tuple that includes a count of each element.
  """
  output = SzochResults([1, 1, 1])

  measure_offset = 0
  note_offset = 0
  moved_paths = []
  symbol_classes = []

  for index, (key, value) in enumerate(ground_truth.items()):
    next_note_path = note_and_measure_offset(
                    path=key,
                    measure_offset=measure_offset,
                    note_offset=note_offset)
    next_measure_path = note_and_measure_offset(
                    path=key,
                    measure_offset=measure_offset,
                    note_offset=note_offset)
    path_list = key.split(".")

    if isinstance(value, str):
      if path_list[-1] == "step":
        if "step" not in symbol_classes:
          symbol_classes.append("step")
        try:
          if ground_truth[next_note_path] == omr_output[key]:
            output.correct_step += 1
          else:
            temp_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            if ground_truth[temp_note_path] == omr_output[key] and temp_note_path not in moved_paths:
              output.correct_step += 1
              moved_paths.append(track_moved_notes(temp_note_path))
              note_offset += 1
              next_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            output.wrong_step += 1
        except KeyError:
          output.wrong_step += 1
        output.expected_step += 1

      elif path_list[-1] == "accidental":
        if "accidental" not in symbol_classes:
          symbol_classes.append("accidental")
        try:
          if ground_truth[next_note_path] == omr_output[key]:
            output.correct_accidental += 1
          else:
            temp_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            if ground_truth[temp_note_path] == omr_output[key] and temp_note_path not in moved_paths:
              moved_paths.append(track_moved_notes(temp_note_path))
              output.correct_accidental += 1
              note_offset += 1
              next_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            output.wrong_accidental += 1
        except KeyError:
          output.wrong_accidental += 1
        output.expected_accidental += 1

      elif path_list[-1] == "duration":
        if "duration" not in symbol_classes:
          symbol_classes.append("duration")
        try:
          if ground_truth[next_note_path] == omr_output[key]:
            output.correct_duration += 1
          else:
            temp_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            if ground_truth[temp_note_path] == omr_output[key] and temp_note_path not in moved_paths:
              moved_paths.append(track_moved_notes(temp_note_path))
              output.correct_duration += 1
              note_offset += 1
              next_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            output.wrong_duration += 1
        except KeyError:
          output.wrong_duration += 1
        output.expected_duration += 1

      elif path_list[-1] == "stem_direction":
        if "stem_direction" not in symbol_classes:
          symbol_classes.append("stem_direction")
        try:
          if ground_truth[next_note_path] == omr_output[key]:
            output.correct_stem_dir += 1
          else:
            temp_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            if ground_truth[temp_note_path] == omr_output[key] and temp_note_path not in moved_paths:
              moved_paths.append(track_moved_notes(temp_note_path))
              output.correct_stem_dir += 1
              note_offset += 1
              next_note_path = note_and_measure_offset(key, measure_offset, note_offset + 1)
            output.wrong_stem_dir += 1
        except KeyError:
          output.wrong_stem_dir += 1
        output.expected_stem_dir += 1

    elif isinstance(value, list):
      if path_list[-1] == "clef":
        if "clef" not in symbol_classes:
          symbol_classes.append("clef")
        try:
          c, w, e = compare_list_items(ground_truth[next_measure_path], omr_output[key])
          output.correct_clef += c
          output.wrong_clef += w
          output.expected_clef += e
        except KeyError:
          output.wrong_clef += 1
          output.expected_clef += 1

      elif path_list[-1] == "time_signature":
        if "time_signature" not in symbol_classes:
          symbol_classes.append("time_signature")
        try:
          c, w, e = compare_list_items(ground_truth[next_measure_path], omr_output[key])
          output.correct_time_signature += c
          output.wrong_time_signature += w
          output.expected_time_signature += e
        except KeyError:
          output.wrong_time_signature += len(ground_truth[next_measure_path])
          output.expected_time_signature += len(ground_truth[next_measure_path])

      elif path_list[-1] == "key_signature_fifth" or path_list[-1] == "key_signature_mode":
        if "key_signature" not in symbol_classes:
          symbol_classes.append("key_signature")
        try:
          omr_output[key]
          c, w, e = compare_list_items(ground_truth[next_measure_path], omr_output[key])
          output.correct_key_signature += c
          output.wrong_key_signature += w
          output.expected_key_signature += e
        except KeyError:
          # if key does not exist in omr_output
          output.wrong_key_signature += len(ground_truth[next_measure_path])
          output.expected_key_signature += len(ground_truth[next_measure_path])

      elif path_list[-1] == "articulation":
        if "articulation" not in symbol_classes:
          symbol_classes.append("articulation")
        try:
          c, w, e = compare_list_items(ground_truth[next_note_path], omr_output[key])
          output.correct_articulation += c
          output.wrong_articulation += w
          output.expected_articulation += e
        except KeyError:
          output.wrong_articulation += len(ground_truth[next_note_path])
          output.expected_articulation += len(ground_truth[next_note_path])

  output.Correctly_Identified = (
    output.correct_step +
    output.correct_duration +
    output.correct_stem_dir +
    output.correct_accidental +
    output.correct_clef +
    output.correct_articulation +
    output.correct_time_signature +
    output.correct_key_signature
  )

  output.Wrongly_Identified = (
    output.wrong_step +
    output.wrong_duration +
    output.wrong_stem_dir +
    output.wrong_accidental +
    output.wrong_clef +
    output.wrong_articulation +
    output.wrong_time_signature +
    output.wrong_key_signature
  )

  output.All_Symbols = (
    output.expected_step +
    output.expected_duration +
    output.expected_stem_dir +
    output.expected_accidental +
    output.expected_clef +
    output.expected_articulation +
    output.expected_time_signature +
    output.expected_key_signature
  )

  output.Symbol_Classes = len(symbol_classes)

  return output
