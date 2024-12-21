import argparse
import psycopg2

from playhouse.migrate import *

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

status = IntegerField(null=True)
import_id = CharField(unique=True, null=True)

migrate(
    migrator.add_column("payment", "status", status),
    migrator.add_column("exchange", "import_id", import_id),

    migrator.drop_not_null("payment", "import_id"),
    migrator.drop_not_null("payment", "category"),
    migrator.drop_not_null("transaction", "category"),
    migrator.drop_not_null("credit", "category")
)

class BaseModel(Model):
    class Meta:
        database = db

class Payment(BaseModel):
    id = AutoField()
    processed = BooleanField(default=False)
    pending = BooleanField(default=False)
    status = IntegerField(null=True)

for payment in Payment.select():
    payment.status = 3 if payment.processed else 2
    payment.save()

migrate(
    migrator.add_not_null("payment", "status"),
    migrator.drop_column("payment", "processed"),
    migrator.drop_column("payment", "pending"),
)
