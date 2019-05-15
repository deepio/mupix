import attr

from gandalf.extra import compare_list_items
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


def handle_str(self, item, key, true_data, test_data):
  if item not in self.symbol_classes:
    self.symbol_classes.append(item)
  try:
    temp = attr.asdict(self.output)
    if true_data[self.next_note_path] == test_data[key]:
      # output.correct_X += 1
      for pattern in temp:
        if item in pattern and "correct" in temp:
          self.output.__setattr__(pattern, temp.get(pattern) + 1)
    else:
      temp_note_path = note_and_measure_offset(key, self.measure_offset, self.note_offset + 1)
      if true_data[temp_note_path] == test_data[key] and temp_note_path not in self.moved_paths:
        # output.correct_X += 1
        # temp = attr.asdict(self.output)
        for pattern in temp:
          if item in pattern and "correct" in temp:
            self.output.__setattr__(pattern, temp.get(pattern) + 1)
        self.moved_paths.append(track_moved_notes(temp_note_path))
        self.note_offset += 1
        self.next_note_path = note_and_measure_offset(key, self.measure_offset, self.note_offset + 1)
      # output.wrong_X += 1
      # temp = attr.asdict(self.output)
      for pattern in temp:
        if item in pattern and "wrong" in temp:
          self.output.__setattr__(pattern, temp.get(pattern) + 1)
  except KeyError:
    # output.wrong_X += 1
    for pattern in temp:
      if (item in pattern and "wrong" in temp):
        self.output.__setattr__(pattern, temp.get(pattern) + 1)
  # output.expected_X += 1
  for pattern in temp:
      if (item in pattern and "expected" in temp):
        self.output.__setattr__(pattern, temp.get(pattern) + 1)


def handle_lists(self, dictionary_term, key):
  """
  This function will compare two lists and count the number of correct, expected, or wrong data.
  If a correct relation was not found between test_data and true_data, the next measure or note
  (depending on the type of list item) will be checked. If the following measure or note has
  correct data for the specific entry, then correct and wrong receive +1, while expected receives +2.

  Args:
    self (self object): Receive all items particular to a specific class.

    dictionary_term (string): One of the dictionary keys, like "clef" or "time_signature".

    key (string): Full path in parsed musicXML dictionary for the current item to be evaluated.

  Returns:
    (None)
  """
  if dictionary_term not in self.symbol_classes:
    self.symbol_classes.append(dictionary_term)

  temp = attr.asdict(self.output)
  try:
    c, w, e = compare_list_items(self.true_data[self.next_measure_path], self.test_data[key])
    for pattern in temp:
      if dictionary_term in pattern and "correct" in pattern:
        self.output.__setattr__(pattern, temp.get(pattern) + c)
      elif dictionary_term in pattern and "wrong" in pattern:
        self.output.__setattr__(pattern, temp.get(pattern) + w)
      elif dictionary_term in pattern and "expected" in pattern:
        self.output.__setattr__(pattern, temp.get(pattern) + e)
  except KeyError:
    for pattern in temp:
      if dictionary_term in pattern and "wrong" in pattern:
        self.output.__setattr__(pattern, temp.get(pattern) + len(self.true_data[self.next_measure_path]))
      elif dictionary_term in pattern and "expected" in pattern:
        self.output.__setattr__(pattern, temp.get(pattern) + len(self.true_data[self.next_measure_path]))


def handle_dicts(self, key):

  temp = attr.asdict(self.output)

  try:
    # Compare .step.rest vs .step.rest
    if self.test_data[key]:
      self.output.correct_step += 1
    else:
      self.output.wrong_step += 1
    self.output.expected_step += 1

    # Individual keys and values inside the step.Note dictionary
    for k, v in self.true_data[self.next_measure_path].items():
      if k not in self.symbol_classes:
        self.symbol_classes.append(k)

      # Count each item inside the note dictionary
      for pattern in temp:
        if k in pattern and "expected" in pattern:
          self.output.__setattr__(pattern, temp.get(pattern) + 1)

      # Evaluate correct/wrong
      if self.true_data[self.next_measure_path][k] == self.test_data[self.next_measure_path][k]:
        for pattern in temp:
          if k in pattern and "correct" in pattern:
            self.output.__setattr__(pattern, temp.get(pattern) + 1)
      else:
        for pattern in temp:
          if k in pattern and "wrong" in pattern:
            self.output.__setattr__(pattern, temp.get(pattern) + 1)

  except KeyError:
    for pattern in temp:
      if k in pattern and "wrong" in pattern:
        self.output.__setattr__(pattern, temp.get(pattern) + 1)


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
