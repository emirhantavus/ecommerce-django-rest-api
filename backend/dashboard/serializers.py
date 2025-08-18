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
      
class TopSellingProductSerializer(serializers.Serializer):
      id = serializers.IntegerField()
      product = serializers.CharField()
      quantity = serializers.IntegerField()
      total_price = serializers.DecimalField(max_digits=12, decimal_places=2)#Maybe we can change max_digits later. !!
      
class AdminDashboardSerializer(serializers.Serializer):
      total_users = serializers.IntegerField()
      total_sellers = serializers.IntegerField()
      total_products = serializers.IntegerField()
      total_orders = serializers.IntegerField()
      total_revenue = serializers.DecimalField(max_digits=12,decimal_places=2)
      top_selling_product = TopSellingProductSerializer()