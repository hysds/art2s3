import click

from .sync import walk, sync


@click.group()
def cli():
    pass

cli.add_command(walk)
cli.add_command(sync)
