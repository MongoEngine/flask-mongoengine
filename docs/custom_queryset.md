# Custom Queryset

flask-mongoengine attaches the following methods to Mongoengine's default QuerySet:

* **get_or_404**: works like .get(), but calls abort(404) if the object DoesNotExist.
  Optional arguments: *message* - custom message to display.
* **first_or_404**: same as above, except for .first().
  Optional arguments: *message* - custom message to display.
* **paginate**: paginates the QuerySet. Takes two arguments, *page* and *per_page*.
* **paginate_field**: paginates a field from one document in the QuerySet.
  Arguments: *field_name*, *doc_id*, *page*, *per_page*.

Examples:

```python
# 404 if object doesn't exist
def view_todo(todo_id):
    todo = Todo.objects.get_or_404(_id=todo_id)

# Paginate through todo
def view_todos(page=1):
    paginated_todos = Todo.objects.paginate(page=page, per_page=10)

# Paginate through tags of todo
def view_todo_tags(todo_id, page=1):
    todo = Todo.objects.get_or_404(_id=todo_id)
    paginated_tags = todo.paginate_field('tags', page, per_page=10)
```

Properties of the pagination object include: iter_pages, next, prev, has_next,
has_prev, next_num, prev_num.

In the template:

```html
{# Display a page of todos #}
<ul>
    {% for todo in paginated_todos.items %}
        <li>{{ todo.title }}</li>
    {% endfor %}
</ul>

{# Macro for creating navigation links #}
{% macro render_navigation(pagination, endpoint) %}
  <div class=pagination>
  {% for page in pagination.iter_pages() %}
    {% if page %}
      {% if page != pagination.page %}
        <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
      {% else %}
        <strong>{{ page }}</strong>
      {% endif %}
    {% else %}
      <span class=ellipsis>…</span>
    {% endif %}
  {% endfor %}
  </div>
{% endmacro %}

{{ render_navigation(paginated_todos, 'view_todos') }}
```
