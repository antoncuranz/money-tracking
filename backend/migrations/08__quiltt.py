import argparse
import psycopg2

from playhouse.migrate import *

from backend.models import BankAccount

# /money-tracking % python -m backend.migrations.08__quiltt

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
    # db = PostgresqlDatabase("money-tracking", user=postgres_user, password=postgres_passwd, host="localhost")
    db = PostgresqlDatabase("postgres", user=postgres_user, password=postgres_passwd, host="localhost", port=5433)
    migrator = PostgresqlMigrator(db)

######

db.create_tables([BankAccount])

bank_account = ForeignKeyField(BankAccount, BankAccount.id, backref="user", null=True)
pending = BooleanField(default=False)

migrate(
    migrator.rename_column("account", "teller_id", "import_id"),
    migrator.add_column("account", "bank_account_id", bank_account),
    migrator.drop_column("account", "teller_access_token"),
    migrator.drop_column("account", "teller_enrollment_id"),
    migrator.drop_not_null("account", "actual_id"),

    migrator.rename_column("payment", "teller_id", "import_id"),
    migrator.add_column("payment", "pending", pending),

    migrator.rename_column("transaction", "teller_id", "import_id"),

    migrator.rename_column("credit", "teller_id", "import_id")
)
