"""Test the statsd extension module."""
# pylint: disable=no-member
import unittest
from functools import wraps
from unittest.mock import MagicMock

from flask import Flask

from flask_exceptions import AddExceptions, extension  # isort:skip


def create_app():
    """Create a Flask app for context."""
    app = Flask(__name__)
    exceptions = AddExceptions()
    exceptions.init_app(app)
    return app


def mock_statsd(func):
    """Decorator to mock statsd object."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Wrapper for mocking statsd."""
        self.app.statsd = MagicMock()
        self.app.statsd.incr = MagicMock()
        return func(self, *args, **kwargs)

    return wrapper


class TestExceptions(unittest.TestCase):
    """Test extension module."""

    def setUp(self):
        """Set up tests."""
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Tear down tests."""
        self.ctx.pop()

    def test_default_config(self):
        """Test the default configs."""
        exceptions = AddExceptions(self.app)
        self.assertEqual(True, exceptions.messages)
        self.assertEqual(extension.DEFAULT_PREFIX, exceptions.prefix)
        self.assertEqual(None, exceptions.statsd)

    def test_custom_app_config(self):
        """Test custom configs set on app."""
        self.app.config['EXCEPTION_MESSAGE'] = False
        self.app.config['EXCEPTION_PREFIX'] = 'foo'
        self.app.config['EXCEPTION_COUNTER'] = 'instrumentation'

        self.app.instrumentation = MagicMock()
        exceptions = AddExceptions(self.app)

        self.assertEqual(False, exceptions.messages)
        self.assertEqual('foo', exceptions.prefix)
        self.assertIsInstance(exceptions.statsd, MagicMock)

    def test_init_kwarg_config(self):
        """Test custom configs passed via kwargs."""
        config = {
            'EXCEPTION_MESSAGE': False,
            'EXCEPTION_PREFIX': 'foo',
            'EXCEPTION_COUNTER': 'instrumentation'
        }

        self.app.instrumentation = MagicMock()
        exceptions = AddExceptions(self.app, config)

        self.assertEqual(False, exceptions.messages)
        self.assertEqual('foo', exceptions.prefix)
        self.assertIsInstance(exceptions.statsd, MagicMock)

    def test_init_app_kwarg_config(self):
        """Test custom configs passed via kwargs to init_app."""
        config = {
            'EXCEPTION_MESSAGE': False,
            'EXCEPTION_PREFIX': 'foo',
            'EXCEPTION_COUNTER': 'instrumentation'
        }

        self.app.instrumentation = MagicMock()
        exceptions = AddExceptions()
        exceptions.init_app(self.app, config)

        self.assertEqual(False, exceptions.messages)
        self.assertEqual('foo', exceptions.prefix)
        self.assertIsInstance(exceptions.statsd, MagicMock)

    # Test ALL flows with 400/Bad Request once, then each exception shouldn't need to test
    # each edge case usage

    @mock_statsd
    def test_bad_request(self):
        """Test BadRequest/400 exception."""
        exceptions = AddExceptions(self.app)
        bad_request = exceptions.bad_request()

        self.assertIsInstance(bad_request, extension.BadRequest)
        self.assertDictEqual(bad_request.to_dict(), {'message': 'Invalid request parameters'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.400')

    @mock_statsd
    def test_bad_request_custom_msg_arg(self):
        """Test BadRequest/400 exception with a custom error message passed as an arg."""
        exceptions = AddExceptions(self.app)
        bad_request = exceptions.bad_request('Oh noes!')

        self.assertIsInstance(bad_request, extension.BadRequest)
        self.assertDictEqual(bad_request.to_dict(), {'message': 'Oh noes!'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.400')

    @mock_statsd
    def test_bad_request_custom_msg(self):
        """Test BadRequest/400 exception with a custom error message passed as a kwarg."""
        exceptions = AddExceptions(self.app)
        bad_request = exceptions.bad_request(message='Oh noes!')

        self.assertIsInstance(bad_request, extension.BadRequest)
        self.assertDictEqual(bad_request.to_dict(), {'message': 'Oh noes!'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.400')

    @mock_statsd
    def test_bad_request_no_msg(self):
        """Test BadRequest/400 exception with no message."""
        self.app.config['EXCEPTION_MESSAGE'] = False
        exceptions = AddExceptions(self.app)
        bad_request = exceptions.bad_request()

        self.assertIsInstance(bad_request, extension.BadRequest)
        self.assertDictEqual(bad_request.to_dict(), {})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.400')

    @mock_statsd
    def test_bad_request_payload(self):
        """Test BadRequest/400 exception with custom payload."""
        exceptions = AddExceptions(self.app)
        bad_request = exceptions.bad_request(payload={'code': '4-8-15-16-23-42'})

        self.assertIsInstance(bad_request, extension.BadRequest)
        self.assertDictEqual(bad_request.to_dict(), {
            'code': '4-8-15-16-23-42', 'message': 'Invalid request parameters'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.400')

    @mock_statsd
    def test_bad_request_no_statsd(self):
        """Test BadRequest/400 exception with no statsd object in config."""
        self.app.config['EXCEPTION_COUNTER'] = None
        exceptions = AddExceptions(self.app)
        bad_request = exceptions.bad_request()

        self.assertIsInstance(bad_request, extension.BadRequest)
        self.assertDictEqual(bad_request.to_dict(), {'message': 'Invalid request parameters'})
        self.app.statsd.incr.assert_not_called()

    @mock_statsd
    def test_unauthorized(self):
        """Test Unauthorized/401 exception."""
        exceptions = AddExceptions(self.app)
        unauthorized = exceptions.unauthorized()

        self.assertIsInstance(unauthorized, extension.Unauthorized)
        self.assertDictEqual(unauthorized.to_dict(), {'message': 'Unauthorized'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.401')

    @mock_statsd
    def test_forbidden(self):
        """Test Forbidden/403 exception."""
        exceptions = AddExceptions(self.app)
        forbidden = exceptions.forbidden()

        self.assertIsInstance(forbidden, extension.Forbidden)
        self.assertDictEqual(forbidden.to_dict(), {'message': 'Forbidden'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.403')

    @mock_statsd
    def test_not_found(self):
        """Test NotFound/404 exception."""
        exceptions = AddExceptions(self.app)
        not_found = exceptions.not_found()

        self.assertIsInstance(not_found, extension.NotFound)
        self.assertDictEqual(not_found.to_dict(), {'message': 'Resource not found'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.404')

    @mock_statsd
    def test_conflict(self):
        """Test Conflict/409 exception."""
        exceptions = AddExceptions(self.app)
        conflict = exceptions.conflict()

        self.assertIsInstance(conflict, extension.Conflict)
        self.assertDictEqual(conflict.to_dict(), {'message': 'Conflict'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.409')

    @mock_statsd
    def test_gone(self):
        """Test Gone/410 exception."""
        exceptions = AddExceptions(self.app)
        gone = exceptions.gone()

        self.assertIsInstance(gone, extension.Gone)
        self.assertDictEqual(gone.to_dict(), {'message': 'Gone'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.410')

    @mock_statsd
    def test_unsupported_media(self):
        """Test UnsupportedMedia/415 exception."""
        exceptions = AddExceptions(self.app)
        unsupported_media = exceptions.unsupported_media()

        self.assertIsInstance(unsupported_media, extension.UnsupportedMedia)
        self.assertDictEqual(unsupported_media.to_dict(), {'message': 'Unsupported Media'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.415')

    @mock_statsd
    def test_unprocessable_entity(self):
        """Test UnprocessableEntity/422 exception."""
        exceptions = AddExceptions(self.app)
        unprocessable_entity = exceptions.unprocessable_entity()

        self.assertIsInstance(unprocessable_entity, extension.UnprocessableEntity)
        self.assertDictEqual(unprocessable_entity.to_dict(), {'message':
                                                              'Unprocessable Entity'})
        self.app.statsd.incr.assert_called_once_with(extension.DEFAULT_PREFIX + '.422')
