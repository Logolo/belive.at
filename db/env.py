# -*- coding: utf-8 -*-

"""Boilerplate to run ``alembic`` in online mode, using the ``sqlalchemy.*``
  configuration from the ``[app:main]`` section of the ``.ini`` config.
"""

# Import the ``alembic.environment.EnvironmentContext`` instance, populated by
# the current ``alembic ...`` command as ``context``.
from alembic import context
config = context.config

# Setup logging.
from logging.config import fileConfig
fileConfig(config.config_file_name)

# Run migrations in online mode, connecting to the db with an SQLAlchemy Engine.
from sqlalchemy import engine_from_config, pool
config_section = config.get_section('app:main')
engine = engine_from_config(config_section, prefix='sqlalchemy.',
                            poolclass=pool.NullPool)
connection = engine.connect()
context.configure(connection=connection)
try:
    with context.begin_transaction():
        context.run_migrations()
finally:
    connection.close()

