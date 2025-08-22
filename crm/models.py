from django.db import models


class Customer(models.Model):
    """Customer model.
    Attributes:
        name (str): The name of the customer.
        email (str): The email address of the customer.
        phone (str): The phone number of the customer.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)


class Product(models.Model):
    """Product model.
    Attributes:
        name (str): The name of the product.
        stock (int): The number of items available for sale.
        price (Decimal): The price of the product.
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)


class Order(models.Model):
    """Order model.
    Attributes:
        customer (Customer): The customer who placed the order.
        product (Product): The product being ordered.
        status (str): The current status of the order.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
