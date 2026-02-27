import os
from dotenv import load_dotenv
from typing import List
from datetime import datetime

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

import json
# Internal Module Imports
from src.search import RAGSearch
from src.tools import (
    create_it_ticket, 
    request_software_license, 
    reset_access_credentials,
    check_system_status,
    request_laptop_replacement,
    check_leave_balance, 
    submit_reimbursement_claim,
    get_employee_details,
    validate_policy_compliance,
    list_employees_by_insurance,
    check_repo_health,
    request_deployment_slot,
    search_benefits
)
load_dotenv()

class EnterpriseAgent:
    def __init__(self):
        self.rag_engine = RAGSearch()
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

        @tool
        def search_enterprise_knowledge(query: str) -> str:
            """Searches the HCLTech Annual Report and internal docs for factual answers."""
            # We access rag_engine directly from the class scope here
            answer, sources = self.rag_engine.get_answer(query)

            payload = {
                "status": "SUCCESS" if answer else "NOT_FOUND",
                "result": answer,
                "source_metadata": sources,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
            return json.dumps(payload) # This stops the "Unexpected token I" error

        self.tools = [
            search_enterprise_knowledge, 
            create_it_ticket,
            request_software_license,
            reset_access_credentials,
            check_system_status,
            request_laptop_replacement,
            check_leave_balance, 
            submit_reimbursement_claim,
            get_employee_details,
            validate_policy_compliance,
            list_employees_by_insurance,
            check_repo_health,
            request_deployment_slot,
            search_benefits
        ] 

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the 'NexaSupport' Enterprise Assistant for HCLTech.
            RULES: 
            1. For questions about company performance, use 'search_enterprise_knowledge'. 
            2. For IT requests, use the appropriate action tool. 
            3. When an action is performed, display the JSON output clearly. 
            4. If details like priority or category are missing, assign defaults and proceed.
            5. For every action tool invoked (Status Checks, Credential Resets, etc.), you MUST include the technical payload or JSON result in your final response so it can be parsed by the system. Do not just summarize; provide the data.
            6. You have access to hr_policy.json and network_topology.json via your search tool. These files contain key-value pairs. If asked about a specific Employee ID or Office, search for that ID/Office name specifically. For example, if asked for EMP_6621, search for 'EMP_6621' in the enterprise knowledge.
            7. MANDATORY RULE: For every tool you call, you must copy the complete JSON output of that tool into your final response. Wrap each JSON block in triple backticks and start it with the word 'json'. If you do not include the JSON, the system monitor will fail. Do not just summarize; provide the raw data blocks.
            8. CRITICAL SECURITY RULE: The currently logged-in user is {current_emp_id}. You are ONLY allowed to retrieve data or perform actions for {current_emp_id}.If the user claims to be someone else or asks for another employee's data, you MUST refuse and state that you can only assist with their own account."""),            
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        try:
            self.agent = create_tool_calling_agent(
                llm=self.llm, 
                tools=self.tools, 
                prompt=self.prompt
            )
            
            self.agent_executor = AgentExecutor(
                agent=self.agent, 
                tools=self.tools, 
                verbose=True,
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
        except Exception as e:
            print(f"Initialization Error: {e}")

    def run(self, user_input: str, history: list = [],current_emp_id: str = "Unknown"):
        """Executes the agent logic and returns the full dictionary"""
        return self.agent_executor.invoke({
            "input": user_input, 
            "chat_history": history,
            "current_emp_id": current_emp_id
        })