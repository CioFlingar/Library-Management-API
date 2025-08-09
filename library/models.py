from django.db import models
from users.models import User
from django.utils import timezone
from datetime import timedelta

class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class Borrow(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=14)
        super().save(*args, **kwargs)

    def is_late(self):
        if self.return_date and self.return_date > self.due_date:
            return True
        elif not self.return_date and timezone.now() > self.due_date:
            return True
        return False

    def days_late(self):
        if self.return_date and self.return_date > self.due_date:
            delta = self.return_date - self.due_date
            return delta.days
        elif not self.return_date and timezone.now() > self.due_date:
            delta = timezone.now() - self.due_date
            return delta.days
        return 0

    def __str__(self):
        return f'{self.user.username} borrowed {self.book.title}'
