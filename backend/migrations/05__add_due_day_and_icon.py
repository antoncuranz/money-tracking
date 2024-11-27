import argparse
import psycopg2

from playhouse.migrate import *

# get credentials from k8s money-tracking pod
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user")
parser.add_argument("-p", "--password")
args = parser.parse_args()

postgres_user = args.user
postgres_passwd = args.password

if postgres_user is None:
    db = SqliteDatabase("sqlite.db", pragmas=(("foreign_keys", "on"),))
    migrator = SqliteMigrator(db)
else:
    db = PostgresqlDatabase("money-tracking", user=postgres_user, password=postgres_passwd, host="localhost")
    migrator = PostgresqlMigrator(db)

######

due_day = IntegerField(null=True)
autopay_offset = IntegerField(null=True)
icon = CharField(null=True)
color = CharField(null=True)

migrate(
    migrator.add_column("account", "due_day", due_day),
    migrator.add_column("account", "autopay_offset", autopay_offset),
    migrator.add_column("account", "icon", icon),
    migrator.add_column("account", "color", color),
)
