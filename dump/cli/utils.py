import logging


log = logging.getLogger('compose-dump')


def directory_exists(path):
    if not path.exists():
        log.error('%s does not exist.' % path)
        raise SystemExit(1)
    if not path.is_dir():
        log.error('%s is not a directory' % path)
        raise SystemExit(1)
