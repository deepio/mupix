# Mupix - musicfile comparison for humans

![Travis (.com)](https://img.shields.io/travis/com/deepio/mupix)
![GitHub last commit](https://img.shields.io/github/last-commit/deepio/mupix)
![GitHub tag (latest by date)](https://img.shields.io/github/tag-date/deepio/mupix)
![GitHub repo size](https://img.shields.io/github/repo-size/deepio/mupix)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mupix)
![License](https://img.shields.io/github/license/deepio/mupix)

### Installation
Build the latest version using poetry
- `poetry install`

Build the latest version using pip
- `pip install .`

Install it from PyPi
- `pip install mupix`


### Usage
For up-to-date usage information
  - Checkout the [ReadTheDocs](https://mupix.readthedocs.io/en/latest/commands/)!
  - For the offline version run `mupix` or `mupix --help`

### Features
- Outputs valid `JSON` data
- Open and read (output to screen as JSON) symbolic music files
- Align musical markings from two or more symbolic files using sequence alignment algorithms
- Output the deferences between two files as full `error descriptions` or as `counted types`.
  - **Error Description**

  ```json
  {
    "ErrorDescription": {
      "part2_0.0_C major": "part2_0.0_G major",
      "part2_0.0_<music21.note.Note C>": "part2_0.0_<music21.note.Note G>",
      "part2_1.0_<music21.note.Note D>": "part2_1.0_<music21.note.Note A>",
      "part2_2.0_<music21.note.Note E>": "part2_2.0_<music21.note.Note B>",
      "part2_3.0_<music21.note.Note F>": "part2_3.0_<music21.note.Note C>",
      "part2_0.0_<music21.note.Note G>": "part2_0.0_<music21.note.Note D>",
      "part2_1.0_<music21.note.Note A>": "part2_1.0_<music21.note.Note E>",
      "part2_2.0_<music21.note.Note B>": "part2_2.0_<music21.note.Note F#>",
      "part2_3.0_<music21.note.Note C>": "part2_3.0_<music21.note.Note G>"
    }
  }
  ```

  - **Counted error types**

  ```python
  # Syntax highlighting as python because of the need for comments.
  {
    "Notes": [
      {
        "right": 8,
        "wrong": 8,
        "name": "NoteNameResult"
      }, # example was truncated
      {
        "right": 111,
        "wrong": 17,
        "name": "NoteTotalResult"
      }
    ]
  }
  ```
