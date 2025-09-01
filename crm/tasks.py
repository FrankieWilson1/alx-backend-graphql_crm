import sys
import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report by querying the GraphQL endpoint.
    """
    try:
        # GraphQL Setup
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # GraphQL query to get the required data
        query = gql(
            """
            query CrmReport {
                allCustomers {
                  totalCount
                }
                allOrders {
                  totalCount
                  edges {
                    node {
                      totalAmount
                    }
                  }
                }
            }
            """
        )
        
        # Execute the query
        result = client.execute(query)
        
        # Extract the data
        total_customers = result.get('allCustomers', {}).get('totalCount')
        all_orders = result.get('allOrders', {}).get('edges', [])
        total_orders = len(all_orders)
        
        # Calculate total revenue
        total_revenue = sum(
            order.get('node', {}).get('totalAmount', 0)
            for order in all_orders
        )

        # Log the report
        log_file_path = "/tmp/crm_report_log.txt"
        with open(log_file_path, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue."
            log_file.write(log_message + "\n")
        
        print(log_message)

    except Exception as e:
        # Log any errors
        log_file_path = "/tmp/crm_report_log.txt"
        with open(log_file_path, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_message = f"[{timestamp}] - ERROR generating report: {e}"
            log_file.write(error_message + "\n")
        sys.stderr.write(error_message + "\n")
        