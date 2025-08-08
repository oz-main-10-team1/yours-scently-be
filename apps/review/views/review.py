from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from apps.product.models import Product
from apps.review.serializers.review import ReviewCreateSerializer


class ReviewCreateAPIView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id = kwargs.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("해당 향수 상품을 찾을 수 없습니다.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
