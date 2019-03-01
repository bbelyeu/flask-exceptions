"""Flask Exceptions Extension module."""
from functools import wraps

DEFAULT_PREFIX = 'exceptions'


def exception(message):
    """Exception method convenience wrapper."""

    def decorator(method):
        """Inner decorator so we can accept arguments."""

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            """Innermost decorator wrapper - this is confusing."""
            if self.messages:
                kwargs['message'] = args[0] if args else kwargs.get('message', message)
            else:
                kwargs['message'] = None
            kwargs['prefix'] = self.prefix
            kwargs['statsd'] = self.statsd

            return method(self, **kwargs)

        return wrapper

    return decorator


class APIException(Exception):
    """Initialize the Exception with a code, message, and payload."""

    def __init__(self, status_code, message=None, payload=None, prefix='exceptions', statsd=None):
        super(APIException, self).__init__(*((message,) if message else ()))
        self.status_code = status_code
        self.message = message
        self.payload = payload

        if statsd:
            key = '{}.{}'.format(prefix, status_code) if prefix else '{}'.format(status_code)
            statsd.incr(key)

    def to_dict(self):
        """Convert Exception class to a Python dictionary."""
        val = dict(self.payload or ())
        if self.message:
            val['message'] = self.message
        return val

# Sorted by error code


class BadRequest(APIException):
    """A 400 Exception normally coming from request parameter validation."""
    def __init__(self, **kwargs):
        super().__init__(400, **kwargs)


class Unauthorized(APIException):
    """A 401 Unauthorized error from bad authentication."""
    def __init__(self, **kwargs):
        super().__init__(401, **kwargs)


class Forbidden(APIException):
    """A 403 Forbidden exception when a user doesn't have access to a resource."""
    def __init__(self, **kwargs):
        super().__init__(403, **kwargs)


class NotFound(APIException):
    """A 404 typical exception when a resource can't be found in datastores."""
    def __init__(self, **kwargs):
        super().__init__(404, **kwargs)


class Conflict(APIException):
    """A 409 conflict when there's a conflict creating or updating a resource."""
    def __init__(self, **kwargs):
        super().__init__(409, **kwargs)


class Gone(APIException):
    """A 410 gone when let clients know a resource previously existed but has been removed."""
    def __init__(self, **kwargs):
        super().__init__(410, **kwargs)


class UnsupportedMedia(APIException):
    """A 415 indicates an invalid Accept or Content-Type header."""
    def __init__(self, **kwargs):
        super().__init__(415, **kwargs)


class UnprocessableEntity(APIException):
    """A 422 POST or PUT means the parameters given can't be used."""
    def __init__(self, **kwargs):
        super().__init__(422, **kwargs)


class FailedDependency(APIException):
    """
    A 424 Failed Dependency Exception.

    From httpstatuses.com:
    The method could not be performed on the resource because the requested
    action depended on another action and that action failed.
    """
    def __init__(self, **kwargs):
        super().__init__(424, **kwargs)


class AddExceptions():
    """Class to wrap Flask app and provide access to additional exceptions."""

    def __init__(self, app=None, config=None, statsd=None):
        self.config = config
        if app is not None:
            self.app = app
            self.init_app(app, statsd=statsd)
        else:
            self.app = None

    def init_app(self, app, config=None, statsd=None):
        """Init Flask Extension."""
        if config is not None:
            self.config = config
        elif self.config is None:
            self.config = app.config

        self.messages = self.config.get('EXCEPTION_MESSAGE', True)
        self.prefix = self.config.get('EXCEPTION_PREFIX', DEFAULT_PREFIX)
        self.statsd = statsd

    # Exception class wrappers sorted by error code

    @exception('Invalid request parameters')
    def bad_request(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 400."""
        return BadRequest(**kwargs)

    @exception('Unauthorized')
    def unauthorized(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 401."""
        return Unauthorized(**kwargs)

    @exception('Forbidden')
    def forbidden(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 403."""
        return Forbidden(**kwargs)

    @exception('Resource not found')
    def not_found(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 404."""
        return NotFound(**kwargs)

    @exception('Conflict')
    def conflict(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 409."""
        return Conflict(**kwargs)

    @exception('Gone')
    def gone(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 410."""
        return Gone(**kwargs)

    @exception('Unsupported Media')
    def unsupported_media(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 415."""
        return UnsupportedMedia(**kwargs)

    @exception('Unprocessable Entity')
    def unprocessable_entity(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 422."""
        return UnprocessableEntity(**kwargs)

    @exception('Failed Dependency')
    def failed_dependency(self, *_, **kwargs):
        """Return an Exception to use when you want to return a 424."""
        return FailedDependency(**kwargs)
