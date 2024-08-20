from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'phone', 'address', 'gender', 'age', 'description', 'first_name', 'last_name', 'email']
        extra_kwargs = {
            'password' : {'write_only' : True, 'min_length' : 4}
        }
    def validate_password(self, pas):
        return make_password(pas)