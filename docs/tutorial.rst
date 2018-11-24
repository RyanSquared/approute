.. _tutorial:

Tutorial
========

The AppRoute framework tends to impose a specific set of requirements on most
projects. Pages that use the AppRoute framework are intended to handle flashed
content as well as strictly follow a certain data flow. Data should be split
into two sections: viewed data, and submitted data. To start off with, let's
get the handle on displaying the viewed data.

Starting the Project
--------------------

As a basic example, we should make our view class and HTML template.

.. literalinclude:: examples/start.html
   :language: html
   :linenos:

.. literalinclude:: examples/start.py
   :language: python
   :linenos:

This is the most simple example, but can easily show how AppRoute creates a
distinction between the data and the "container" for the data, the HTML. You
can view this in the browser by running: ``python3 examples/start.py``, then
going to your browser with the URL ``http://localhost:5000``.

Additionally, to test out JSON, you can use the following command:

.. code-block:: shell

   curl -H "Accept: application/json" localhost:5000
