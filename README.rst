 storage is used)

``backup_sites`` (default ``{}``)

This object contains names and configurations for the different PostgreSQL
clusters (here called ``sites``) from which to take backups.  The
configuration keys for sites are listed below.

* ``compression`` WAL/basebackup compression parameters

 * ``algorithm`` default ``"snappy"`` if available, otherwise ``"lzma"`` or ``"zstd"``
 * ``level`` default ``"0"`` compression level for ``"lzma"`` or ``"zstd"`` compression
 * ``thread_count`` (default max(cpu_count, ``5``)) number of parallel compression threads

``hash_algorithm`` (default ``"sha1"``)

The hash algorithm used for calculating checksums for WAL or other files. Must
be one of the algorithms supported by Python's hashlib.

``http_address`` (default ``"127.0.0.1"``)

Address to bind the PGHoard HTTP server to.  Set to an empty string to
listen to all available IPv4 addresses.   Set it to the IPv6 ``::`` wildcard
address to bind to all available IPv4 and IPv6 addresses.

``http_port`` (default ``16000``)

HTTP webserver port. Used for the archive command and for fetching of
basebackups/WAL's when restoring if not using an object store.

``json_state_file_path`` (default ``"/var/lib/pghoard/pghoard_state.json"``)

Location of a JSON state file which describes the state of the ``pghoard``
process.

``log_level`` (default ``"INFO"``)

Determines log level of ``pghoard``.

``maintenance_mode_file`` (default ``"/var/lib/pghoard/maintenance_mode_file"``)

If a file exists in this location, no new backup actions will be started.

``pg_receivexlog``

When active backup mode is set to ``"pg_receivexlog"`` this object may
optionally specify additional configuration options. The currently available
options are all related to monitoring disk space availability and optionally
pausing xlog/WAL receiving when disk space goes below configured threshold.
This is useful when PGHoard is configured to create its temporary files on
a different volume than where the main PostgreSQL data directory resides. By
default this logic is disabled and the minimum free bytes must be configured
to enable it.

``pg_receivexlog.disk_space_check_interval`` (default ``10``)

How often to check available disk space.

``pg_receivexlog.min_disk_free_bytes`` (default undefined)

Minimum bytes (as an integer) that must be available in order to keep on
receiving xlogs/WAL from PostgreSQL. If available disk space goes below this
limit a ``STOP`` signal is sent to the ``pg_receivexlog`` / ``pg_receivewal``
application.

``pg_receivexlog.resume_multiplier`` (default ``1.5``)

Number of times the ``min_disk_free_bytes`` bytes of disk space that is
required to start receiving xlog/WAL again (i.e. send the ``CONT`` signal to
the ``pg_receivexlog`` / ``pg_receivewal`` process). Multiplier above 1
should be used to avoid stopping and continuing the process constantly.

``restore_prefetch`` (default ``transfer.thread_count``)

Number of files to prefetch when performing archive recovery.  The default
is the number of Transfer Agent threads to try to utilize them all.

``statsd`` (default: disabled)

Enables metrics sending to a statsd daemon that supports Telegraf
or DataDog syntax with tags.

The value is a JSON object::

  {
      "host": "<statsd address>",
      "port": <statsd port>,
      "format": "<statsd message format>",
      "tags": {
          "<tag>": "<value>"
      }
  }

``format`` (default: ``"telegraf"``)

Determines statsd message format. Following formats are supported:

* ``telegraf`` `Telegraf spec`_

.. _`Telegraf spec`: https://github.com/influxdata/telegraf/tree/master/plugins/inputs/statsd

* ``datadog`` `DataDog spec`_

.. _`DataDog spec`: http://docs.datadoghq.com/guides/dogstatsd/#datagram-format

The ``tags`` setting can be used to enter optional tag values for the metrics.

``pushgateway`` (default: disabled)

Enables metrics sending to a Prometheus Pushgateway with tags.

The value is a JSON object::

  {
      "endpoint": "<pushgateway address>",
      "tags": {
          "<tag>": "<value>"
      }
  }

The ``tags`` setting can be used to enter optional tag values for the metrics.

``prometheus`` (default: disabled)

Expose metrics through a Prometheus endpoint.

The value is a JSON object::

  {
      "tags": {
          "<tag>": "<value>"
      }
  }

