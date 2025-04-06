from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.validators import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django_filters.rest_framework import DjangoFilterBackend
from products.pagination import ProductPaginaton
from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from products.models import (
    Product,
    Review,
    FavoriteProduct,
    Cart, ProductTag, ProductImage, CartItem
)
from products.serializers import (
    ProductSerializer,
    ReviewSerializer,
    FavoriteProductSerializer,
    CartSerializer,
    ProductTagSerializer, ProductImageSerializer, CartItemSerializer, ResetPasswordSerializer
    )

from products.permissions import IsObjectOwnerOrReadOnly
from users.models import User

class ProductViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categories', 'price']
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_product(self, request):
        owned_products = request.user.owned_products.all()
        return owned_products
    

    
class ReviewViewSet(ListModelMixin, CreateModelMixin, GenericViewSet, DestroyModelMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user != review.user:
            raise PermissionError
        return self.destroy(request, *args, **kwargs)
    
class FavoriteProductViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product__name']

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    
class CartViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset
    
    
class TagList(ListModelMixin, GenericViewSet):
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [IsAuthenticated]

class ProductImageViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return self.queryset.filter(product__id=self.kwargs['product_id'])
    
    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
    

class CartItemView(GenericViewSet, DestroyModelMixin, CreateModelMixin, ListModelMixin):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)
    
    
class ResetPasswordView(CreateModelMixin, GenericViewSet):
    serializer_class = ResetPasswordSerializer
    
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # reset_url = request.build_absolute_uri(
            #     reverse('password_reset_confrim', kwargs={'uidb64' : uid, 'token':token})
            # )
            reset_url = f'http://127:0:0:1/reset_password_confrim/{uid}/{token}/'
            
            send_mail(
                'parolis agdgena',
                f'daawiret links resetistvis {reset_url}',
                'ragaca@gmail.com',
                [user.email],
                fail_silently = False
            )
            
            return Response({'message': 'gaigzavna'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)