from typing import Any
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task
from charities.serializers import (
    TaskSerializer, CharitySerializer, BenefactorSerializer
)


class BenefactorRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {
            "user": request.user.id,
            "experience": request.data.get("experience"),
            "free_time_per_week": request.data.get("free_time_per_week"),
        }
        serializer = BenefactorSerializer(data=data)
        if serializer.is_valid():
            benefactor = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CharityRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {
            "user": request.user.id,
            "name": request.data.get("name"),
            "reg_number": request.data.get("reg_number"),
        }
        serializer = CharitySerializer(data=data)
        if serializer.is_valid():
            charity = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    permission_classes = [IsBenefactor]
    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if task.state != "P":
            return Response(
                data={'detail': 'This task is not pending.'},
                status=status.HTTP_404_NOT_FOUND
            )
        task.state = "W"
        u = Benefactor.objects.get(user=request.user)
        task.assign_to_benefactor(u)
        task.save()
        return Response(data={'detail': 'Request sent.'},status=status.HTTP_200_OK)
    
    



class TaskResponse(APIView):
    permission_classes = [IsAuthenticated, IsCharityOwner]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if request.data['response'] != ('R' and 'A'): #request.data['response'] != 'A':
            return Response(
                data={'detail': 'Required field ("A" for accepted / "R" for rejected)'},
                status=status.HTTP_400_BAD_REQUEST
                )
        if task.state != 'W':
            return Response(
                data={'detail': 'This task is not waiting.'},
                status=status.HTTP_404_NOT_FOUND
            )
        task.response_to_benefactor_request(request.data['response'])
        return Response(
            data={'detail': 'Response sent.'},
            status=status.HTTP_200_OK
        )



class DoneTask(APIView):
    permission_classes = [IsAuthenticated, IsCharityOwner]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if task.state != 'A':
            return Response(
                data={'detail': 'Task is not assigned yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        task.done()
        return Response(
            data={'detail': 'Task has been done successfully.'},
            status=status.HTTP_200_OK
        )