from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import SellerDashboardSerializer, AdminDashboardSerializer
from .permissions import IsSeller , IsAdmin
from products.models import Product
from order.models import OrderItem, Order
from django.db.models import Sum , F
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()

class SellerDashboardView(APIView):
      permission_classes = [IsSeller]
      
      @swagger_auto_schema(request_body=SellerDashboardSerializer)
      def get(self, request):
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
            
            serializer = SellerDashboardSerializer(data=data)
            if serializer.is_valid():
                  return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
      
      
class AdminDashboardView(APIView):
      permission_classes = [IsAdmin]
      
      @swagger_auto_schema(request_body=AdminDashboardSerializer)
      def get(self, request):
            
            total_users = User.objects.count()
            total_sellers = User.objects.filter(role='seller').count()
            total_products = Product.objects.count()
            total_orders = Order.objects.count()
            total_revenue = (OrderItem.objects.all().annotate(
                  line_total=F("price")*F('quantity')).aggregate(Sum("line_total"))["line_total__sum"] or 0)
            
            top_selling_product = (OrderItem.objects.values("product__name").annotate(
                  total_price=F("price")*F("quantity")).annotate(quantity=Sum('quantity')).order_by("-quantity").first())
            
            #None control
            if top_selling_product:
                  top_product_data={
                  "product":top_selling_product["product__name"],
                  "quantity":top_selling_product["quantity"],
                  "total_price":top_selling_product["total_price"]
                  }
            else:
                  top_product_data = {
                        "product":None,
                        "quantity":0,
                        "total_price":0
                  }
            
            data = {
                  "total_users":total_users,
                  "total_sellers":total_sellers,
                  "total_products":total_products,
                  "total_orders":total_orders,
                  "total_revenue":total_revenue,
                  "top_selling_product":top_product_data
            }
            
            serializer = AdminDashboardSerializer(data)
            return Response(serializer.data,status=200)