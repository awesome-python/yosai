"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from abc import ABCMeta, abstractmethod


class AccountStore(metaclass=ABCMeta):
    pass

#    @abstractmethod
#    def get_account(self, request):
#        """
#        Obtains the most complete Account object available from the AccountStore,
#        consisting of both authentication AND authorization related information
#        when they are available.
#
#        :param request:  the request object defining the criteria by which
#                         to query the account store
#        :type request:  AuthenticationToken or Account
#
#        :returns: Account
#        """
#        pass


class LockingAccountStore(AccountStore):

    @abstractmethod
    def lock_account(self, account):
        pass


class CredentialsAccountStore(AccountStore):

    @abstractmethod
    def get_authc_info(self, authc_token):
        """
        :returns: Account
        """
        pass


class AuthorizationAccountStore(AccountStore):

    @abstractmethod
    def get_authz_info(self, identifiers):
        """
        creates an Account that includes only the authorization information
        (and not credentials)
        :returns: Account
        """
        pass
