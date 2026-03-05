from .models import tbl_category


def categories_processor(request):
    return {
        'categories': tbl_category.objects.all()
    }