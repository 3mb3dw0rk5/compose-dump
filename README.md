# compose-dump

***********************************************************************
This piece of code is tested with only a small number of use-cases yet.
Use  it  at  your   own   risk.    You   are   invited  to  contribute.
***********************************************************************

`compose-dump` let's you backup and restore
[Docker-Compose](https://github.com/docker/compose)-projects.
Like `docker-compose` this tool operates usually in a project-folder.
It's intended to be a simple tool a with docker-compose-like interface to
wrap into your backup-logic.


## Installation

Compose's latest released version's dependencies must be installed.

    git clone -o upstream git@github.com:funkyfuture/compose-dump.git
    cd compose-dump
    git submodule init
    git submodule update
    pip install -r requirements.txt
    # only if docker-compose is not installed in your environment:
    pip install -r requirements-compose.txt
    python setup.py develop

#### Updating

    git pull upstream master
    git submodule update


## Usage

### Examples

Fully dump a compose-project from `project_path` to `/var/backups/composeprojects`:

    cd project_path
    compose-dump backup -t /var/backups/composeprojects

Only dump configuration and data from container-volumes of the service `web`:

    compose-dump backup --config --volumes -t /var/backups/composeprojects web

Command line reference:

    compose-dump --help
    compose-dump help backup

### Backup structure

Any data that is ouside the project's scope is ignored. In particular that are
mounted volumes that are not in the project-path or below and volumes in
`volumes_from`-referenced containers. Consider this not as a limitation;
handle these objects in your backup-logic.

Dumping build-contexts as part of the `--config`-handling respects a
`.dockerignore`-file.

The resulting dump is structured this way:
```
+ <hostname>__<shorted_path_hash>__<project_name>__<iso_timestamp>
  - Manifest.yml
  + config
    - <config_files>…  # Usually docker-compose.yml and its referenced files
    - <build_contexts>…
  + data
    + <service>…
      + mounts
        <host_path_relative_to_project_path>…
      + volumes
        <absolute_container_path>…
```


## Contributing

Fork it, report issues and open pull requests at
https://github.com/funkyfuture/compose-dump


## TODO / Known issues

- add license
- use compose.config.load to get Context inst. and inst. compose.Project with it
- more docs
- use current docker-py features
- consider volumes defined in the image
- adapt version2 config files
- use pathlib properly
- decouple dump and store
- do not store data contents in a temporary folder 
- tests tests tests

#### backup

- symbolic links are not preserved :unamused:
- add log-messages to Manifest
- save extends-files from extends-files
- handle volumes defined in extended services
- backup-configuration in a file
- add warning when mounted directories are in a build-context
- make top-level name configurable
- maybe:
  - change to click framework
  - .backupignore
  - pre_ and post_command to be executed in

#### restore

- implement an automated restoration of a project-dump
- test if config is changed and warn
- read from stdin
