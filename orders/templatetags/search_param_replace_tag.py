from django import template

# Сохранение поисковых запросов в адресной строке при перемещении по страницам с пагинацией
register = template.Library()
@register.simple_tag(takes_context=True)
def search_param_replace(context, **kwargs):
    params = context['request'].GET.copy()

    for key, value in kwargs.items():
        params[key] = value
    
    for key in [key for key, value in params.items() if not value]:
        del params[key]
    
    return params.urlencode()