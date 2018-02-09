"""A base set of API Exceptions for Flask apps."""
from setuptools import setup

setup(
    name='Flask-Exceptions',
    version='1.0.1',
    url='https://github.com/bbelyeu/flask-exceptions',
    download_url='https://github.com/bbelyeu/flask-exceptions/archive/1.0.1.zip',
    license='MIT',
    author='Brad Belyeu',
    author_email='bradleylamar@gmail.com',
    description='A base set of API Exceptions for Flask apps',
    long_description=__doc__,
    packages=['flask_exceptions'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=['flask', 'exceptions', 'api'],
    test_suite='flask_exceptions.tests',
)
