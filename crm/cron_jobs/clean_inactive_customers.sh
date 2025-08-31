#!/bin/bash

# Navigate to the project directory and activate the virtual environment
# If it exists
# This script will print the number of deleted customers.
cd /Ubuntu/home/frankie/alx_projects/alx-backend-graphql_crm/
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Define log file path
LOG_FILE="/tmp/clean_inactive_customers_log.txt"

# Get the current timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

DELETED_CUSTOMERS=$(python manage.py shell -c"
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer, Order
import sys

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers_with_orders = Order.objects.filter(
    date_created__gte=one_year_ago
).values_list('customer', flat=True).distinct()

customers_to_delete = Customer.objects.exclude(
    id__in=inactive_customers_with_orders
)
deleted_count = customers_to_delete.count()
customers_to_delete.delete()

sys.stdout.write(str(deleted_count))
")

# Log the result with timestamp
echo "[${TIMESTAMP}] - Successfully deleted ${DELETED_CUSTOMERS} inactive customers." >> ${LOG_FILE}

# Deactivate the virtual environment
if [ -d "venv" ]; then
    deactivate
fi
