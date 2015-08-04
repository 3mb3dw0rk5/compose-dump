from __future__ import print_function
from __future__ import unicode_literals
from inspect import getdoc
import logging
import re
import sys

from docker.errors import APIError

from .. import __version__
from ..dump import ProjectDump
from compose import legacy
from compose.project import NoSuchService, ConfigurationError
from compose.service import BuildError, NeedsBuildError
from compose.cli.command import Command
from compose.cli.docopt_command import NoSuchCommand
from compose.cli.errors import UserError

log = logging.getLogger(__name__)


def main():
    setup_logging()
    try:
        command = TopLevelCommand()
        command.sys_dispatch()
    except KeyboardInterrupt:
        log.error("\nAborting.")
        sys.exit(1)
    except (UserError, NoSuchService, ConfigurationError, legacy.LegacyContainersError) as e:
        log.error(e.msg)
        sys.exit(1)
    except NoSuchCommand as e:
        log.error("No such command: %s", e.command)
        log.error("")
        log.error("\n".join(parse_doc_section("commands:", getdoc(e.supercommand))))
        sys.exit(1)
    except APIError as e:
        log.error(e.explanation)
        sys.exit(1)
    except BuildError as e:
        log.error("Service '%s' failed to build: %s" % (e.service.name, e.reason))
        sys.exit(1)
    except NeedsBuildError as e:
        log.error("Service '%s' needs to be built, but --no-build was passed." % e.service.name)
        sys.exit(1)


def setup_logging():
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter())
    console_handler.setLevel(logging.INFO)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)

    # Disable requests logging
    logging.getLogger("requests").propagate = False


# stolen from docopt master
def parse_doc_section(name, source):
    pattern = re.compile('^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
                         re.IGNORECASE | re.MULTILINE)
    return [s.strip() for s in pattern.findall(source)]


class TopLevelCommand(Command):
    """Backup and restore Docker-Compose projects

    Usage:
      compose-dump [options] [COMMAND] [ARGS...]
      compose-dump -h|--help

    Options:
      -f, --file FILE           Specify an alternate compose file (default: docker-compose.yml)
      -p, --project-name NAME   Specify an alternate project name (default: directory name)
      --verbose                 Show more output
      -v, --version             Print version and exit

    Commands:
      backup             Backup a project and it's data
      pause              Pause services
      restore            Restore a project
      unpause            Unpause services

    """
    def docopt_options(self):
        options = super(TopLevelCommand, self).docopt_options()
        options['version'] = __version__
        return options

    def help(self, project, options):
        """
        Get help on a command.

        Usage: help COMMAND
        """
        handler = self.get_handler(options['COMMAND'])
        raise SystemExit(getdoc(handler))

    def backup(self, project, options):
        """
        Backup a project and it's data. Containers are not saved.

        For example:

            $ compose-dump backup -t /var/backups/docker-compose

        Usage: backup [options] [SERVICE...]

        Options:
            -C, --config            Backup configuration including additional files and build-contexts.
            -x (none|tar|gz|bz2),   Overrides --compression,
            --dumpformat=FORMAT     Target format [default: none]
            --full                  Backup config, mounted and container-volumes, default
            -m, --mounted           Backup mounted volumes, skips paths outside project folder
            --no-pause               Don't pause containers during backup
            -t PATH, --target=PATH  Dump target [default: stdout]
            -V, --volumes           Include containers' volumes
        """

        # figure out options

        if not (options['--config'] or options['--mounted'] or options['--volumes']) or options['--full']:
            for option in ('--config', '--mounted', '--volumes'):
                options[option] = True
        if options['-x'] is not None:
            options['--dumpformat'] = options['-x']

        ProjectDump(project, options).store()
