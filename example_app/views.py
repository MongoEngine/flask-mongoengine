import flask

from .models import Todo


def index():
    # As a list to test debug toolbar
    Todo.objects().delete()  # Removes
    Todo(title="Simple todo A", text="12345678910").save()  # Insert
    Todo(title="Simple todo B", text="12345678910").save()  # Insert
    Todo.objects(title__contains="B").update(set__text="Hello world")  # Update
    todos = list(Todo.objects[:10])
    todos = Todo.objects.all()
    return flask.render_template("index.html", todos=todos)


def pagination():
    Todo.objects().delete()
    for i in range(10):
        Todo(title="Simple todo {}".format(i), text="12345678910").save()  # Insert

    page_num = int(flask.request.args.get("page") or 1)
    todos_page = Todo.objects.paginate(page=page_num, per_page=3)

    return flask.render_template("pagination.html", todos_page=todos_page)
