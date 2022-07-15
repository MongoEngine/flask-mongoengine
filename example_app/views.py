import flask
from mongoengine.context_managers import switch_db


def index():
    from models import Todo

    with switch_db(Todo, "default") as Todo:
        # As a list to test debug toolbar
        Todo.objects().delete()  # Removes
        Todo(title="Simple todo A", text="12345678910").save()  # Insert
        Todo(title="Simple todo B", text="12345678910").save()  # Insert
        Todo(title="Simple todo C", text="12345678910").save()  # Insert
        # Bulk insert
        bulk = (Todo(title="Bulk 1"), Todo(title="Bulk 2"))
        Todo.objects().insert(bulk)
        Todo.objects(title__contains="B").order_by("-title").update(
            set__text="Hello world"
        )  # Update
        Todo.objects(title__contains="C").order_by("-title").delete()  # Removes
        todos = list(Todo.objects.order_by("-title", "done")[2:10])
        todos = Todo.objects.all().order_by("-title")
    return flask.render_template("index.html", todos=todos)


def pagination():
    from models import Todo

    with switch_db(Todo, "secondary") as Todo:
        Todo.objects().delete()
        for i in range(10):
            Todo(title=f"Simple todo {i}", text="12345678910").save()

        page_num = int(flask.request.args.get("page") or 1)
        todos_page = Todo.objects.paginate(page=page_num, per_page=3)

    return flask.render_template("pagination.html", todos_page=todos_page)
