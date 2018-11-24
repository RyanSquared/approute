import functools

from typing import Callable

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask.views import MethodView


MIMETYPES = ["application/json", "text/html"]


def _is_json():
    if request.is_json:
        return True
    best = request.accept_mimetypes.best_match(MIMETYPES)
    return best == "application/json"


def category_response(message: str, status_code: int = 200,
                      category: str = None, payload: dict = None,
                      flash_category: str = "notification") -> dict:
    """
    When a message is JSON, return either a payload (higher priority) or a
    message string, as well as a status code. When a message is form-based,
    flash a message string on the ``flash_category`` stream.

    Flashed messages contain "message|category" formatting style and can use
    ``{% set message, category = flashed_message.split("|") %}``.

    :param message: Message flashed with non-JSON, or when no payload provided
    :param status_code: Status code given to JSON or determining ``category``
    :param category: One of ``"success"``, ``"warning"``, ``"danger"``, used
        when flashing
    :param payload: Passed to JSON object, used for handling more contextual
        information than just a string-based message
    :param flash_category: Category concatenated to message when flashing
    """
    if _is_json():
        if payload is not None:
            # return payload
            return {
                "payload": payload,
                "status_code": status_code
            }
        else:
            return {
                "message": message,
                "status_code": status_code
            }
    if category is None:
        category = "success"
        if status_code >= 500:
            category = "danger"
        elif status_code >= 400:
            category = "warning"
    flash("%s|%s" % (message, category), flash_category)
    return {}


def response_manager(category: str) -> Callable[[str], dict]:
    """
    Return a callable function which will handle responses for a certain
    flash category. Synonymous with a partial :meth:`category_response`.

    :param category: String passed to ``flash_category``.
    """
    return functools.partial(category_response, flash_category=category)


response: Callable[[str], dict] = response_manager("notification")


class AppRouteView(MethodView):
    """
    Base method class for Flask routes. Methods should be overridden which will
    then be called to perform interface-agnostic tasks.

    **Usage:**

    .. code-block:: python

       class Register(AppRouteView):
           decorators = [login_required]
           redirect_to = "index"
           template_name = "device/register.html"

           def handle_post(self, values):
               name = values["device_name"]
               thing = Thing("", uuid.uuid4().hex)
               thing.sync(create=True)
               device = Device(arn=thing.arn,
                               client_id=g.user.client_id,
                               name=name)
               db.session.add(device)
               db.session.commit()

               return response("Device created: %s" % name,
                               payload={"name": name,
                                        "arn": thing.arn})
    """

    #: HTML template to be rendered on GET requests
    template_name: str = None

    #: Route name given to `url_for()` when determining where to redirect after
    #: a POST request, handled in :meth:`handle_post`
    redirect_to: str = None

    #: Args provided to `url_for()` when redirecting a request, see
    #: :attr:`redirect_to`
    redirect_args = {}

    def get_template_name(self):
        """
        *Override*

        Function to be overridden if it is reasonable to use a dynamic
        template name, such as if it depends on some kind of state.

        By default, the set :attr:`template_name` is returned.

        **Usage:**

        .. code-block:: python

           class Example(AppRouteView):
               def get_template_name(self):
                   return "template.html"
        """
        return self.template_name

    def _render_template(self, **context):
        """
        *Internal*

        Render the assigned template, given from :meth:`get_template_name`,
        with the keyword arguments passed to the function. Meant to replicate
        the signature of :meth:`flask.render_template`
        """
        return render_template(self.get_template_name(), **context)

    # POST requests
    # All HTTP POST requests should redirect to avoid refresh-duplication, so
    # do not overwrite post_html without a redirect

    def handle_post(self, values: dict, *args, **kwargs) -> dict:
        """
        *Override*

        Handle incoming data from a POST message, whether from an HTTP form or
        from an incoming JSON object.

        :param values: Dictionary with values from client
        :exc NotImplementedError: Raised by default when not overridden
        """
        raise NotImplementedError()

    def post_json(self, *args, **kwargs):
        """
        *Internal*

        Handle incoming values from a JSON source (typically determined by
        :attr:`flask.request.is_json` but also relies on incoming Accept
        header types) and return a JSON response.
        """
        values = request.json
        result = self.handle_post(values, *args, **kwargs)
        if "payload" in result:
            return jsonify(result["payload"]), result.get("status_code", 200)
        return (jsonify({"message": result.get("message", "no output")}),
                result.get("status_code", 200))

    def post_html(self, *args, **kwargs):
        """
        *Internal*

        Handle incoming values from an HTML source and return an HTTP redirect
        for a target page.
        """
        values = request.form
        self.handle_post(values, *args, **kwargs)
        if self.redirect_to is not None:
            return redirect(url_for(self.redirect_to, **self.redirect_args))
        return redirect(url_for(self.route, **self.redirect_args))

    # GET requests

    def populate(self, *args, **kwargs):
        """
        *Override*

        Function for finding and populating data for GET requests which will
        then be passed to :meth:`_render_template`.

        Arguments passed to this function match the arguments passed to
        :class:`flask.views.MethodView`'s ``.get()``
        """
        return {}

    def get_json(self, *args, **kwargs):
        """
        *Internal*

        Return a JSON object containing values from :meth:`populate`.
        """
        values = self.populate(*args, **kwargs)
        return jsonify(values), values.get("status_code", 200)

    def get_html(self, *args, **kwargs):
        """
        *Internal*

        Return a rendered template with values populated from :meth:`populate`.
        """
        return self._render_template(**self.populate(*args, **kwargs))

    # MethodView overrides

    def get(self, *args, **kwargs):
        """
        *Internal*

        Choose between :meth:`get_html` and :meth:`get_json`.
        """
        if _is_json():
            return self.get_json(*args, **kwargs)
        return self.get_html(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        *Internal*

        Choose between :meth:`post_html` and :meth:`post_json`.
        """
        if _is_json():
            return self.post_json(*args, **kwargs)
        else:
            return self.post_html(*args, **kwargs)