The ``tags`` setting can be used to enter optional tag values for the metrics.

``syslog`` (default ``false``)

Determines whether syslog logging should be turned on or not.

``syslog_address`` (default ``"/dev/log"``)

Determines syslog address to use in logging (requires syslog to be true as
well)

``syslog_facility`` (default ``"local2"``)

Determines syslog log facility. (requires syslog to be true as well)

* ``transfer`` WAL/basebackup transfer parameters

 * ``thread_count`` (default max(cpu_count, ``5``)) number of parallel uploads/downloads

``upload_retries_warning_limit`` (default ``3``)

After this many failed upload attempts for a single file, create an
alert file.

``tar_executable`` (default ``"pghoard_gnutaremu"``)

The tar command to use for restoring basebackups. This must be GNU tar because some
advanced switches like ``--transform`` are needed. If this value is not defined (or
is explicitly set to ``"pghoard_gnutaremu"``), Python's internal tarfile
implementation is used. The Python implementation is somewhat slower than the
actual tar command and in environments with fast disk IO (compared to available CPU
capacity) it is recommended to set this to ``"tar"``.

Backup site configuration
=========================

The following options control the behavior of each backup site.  A backup
site means an individual PostgreSQL installation ("cluster" in PostgreSQL
terminology) from which to take backups.

``basebackup_age_days_max`` (default undefined)

Maximum age for basebackups. Basebackups older than this will be removed. By
default this value is not defined and basebackups are deleted based on total
count instead.

``basebackup_chunks_in_progress`` (default ``5``)

How many basebackup chunks can there be simultaneously on disk while
it is being taken. For chunk size configuration see ``basebackup_chunk_size``.

``basebackup_chunk_size`` (default ``2147483648``)

In how large backup chunks to take a ``local-tar`` basebackup. Disk
space needed for a successful backup is this variable multiplied by
``basebackup_chunks_in_progress``.

``basebackup_compression_threads`` (default ``0``)

Number of threads to use within compression library during basebackup. Only
applicable when using compression library that supports internal multithreading,
namely zstd at the moment. Default value 0 means not to use multithreading.

``basebackup_count`` (default ``2``)

How many basebackups should be kept around for restoration purposes.  The
more there are the more diskspace will be used. If ``basebackup_max_age`` is
defined this controls the maximum number of basebackups to keep; if backup
interval is less than 24 hour or extra backups are created there can be more
than one basebackup per day and it is often desirable to set
``basebackup_count`` to something slightly higher than the max age in days.

``basebackup_count_min`` (default ``2``)

Minimum number of basebackups to keep. This is only effective when
``basebackup_age_days_max`` has been defined. If for example the server is
powered off and then back on a month later, all existing backups would be very
old. However, in that case it is usually not desirable to immediately delete
all old backups. This setting allows specifying a minimum number of backups
that should always be preserved regardless of their age.

``basebackup_hour`` (default undefined)

The hour of day during which to start new basebackup. If backup interval is
less than 24 hours this is the base hour used to calculate the hours at which
backup should be taken. E.g. if backup interval is 6 hours and this value is
set to 1 backups will be taken at hours 1, 7, 13 and 19. This value is only
effective if also ``basebackup_interval_hours`` and ``basebackup_minute`` are
set.

``basebackup_interval_hours`` (default ``24``)

How often to take a new basebackup of a cluster.  The shorter the interval,
the faster your recovery will be, but the more CPU/IO usage is required from
the servers it takes the basebackup from.  If set to a null value basebackups
are not automatically taken at all.

``basebackup_minute`` (default undefined)

The minute of hour during which to start new basebackup. This value is only
effective if also ``basebackup_interval_hours`` and ``basebackup_hour`` are
set.

``basebackup_mode`` (default ``"basic"``)

The way basebackups should be created.  The default mode, ``basic`` runs
``pg_basebackup`` and waits for it to write an uncompressed tar file on the
disk before compressing and optionally encrypting it.  The alternative mode
``pipe`` pipes the data directly from ``pg_basebackup`` to PGHoard's
compression and encryption processing reducing the amount of temporary disk
space that's required.

Neither ``basic`` nor ``pipe`` modes support multiple tablespaces.

