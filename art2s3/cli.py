import click

from .sync import walk


@click.group()
def cli():
    pass

cli.add_command(walk)
