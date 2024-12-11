import argparse
import psycopg2

from playhouse.migrate import *

from backend.models import User

# /money-tracking % python -m backend.migrations.07__add_users

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

db.create_tables([User])

User.create(name="ant0n", super_user=True)

user = ForeignKeyField(User, User.id, backref="accounts", default=1)

migrate(
    migrator.add_column("account", "user_id", user),
    migrator.drop_column_default("account", "user_id")
)
