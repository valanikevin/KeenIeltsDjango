from django.contrib.sitemaps import Sitemap
from ieltstest.models import Book
from django.conf import settings


class BookSiteMap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Book.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/book/{obj.slug}/'


CUSTOM_URLS = [
    '/',
    '/login/',
    '/register/',
    '/ieltstest/listening/',
    '/ieltstest/reading/',
    '/ieltstest/writing/',
    '/ieltstest/speaking/',
    '/ieltstest/fulltest/',
]


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return CUSTOM_URLS

    def location(self, item):
        return item

    def priority(self, item):
        if item in ['/', ]:
            return 1.0  # Higher priority for main and full test pages
        else:
            return 0.9  # Lower priority for other pages
