import sys
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

print("Order reminders processed!")

# --- GraphQL Setup ---
transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql/',
)

# Create a Graphql client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Define Graph Qeury
query = gql(
    """
    query FindRecentOrders($startDate: Date!, $endDate: Date!){
        allOrders(orderDate_Gte: $startDate, orderDate_Lte: $endDate) {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                }
            }
        }
    }
    """
)

try:
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    params = {"startDate": start_date, "endDate": end_date}
    result = client.execute(query, variable_values=params)

    orders = result.get('allOrders', {}).get('edges', [])
    
    log_file_path = "/tmp/order_reminders_log.txt"
    with open(log_file_path, "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not orders:
            log_message = f"[{timestamp}] - No new orders found in the last 7 days."
            log_file.write(log_message + "\n")
            print(log_message)
        
        for edge in orders:
            order_node = edge.get('node')
            if order_node:
                order_id = order_node.get('id')
                customer_email = order_node.get('customer', {}).get('email')
                
                log_message = f"[{timestamp}] - Reminder for Order ID: {order_id}, Customer Email: {customer_email}"
                log_file.write(log_message + "\n")
                print(log_message)
except Exception as e:
    # Log any errors that occur during the process
    log_file_path = "/tmp/order_reminders_log.txt"
    with open(log_file_path, "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] - ERROR: {e}\n")
    sys.stderr.write(f"An error occurred: {e}\n")