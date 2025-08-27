import requests
from django.conf import settings
from uuid import uuid4
from collections import defaultdict

SHIPMENT_API_URL = "http://shipping-api:9000/api/shipments/"

def create_shipment(order_item):
      order = order_item.order
      product = order_item.product
      seller = product.seller
      
      sender_name = seller.get_full_name()
      sender_address = seller.address
      
      receiver_name = order.user.get_full_name()
      receiver_address = order.address
      receiver_phone = order.user.phone_number
            
      payload = {
            "sender_name": sender_name,
            "sender_address": sender_address,
            "receiver_name": receiver_name,
            "receiver_address": receiver_address,
            "receiver_phone": receiver_phone,
            "description": f"{product.name} x {order_item.quantity}"
      }
      
      try:
            response = requests.post(SHIPMENT_API_URL, json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()
            tracking_number = data.get('tracking_number')
            if tracking_number:
                  order_item.tracking_number = tracking_number
                  order_item.save(update_fields=['tracking_number'])
            return data
      except Exception as e:
            print("Shipment API Error: ",e)
            return {'error':str(e)}

def get_shipment_by_tracking_number(tracking_number):
      try:
            url = f"{SHIPMENT_API_URL}tracking_number/{tracking_number}/"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                  return response.json()
            else:
                  return None
            
      except Exception as e:
            print("Shipment API Error: ",e)
            return {'error':str(e)}