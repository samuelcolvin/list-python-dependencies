# List Python Dependencies

[![CI](https://github.com/samuelcolvin/list-python-dependencies/workflows/CI/badge.svg?event=push)](https://github.com/samuelcolvin/list-python-dependencies/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)

GitHub action to list all valid versions of dependency for a Python project.

This action is designed to allow all (or a random sample) of package dependency versions to be tested without manual configuration.

## Usage

Example usage:

```yaml
jobs:
  # this job does just one thing - it builds a set of test cases by inspecting either
  # `pyproject.toml` or `setup.py` for package dependencies
  find_dependency_cases:
    runs-on: ubuntu-latest

    outputs:
      PYTHON_DEPENDENCY_CASES: ${{ steps.list-python-dependencies.outputs.PYTHON_DEPENDENCY_CASES }}

    steps:
      - uses: actions/checkout@v3
      - uses: samuelcolvin/list-python-dependencies@main
        id: list-python-dependencies
        with:
          # if you want to limit the number of cases tested, set `max_cases` here
          # if omitted, all cases will be tested
          max_cases: 10

  # this is the main test job, the only special thing about it `strategy.matrix` which is
  # generated from the output of `find_dependency_cases` above
  test_matrix:
    runs-on: ubuntu-latest

    needs:
      - find_dependency_cases

    strategy:
      matrix:
        PYTHON_DEPENDENCY_CASE: ${{ fromJSON(needs.find_dependency_cases.outputs.PYTHON_DEPENDENCY_CASES) }}

    name: testing ${{ matrix.PYTHON_DEPENDENCY_CASE }}
    steps:
      - uses: actions/checkout@v3

      - name: set up python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # set up the environment for the test case as you usually would
      - run: pip install -e .
      - run: pip install -r tests/requirements.txt
      # install specific versions of dependencies using `matrix.PYTHON_DEPENDENCY_CASE`
      - run: pip install ${{ matrix.PYTHON_DEPENDENCY_CASE }}
      - run: pytest
```
