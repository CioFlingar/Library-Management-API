from rest_framework import serializers
from users.models import User
from .models import Author, Category, Book, Borrow

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'author', 'author_id', 'category', 'category_id', 'total_copies', 'available_copies']

class BorrowSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )

    class Meta:
        model = Borrow
        fields = ['id', 'user', 'book', 'book_id', 'borrow_date', 'due_date', 'return_date']
        read_only_fields = ['user', 'borrow_date', 'due_date', 'return_date']
