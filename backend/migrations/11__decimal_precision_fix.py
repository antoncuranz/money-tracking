import argparse
import psycopg2

from playhouse.migrate import *

# /money-tracking % python -m backend.migrations.XY__abc

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user")
parser.add_argument("-p", "--password")
args = parser.parse_args()

postgres_user = args.user
postgres_passwd = args.password

if postgres_user is None:
    db = PostgresqlDatabase("postgres", user="postgres", password="postgres", host="localhost", port=5433)
else:
    db = PostgresqlDatabase("money-tracking", user=postgres_user, password=postgres_passwd, host="localhost")
migrator = PostgresqlMigrator(db)

######

migrate(
    migrator.alter_column_type("exchange", "exchange_rate", DecimalField(decimal_places=8)),
    migrator.alter_column_type("exchangerate", "exchange_rate", DecimalField(decimal_places=8)),
)