Setting ``basebackup_mode`` to ``local-tar`` avoids using ``pg_basebackup``
entirely when ``pghoard`` is running on the same host as the database.
PGHoard reads the files directly from ``$PGDATA`` in this mode and
compresses and optionally encrypts them.  This mode allows backing up user
tablespaces.

When using ``delta`` mode, only changed files are uploaded into the storage.
On every backup snapshot of the data files is taken, this results in a manifest file,
describing the hashes of all the files needed to be backed up.
New hashes are uploaded to the storage and used together with complementary
manifest from control file for restoration.
In order to properly assess the efficiency of ``delta`` mode in comparison with
``local-tar``, one can use ``local-tar-delta-stats`` mode, which behaves the same as
``local-tar``, but also collects the metrics as if it was ``delta`` mode. It can help
in decision making of switching to ``delta`` mode.

``basebackup_threads`` (default ``1``)

How many threads to use for tar, compress and encrypt tasks. Only applies for
``local-tar`` basebackup mode. Only values 1 and 2 are likely to be sensible for
this, with higher thread count speed improvement is negligible and CPU time is
lost switching between threads.

``encryption_key_id`` (no default)

Specifies the encryption key used when storing encrypted backups. If this
configuration directive is specified, you must also define the public key
for storing as well as private key for retrieving stored backups. These
keys are specified with ``encryption_keys`` dictionary.

``encryption_keys`` (no default)

This key is a mapping from key id to keys. Keys in turn are mapping from
``public`` and ``private`` to PEM encoded RSA public and private keys
respectively. Public key needs to be specified for storing backups. Private
key needs to be in place for restoring encrypted backups.

You can use ``pghoard_create_keys`` to generate and output encryption keys
in the ``pghoard`` configuration format.

``object_storage`` (no default)

Configured in ``backup_sites`` under a specific site.  If set, it must be an
object describing a remote object storage.  The object must contain a key
``storage_type`` describing the type of the store, other keys and values are
specific to the storage type.

``proxy_info`` (no default)

Dictionary specifying proxy information. The dictionary must contain keys ``type``,
``host`` and ``port``. Type can be either ``socks5`` or ``http``.  Optionally,
``user`` and ``pass`` can be specified for proxy authentication.  Supported by
Azure, Google and S3 drivers.

The following object storage types are supported:

* ``local`` makes backups to a local directory, see ``pghoard-local-minimal.json``
  for example. Required keys:

 * ``directory`` for the path to the backup target (local) storage directory

* ``sftp`` makes backups to a sftp server, required keys:

 * ``server``
 * ``port``
 * ``username``
 * ``password`` or ``private_key``

* ``google`` for Google Cloud Storage, required configuration keys:

 * ``project_id`` containing the Google Storage project identifier
 * ``bucket_name`` bucket where you want to store the files
 * ``credential_file`` for the path to the Google JSON credential file

* ``s3`` for Amazon Web Services S3, required configuration keys:

 * ``aws_access_key_id`` for the AWS access key id
 * ``aws_secret_access_key`` for the AWS secret access key
 * ``region`` S3 region of the bucket
 * ``bucket_name`` name of the S3 bucket

Optional keys for Amazon Web Services S3:

 * ``encrypted`` if True, use server-side encryption. Default is False.

* ``s3`` for other S3 compatible services such as Ceph, required
  configuration keys:

 * ``aws_access_key_id`` for the AWS access key id
 * ``aws_secret_access_key`` for the AWS secret access key
 * ``bucket_name`` name of the S3 bucket
 * ``host`` for overriding host for non AWS-S3 implementations
 * ``port`` for overriding port for non AWS-S3 implementations
 * ``is_secure`` for overriding the requirement for https for non AWS-S3
 * ``is_verify_tls`` for configuring tls verify for non AWS-S3
   implementations

* ``azure`` for Microsoft Azure Storage, required configuration keys:

 * ``account_name`` for the name of the Azure Storage account
 * ``account_key`` for the secret key of the Azure Storage account
 * ``bucket_name`` for the name of Azure Storage container used to store
   objects
 * ``azure_cloud`` Azure cloud selector, ``"public"`` (default) or ``"germany"``

