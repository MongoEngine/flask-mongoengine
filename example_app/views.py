"""Demo views for example application."""
from faker import Faker
from flask import render_template, request
from mongoengine.context_managers import switch_db

from example_app import models


def generate_data():
    """Generates fake data for all supported models and views."""
    fake = Faker(locale=["en_US"])

    with switch_db(models.Todo, "default"):
        models.Todo.objects().delete()  # Removes
        models.Todo(
            title="Simple todo A", text=fake.sentence(), done=False
        ).save()  # Insert
        models.Todo(
            title="Simple todo B", text=fake.sentence(), done=True
        ).save()  # Insert
        models.Todo(
            title="Simple todo C", text=fake.sentence(), done=True
        ).save()  # Insert
        # Bulk insert
        bulk = (
            models.Todo(title="Bulk 1", text=fake.sentence(), done=False),
            models.Todo(title="Bulk 2", text=fake.sentence(), done=True),
        )
        models.Todo.objects().insert(bulk)
        models.Todo.objects(title__contains="B").order_by("-title").update(
            set__text="Hello world"
        )  # Update
        models.Todo.objects(title__contains="C").order_by("-title").delete()  # Removes

    with switch_db(models.Todo, "secondary"):
        models.Todo.objects().delete()
        for _ in range(10):
            models.Todo(
                title=fake.text(max_nb_chars=59),
                text=fake.sentence(),
                done=fake.pybool(),
                pub_date=fake.date(),
            ).save()


def delete_data():
    """Clear database."""
    from example_app.app import db

    db.connection["default"].drop_database("example_app")
    db.connection["secondary"].drop_database("example_app_2")


def index():
    """Return page with welcome words and instructions."""
    message = None
    if request.method == "POST":
        if request.form["button"] == "Generate data":
            generate_data()
            message = "Fake data generated"
        if request.form["button"] == "Delete data":
            delete_data()
            message = "All data deleted"
    return render_template("index.html", message=message)


def pagination():
    """Return pagination and easy form demonstration."""
    form = models.TodoForm()

    with switch_db(models.Todo, "secondary"):
        if request.method == "POST":
            form.validate_on_submit()
            form.save()
        page_num = int(request.args.get("page") or 1)
        todos_page = models.Todo.objects.paginate(page=page_num, per_page=3)

    return render_template("pagination.html", todos_page=todos_page, form=form)


def demo_view(model, view_name, pk=None):
    """Return all fields demonstration."""
    FormClass = model.to_wtf_form()
    form = FormClass()
    if pk:
        obj = model.objects.get(pk=pk)
        form = FormClass(obj=obj)

    if request.method == "POST" and form.validate_on_submit():
        form.save()
        # form = FormClass(obj=form.instance)
    page_num = int(request.args.get("page") or 1)
    page = model.objects.paginate(page=page_num, per_page=100)

    return render_template(
        "form_demo.html", view=view_name, page=page, form=form, model=model
    )
