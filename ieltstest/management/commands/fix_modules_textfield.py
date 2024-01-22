from django.core.management.base import BaseCommand
from ieltstest.models import WritingSection, ListeningSection, ReadingSection, SpeakingSection
from bs4 import BeautifulSoup
from KeenIeltsDjango.utils import imgix_url
from base.models import Storage
import requests
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Make images and tables in WritingSection responsive and print image links'

    def handle(self, *args, **options):
        section_choice = input(
            "Enter section number (1-4): \nListening (1)\nReading (2)\nWriting (3)\nSpeaking (4)\n")

        if section_choice == '1':
            sections = ListeningSection.objects.all()
            field_names = ['questions']
        elif section_choice == '2':
            sections = ReadingSection.objects.all()
            field_names = ['questions', 'passage']
        elif section_choice == '3':
            sections = WritingSection.objects.all()
            field_names = ['task', 'questions']
        elif section_choice == '4':
            sections = SpeakingSection.objects.all()
            field_names = ['questions']
        else:
            sections = WritingSection.objects.all()
            field_names = ['task', 'questions']

        for section in sections:
            for field_name in field_names:
                content = getattr(section, field_name, None)
                if content is not None:
                    soup = BeautifulSoup(content, 'html.parser')
                    self.print_image_links(soup)
                    self.make_images_responsive(soup)
                    self.make_tables_responsive(soup)

                    # Update the field with modified HTML
                    updated_content = str(soup)
                    setattr(section, field_name, updated_content)

            section.save()
            self.stdout.write(self.style.SUCCESS(
                f'Updated section: {section.id}'))

    def make_images_responsive(self, soup):
        images = soup.find_all('img')
        for img in images:
            img['style'] = 'width: 100%; height: auto;'

    def make_tables_responsive(self, soup):
        tables = soup.find_all('table')
        for table in tables:
            # Add classes to the original table
            table_classes = table.get('class', [])
            table_classes.extend(
                ['table', 'table-striped', 'writingsection-table'])
            table['class'] = table_classes

            # Create a responsive wrapper and wrap the table
            responsive_wrapper = soup.new_tag('div')
            responsive_wrapper['class'] = 'table-responsive'
            table.wrap(responsive_wrapper)

    def print_image_links(self, soup):
        images = soup.find_all('img')
        local_domains = [
            "api.keenielts.com",
            "localhost",
            "localhost:8000",
            "keenielts.com",
            "192.168.10.55:8000"
        ]

        for img in images:
            img_src = img.get('src')

            # Skip if the src is one of the local domains
            if any(domain in img_src for domain in local_domains):
                continue

            if img_src.startswith('/'):
                # Use imgix_url for internal links
                new_src = imgix_url(img_src)
                img['src'] = new_src
                self.stdout.write(f'Updated internal image URL: {new_src}')
            else:
                # Process external image links
                try:
                    response = requests.get(img_src, stream=True)
                    if response.status_code == 200:
                        # Create a new Storage object and save the image
                        img_name = img_src.split('/')[-1]
                        storage = Storage(name="External Image", file=ContentFile(
                            response.content, name=img_name))
                        storage.save()

                        # Update the img src to the new saved image URL
                        new_src = imgix_url(storage.file.url)
                        img['src'] = new_src
                        self.stdout.write(f'Saved external image: {new_src}')
                except Exception as e:
                    self.stdout.write(
                        f'Error saving external image from {img_src}: {str(e)}')
