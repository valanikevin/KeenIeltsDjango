from django.core.management.base import BaseCommand
from ieltstest.models import Book


class Command(BaseCommand):
    help = 'Generate empty modules for all tests of all the books'

    def handle(self, *args, **options):
        books = Book.objects.order_by('-id')

        for book in books:
            print(f'Book: {book.name} | ID: {book.id}')
            create_test = input('Create empty modules for this book? (y/n): ')
            if create_test.lower() == 'y':
                book.create_empty_tests()
                print('Done!')
            else:
                print('Skipped!')
