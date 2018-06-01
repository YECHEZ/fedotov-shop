from django.shortcuts import render, get_object_or_404, render_to_response
from .models import *
from django.utils import timezone
#from cart.forms import CartAddProductForm


# Страница с товарами
def ProductList(request):
    categories = Category.objects.filter(parent=None)
    return render(request, 'products/index.html', {
        'categories': categories,
    })

def show_category(request,hierarchy=None):
    session_key = request.session.session_key
    if not session_key:
        request.session.cycle_key()
    category_slug = hierarchy.split('/')
    parent = None
    root = Category.objects.all()
    categories = Category.objects.all()

    for slug in category_slug[:-1]:
        parent = root.get(parent=parent, slug = slug)

    try:
        instance = Category.objects.get(parent=parent,slug=category_slug[-1])
    except:
        instance = get_object_or_404(Product, slug = category_slug[-1])
        rel_filt = Product.objects.filter(category = instance.category, created__lte=timezone.now()).order_by('-created')
        relative = rel_filt.exclude(id=instance.id)[:2]
        i_images = ProductImage.objects.filter(product__id = instance.id, is_active=True, is_main=False)
        return render(request, "products/productDetail.html", {
            'instance': instance,
            'categories': categories,
            'relative': relative,
            'i_images': i_images,
            })
    else:
        return render(request, 'products/productInCats.html', {
        'instance':instance,
        'categories': categories,
        })
