from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import SellerDashboardSerializer, AdminDashboardSerializer
from .permissions import IsSeller , IsAdmin
from products.models import Product
from order.models import OrderItem, Order
from django.db.models import Sum , F, Count, Q, DecimalField, ExpressionWrapper, Value
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from django.db.models.functions import Coalesce
from django.core.cache import cache

User = get_user_model()

class SellerDashboardView(APIView):
      permission_classes = [IsSeller]
      
      def get(self, request):
            cache_key = f'dash:v1:seller:{request.user.id}'
            data = cache.get(cache_key)
            if not data:
                  user = request.user
                  products = Product.objects.filter(seller=user).order_by("-created_at")
                  total_products = products.count()

                  stock_alerts = products.filter(stock__lte=5).annotate(product=F("name"))
                  stock_alerts = list(stock_alerts.values("product","stock"))

                  total_sales = OrderItem.objects.filter(product__seller=user).aggregate(Sum("quantity"))["quantity__sum"] or 0

                  total_revenue = OrderItem.objects.filter(product__seller=user).annotate(
                        line_total=F("quantity")*F("price")).aggregate(
                              Sum("line_total")
                        )["line_total__sum"] or 0

                  pending_orders = OrderItem.objects.filter(product__seller=user,order__status='paid')
                  pending_orders_count = pending_orders.count()
            
                  data = {
                        "total_products": total_products,
                        "total_sales": total_sales,
                        "total_revenue": total_revenue,
                        "pending_orders": pending_orders_count,
                        "stock_alerts": stock_alerts
                  }
                  cache.set(cache_key, data, 60*30)
            
            serializer = SellerDashboardSerializer(data=data)
            if serializer.is_valid():
                  return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
      
      
class AdminDashboardView(APIView):
      permission_classes = [IsAdmin]
      
      def get(self, request):
            cache_key = 'dash:v1:admin'
            data = cache.get(cache_key)
            
            if not data:
                  users_agg = (
                        User.objects.aggregate(
                              total_users=Count('id'),
                              total_sellers=Count('id',filter=Q(role='seller'))
                        )
                  )
                  total_users = users_agg['total_users']
                  total_sellers=users_agg['total_sellers']

                  product_agg= (
                        Product.objects.aggregate(
                              total_products=Count('id')
                        )
                  )
                  total_products = product_agg['total_products']

                  orders_agg=(
                        Order.objects.aggregate(
                              total_orders=Count('id')
                        )
                  )
                  total_orders= orders_agg['total_orders']

                  oi_qs = OrderItem.objects.annotate(
                        line_total=ExpressionWrapper(
                              F('price') * F('quantity'),
                              output_field=DecimalField(max_digits=12, decimal_places=2),
                        )
                  )
            
                  total_revenue = oi_qs.aggregate(
                        total=Coalesce(
                              Sum('line_total'),
                              Value(0, output_field=DecimalField(max_digits=12,decimal_places=2))
                        )
                  )['total']

                  top = (
                        oi_qs.values('product_id', 'product__name')
                        .annotate(
                           quantity=Sum('quantity'),
                           total_price=Sum('line_total'),
                        )
                       .order_by('-quantity')
                       .first()
                  )
            
                  if top:
                        top_selling_product = {
                            "id": top['product_id'],
                            "product": top['product__name'],
                            "quantity": top['quantity'],
                            "total_price": top['total_price'],
                        }
                  else:
                        top_selling_product = {"id":None ,"product": None, "quantity": 0, "total_price": 0}

                  data = {
                        "total_users":total_users,
                        "total_sellers":total_sellers,
                        "total_products":total_products,
                        "total_orders":total_orders,
                        "total_revenue":total_revenue,
                        "top_selling_product":top_selling_product
                  }
                  cache.set(cache_key, data, 60*30)
            
            serializer = AdminDashboardSerializer(data)
            return Response(serializer.data,status=200)