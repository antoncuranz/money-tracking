import argparse
import psycopg2

from playhouse.migrate import *

from backend import User

# /money-tracking % python -m backend.migrations.09__pending_payments

# get credentials from k8s money-tracking pod
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

user = ForeignKeyField(User, User.id, backref="bank_accounts", default=1)

migrate(
    migrator.add_column("bankaccount", "user_id", user),
    migrator.drop_column_default("bankaccount", "user_id")
)
