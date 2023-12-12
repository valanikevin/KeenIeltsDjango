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
                no_of_practice_tests = int(
                    input('Enter number of practice tests: '))
                module_type = input(
                    'Enter module type (1. academic, 2.general): ')
                module_type = 'academic' if module_type == '1' else 'general'
                book.create_empty_tests(
                    no_of_practice_test=no_of_practice_tests, module_type=module_type)
                print('Done!')
            else:
                print('Skipped!')
