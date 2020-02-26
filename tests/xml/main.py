import json

import click


def read_json() -> dict:
	with open("sheets_list.json", "r") as f:
		return json.load(f)


def write_json(data: dict):
	with open("sheets_list.json", "w") as f:
		json.dump(data, f, indent=2)


def add_sheet(data: dict):
	old_data = read_json()
	last = max([int(keys) for keys in old_data])
	data = {str(last + 1): data}
	write_json({**old_data, **data})


def reset_sheet():
	basic = {
		"1": {
			"filename": "1.xml",
			"description": "[Object list normalization] - Testing missing keys, clefs, times and inputs them in every measure."
		}
	}
	write_json(basic)

# reset_sheet()
@click.group()
def cli():
	pass


@click.command("add", short_help="Add an entry to the list of files.")
@click.argument("filename",)  # @click.argument("filename", type=click.File("rb"))
@click.argument("description", nargs=-1)
def add(filename, description):
	"""A simple program to add, remove, or read MusicXML page entries to test specific aspects of Mupix."""
	print(filename)
	print(description)
	# for x in range(count):
	# 	click.echo('add %s!' % name)


@click.command("read", short_help="Read an entries in the list")
@click.argument("filename",)  # @click.argument("filename", type=click.File("rb"))
def read(filename):
	try:
		print(json.dumps(read_json()[filename.replace(".xml", "")], indent=2))
	except KeyError:
		print("[-] Entry does not exist.")


if __name__ == "__main__":
	cli.add_command(add)
	cli.add_command(read)
	cli()
