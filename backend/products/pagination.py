from rest_framework.pagination import CursorPagination

class ProductCursorPagination(CursorPagination):
      page_size = 20
      page_size_query_param = 'limit'
      max_page_size= 100
      ordering='id'