import requests
from django.conf import settings
from uuid import uuid4
from collections import defaultdict

SHIPMENT_API_URL = "http://shipping-api:9000/api/shipments/"

def create_shipment(order):
      print("### DENEME TEST SHİPMENT SERVİCE ###")
      shipments = []
      items_by_seller = defaultdict(list)
      for item in order.order_items.all(): # [{1: [item..., item]}] seller: items
            items_by_seller[item.product.seller].append(item)
            
      for seller, items in items_by_seller.items(): # one tracking_number for per seller
            description = "test"
            
            if hasattr(seller, "profile") and (seller.profile.seller_name or seller.profile.company_name):
                  sender_name = seller.profile.seller_name or seller.profile.company_name
            elif seller.first_name or seller.last_name:
                  sender_name = f"{seller.first_name or ''} {seller.last_name or ''}".strip()
            else:
                  sender_name = seller.email
            
            payload = {
                  "sender_name": seller.profile.seller_name or f"{seller.first_name}",
                  "sender_address": seller.address,
                  "receiver_name": order.user.first_name,
                  "receiver_address": order.address,
                  "receiver_phone": order.user.phone_number,
                  "description": description
            }
      
            try:
                  response = requests.post(SHIPMENT_API_URL, json=payload, timeout=5)
                  response.raise_for_status()
                  data = response.json()
                  tracking_number = data.get('tracking_number')
                  for i in items:
                        i.tracking_number = tracking_number
                        i.save()
                  shipments.append(data)
            except Exception as e:
                  print("Shipment API Error: ",e)
                  shipments.append({"error": str(e), "seller": sender_name})
      return shipments

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
            return None