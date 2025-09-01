import datetime
import os
import sys

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """Logs a heartbeat message to a file every 5 minutes and optionally
    checks the GraphQL endpoint for health.
    """
    try:
        # Generate the timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Verify if app is running
        graphql_status = "UNKWOWN"
        try transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql(" {hello }")
        result = client.execute(query)
        if result.get('hello') == "Hello, GraphQL!":
            graphql_status = "OK"
        except Exception:
            graphql_status = "ERROR"
        
        # --- Log the heartbeat message
        with open (LOG_FILE, "a") as f:
            log_message = f"{timestamp} CRM is alive (GraphQL: {graphql_status})"
            f.write(log_message + "\n")
        
        print(log_message)
    
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
            error_message = f"{timestamp} CRON JOB ERROR: {e}"
            f.write(error_message + "\n")
            
        sys.stderr.write(error_message + "\n")
