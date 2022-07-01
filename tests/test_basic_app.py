import flask
import pytest
from bson import ObjectId


@pytest.fixture(autouse=True)
def setup_endpoints(app, todo):
    Todo = todo

    @app.route("/")
    def index():
        return "\n".join(x.title for x in Todo.objects)

    @app.route("/add", methods=["POST"])
    def add():
        form = flask.request.form
        todo = Todo(title=form["title"], text=form["text"])
        todo.save()
        return "added"

    @app.route("/show/<id>/")
    def show(id):
        todo = Todo.objects.get_or_404(id=id)
        return "\n".join([todo.title, todo.text])


def test_with_id(app, todo):
    Todo = todo
    client = app.test_client()
    response = client.get(f"/show/{ObjectId()}/")
    assert response.status_code == 404

    client.post("/add", data={"title": "First Item", "text": "The text"})

    response = client.get(f"/show/{Todo.objects.first_or_404().id}/")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "First Item\nThe text"


def test_basic_insert(app):
    client = app.test_client()
    client.post("/add", data={"title": "First Item", "text": "The text"})
    client.post("/add", data={"title": "2nd Item", "text": "The text"})
    response = client.get("/")
    assert response.data.decode("utf-8") == "First Item\n2nd Item"
