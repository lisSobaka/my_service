from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def search_param_replace(context, **kwargs):
    params = context['request'].GET.copy()

    for key, value in kwargs.items():
        params[key] = value
    
    for key in [key for key, value in params.items() if not value]:
        del params[key]
    
    return params.urlencode()


'''
<QueryDict: {'date': ['year'], 'employee': [''], 'page': ['2']}>


for key, value in params:
    if value == "":
        del params[key]

for key in
    for key, value in params.items():
        if key not value:
            del params[key]
        


'''