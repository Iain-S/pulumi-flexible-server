# Migrate Single to Flexible Postgres Server

Migrating from an Azure Database for PostgreSQL Single Server (deprecated in 2025) to a Flexible Server.

An unknown (unknowable?) IP address needs to be added to the firewall rules in order to create a new user.

## Instructions

1. Install the project with, for example, `poetry install; poetry shell`.

### Single Server

Note that this creates a firewall rule to 

1. Choose Single Server with `pulumi config set SINGLE_OR_FLEXI SINGLE`.
1. Set your IP address for the firewall with `pulumi config set MY_IP <your-ip-address>`.
2. Run `pulumi up`.
3. Connect as the new user with `psql --username=carebear@single-server-8765 --host=single-server-8765.postgres.database.azure.com --dbname=postgres`.
4. Use the password printed to console during the `pulumi up` step.

### Flexible Server

1. Choose Flexible Server with `pulumi config set SINGLE_OR_FLEXI FLEXI`.
2. Run `pulumi up`.
3. Get an error (see below)

```text
Diagnostics:
  postgresql:index:Role (dev-role):
    error: 1 error occurred:
        * error detecting capabilities: error PostgreSQL version: read tcp 10.10.8.16:51843->20.108.54.30:5432: read: connection reset by peer
```
