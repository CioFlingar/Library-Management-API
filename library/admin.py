from django.contrib import admin
from .models import Author, Category, Book
from .models import Borrow


admin.site.register(Borrow)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
