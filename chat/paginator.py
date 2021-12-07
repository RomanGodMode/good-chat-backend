from django.core.paginator import Paginator


class PaginatorWithOffset(Paginator):
    def __init__(self, object_list, per_page, shift=0):
        super().__init__(object_list, per_page)
        self.shift = shift

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page

        bottom += self.shift
        top += self.shift

        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.object_list[bottom:top], number, self)
