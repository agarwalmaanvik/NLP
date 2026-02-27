import json
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
import os
import streamlit as st

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

from pydantic import BaseModel, Field
from typing import Optional

class SoftwareRequestInput(BaseModel):
    software_name: str = Field(description="Name of the software (e.g., Adobe, JetBrains, Office365)")
    business_justification: str = Field(description="The reason why the employee needs this software")
    license_type: str = Field(description="Standard, Pro, or Enterprise", default="Standard")

class AccessResetInput(BaseModel):
    system_name: str = Field(description="The system needing access (e.g., VPN, SAP, Email, GitHub)")
    issue_type: str = Field(description="Password Reset, MFA Resync, or Locked Account")

SOFTWARE_INVENTORY_PATH = os.path.join("data", "it_docs", "software_inventory.json")

@tool("request_software_license", args_schema=SoftwareRequestInput)
def request_software_license(software_name: str, business_justification: str, license_type: str = "Standard") -> str:
    """Checks the internal software inventory and initiates a provisioning request if available."""
    
    # 1. Load Software Inventory
    if not os.path.exists(SOFTWARE_INVENTORY_PATH):
        return f"ERROR: Software database not found at {SOFTWARE_INVENTORY_PATH}"

    try:
        with open(SOFTWARE_INVENTORY_PATH, "r") as f:
            inventory = json.load(f)
    except Exception as e:
        return f"ERROR: Could not read software database: {str(e)}"

    # 2. Fuzzy Search for the Software
    search_query = software_name.lower()
    software_entry = None
    
    for item in inventory:
        if search_query in item["name"].lower():
            software_entry = item
            break
            
    # 3. Decision Logic based on Inventory & Policy
    if not software_entry:
        return f"NOT_FOUND: '{software_name}' is not in the HCLTech approved software list. Please file a custom procurement request."

    # Check availability
    if software_entry["available_licenses"] <= 0:
        status = "DENIED"
        message = f"Currently 0 licenses available for {software_entry['name']}."
    else:
        status = "PENDING_APPROVAL" if "Manager" in software_entry["policy"] else "AUTO_APPROVED"
        message = f"License available. Policy: {software_entry['policy']}"

    # 4. Return Technical Payload
    report = {
        "status": status,
        "action": "SOFTWARE_PROVISIONING_REQUEST",
        "data": {
            "software_full_name": software_entry["name"],
            "requested_by_justification": business_justification,
            "policy_applied": software_entry["policy"],
            "remaining_inventory": software_entry["available_licenses"],
            "department_owner": software_entry["department"],
            "system_message": message
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return json.dumps(report, indent=2)

@tool("reset_access_credentials", args_schema=AccessResetInput)
def reset_access_credentials(system_name: str, issue_type: str):
    """Use this for MFA resets, account lockouts, or password reset requests."""
    payload = {
        "action": "IDENTITY_ACCESS_MANAGEMENT",
        "system": system_name,
        "type": issue_type,
        "automation_eligible": True
    }
    return json.dumps(payload, indent=2)

NETWORK_DATA_PATH = os.path.join("data", "it_docs", "network_topology.json")

class NetworkCheckInput(BaseModel):
    region: str = Field(description="The office region or city, e.g., Noida, Bangalore, Singapore")

@tool("check_system_status", args_schema=NetworkCheckInput)
def check_system_status(region: str) -> str:
    """Consults the live network topology logs to check for outages and system health."""
    
    if not os.path.exists(NETWORK_DATA_PATH):
        return f"ERROR: Network database not found at {NETWORK_DATA_PATH}"

    try:
        with open(NETWORK_DATA_PATH, "r", encoding='utf-8') as f:
        # Use .read() and then json.loads to ensure we are pulling fresh bits
            topology_data = json.loads(f.read())
    except Exception as e:
        return f"ERROR: Could not read network database: {str(e)}"

    # 2. Search for the region (Case-insensitive fuzzy match)
    search_query = region.lower()
    found_region = None
    
    for key in topology_data.keys():
        if search_query in key.lower():
            found_region = key
            break
    
    # 3. Handle Result
    if found_region:
        status_info = topology_data[found_region]
        
        # We build a structured response payload
        report = {
            "status": "SUCCESS",
            "action": "NETWORK_HEALTH_CHECK",
            "data": {
                "office_location": found_region,
                "health": status_info["status"],
                "gateway": status_info["gateway"],
                "known_issue": status_info["known_issue"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        # Returning as a string so the agent can display it/app.py can parse it
        return json.dumps(report, indent=2)
    else:
        return f"OFFICE_NOT_FOUND: No network data available for '{region}'. Please check the spelling or provide a major hub name (e.g., Noida, London)."

class ReplacementInput(BaseModel):
    asset_id: str = Field(description="The Asset Tag of the laptop")
    years_old: int = Field(description="How many years the laptop has been in use")

@tool("request_laptop_replacement", args_schema=ReplacementInput)
def request_laptop_replacement(asset_id: str, years_old: int):
    """Use this to start a replacement workflow for old hardware."""
    if years_old >= 4:
        return {
            "status": "APPROVED",
            "action": "ORDER_NEW_HARDWARE",
            "model_suggestion": "HCL-EliteBook-2026",
            "reason": "Hardware lifecycle exceeded (4+ years)."
        }
    else:
        return {
            "status": "DENIED",
            "reason": f"Hardware is only {years_old} years old. Policy requires 4 years for replacement."
        }
    
@tool("analyze_server_logs")
def analyze_server_logs(error_code: str) -> str:
    """Scans raw server logs to find the root cause of a specific error code."""
    path = os.path.join("data", "it_docs", "server_logs.txt")
    if not os.path.exists(path): return "Log file not found."
    
    with open(path, "r") as f:
        logs = f.readlines()
    
    relevant_lines = [line for line in logs if error_code in line]
    
    if relevant_lines:
        return f"LOG_ANALYSIS_FOUND: {relevant_lines[-1]}"
    return "No matching error code found in recent logs."

it_tools = [create_it_ticket, request_software_license, reset_access_credentials, check_system_status, request_laptop_replacement, analyze_server_logs]

HR_POLICY_PATH = os.path.join("data", "hr_docs", "hr_policy.json")

@tool("get_employee_details")
def get_employee_details(emp_id: str) -> str:
    """Fetches manager, designation, and leave balances for an employee ID."""
    if not os.path.exists(HR_POLICY_PATH):
        return "HR database file not found."
    
    with open(HR_POLICY_PATH, "r") as f:
        data = json.load(f)
    authenticated_id = st.session_state.get('emp_id', 'Unknown')

    if emp_id.upper() != authenticated_id.upper():
        return f"SECURITY ERROR: You ( {authenticated_id} ) are not authorized to access data for {emp_id}."
    record = data.get(emp_id.upper())
    
    if record:
        return json.dumps({"status": "SUCCESS", "employee_data": record})
    return f"No record found for Employee ID: {emp_id}"

class LeaveCheckInput(BaseModel):
    emp_id: str = Field(description="The Employee ID, e.g., EMP_6621")
    leave_type: str = Field(description="casual, sick, or earned")

@tool("check_leave_balance", args_schema=LeaveCheckInput)
def check_leave_balance(emp_id: str, leave_type: str) -> str:
    """Checks the remaining leave balance for a specific employee."""
    if not os.path.exists(HR_POLICY_PATH): return "HR Database not found."
    
    with open(HR_POLICY_PATH, "r") as f:
        data = json.load(f)
    
    emp_data = data.get(emp_id.upper())
    if not emp_data: return f"Employee ID {emp_id} not found."
    
    authenticated_id = st.session_state.get('emp_id', 'Unknown')

    if emp_id.upper() != authenticated_id.upper():
        return f"SECURITY ERROR: You ( {authenticated_id} ) are not authorized to access data for {emp_id}."
    balance_key = f"{leave_type.lower()}_leave_balance"
    balance = emp_data.get(balance_key, "N/A")
    
    return json.dumps({
        "status": "SUCCESS",
        "data": {
            "employee": emp_data["name"],
            "leave_type": leave_type,
            "balance": balance,
            "manager": emp_data["manager"]
        }
    })

class ReimbursementInput(BaseModel):
    item: str = Field(description="The item being claimed (e.g., Gym, Internet, Certifications)")
    amount: int = Field(description="The amount in INR")

@tool("submit_reimbursement_claim", args_schema=ReimbursementInput)
def submit_reimbursement_claim(item: str, amount: int) -> str:
    """Processes a reimbursement request for the logged-in user."""
    limits = {"gym": 2000, "internet": 1000, "certification": 15000}
    item_key = item.lower()
    limit = limits.get(item_key, 500)
    
    status = "APPROVED" if amount <= limit else "FLAGGED_FOR_REVIEW"
    authenticated_id = st.session_state.get('emp_id', 'Unknown')
    
    return json.dumps({
        "status": status,
        "employee_id": authenticated_id,
        "action": "FINANCE_REIMBURSEMENT_POST",
        "details": {
            "category": item,
            "amount_claimed": amount,
            "note": "Auto-approved" if status == "APPROVED" else "Exceeds limit"
        }
    })

@tool("validate_policy_compliance")
def validate_policy_compliance(request_type: str, details: str) -> str:
    """Checks if a specific request aligns with HCLTech's 2025 policies."""
    
    report = {
        "status": "PENDING_INPUT",
        "action": "POLICY_VALIDATION_QUEUE",
        "details": {
            "type": request_type,
            "user_input": details
        },
        "next_step": f"Search enterprise knowledge for '{request_type} policy' to finalize."
    }
    
    return json.dumps(report) # This prevents the 'P' parse error

@tool("list_employees_by_insurance")
def list_employees_by_insurance(plan_name: str) -> str:
    """Filters the HR database for all employees on a specific insurance plan."""
    if not os.path.exists(HR_POLICY_PATH): return json.dumps({"error": "DB not found"})
    
    with open(HR_POLICY_PATH, "r") as f:
        data = json.load(f)
    
    matches = {k: v['name'] for k, v in data.items() if plan_name.lower() in v['insurance_plan'].lower()}
    
    return json.dumps({"status": "SUCCESS", "plan": plan_name, "matches": matches})

hr_tools = [check_leave_balance, submit_reimbursement_claim, get_employee_details, validate_policy_compliance, list_employees_by_insurance]

DEV_REPOS_PATH = os.path.join("data", "dev_docs", "github_repos.json")

class RepoCheckInput(BaseModel):
    repo_name: str = Field(description="The name of the repository to check")

@tool("check_repo_health", args_schema=RepoCheckInput)
def check_repo_health(repo_name: str) -> str:
    """Checks the status, language, and vulnerabilities of a specific HCL repository."""
    if not os.path.exists(DEV_REPOS_PATH): return "Dev database not found."
    
    with open(DEV_REPOS_PATH, "r") as f:
        repos = json.load(f)
    
    found_repo = next((k for k in repos if repo_name.lower() in k.lower()), None)
    
    if found_repo:
        data = repos[found_repo]
        return json.dumps({
            "status": "SUCCESS",
            "repo": found_repo,
            "details": data
        })
    return f"Repository '{repo_name}' not found in internal HCLTech Git."

@tool("request_deployment_slot")
def request_deployment_slot(service_name: str, environment: str = "Staging") -> str:
    """Books a deployment window in the CI/CD pipeline."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:00")
    return json.dumps({
        "status": "SLOT_BOOKED",
        "service": service_name,
        "env": environment,
        "window": f"{timestamp} to 4 hours later",
        "action": "TRIGGER_JENKINS_PIPELINE"
    })

dev_tools = [check_repo_health, request_deployment_slot]


@tool("search_benefits")
def search_benefits(query: str) -> str:
    """Searches the Benefits Summary (TXT) for policy and financial data."""
    
    query_lower = query.lower()
    search_hits = []

    # Logic for Benefits Summary (TXT Context)
    if any(k in query_lower for k in ["wellness", "reimbursement", "gym", "bonus", "leave", "policy"]):
        search_hits.append({
            "source": "benefits_summary.txt",
            "content": "Employees are eligible for gym reimbursement up to ₹2,000/month. No 'Wellness Day' policy found; please refer to standard leave types."
        })

    if not search_hits:
        payload = {
            "status": "NOT_FOUND",
            "message": f"No data found for '{query}' in the Benefits Summary.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        payload = {
            "status": "SUCCESS",
            "matches": search_hits,
            "metadata": {
                "engine": "MilvusHybridStore",
                "embedding_model": "BGE-M3"
            }
        }
    return json.dumps(payload, indent=2)