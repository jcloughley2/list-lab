from django import template

register = template.Library()

@register.filter
def has_forked(list_obj, user):
    """Check if a user has forked a list"""
    if not user.is_authenticated:
        return False
    return list_obj.forks.filter(owner=user).exists()

@register.filter
def has_liked(list_obj, user):
    """Check if a user has liked a list"""
    if not user.is_authenticated:
        return False
    return user.liked_lists.filter(id=list_obj.id).exists() 