* ``swift`` for OpenStack Swift, required configuration keys:

 * ``user`` for the Swift user ('subuser' in Ceph RadosGW)
 * ``key`` for the Swift secret_key
 * ``auth_url`` for Swift authentication URL
 * ``container_name`` name of the data container

 * Optional configuration keys for Swift:

  * ``auth_version`` - ``2.0`` (default) or ``3.0`` for keystone, use ``1.0`` with
    Ceph Rados GW.
  * ``segment_size`` - defaults to ``1024**3`` (1 gigabyte).  Objects larger
    than this will be split into multiple segments on upload.  Many Swift
    installations require large files (usually 5 gigabytes) to be segmented.
  * ``tenant_name``
  * ``region_name``
  * ``user_id`` - for auth_version 3.0
  * ``user_domain_id`` - for auth_version 3.0
  * ``user_domain_name`` - for auth_version 3.0
  * ``tenant_id`` - for auth_version 3.0
  * ``project_id`` - for auth_version 3.0
  * ``project_name`` - for auth_version 3.0
  * ``project_domain_id`` - for auth_version 3.0
  * ``project_domain_name`` - for auth_version 3.0
  * ``service_type`` - for auth_version 3.0
  * ``endpoint_type`` - for auth_version 3.0

``nodes`` (no default)

Array of one or more nodes from which the backups are taken.  A node can be
described as an object of libpq key: value connection info pairs or libpq
connection string or a ``postgres://`` connection uri. If for example you'd
like to use a streaming replication slot use the syntax {... "slot": "slotname"}.

``pg_bin_directory`` (default: find binaries from well-known directories)

Site-specific option for finding ``pg_basebackup`` and ``pg_receivexlog``
commands matching the given backup site's PostgreSQL version.  If a value is
not supplied PGHoard will attempt to find matching binaries from various
well-known locations.  In case ``pg_data_directory`` is set and points to a
valid data directory the lookup is restricted to the version contained in
the given data directory.

``pg_data_directory`` (no default)

This is used when the ``local-tar`` ``basebackup_mode`` is used.  The data
directory must point to PostgreSQL's ``$PGDATA`` and must be readable by the
``pghoard`` daemon.

``prefix`` (default: site name)

Path prefix to use for all backups related to this site.  Defaults to the
name of the site.


Alert files
===========

Alert files are created whenever an error condition that requires human
intervention to solve.  You're recommended to add checks for the existence
of these files to your alerting system.

``authentication_error``

There has been a problem in the authentication of at least one of the
PostgreSQL connections.  This usually denotes a wrong username and/or
password.

``configuration_error``

There has been a problem in the authentication of at least one of the
PostgreSQL connections.  This usually denotes a missing ``pg_hba.conf`` entry or
incompatible settings in postgresql.conf.

``upload_retries_warning``

Upload of a file has failed more times than
``upload_retries_warning_limit``. Needs human intervention to figure
out why and to delete the alert once the situation has been fixed.

``version_mismatch_error``

Your local PostgreSQL client versions of ``pg_basebackup`` or
``pg_receivexlog`` do not match with the servers PostgreSQL version.  You
need to update them to be on the same version level.

``version_unsupported_error``

Server PostgreSQL version is not supported.


License
=======

PGHoard is licensed under the Apache License, Version 2.0. Full license text
is available in the ``LICENSE`` file and at
http://www.apache.org/licenses/LICENSE-2.0.txt


Credits
=======

PGHoard was created by Hannu Valtonen <hannu.valtonen@aiven.io> for
`Aiven`_ and is now maintained by Aiven developers <opensource@aiven.io>.

.. _`Aiven`: https://aiven.io/

Recent contributors are listed on the GitHub project page,
https://github.com/aiven/pghoard/graphs/contributors


Contact
=======

Bug reports and patches are very welcome, please post them as GitHub issues
and pull requests at https://github.com/aiven/pghoard .  Any possible
vulnerabilities or other serious issues should be reported directly to the
maintainers <opensource@aiven.io>.


Trademarks
==========

Postgres, PostgreSQL and the Slonik Logo are trademarks or registered trademarks of the PostgreSQL Community Association of Canada, and used with their permission.

Telegraf, Vagrant and Datadog are trademarks and property of their respective owners. All product and service names used in this website are for identification purposes only and do not imply endorsement.


Copyright
=========

Copyright (C) 2015 Aiven Ltd
