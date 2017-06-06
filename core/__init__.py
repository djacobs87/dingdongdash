from organizations.apps import OrganizationsConfig

default_app_config = 'core.apps.CoreConfig'

class DDDOrganizationConfig(OrganizationsConfig):
    verbose_name = "User Management"