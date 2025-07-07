from rest_framework.permissions import BasePermission

class IsSellerOrAdmin(BasePermission):
      def has_permission(self, request, view):
            return request.user.is_authenticated and (request.user.role in ['seller', 'admin'])
      
class IsCustomer(BasePermission):
      def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.role == 'customer'