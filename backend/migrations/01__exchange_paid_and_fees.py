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

amount_eur = IntegerField(null=True)
fees_eur = IntegerField(null=True)

migrate(
    migrator.rename_column("exchange", "amount_eur", "paid_eur"),
    migrator.add_column("exchange", "amount_eur", amount_eur),
    migrator.add_column("exchange", "fees_eur", fees_eur),
)
