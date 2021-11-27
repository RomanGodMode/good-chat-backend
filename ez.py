class GigaBase:
    def show(self):
        print('base')


class EzMixin:
    def show(self):
        print('mixin')


class GuchiComposition(GigaBase, EzMixin):
    def show(self):
        super().show()


composition = GuchiComposition()
composition.show()
