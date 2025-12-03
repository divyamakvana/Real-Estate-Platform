from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(int(key))
    except:
        return dictionary.get(key)

@register.filter
def times(number):
    return range(number)
        


