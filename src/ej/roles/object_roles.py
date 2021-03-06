import uuid

from django.db.models import QuerySet, Model
from hyperpython import html, div, h2, span, Text
from hyperpython.components import fa_icon, html_list


@html.register(QuerySet, role='collapsible-list')
@html.register(list, role='collapsible-list')
def render_collapsible(lst, item_role='collapsible-item', title=None, expanded=False, **kwargs):
    """
    Renders a queryset or list of objects

    Args:
        lst:
            List or queryset of objects inside the collapsible list.
        item_role:
            Role assigned to each element in the list. Defaults to
            'collapsible-item'.
        title (bool):
            Title in which the list of object is displayed.
        expanded (str):
            If true, start list in the "expanded" state.
    """
    if title is None:
        if isinstance(lst, QuerySet):
            title = title.model._meta.verbose_name_plural
        else:
            raise TypeError('must provide an explicit title!')

    data = [html(x, item_role, **kwargs) for x in lst]
    random_id = str(uuid.uuid4())
    display = 'block' if expanded else 'none'

    return div(class_='CollapsibleList')[
        h2(
            onclick=f"$('#{random_id}').toggle()",
            children=[title, span(f'({len(data)})'), fa_icon('angle-down')]
        ),
        html_list(data, style=f'display: {display}', id=random_id),
    ]


@html.register(Model)
def render_model(obj, role=None):
    return Text(str(obj))
