import pytest
from unittest import mock
from yosai.core.subject.subject import global_subject_context, global_yosai_context
from yosai.web.subject.subject import global_webregistry_context

from yosai.core import (
    AuthorizationException,
    DelegatingSubject,
    SubjectBuilder,
    IdentifiersNotSetException,
    IllegalStateException,
    YosaiContextException,
    Yosai,
)

from yosai.core.subject.subject import (
    global_subject_context,
)


@mock.patch.object(global_subject_context, 'stack')
def test_yosai_get_subject_returns_subject(mock_stack, yosai, monkeypatch):
    mock_sb = mock.create_autospec(SubjectBuilder)
    mock_sb.build_subject.return_value = 'built'
    monkeypatch.setattr(yosai, 'subject_builder', mock_sb)
    result = yosai._get_subject()

    mock_sb.build_subject.assert_called_once_with()
    mock_stack.append.assert_called_once_with('built')
    assert result == 'built'


def test_yosai_context(yosai):
    """
    When entering a new Yosai context, a yosai instance is pushed onto a yosai_context
    stack.
    When closing the context: the global_yosai_context stack is cleared as is the
    global_subject_context stack.

    elements tested include:
        get_current_yosai
        get_current_subject
    """
    # first ensure that the threadlocal is empty
    assert (global_subject_context.stack == [] and
            global_yosai_context.stack == [])

    with Yosai.context(yosai):
        assert (global_subject_context.stack == [] and
                global_yosai_context.stack == [yosai])

    # this tests context exit
    assert (global_subject_context.stack == [] and
            global_yosai_context.stack == [])


def test_requires_authentication_succeeds(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    @staticmethod
    def mock_gcs():
        return mock.MagicMock(authenticated=True)

    @staticmethod
    def mock_cwr():
        m = mock.MagicMock()
        m.raise_unauthorized.return_value = Exception
        return m

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_authentication
    def do_this():
        return 'dothis'

    result = do_this()

    assert result == 'dothis'


def test_requires_authentication_raises(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    @staticmethod
    def mock_gcs():
        return mock.MagicMock(authenticated=False)

    @staticmethod
    def mock_cwr():
        m = mock.MagicMock()
        m.raise_unauthorized.return_value = Exception
        return m

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_authentication
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_user_succeeds(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    @staticmethod
    def mock_gcs():
        return mock.MagicMock(identifiers='username12345')

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_user
    def do_this():
        return 'dothis'

    result = do_this()

    assert result == 'dothis'


def test_requires_user_raises(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    @staticmethod
    def mock_gcs():
        return mock.MagicMock(identifiers=None)

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_user
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_guest(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    Two parametrized tests:  one that succeeds and another that fails
    """
    @staticmethod
    def mock_gcs():
        return mock.MagicMock(identifiers=None)

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_guest
    def do_this():
        return 'dothis'

    result = do_this()

    assert result == 'dothis'


def test_requires_guest_raises(monkeypatch):

    @staticmethod
    def mock_gcs():
        return mock.MagicMock(identifiers='userid12345')

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_guest
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_permission_succeeds(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    mock_ds = mock.create_autospec(DelegatingSubject)

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_permission(['something:anything'])
    def do_this():
        return 'dothis'

    result = do_this()

    assert result == 'dothis'
    mock_ds.check_permission.assert_called_once_with(['something:anything'], all)


def test_requires_permission_raises_one(monkeypatch):

    @staticmethod
    def mock_gcs():
        m = mock.create_autospec(DelegatingSubject)
        m.check_permission.side_effect = IdentifiersNotSetException

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_permission(['something_anything'])
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_permission_raises_two(monkeypatch):

    mock_ds = mock.create_autospec(DelegatingSubject)
    mock_ds.check_permission.side_effect = AuthorizationException

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_permission(['something_anything'])
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_dynamic_permission_succeeds(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    mock_ds = mock.create_autospec(DelegatingSubject)

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_dynamic_permission(['something:anything:{one}'])
    def do_that(one='one'):
        return 'dothis'

    result = do_that(one='one')

    assert result == 'dothis'
    mock_ds.check_permission.assert_called_once_with(['something:anything:one'], all)


def test_requires_dynamic_permission_raises_one(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    mock_ds = mock.create_autospec(DelegatingSubject)
    mock_ds.check_permission.side_effect = IdentifiersNotSetException

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_dynamic_permission(['something:anything:{one}'])
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_dynamic_permission_raises_two(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """
    mock_ds = mock.create_autospec(DelegatingSubject)
    mock_ds.check_permission.side_effect = AuthorizationException

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_dynamic_permission(['something:anything:{one}'])
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_role_succeeds(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """

    mock_ds = mock.create_autospec(DelegatingSubject)

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_role(['role1'])
    def do_this():
        return 'dothis'

    result = do_this()

    assert result == 'dothis'
    mock_ds.check_role.assert_called_once_with(['role1'], all)


def test_requires_role_raises_one(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """

    mock_ds = mock.create_autospec(DelegatingSubject)
    mock_ds.check_role.side_effect = IdentifiersNotSetException

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_role(['role1'])
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()


def test_requires_role_raises_two(monkeypatch):
    """
    This test verifies that the decorator works as expected.
    """

    mock_ds = mock.create_autospec(DelegatingSubject)
    mock_ds.check_role.side_effect = AuthorizationException

    @staticmethod
    def mock_gcs():
        return mock_ds

    monkeypatch.setattr(Yosai, 'get_current_subject', mock_gcs)

    @Yosai.requires_role(['role1'])
    def do_this():
        return 'dothis'

    with pytest.raises(Exception):
        do_this()
