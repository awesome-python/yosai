from yosai.authz import abcs as authz_abcs

class MockAuthzAccountStoreRealm(authz_abcs.Authorizer,
                                 authz_abcs.PermissionResolverAware,
                                 authz_abcs.RolePermissionResolverAware):

    def __init__(self):
        self.id = id(self)  # required for uniqueness among set members
        self._permission_resolver = None

    def check_permission(self, principals, permission_s):
        pass
    
    def check_role(self, principals, role_s):
        return False 

    def has_role(self, principals, roleid_s):
        return False 

    def has_all_roles(self, principals, roleid_s):
        return False 

    def is_permitted(self, principals, permission_s):
        return False 

    def is_permitted_all(self, principals, permission_s):
        return False 

    @property
    def permission_resolver(self):
        return self._permission_resolver 

    @permission_resolver.setter
    def permission_resolver(self, permission_resolver):
        self._permission_resolver = permission_resolver 
    
    @property
    def role_permission_resolver(self):
        return self._role_permission_resolver 

    @permission_resolver.setter
    def role_permission_resolver(self, permission_resolver):
        self._role_permission_resolver = permission_resolver 


class MockPermission(authz_abcs.Permission):
   
    # using init to define whether implies is always True or False
    def __init__(self, implied):
        self.implied = implied

    def implies(self, permission):
        return self.implied