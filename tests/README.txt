Tests for OpenLP
================

This directory contains unit tests for OpenLP. The ``functional`` directory contains functional unit tests.

Prerequisites
-------------

In order to run the unit tests, you will need the following Python packages/libraries installed:

 - pytest
 - pylint3

On Ubuntu you can simple install the python3-pytest and pylint3 packages. Most other distributions will also have these
packages. On Windows and Mac OS X you will need to use ``pip`` or ``easy_install`` to install these packages.

Running the Tests
-----------------

To run the tests, navigate to the root directory of the OpenLP project, and then run the following command::

    pytest -v tests

Or, to run only the functional tests, run the following command::

    pytest -v tests/functional

Or, to run only a particular test suite within a file, run the following command::

    pytest -v tests/functional/openlp_core/test_app.py
