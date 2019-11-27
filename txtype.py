#! /usr/bin/env python3
import click

from application import Application


@click.command(short_help='Command line typing software')
@click.option('-c', '--config', help="specify configuration path")
@click.option('-n', '--new', is_flag=True, help="create specified configuration file if not exist")
def txtype(config, new):
    """
    Command line typing software
    """
    Application(config, new).start()


txtype()
