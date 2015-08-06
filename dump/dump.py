# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import datetime
from hashlib import md5
import logging
import os
from path import Path, tempdir
from platform import node as gethostname
from shutil import ignore_patterns
import sys
import yaml

from compose import config
from compose.cli.docker_client import docker_client

log = logging.getLogger(__name__)
client = docker_client()


class path(Path):
    def copy2_with_full_path(self, dst, *args, **kwargs):
        if not dst.dirname().exists():
            dst.makedirs()
        path(self).copy2(dst, *args, **kwargs)


class ProjectDump:
    def __init__(self, project, options):
        self.invocation_time, self.finish_time = None, None
        self.host = gethostname()
        cwd = path.getcwd()

        if options['--dumpformat'] == '--tar':
            self.dumpformat = ':'
        elif options['--dumpformat'][2:] in ('bz2', 'gz'):
            self.dumpformat = ':' + options['--dumpformat'][2:]
        else:
            self.dumpformat = None

        self.no_pause = options['--no-pause']
        self.project = project
        self.services = options.get('SERVICE') or project.service_names
        self.sources = [x[2:] for x in options if x[2:] in ('config', 'mounted', 'volumes') and options[x] is True]
        target = options['--target'].rstrip('/')
        if target == 'stdout':
            self.target = 'stdout'
        else:
            self.target = cwd.joinpath(target).abspath()

        # TODO enable when depending on compose >= 1.4
        # config_file = options.get('--file') or os.environ.get('COMPOSE_FILE') or os.environ.get('FIG_FILE')
        # if not config_file:
        #     self.config_path = abspath(config.get_config_path(cwd))
        #     self.project_path = cwd
        # else:
        #     self.config_path = abspath(join(cwd, config_file))
        #     self.project_path = dirname(self.config_path)
        # TODO remove when depending on compose >= 1.4
        config_file = options.get('--file') or os.environ.get('COMPOSE_FILE') or \
            os.environ.get('FIG_FILE') or 'docker-compose.yml'
        self.config_path = cwd / config_file
        self.project_path = cwd

        self.project_config = config.load_yaml(self.config_path)

        if not self.target.isdir():
            log.error("Target %s is not a directory." % str(self.target))
            sys.exit(1)

        if self.target == 'stdout' or self.dumpformat is not None:  # FIXME
            raise NotImplementedError

    def store(self):
        log.info("Dumping project in %s" % self.project_path)
        try:
            dump, dumped_services = self.__create_dump()
        except:
            self.project.unpause(service_names=self.services)
            self.tempdir.rmtree()
            log.error("Dump creation failed. Please open a proper bug report.")
            raise

        self.project.unpause(service_names=self.services)
        self.finish_time = datetime.datetime.now().isoformat()

        self.__write_manifest(dumped_services)

        try:
            if not dump.endswith(('.tar', '.tar.bz2', '.tar.gz')):
                dst = self.target / self.dumptag
                self.dumpdir.copytree(dst, symlinks=True)
                log.info("Project-dump stored in %s" % str(dst))
            else:
                dump.move(self.target)
                log.info("Backup stored at %s" % str(self.target.joinpath(dump)))
        except:
            log.error("Failed to store project-dump. Please open a proper bug report.")
            raise
        finally:
            self.tempdir.rmtree()

    def __init_create_dump(self):
        self.invocation_time = datetime.datetime.now().isoformat()
        log.info("Backup starts at %s" % self.invocation_time)
        self.dumptag = self.host + '__' + md5(self.project_path).hexdigest()[:6] + \
            '__' + self.project.name + '__' + self.invocation_time[:-7]
        self.tempdir = tempdir(suffix='_composebak')
        self.dumpdir = self.tempdir / self.dumptag
        self.dump_conf_dir = self.dumpdir / 'config'
        self.dump_data_dir = self.dumpdir / 'data'

    def __create_dump(self):
        self.__init_create_dump()

        if 'config' in self.sources:
            self.__copy_config()

        if not self.no_pause:
            self.project.pause(service_names=self.services)

        if 'mounted' in self.sources or 'volumes' in self.sources:
            dumped_services = self.__dump_service_volumes()
        else:
            dumped_services = {}

        if self.dumpformat is None:
            return self.dumpdir, dumped_services
        # TODO tar backup
        # TODO compress backup
        # use  (code from) https://github.com/tsileo/dirtools/blob/master/dirtools.py

    def __copy_config(self):
        log.debug("Dumping config.")
        self.dump_conf_dir.makedirs()
        self.config_path.copy2_with_full_path(self.dump_conf_dir)

        for service in self.project_config:

            for extra_config in ('dockerfile', 'env_file'):
                if extra_config in self.project_config[service]:
                    extra_file = self.project_config[service][extra_config]
                    self.config_path.dirname().joinpath(extra_file)\
                        .copy2_with_full_path(self.dump_conf_dir / extra_file)
                    self.config_path.dirname().joinpath(extra_file).copyfile(self.dump_conf_dir)

            if 'extends' in self.project_config[service]:
                extends_file = self.project_config[service]['extends']['file']
                self.config_path.dirname().joinpath(extends_file)\
                    .copy2_with_full_path(self.dump_conf_dir / extends_file)

            if 'build' in self.project_config[service]:
                src = self.project_path.joinpath(self.project_config[service]['build']).abspath()
                dst = self.dump_conf_dir.joinpath(self.project_config[service]['build']).abspath()
                patterns = read_ignore_patterns(src, '.dockerignore')
                src.mergetree(dst, symlinks=True, ignore=ignore_patterns(*patterns))  # FIXME symlinks are NOT preserved; used method works in tests and on shell-usage

    def __dump_service_volumes(self,):
        dumped_services = {}
        self.dump_data_dir.makedirs()

        for service in [x for x in self.project.get_services(self.services)
                        if 'volumes' in self.project_config[x.name]]:

            name = service.name
            dumped_services[name] = {}

            if not service.containers(stopped=True):
                log.critical("No containers for service '%s'." % name)
                if 'mounted' not in self.sources:
                    continue
                container = None
            else:
                container = service.containers(stopped=True)[0]
                container.volumes = client.inspect_container(container.id)['Volumes']  # TODO add property to compose.container.Container, service.Service
                if len(service.containers()) > 1:
                    log.info("Service '%s' is scaled to more than one container. "
                             "All operations are done on the first." % service)

            if container:
                # TODO test if config_hash has diverged from instance
                # client.inspect_container(container.id)['Config']['Labels']['com.docker.compose.config-hash']
                dumped_services[name]['config_hash'] = service.config_hash

            for volume in self.project_config[name]['volumes']:
                dumped_services[name]['volumes'] = {}
                c_path, h_path = config.split_path_mapping(volume)

                if h_path is not None and 'mounted' in self.sources:
                    if h_path.startswith(('/', '../', '~/')):  # TODO check that more properly based on abspaths
                        log.info("Skipping '%s' from '%s', path is not inside project-directory." % (h_path, name))
                    else:
                        log.info("Handling mount '%s' for service '%s'." % (volume, name))
                        src = self.project_path / h_path
                        dst = path(name) / 'mounts' / h_path
                        if src.isfile():
                            src.copy2_with_full_path(dst)
                        elif src.isdir():
                            src.copytree(self.dump_data_dir / dst, symlinks=False)
                        else:
                            log.warn("Neither file or directory: Skipping %s" % str(src))
                        dumped_services[name]['volumes'] = {c_path: str(path('data') / dst)}

                if h_path is None and 'volumes' in self.sources and container and container.volumes:
                    log.info("Handling volume '%s' from service '%s'." % (volume, name))
                    h_path = container.volumes[c_path]
                    dst = path(name) / 'volumes' / c_path[1:]
                    path(h_path).copytree(self.dump_data_dir / dst, symlinks=False)
                    dumped_services[name]['volumes'] = {c_path: str(path('data') / dst)}

        return dumped_services

    def __write_manifest(self, dumped_services):
        # TODO save meta in that order
        manifest = {'meta': {'invocation_time': self.invocation_time,
                             'finish_time': self.finish_time,
                             'project_path': str(self.project_path),
                             'docker_compose_config': str(self.config_path),  # FIXME relative to target's location
                             'content': self.sources,
                             'argv': sys.argv,
                             'host': self.host,
                             'uid': os.getuid(),
                             'gid': os.getgid()},
                    'services': dumped_services}
        with open(self.dumpdir / 'Manifest.yml', 'w+') as f:
            log.debug("Writing Manifest.yml")
            print(yaml.safe_dump(manifest), file=f)


def read_ignore_patterns(_path, ignorefile):
    """ Loads ignorepatterns from an ignorefile.

    :param _path: A directory-path that contains the ignorefile.
    :param ignorefile: Name of the ignorefile.
    :return: Ignore-patterns as tuple, empty if file doesn't exist.
    """
    ignorefile = path(_path) / ignorefile
    if ignorefile.isfile():
        with open(ignorefile, 'rt') as f:
            patterns = tuple(f.readlines())
    else:
        patterns = ()
    return patterns


# TODO add docstrings
