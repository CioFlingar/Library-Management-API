from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import Author, Category, Book, Borrow
from .serializers import AuthorSerializer, CategorySerializer, BookSerializer, BorrowSerializer
from rest_framework.decorators import action

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['author__name', 'category__name']

class BorrowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        borrows = Borrow.objects.filter(user=request.user, return_date__isnull=True)
        serializer = BorrowSerializer(borrows, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request):
        user = request.user
        book_id = request.data.get('book_id')

        if not book_id:
            return Response({"detail": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check borrowing limit (max 3 active)
        active_borrows_count = Borrow.objects.filter(user=user, return_date__isnull=True).count()
        if active_borrows_count >= 3:
            return Response({"detail": "Borrowing limit reached (max 3 active borrows)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.select_for_update().get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        if book.available_copies < 1:
            return Response({"detail": "No copies available."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Borrow record and decrement available copies atomically
        borrow = Borrow(user=user, book=book)
        borrow.borrow_date = timezone.now()
        borrow.due_date = borrow.borrow_date + timedelta(days=14)
        borrow.save()

        book.available_copies -= 1
        book.save()

        serializer = BorrowSerializer(borrow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def return_book(self, request):
        borrow_id = request.data.get('borrow_id')
        if not borrow_id:
            return Response({"detail": "borrow_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            borrow = Borrow.objects.select_for_update().get(id=borrow_id, user=request.user, return_date__isnull=True)
        except Borrow.DoesNotExist:
            return Response({"detail": "Active borrow record not found."}, status=status.HTTP_404_NOT_FOUND)

        borrow.return_date = timezone.now()
        borrow.save()

        # Increment available copies
        book = borrow.book
        book.available_copies += 1
        book.save()

        # Calculate penalty points if late
        days_late = borrow.days_late()
        if days_late > 0:
            user = request.user
            user.penalty_points += days_late
            user.save()

        serializer = BorrowSerializer(borrow)
        return Response(serializer.data)
