class GetUserSerializerMixin:
    def get_user(self):
        return self.context['request'].user
