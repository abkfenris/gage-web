from flask_script import Manager
from flask_security.script import (CreateUserCommand,
                                   CreateRoleCommand,
                                   AddRoleCommand,
                                   RemoveRoleCommand,
                                   ActivateUserCommand,
                                   DeactivateUserCommand)


def sub_opts(app, **kwargs):
    pass

user_manager_desc = ('User management. Use email address as username.')
user_manager = Manager(sub_opts, usage='User and role management',
                       description=user_manager_desc)


class CreateUserC(CreateUserCommand):
    """
    Create a user:
    -e or --email name@server.com,
    -p or --password initialpass,
    -a or --active y or active
    """
    pass


class CreateRoleC(CreateRoleCommand):
    """
    Create a role:
    -n or --name role_name,
    -d or --desc role_description
    """
    pass


class AddRoleC(AddRoleCommand):
    """
    Add a role to a user:
    -u or --user name@server.com,
    -r or --role role_name
    """
    pass


class RemoveRoleC(RemoveRoleCommand):
    """
    Removes a role to a user:
    -u or --user name@server.com,
    -r or --role role_name
    """
    pass


class ActivateUserC(ActivateUserCommand):
    """
    Activates a user:
    -u or --user name@server.com
    """
    pass


class DeactivateUserC(DeactivateUserCommand):
    """
    Deactivates a user:
    -u or --user name@server.com
    """
    pass


user_manager.add_command('create_user', CreateUserC())
user_manager.add_command('create_role', CreateRoleC())
user_manager.add_command('add_role', AddRoleC())
user_manager.add_command('remove_role', RemoveRoleC())
user_manager.add_command('activate_user', ActivateUserC())
user_manager.add_command('deactivate_user', DeactivateUserC())
