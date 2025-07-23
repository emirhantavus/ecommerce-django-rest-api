from rest_framework import serializers

class StockAlertSerializer(serializers.Serializer):
      product = serializers.CharField(source='name')
      stock = serializers.IntegerField()

class SellerDashboardSerializer(serializers.Serializer):
      total_products = serializers.IntegerField()
      total_sales = serializers.IntegerField()
      total_revenue = serializers.DecimalField(max_digits=10,decimal_places=2)
      pending_orders = serializers.IntegerField()
      stock_alerts = StockAlertSerializer(many=True)