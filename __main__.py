"""Pulumi script for creating a Function App (and dependencies) on Azure."""
import pulumi
import pulumi_random
from pulumi import ResourceOptions, Output
from pulumi_azure_native import resources
from pulumi_postgresql import Provider, ProviderArgs, Role, RoleArgs

import pulumi_azure_native.dbforpostgresql.v20221201 as flexi_server
import pulumi_azure_native.dbforpostgresql as single_server

config = pulumi.Config()

STACK_NAME = f"{pulumi.get_stack()}"

# "FLEXI" for flexi server and "SINGLE" for single server
SINGLE_OR_FLEXI = config.require("SINGLE_OR_FLEXI")
assert SINGLE_OR_FLEXI in ("SINGLE", "FLEXI"), "Expected SINGLE or FLEXI"


# E.g. ask Google for your IP
MY_IP = config.require_secret("MY_IP")

DB_ADMIN_USERNAME = "honeybadger"


resource_group = resources.ResourceGroup(
    f"{STACK_NAME}-rg",
    resources.ResourceGroupArgs(location="UK South"),
)
password = pulumi_random.RandomPassword(
    "db-password",
    length=16,
    special=True,
    override_special="_@",
    opts=ResourceOptions(additional_secret_outputs=["result"]),
)
password.result.apply(lambda x: print("password:", x))

if SINGLE_OR_FLEXI == "FLEXI":
    server = flexi_server.Server(
        f"{SINGLE_OR_FLEXI}-{STACK_NAME}-server",
        flexi_server.ServerArgs(
            resource_group_name=resource_group.name,
            location=resource_group.location,
            server_name=f"{SINGLE_OR_FLEXI.lower()}-server-8765",
            version=flexi_server.ServerVersion.SERVER_VERSION_11,
            create_mode="Default",
            administrator_login=DB_ADMIN_USERNAME,
            administrator_login_password=password.result,
            storage=flexi_server.StorageArgs(storage_size_gb=128),
            sku=flexi_server.SkuArgs(
                name="Standard_B2s", tier=flexi_server.SkuTier.BURSTABLE
            ),
        ),
    )

    database = flexi_server.Database(
        f"{SINGLE_OR_FLEXI}-{STACK_NAME}-db",
        flexi_server.DatabaseArgs(
            resource_group_name=resource_group.name,
            server_name=server.name,
            database_name="mydbname",
        ),
    )
    firewall_rule = flexi_server.FirewallRule(
        f"{SINGLE_OR_FLEXI}-{STACK_NAME}-firewall",
        flexi_server.FirewallRuleArgs(
            start_ip_address=MY_IP,
            end_ip_address=MY_IP,
            firewall_rule_name="access_ip",
            resource_group_name=resource_group.name,
            server_name=server.name,
        ),
    )
else:
    # else SINGLE
    server = single_server.Server(
        f"{SINGLE_OR_FLEXI}-{STACK_NAME}-server",
        single_server.ServerArgs(
            resource_group_name=resource_group.name,
            location=resource_group.location,
            server_name=f"{SINGLE_OR_FLEXI}-server-8765",
            sku=single_server.SkuArgs(
                capacity=2,
                family="Gen5",
                name="GP_Gen5_2",
                tier="GeneralPurpose",
            ),
            properties=single_server.ServerPropertiesForDefaultCreateArgs(
                administrator_login=DB_ADMIN_USERNAME,
                administrator_login_password=password.result,
                create_mode="Default",
                minimal_tls_version="TLS1_2",
                ssl_enforcement=single_server.SslEnforcementEnum.ENABLED,
                storage_profile=single_server.StorageProfileArgs(
                    backup_retention_days=7,
                    geo_redundant_backup="Disabled",
                    storage_mb=5120,
                    storage_autogrow="Enabled",
                ),
                version="11",
            ),
        ),
    )

    database = single_server.Database(
        f"{SINGLE_OR_FLEXI}-{STACK_NAME}-db",
        single_server.DatabaseArgs(
            resource_group_name=resource_group.name,
            server_name=server.name,
            database_name="mydbname",
        ),
    )

    firewall_rule = single_server.FirewallRule(
        f"{SINGLE_OR_FLEXI}-{STACK_NAME}-firewall",
        single_server.FirewallRuleArgs(
            start_ip_address=MY_IP,
            end_ip_address=MY_IP,
            firewall_rule_name="access_ip",
            resource_group_name=resource_group.name,
            server_name=server.name,
        ),
    )

admin_full_username = Output.concat(DB_ADMIN_USERNAME, "@", server.name)

provider = Provider(
    f"{STACK_NAME}-provider",
    ProviderArgs(
        host=server.fully_qualified_domain_name,
        username=admin_full_username,
        password=password.result,
        superuser=False,
        sslmode="require",
    ),
    # The provider seems to need to access the server
    opts=ResourceOptions(depends_on=firewall_rule),
)

new_user = Role(
    f"{STACK_NAME}-role",
    RoleArgs(
        login=True,
        name="carebear",
        password=password.result,
        skip_drop_role=True,
        skip_reassign_owned=True,
    ),
    opts=ResourceOptions(provider=provider)
)
