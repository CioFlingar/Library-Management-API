from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AuthorViewSet, CategoryViewSet, BookViewSet, BorrowViewSet

router = DefaultRouter()
router.register('authors', AuthorViewSet)
router.register('categories', CategoryViewSet)
router.register('books', BookViewSet)

borrow_list = BorrowViewSet.as_view({'get': 'list', 'post': 'create'})
borrow_return = BorrowViewSet.as_view({'post': 'return_book'})

urlpatterns = [
    path('', include(router.urls)),
    path('borrow/', borrow_list, name='borrow-list'),
    path('return/', borrow_return, name='borrow-return'),
]
