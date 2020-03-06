# [TODO] This is only testing one file until many files can be generated
# for tests
import itertools

from click.testing import CliRunner
import pytest

from mupix.commands import (
	validate,
	xml_finder,
	cli,
)
from mupix.extra import __return_root_path

ROOT_DIR = __return_root_path() + "/tests/xml"
true_file = ROOT_DIR + "/sheets/1-right.xml"
test_file = ROOT_DIR + "/sheets/1-wrong.xml"
print_options = ["-p", "-n", "-r", "-t", "-k", "-c", "-z", "-T"]
sort_options = ["--sort=basic", "--sort=anw", "--sort=anw-1"]


@pytest.mark.slow
def test_cli_validator():
	"""
	Test that the command line arguments work for xml_validation
	"""
	runner = CliRunner()
	result = runner.invoke(validate, [test_file])
	assert result.exit_code == 0
	assert "True" in result.output


def test_cli_xml_finder():
	"""
	Test that the command line arguments work for xml_finder
	"""
	runner = CliRunner()
	result = runner.invoke(xml_finder, [test_file])
	assert result.exit_code == 0
	assert "Partwise" in result.output


@pytest.mark.slow
def test_cli_read():
	"""
	Does reading work with every flag?
	"""
	runner = CliRunner()

	for length in range(1, len(print_options) + 1):
		for print_option in itertools.permutations(iterable=print_options, r=length):
			result = runner.invoke(cli, [print_option, "read", test_file])
			assert result.exit_code == 0


@pytest.mark.slow
def test_cli_compare():
	"""
	Does comparing work with every flag?
	"""
	runner = CliRunner()

	for length in range(1, len(print_options) + 1):
		for print_option in itertools.permutations(iterable=print_options, r=length):
			for sort_option in sort_options:
				result = runner.invoke(cli, [print_option, "compare", sort_option, true_file, test_file])
				assert result.exit_code == 0
