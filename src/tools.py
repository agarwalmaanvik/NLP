import json
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field

# 1. Define the Input Schema (The "Validation" layer)
# This tells the LLM: "You cannot call this tool unless you find these 4 things."
class ITTicketInput(BaseModel):
    subject: str = Field(description="A short, clear title for the IT issue")
    description: str = Field(description="The full context or error message provided by the user")
    priority: str = Field(description="Urgency level: Low, Medium, High, or Critical")
    category: str = Field(description="Type of issue: Hardware, Software, Access, or Network")

# 2. Define the IT Action Tool
@tool(args_schema=ITTicketInput)
def create_it_ticket(subject: str, description: str, priority: str, category: str) -> str:
    """
    Creates a mock IT support ticket. Trigger this tool ONLY when the user 
    wants to 'file a ticket', 'log an issue', or 'open a request'.
    """
    valid_priorities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    action_payload = {
        "status": "SUCCESS",
        "action": "TRIGGER_API_CREATE_INCIDENT",
        "metadata": {
            "source": "Kshitij_Agent_v1",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "json_output": {
            "ticket_id": f"HCL-INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "details": {
                "title": subject,
                "body": description,
                "urgency": priority.upper() if priority.upper() in valid_priorities else "MEDIUM",
                "department": category,
                "assigned_to": "ServiceDesk_Level1_Queue"
            }
        }
    }
    return json.dumps(action_payload, indent=4)

# 3. List of tools to be imported by your Agent Brain
it_tools = [create_it_ticket]