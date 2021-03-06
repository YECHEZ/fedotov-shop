from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
# Create your models here.

class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
    #slug = models.SlugField()
    slug = models.SlugField(unique=True,max_length=200, db_index=True)

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    class Meta:
        unique_together = (('parent', 'slug',))
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'

    def get_all_products(self):
        return Product.objects.filter(category__in=self.get_descendants(include_self=True))

    def get_count(self):
        #return Product.objects.filter(category=self).count()
        return Product.objects.filter(category__in=self.get_descendants(include_self=True)).count()

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = []
        else:
            ancestors = [ i.slug for i in ancestors]
            slugs = []
            for i in range(len(ancestors)):
                slugs.append('/'.join(ancestors[:i+1]))
            return slugs

    def get_absolut_url(self):
        slugs = []
        slugs = self.get_slug_list()
        last = slugs[-1]
        return last + '/'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = TreeForeignKey('Category',null=True,blank=True,on_delete=models.CASCADE, verbose_name="Категории")
    name = models.CharField(max_length=200, db_index=True, verbose_name="Название")
    slug = models.SlugField(unique=True,max_length=200, db_index=True)
    description = models.TextField(blank=True, verbose_name="Описание")
    discount = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    available = models.BooleanField(default=True, verbose_name="Выставлен")
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_discount_price(self):
        ret_price = self.price - (self.price / 100 * self.discount)
        return ret_price

    def get_absolut_url(self):
        slugs = []
        slugs = self.category.get_slug_list()
        last = slugs[-1]
        return last + '/' + self.slug

    def get_main_image(self):
        images = ProductImage.objects.get(is_active=True, is_main=True, product__id=self.id)
        #print(images)
        #print(images.image.url)
        return "%s" % images.image.url


class ProductImage(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, verbose_name="Фотография товара")
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, auto_now_add=False, verbose_name='Дата обновления')

    def __str__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
