from rest_framework import serializers
from django.contrib.auth.hashers import *
from .models import Benefactor
from .models import Charity, Task, User


class BenefactorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Benefactor
        fields = ['experience', 'free_time_per_week', 'user']

    def create(self, validated_data):
        return Benefactor.objects.create(**validated_data)

class CharitySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Charity
        fields = ['name', 'reg_number', 'user']

    def create(self, validated_data):
        # Ensure the charity is created correctly
        return Charity.objects.create(**validated_data)      




class TaskSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(read_only=True, choices=Task.TaskStatus.choices)
    assigned_benefactor = BenefactorSerializer(required=False)
    charity = CharitySerializer(read_only=True)
    charity_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Charity.objects.all(), source='charity')

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'state',
            'charity',
            'charity_id',
            'description',
            'assigned_benefactor',
            'date',
            'age_limit_from',
            'age_limit_to',
            'gender_limit',
        )
