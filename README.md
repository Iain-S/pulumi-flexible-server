# Migrate Single to Flexible Postgres Server

Migrating from an Azure Database for PostgreSQL Single Server (deprecated in 2025) to a Flexible Server.

An unknown (unknowable?) IP address needs to be added to the firewall rules in order to create a new user.

**Update** The issue seems to be fixed by downloading the `DigiCert Global Root CA` lined to from [this](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-connect-tls-ssl#applications-that-require-certificate-verification-for-tlsssl-connectivity) Microsoft page and providing the local path to it to the `Provider`.

## Instructions

1. Install the project with, for example, `poetry install; poetry shell`.

### Single Server

1. Choose Single Server with `pulumi config set SINGLE_OR_FLEXI SINGLE`.
2. Set your IP address for the firewall with `pulumi config set MY_IP <your-ip-address>`.
3. Run `pulumi up`.
4. Connect as the new user with `psql --username=carebear@single-server-8765 --host=single-server-8765.postgres.database.azure.com --dbname=postgres`.
5. Use the password printed to console during the `pulumi up` step.

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

### Flexible Server with Root Cert

1. Download this [DigiCertGlobalRootCA.crt.pem](https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem) file.
2. Set the path to it with `pulumi config set DB_ROOT_CERT_PATH /path/to/your/downloaded/DigiCertGlobalRootCA.crt.pem`.
3. Run `pulumi up`
4. Connect as the new user with `psql --username=carebear --host=flexi-server-8765.postgres.database.azure.com --dbname=postgres`.
5. Use the password printed to console during the `pulumi up` step.
