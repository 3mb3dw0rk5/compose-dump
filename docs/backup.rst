Backup command
==============

.. note::

    If no argument is provided, a complete backup will be dumped as ``tar``-
    archive to ``stdout``.

Each backup includes a ``Manifest.yml`` with metadata about the backup,
including mappings from configured volumes to volume archives and the logging
output.

By default a project's containers are paused when volumes are dumped.
The pausing mechanism is planned to be more sensible in a future release.

Arguments
---------

The ``backup`` command takes service names as arguments to determine the
services whose volumes and build contexts will be included in the backup.
If none is given, all services are taken into account.


Options
-------

The following options are available:


Source
~~~~~~

``--file``
..........

Alias: ``-f``

Selects one or more instances of a  `compose file` that resemble(s) a project.
If omitted, it's looked for from the current working directory upwards.

``--project-dir``
.................

Explicitly specifies a path that is used to look for a project's configuration.


Scopes
~~~~~~

If none of the scope options is provided, all will be included.

``--config``
............

Includes a project's configuration files and build contexts.
They will be stored in the ``config`` folder.

``--mounted``
.............

Includes the mounted volumes.
They will be stored in the ``volumes/mounted`` folder.

``--volumes``
.............

Includes project and service volumes as tar archives.
Project volumes will be stored in ``volumes/project``, service volumes in
``volumes/services``.


Target
~~~~~~

``--compression``
.................

Alias: ``-x``

Sets the format of a backup. Can be ``bz2``, ``gz``, ``tar`` or ``xz``.

This can also be set implicitly by setting a ``--target`` with a corresponding
file extension.

This option should be used only when writing to ``stdout``.

``--target``
............

Store the backup at the defined location. If omitted, the backup will be
written to ``stdout``.
If an existing directory is specified, a backup with a name assembled per
``--target-pattern`` will be created.
A target's file extension sets ``--compression`` implicitly.

``--target-pattern``
....................

Default: ``{host}__{name}__{path_hash}_{date}_{time}``

Defines the backup's name if ``--target`` selects an existing directory. The
following placeholders are available:

- ``{date}``
- ``{host}``
- ``{isodate}``
- ``{name}``
- ``{path_hash}`` (use this to discriminate projects with the same name in different locations)
- ``{time}``

Behaviour
~~~~~~~~~

``--no-pause``
..............

Do not pause running containers of a project during storing its volumes.

``--project-name``
..................

Alias: ``-p``

Specifies the name of a project. If omitted, the configuration's directory name
is used.

``--resolve-symlinks``
......................

If selected, symbolic links in the configuration are resolved and stored as
files. Use this to ensure that a project's configuration contents can be
restored completely without relying on other backups.

``--verbose``
.............

Includes debugging messages in the logs.



.. _`compose file`: https://docs.docker.com/compose/compose-file/
