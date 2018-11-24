.. _api:

API
===

.. module:: approute

Response Managers
-----------------

These can be used as the return value from a :meth:`AppRouteView.handle_post`
request. Flashed messages from these methods should apply to the redirect to
:attr:`AppRouteView.redirect_to`, and should be handled in the template at the
target of that function.

.. autofunction:: category_response
.. autofunction:: response_manager
.. attribute:: response
   
   Call :meth:`category_response` with the ``flash_category`` option set to
   ``"notification"``.

AppRouteView Class
------------------

.. autoclass:: AppRouteView
   :members:
