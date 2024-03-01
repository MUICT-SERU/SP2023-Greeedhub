# -*- coding: utf-8 -*-

from rest_framework import viewsets, routers, serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', UserViewSet)
