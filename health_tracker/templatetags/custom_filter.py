from django import template

register = template.Library()


def endswith(value: str, arg: str):
    accepted = arg.split(",")
    return any([value.endswith(x) for x in accepted])


register.filter('endswith', endswith)