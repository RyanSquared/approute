import approute
import flask


class Index(approute.AppRouteView):
    template_name = "start.html"

    def populate(self):
        return {
            "message": "Hello World!",
            "list": ["eggs", "milk", "bread"]
        }


app = flask.Flask(__name__, template_folder=".")

app.add_url_rule("/", view_func=Index.as_view("index"))

app.run()
