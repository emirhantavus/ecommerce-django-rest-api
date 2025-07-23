from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import SellerDashboardSerializer
from .permissions import IsSeller
from products.models import Product
from order.models import OrderItem
from django.db.models import Sum , F

class SellerDashboardView(APIView):
      permission_classes = [IsSeller]
      
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