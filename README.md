Flask-Exceptions
================

# Installation

To install it, simply run

    pip install flask-exceptions

# Usage

Import it and wrap app

    from flask import Flask
    from flask_exceptions import AddExceptions

    app = Flask(__name__)
    exceptions = AddExceptions(app)

You also need to define the
[Flask app error handler](http://flask.pocoo.org/docs/0.12/patterns/errorpages/#error-handlers)
to catch the base exception used (APIException).

    from flask import jsonify
    from flask_exceptions import APIException

    @app.errorhandler(APIException)
    def handle_exceptions(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

You may add a statsd ([pystatsd](https://pypi.python.org/pypi/pystatsd/) interface) counter via app
configuration with `EXCEPTION_COUNTER`.  Pass the namespaced path to the instantiated statsd
StatsClient-like object.
`app.statsd` is the default location the extension will look for a statsd StatsClient-like object.

The default StatsD counter will be in the form `exceptions.xxx` with xxx being the status code.
This does not take into account any prefix you added when instantiating StatsClient itself.

You may customize the prefix of the StatsD key by setting `EXCEPTION_PREFIX` in your Flask
app config. The default prefix is simple `exceptions`.

Also you may configure whether the error returned to the client includes a message or not by
setting `EXCEPTION_MESSAGE` to `False` in your Flask app config. The default is `True`.

When using one of the custom exceptions, you may pass an optional message and payload to the
exception constructor.

    from app import exceptions

    exceptions.bad_request()  # returns 400 with default message (if enabled)

    exceptions.not_found('Nothing to see here')  # returns a 404 with custom error message

    exceptions.conflict('Race condition!', payload={'error': '4-8-15-16-23-42'})  # custom error & payload

# Development

This project was written and tested with Python 3.6.

On a mac you can use the following commands to get up and running.
``` bash
brew install python3
```
otherwise run
``` bash
brew upgrade python3
```
to make sure you have an up to date version.

This project uses [pipenv](https://docs.pipenv.org) for dependency management. Install pipenv
``` bash
pip3 install pipenv
```

setup the project env
``` base
pipenv install --three --dev
```

create a .env file using this sample
``` bash
export PYTHONPATH=`pwd`
```

now load virtualenv and any .env file
```bash
pipenv shell
```

## Running tests

``` bash
python setup.py test
```

## Before committing any code

We have a pre-commit hook each dev needs to setup.
You can symlink it to run before each commit by changing directory to the repo and running

``` bash
cd .git/hooks
ln -s ../../pre-commit pre-commit
```
