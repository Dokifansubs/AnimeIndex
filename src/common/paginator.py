import math

from bottle import request
from common import UtilClass

class paginator(object):
    def __init__(self, query, page, per_page):
        self.query = query
        self.page = page
        self.per_page = per_page

        self.items = query.limit(per_page).offset((page - 1) * per_page).all()
        self.length = len(self.items)
        self.total = query.count()

    @property
    def first(self):
        return (self.page - 1) * self.per_page + 1

    @property
    def last(self):
        return (self.page - 1)  * self.per_page + self.length

    @property
    def final(self):
        return self.total

    @property
    def last_page_number(self):
        return int(math.ceil(self.total / float(self.per_page)))

    @property
    def is_first(self):
        return self.page == 1

    @property
    def is_last(self):
        return self.page == self.last_page_number

    @property
    def display_previous(self):
        return self.page > 1

    @property
    def display_next(self):
        return self.last_page_number > self.page

    def get_pages(self):
        modifier = 4
        out = []

        first = self.page - modifier if self.page - modifier > 1 else 2
        last = self.page + 1 + modifier if self.page + 1 + modifier < self.last_page_number else self.last_page_number

        if first > 2:
            out.append((False, '', '...'))
        for x in range(first, self.page):
            out.append((UtilClass.link({'page': str(x)}), '', str(x)))
        if self.page > 1 and self.page < self.last_page_number:
            out.append((False, 'red', str(self.page)))
        for x in range(self.page + 1, last):
            out.append((UtilClass.link({'page': str(x)}), '', str(x)))
        if last < self.last_page_number - 1:
            out.append((False, '', '...'))

        return out

    def first_page(self):
        return UtilClass.link({'page': '1'});

    def last_page(self):
        return UtilClass.link({'page': str(self.last_page_number)});

    def previous_page(self):
        return UtilClass.link({'page': str(self.page - 1)});

    def next_page(self):
        return UtilClass.link({'page': str(self.page + 1)});
