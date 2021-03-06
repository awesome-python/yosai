from passlib.totp import TOTP

from yosai.core import (
    DefaultPermission,
    load_logconfig,
    SimpleIdentifierCollection,
    TOTPToken,
    UsernamePasswordToken,
    Yosai,
)

import pytest

load_logconfig()


@pytest.fixture(scope='function')
def thedude_identifier():
    return SimpleIdentifierCollection(source_name='AccountStoreRealm',
                                      identifier='thedude')


@pytest.fixture(scope='function')
def jackie_identifier():
    return SimpleIdentifierCollection(source_name='AccountStoreRealm',
                                      identifier='jackie')


@pytest.fixture(scope='function')
def walter_identifier():
    return SimpleIdentifierCollection(source_name='AccountStoreRealm',
                                      identifier='walter')


@pytest.fixture(scope='function')  # because successful login clears password
def jackie_username_password_token():
    return UsernamePasswordToken(username='jackie',
                                 password='letsgobowling',
                                 remember_me=False,
                                 host='127.0.0.1')


@pytest.fixture(scope='function')  # because successful login clears password
def valid_walter_username_password_token(cache_handler):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    yield UsernamePasswordToken(username='walter',
                                 password='letsgobowling',
                                 remember_me=False,
                                 host='127.0.0.1')

    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

@pytest.fixture(scope='function')  # because successful login clears password
def invalid_walter_username_password_token(cache_handler, yosai, monkeypatch):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)
    with Yosai.context(yosai):
        new_subject = Yosai.get_current_subject()
        da = new_subject.security_manager.authenticator
        monkeypatch.setattr(da.authc_settings, 'account_lock_threshold', 3)
        da.init_locking()
        da.locking_realm.unlock_account('walter')
    yield UsernamePasswordToken(username='walter',
                                 password='letsgobowlinggggg',
                                 remember_me=False,
                                 host='127.0.0.1')

    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)
    with Yosai.context(yosai):
        new_subject = Yosai.get_current_subject()
        da = new_subject.security_manager.authenticator
        monkeypatch.setattr(da.authc_settings, 'account_lock_threshold', 3)
        da.init_locking()
        da.locking_realm.unlock_account('walter')

@pytest.fixture(scope='function')
def valid_thedude_username_password_token(cache_handler):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    yield UsernamePasswordToken(username='thedude',
                                 password='letsgobowling',
                                 remember_me=False,
                                 host='127.0.0.1')

    for key in keys:
        cache_handler.cache_region.delete(key)

@pytest.fixture(scope='function')
def thedude_totp_key():
    return 'DP3RDO3FAAFUAFXQELW6OTB2IGM3SS6G'

@pytest.fixture(scope='function')
def valid_thedude_totp_token(thedude_totp_key, cache_handler):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    token = int(TOTP(key=thedude_totp_key, digits=6).generate().token)
    yield TOTPToken(totp_token=token)

    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)


@pytest.fixture(scope='function')
def invalid_thedude_totp_token(cache_handler, yosai, monkeypatch):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    token = int(TOTP(key='AYAGB3C5RPYX5375L5VY2ULKZXMXWLZF', digits=6).generate().token)
    yield TOTPToken(totp_token=token)

    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    with Yosai.context(yosai):
        new_subject = Yosai.get_current_subject()
        da = new_subject.security_manager.authenticator
        monkeypatch.setattr(da.authc_settings, 'account_lock_threshold', 3)
        da.init_locking()
        da.locking_realm.unlock_account('thedude')


@pytest.fixture(scope='function')  # because successful login clears password
def remembered_valid_thedude_username_password_token(cache_handler):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    yield UsernamePasswordToken(username='thedude',
                                 password='letsgobowling',
                                 remember_me=True,
                                 host='127.0.0.1')

    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

@pytest.fixture(scope='function')
def remembered_valid_thedude_totp_token(thedude_totp_key, cache_handler):
    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)

    token = int(TOTP(key=thedude_totp_key, digits=6).generate().token)
    yield TOTPToken(token, remember_me=True)

    keys = cache_handler.keys('*authentication*')
    for key in keys:
        cache_handler.cache_region.delete(key)


@pytest.fixture(scope='function')
def invalid_thedude_username_password_token(yosai, monkeypatch):
    yield UsernamePasswordToken(username='thedude',
                                 password='never_use__password__',
                                 remember_me=False,
                                 host='127.0.0.1')
    with Yosai.context(yosai):
        new_subject = Yosai.get_current_subject()
        da = new_subject.security_manager.authenticator
        monkeypatch.setattr(da.authc_settings, 'account_lock_threshold', 3)
        da.init_locking()
        da.locking_realm.unlock_account('thedude')


@pytest.fixture(scope='function')
def thedude_testpermissions():
    perm1 = DefaultPermission('money:write:bankcheck_19911109069')
    perm2 = DefaultPermission('money:withdrawal')
    perm3 = DefaultPermission('leatherduffelbag:transport:theringer')
    perm4 = DefaultPermission('leatherduffelbag:access:theringer')

    perms = [perm1, perm2, perm3, perm4]

    expected_results = frozenset([(perm1, True), (perm2, False),
                                  (perm3, True), (perm4, False)])

    return dict(perms=perms, expected_results=expected_results)


@pytest.fixture(scope='function')
def thedude_testroles():
    roles = {'bankcustomer', 'courier', 'gangster'}

    expected_results = frozenset([('bankcustomer', True),
                                  ('courier', True),
                                  ('gangster', False)])

    return dict(roles=roles, expected_results=expected_results)


@pytest.fixture(scope='function')
def jackie_testpermissions():

    perm1 = DefaultPermission('money:access:ransom')
    perm2 = DefaultPermission('leatherduffelbag:access:theringer')
    perm3 = DefaultPermission('money:withdrawal')

    perms = [perm1, perm2, perm3]

    expected_results = frozenset([(perm1, True), (perm2, True),
                                  (perm3, False)])

    return dict(perms=perms, expected_results=expected_results)


@pytest.fixture(scope='function')
def walter_testpermissions():

    perm1 = DefaultPermission('leatherduffelbag:transport:theringer')
    perm2 = DefaultPermission('leatherduffelbag:access:theringer')
    perm3 = DefaultPermission('*:bowl:*')

    perms = [perm1, perm2, perm3]

    expected_results = frozenset([(perm1, True), (perm2, False),
                                  (perm3, True)])

    return dict(perms=perms, expected_results=expected_results)
