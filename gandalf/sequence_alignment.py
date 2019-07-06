import attr
import numpy


@attr.s
class Matrix:
  true_data_len = attr.ib(type=int)
  test_data_len = attr.ib(type=int)

  def __attrs_post_init__(self):
    """
    Creating new values here will be hidden from view when printing the output.
    """
    self.m = numpy.zeros((self.true_data_len, self.test_data_len))
    self.x = numpy.zeros((self.true_data_len, self.test_data_len))
    self.y = numpy.zeros((self.true_data_len, self.test_data_len))

    self.pointer = numpy.zeros((self.true_data_len, self.test_data_len))
    self.x_pointer = numpy.zeros((self.true_data_len, self.test_data_len))
    self.y_pointer = numpy.zeros((self.true_data_len, self.test_data_len))


@attr.s
class SequenceAlignment:
  """
  @timothydereuse 2019
  https://github.com/DDMAL/text-alignment/blob/ba44cb090caf63514cfe925abcc3afd1f2585a1d/textSeqCompare.py#L1-L191
  """
  true_data = attr.ib()
  test_data = attr.ib()
  aligned_true_data = attr.ib(init=False, default=[])
  aligned_test_data = attr.ib(init=False, default=[])

  match = attr.ib(kw_only=True, default=10)
  mismatch = attr.ib(kw_only=True, default=-5)
  gap_extend = attr.ib(kw_only=True, default=-1)

  gap_open_x = attr.ib(kw_only=True, default=-10)
  gap_extend_x = attr.ib(kw_only=True, default=-1)
  gap_open_y = attr.ib(kw_only=True, default=-10)
  gap_extend_y = attr.ib(kw_only=True, default=-1)

  def __attrs_post_init__(self):
    # Convert to list
    self.true_data = self._type_check(self.true_data)
    self.test_data = self._type_check(self.test_data)

    # Add extra character at the end of both, and base the alignment on that.
    self.true_data = self.true_data + [" "]
    self.test_data = self.test_data + [" "]

    self.matrix = Matrix(
      len(self.true_data),
      len(self.test_data),
    )

    self.populate()

  def __str__(self):
    return "{{\n  true_data: {}\n  test_data: {}\n  aligned_true_data: {}\n  aligned_test_data: {}\n}}".format(
      "".join(self.true_data),
      "".join(self.test_data),
      "".join(self.aligned_true_data),
      "".join(self.aligned_test_data),
    )

  def _type_check(self, input):
    if isinstance(input, str):
      input = [char for char in input]
    elif isinstance(input, list):
      pass
    else:
      raise Exception(
        f"{self.__class__}\n\n" +
        f"Input data of type {type(input)} is not acceptible.\n" +
        "Please use a String or a List instead."
      )
    return input

  def scoring_method(self, true, test):
    if true == test:
      return 1
    else:
      return 0

  def populate(self):
    raise Exception(
        f"{self.__class__}\n\n" +
        f"You forgot to specify a populate() method."
      )

  def find_shortest_path(self):
    """
    Fill the array with the best path to take.
    """
    while(self.xpt > 0 and self.ypt > 0):
      # If both values true/test are the same.
      if self.mpt == 0:
        self.true_align.append(self.true_data[self.xpt - 1])
        self.test_align.append(self.test_data[self.ypt - 1])

        self.xpt -= 1
        self.ypt -= 1

      elif self.mpt == 1:
        self.true_align.append(self.true_data[self.xpt - 1])
        self.test_align.append("_")

        self.xpt -= 1

      elif self.mpt == 2:
        self.true_align.append("_")
        self.test_align.append(self.test_data[self.ypt - 1])

        self.ypt -= 1

      self.mpt = self.matrix.pointer[self.xpt][self.ypt]

    while self.ypt > 0:
      self.true_align.append("_")
      self.test_align.append(self.test_data[self.ypt - 1])
      self.ypt -= 1
    while self.xpt > 0:
      self.true_align.append(self.true_data[self.xpt - 1])
      self.test_align.append("_")
      self.xpt -= 1

    self.aligned_true_data = reversed(self.true_align)
    self.aligned_test_data = reversed(self.test_align)

  def traceback(self):
    self.true_align = []
    self.test_align = []
    self.align_record = []
    self.pointer_record = []
    self.xpt = len(self.true_data) - 1
    self.ypt = len(self.test_data) - 1
    self.mpt = self.matrix.pointer[self.xpt][self.ypt]

    # Align the extra characters at the end.
    self.true_align += self.true_data[self.xpt]
    self.test_align += self.test_data[self.ypt]

    return self.find_shortest_path()


@attr.s
class AffineNeedlemanWunsch(SequenceAlignment):
  def populate(self):
    for index, value in enumerate(self.true_data):
      self.matrix.m[index][0] = self.gap_extend * index
      self.matrix.x[index][0] = float("-inf")
      self.matrix.y[index][0] = float("-inf")
    for index, value in enumerate(self.test_data):
      self.matrix.m[0][index] = self.gap_extend * index
      self.matrix.x[0][index] = self.gap_extend * index
      self.matrix.y[0][index] = float("-inf")

    for i in range(1, len(self.true_data)):
      for j in range(1, len(self.test_data)):
        eq_res = self.scoring_method(self.true_data[i - 1], self.test_data[j - 1])
        match_score = self.match if eq_res else self.mismatch

        matrix_values = [
          self.matrix.m[i - 1][j - 1],
          self.matrix.x[i - 1][j - 1],
          self.matrix.y[i - 1][j - 1],
        ]
        self.matrix.m[i][j] = max(matrix_values) + match_score
        self.matrix.pointer[i][j] = matrix_values.index(max(matrix_values))

        x_matrix_values = [
          self.matrix.m[i - 1][j] + self.gap_open_x + self.gap_extend_x,
          self.matrix.x[i - 1][j] + self.gap_extend_x,
          self.matrix.y[i - 1][j] + self.gap_open_x + self.gap_extend_x,
        ]
        self.matrix.x[i][j] = max(x_matrix_values)
        self.matrix.x_pointer[i][j] = x_matrix_values.index(max(x_matrix_values))

        y_matrix_values = [
          self.matrix.m[i][j - 1] + self.gap_open_y + self.gap_extend_y,
          self.matrix.x[i][j - 1] + self.gap_open_y + self.gap_extend_y,
          self.matrix.y[i][j - 1] + self.gap_extend_y,
        ]
        self.matrix.y[i][j] = max(y_matrix_values)
        self.matrix.y_pointer[i][j] = y_matrix_values.index(max(y_matrix_values))

    self.traceback()


if __name__ == "__main__":
  seq1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit '
  seq2 = 'LoLorem fipsudor ..... st emet, c.nnr adizcing eelilit'

  print(
    AffineNeedlemanWunsch(
      # # Accepts Lists
      # [char for char in seq1], [char for char in seq2],

      # # Accepts Strings
      seq1, seq2,

      # # Raises and Exception on everything else.

      # # Tuple
      # (1,2,3,4), seq2,

      # # Int
      # 1243, seq1,

      # # Float
      # 1.123, seq1,

      # # Dicts
      # {"asdf": "zxcv"}, seq2,
    )
  )
