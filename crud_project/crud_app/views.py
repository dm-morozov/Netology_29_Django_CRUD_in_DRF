from crud_app import models
from django.shortcuts import render
from pyexpat import model

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import Comment
from .serializers import CommentSerialiser


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerialiser
    # filter_backends = []
    filterset_fields = ['user',] # ищет полное совпадение
    search_fields = ['text',] # ищет частичное совпадение
    ordering_fields = ['id', 'user', 'text', 'created_at']
    pagination_class = LimitOffsetPagination
