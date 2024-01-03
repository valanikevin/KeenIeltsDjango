from django.core.management.base import BaseCommand
from ieltstest.models import Book, Test, ReadingModule, WritingModule


class Command(BaseCommand):
    help = 'Generate empty modules for all tests of all the books'

    def handle(self, *args, **options):
        books = Book.objects.order_by('-id')

        for book in books:
            print(f'Book: {book.name}')
            create_module = input(
                'Create empty general modules for this book? (y/n): ')
            if create_module.lower() == 'y':
                tests = Test.objects.filter(book=book).order_by('name')
                for index, test in enumerate(tests):
                    r_module = ReadingModule.objects.create(
                        test=test, name=f'General Reading Test {index+1}', test_type='general', status="modules-created")
                    w_module = WritingModule.objects.create(
                        test=test, name=f'General Writing Test {index+1}', test_type='general', status="modules-created")
                    print(f'Created modules for test {test.name}')
            else:
                print('Skipped!')
