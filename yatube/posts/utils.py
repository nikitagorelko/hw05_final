from django.core.paginator import Paginator


def connect_paginator(request, object, page_number):
    paginator = Paginator(object, page_number)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
