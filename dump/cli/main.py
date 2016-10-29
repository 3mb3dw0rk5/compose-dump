import logging
import sys

import click
from compose import config as compose_config

from dump import __version__
from dump.cli.utils import CWD


COMPRESSIONS = ('gz', 'bz2', 'xz')
COMPRESSION_EXTENSIONS = tuple('.' + x for x in COMPRESSIONS)


console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(logging.Formatter())

log_handlers = [console_handler]

log = logging.getLogger('compose-dump')
log.addHandler(console_handler)

# Disable requests logging
logging.getLogger("requests").propagate = False


def set_debug_logging(ctx, para, value):
    log_level = logging.DEBUG if value else logging.INFO
    log.setLevel(log_level)
    for handler in log_handlers:
        handler.setLevel(log_level)


@click.group()
@click.version_option(__version__)
def main(**options):
    pass


@click.command()
@click.option('--config', is_flag=True,
              help='Include configuration files, including referenced files '
                   'and build-contexts.')
@click.option('--compression', '-x', type=click.Choice(COMPRESSIONS),
              help='Sets the compression when an archive file is written. '
                   'Can also be provided as suffix on the target option.')
@click.option('--file', '-f', metavar='FILENAME', multiple=True,
              help='Specifies alternate compose files.')
@click.option('--mounted', is_flag=True,
              help='Include mounted volumes, skips paths outside project folder.')
@click.option('--no-pause', is_flag=True, help="Don't pause containers during backup")
@click.option('--project-name', '-p', default=CWD.name,  envvar='COMPOSE_PROJECT_NAME',
              help='Specifies an alternate project name.')
@click.option('--target', '-t', metavar='PATH', help='Dump target, defaults to stdout. ')
@click.option('--verbose', is_flag=True, is_eager=True, callback=set_debug_logging,
              help='Show debug messages.')
@click.option('--volumes', is_flag=True, help='Include container volumes.')
@click.argument('services', nargs=-1, metavar='SERVICE...')
def backup(**options):
    """
    Backup a project and its data. Containers are not saved.

    If none of the include flags is provided, all are set to true.

    For example:

        $ compose-dump backup -t /var/backups/docker-compose
    """

    # figure out options

    del options['verbose']

    options['compose_files'] = options['file']
    del options['file']

    options['scopes'] = ()
    scopes = ('config', 'mounted', 'volumes')
    for scope in scopes:
        if options[scope]:
            options['scopes'] += (scope,)
        del options[scope]
    if not options['scopes']:
        options['scopes'] = scopes

    if options['target'] is None or \
            options['target'].endswith(COMPRESSION_EXTENSIONS + ('.tar',)):
        options['target_type'] = 'archive'
    else:
        options['target_type'] = 'folder'

    if options['compression'] is None and options['target'] and \
            options['target'].endswith(COMPRESSION_EXTENSIONS):
        options['compression'] = options['target'].rsplit('.', 1)[1]

    base_dir = str(CWD)
    environment = compose_config.environment.Environment.from_env_file(base_dir)
    config_details = compose_config.find(base_dir, options['compose_files'], environment)
    config = compose_config.load(config_details)

    unknown_services = set(options['services']) - set(x['name'] for x in config.services)
    if unknown_services:
        log.error('Unknown services: %s' % ', '.join(unknown_services))
        raise SystemExit(1)
    if not options['services']:
        options['services'] = tuple(x['name'] for x in config.services)

    log.debug('Invoking project dump with these settings: %s' % options)

    # ProjectDump(project, options).store()

main.add_command(backup)
