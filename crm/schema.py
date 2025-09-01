import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Sum
from decimal import Decimal as PyDecimal
import django_filters

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# --- Custom Scalar for Float to Decimal Conversion ---
class FloatDecimal(graphene.Decimal):
    @staticmethod
    def parse_value(value):
        if isinstance(value, float):
            return PyDecimal(str(value))
        return super(FloatDecimal, FloatDecimal).parse_value(value)


# --- GraphQL Type Definitions ---
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
    
    products = graphene.List(ProductType)
    
    def resolve_products(self, info):
        return self.product.all()


# --- GraphQL Input Types ---
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = FloatDecimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customerId = graphene.ID(required=True)
    productIds = graphene.List(graphene.ID, required=True)


# --- GraphQL Mutation Classes ---
class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        input = CustomerInput(required=True)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            return CreateCustomer(customer=customer, message="Customer created successfully.")
        except Exception as e:
            return CreateCustomer(customer=None, message=f"Error creating customer: {str(e)}")


class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        for data in input:
            try:
                customer = Customer.objects.create(
                    name=data.get('name'),
                    email=data.get('email'),
                    phone=data.get('phone')
                )
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"Error for email {data.get('email')}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        input = ProductInput(required=True)

    def mutate(self, info, input):
        if input.price <= 0:
            return CreateProduct(
                product=None,
                message="Error creating product: Price must be a positive number."
            )
        
        if input.stock < 0:
            return CreateProduct(
                product=None,
                message="Error creating product: Stock cannot be a negative number."
            )

        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=input.stock
            )
            return CreateProduct(
                product=product,
                message="Product created successfully!."
            )
        except Exception as e:
            return CreateProduct(
                product=None,
                message=f"Error creating product: {str(e)}"
            )


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    message = graphene.String()

    class Arguments:
        input = OrderInput(required=True)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customerId)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, message="Error creating order: Customer not found.")
        
        if not input.productIds:
            return CreateOrder(order=None, message="Error: An order must contain at least one product.")
        
        products = Product.objects.filter(id__in=input.productIds)
        if len(products) != len(input.productIds):
            existing_ids = set(p.id for p in products)
            missing_ids = [id for id in input.productIds if id not in existing_ids]

            return CreateOrder(
                order=None,
                message=f"Error: Product(s) not found with IDs: {', '.join(map(str, missing_ids))}"
            )
        
        try:
            order = Order.objects.create(customer=customer)
            order.product.set(products)
            total_amount = products.aggregate(Sum('price'))['price__sum']
            order.total_amount = total_amount
            order.save()
            
            return CreateOrder(order=order, message="Order created successfully")
        except Exception as e:
            return CreateOrder(order=None, message=f"Error creating order: {str(e)}"
            )


# ---  Schedule a GraphQL Mutation for Product Stock Alerts ---
class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()
    
    class Arguments:
        pass
    
    def mutate(self, info):
        # Find products with stock less than 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        
        updated_list = []
        for product in low_stock_products:
            # Increment stock by 10
            product.stock += 10
            product.save()
            updated_list.append(product)

        if updated_list:
            message = f"Successfully updated stock for {len(updated_list)} products."
        else:
            message = "No products found with low stock."

        return UpdateLowStockProducts(updated_products=updated_list, message=message)


# --- Root Query and Mutation Classes ---
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    allCustomers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    allProducts = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    allOrders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulkCreateCustomers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
