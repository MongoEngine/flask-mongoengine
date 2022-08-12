import flask
import pytest
from bson import DBRef, ObjectId


@pytest.fixture(autouse=True)
def setup_endpoints(app, todo):
    Todo = todo

    @app.route("/")
    def index():
        return flask.jsonify(result=Todo.objects())

    @app.route("/as_pymongo")
    def as_pymongo():
        return flask.jsonify(result=Todo.objects().as_pymongo())

    @app.route("/aggregate")
    def aggregate():
        return flask.jsonify(
            result=Todo.objects().aggregate([{"$match": {"title": {"$ne": "lksdjh"}}}])
        )

    @app.route("/add", methods=["POST"])
    def add():
        form = flask.request.form
        todo = Todo(title=form["title"], text=form["text"])
        todo.save()
        return flask.jsonify(result=todo)

    @app.route("/show/<id>/")
    def show(id):
        return flask.jsonify(result=Todo.objects.get_or_404(id=id))

    @app.route("/object_id")
    def object_id():
        return flask.jsonify(result=ObjectId())

    @app.route("/dbref")
    def dbref():
        return flask.jsonify(result=DBRef("Todo", ObjectId()))


def test_with_id(app, todo):
    Todo = todo
    client = app.test_client()
    response = client.get(f"/show/{ObjectId()}/")
    assert response.status_code == 404

    response = client.post("/add", data={"title": "First Item", "text": "The text"})
    assert response.status_code == 200

    response = client.get("/dbref")
    assert response.status_code == 200

    response = client.get("/object_id")
    assert response.status_code == 200

    response = client.get(f"/show/{Todo.objects.first().id}/")
    assert response.status_code == 200

    result = flask.json.loads(response.data).get("result")
    assert ("title", "First Item") in result.items()


def test_basic_insert(app):
    client = app.test_client()
    client.post("/add", data={"title": "First Item", "text": "The text"})
    client.post("/add", data={"title": "2nd Item", "text": "The text"})

    rv = client.get("/")
    result = flask.json.loads(rv.data).get("result")
    assert len(result) == 2
    for i in result:
        assert "title" in i
        assert "text" in i

    rv = client.get("/as_pymongo")
    result = flask.json.loads(rv.data).get("result")
    assert len(result) == 2
    for i in result:
        assert "title" in i
        assert "text" in i

    rv = client.get("/aggregate")
    result = flask.json.loads(rv.data).get("result")
    for i in result:
        assert "title" in i
        assert "text" in i
    assert len(result) == 2
