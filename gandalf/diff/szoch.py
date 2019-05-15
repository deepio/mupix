import attr

from gandalf.base import BasicDiff
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


class SzochDiff(BasicDiff):
  """
  Szwoch Diff Tool

  This is an implementation of szoch's proposed diff method, evaluating
  correct, extra, and, expected symbols.

  Returns:
    szwoch (attrs): Returns a mutable named tuple that includes a count of each element.
  """
  def compare(self):
    self.output = SzochResults()
    self.moved_paths = []
    self.symbol_classes = []
    self.measure_offset = 0
    self.note_offset = 0

    for index, (key, value) in enumerate(self.true_data.items()):
      path_list = key.split(".")
      self.next_note_path = note_and_measure_offset(
        path=key,
        measure_offset=self.measure_offset,
        note_offset=self.note_offset,
      )
      self.next_measure_path = note_and_measure_offset(
        path=key,
        measure_offset=self.measure_offset,
        note_offset=self.note_offset
      )

      if isinstance(value, list):
        if path_list[-1] == "clef":
          handle_lists(self, "clef", key)
        elif path_list[-1] == "time_signature":
          handle_lists(self, "time_signature", key)
        elif path_list[-1] == "key_signature_fifth":
          handle_lists(self, "key_signature_fifth", key)
        elif path_list[-1] == "key_signature_mode":
          handle_lists(self, "key_signature_mode", key)
        else:
          raise Exception(f"Uh oh... {path_list[-1]}")

      elif isinstance(value, dict):
        if path_list[-2] == "step":
          # Handles step and its nested dictionary.
          handle_dicts(self, key)
        else:
          raise Exception(f"What is this?: {path_list[-2]}")

      else:
        raise Exception(f"This should not have happened: {key, value}")

  def __str__(self):
    import json
    return json.dumps(attr.asdict(self.output), indent=2)
