import os
from dotenv import load_dotenv
from typing import List, Any

# LangChain Agent Modules
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# Internal Module Imports
from src.search import RAGSearch
from src.tools import it_tools # Your create_it_ticket tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class EnterpriseAgent:
    def __init__(self):
        # 1. Initialize our RAG Engine (with Milvus + BGE-M3 + Reranker)
        self.rag_engine = RAGSearch()
        
        # 2. Define the RAG Tool 
        # We wrap the RAG logic so the Agent can "see" it as a tool
        @tool
        def search_enterprise_knowledge(query: str) -> str:
            """
            Search the HCLTech Annual Report, IT logs, and internal policies.
            Use this for any factual questions or 'Chat with PDF' tasks.
            """
            answer, _ = self.rag_engine.get_answer(query)
            return answer

        # 3. Combine All Tools (Search + Actions)
        self.tools = [search_enterprise_knowledge] + it_tools

        # 4. Initialize the LLM (The Brain)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # 5. Define the System Prompt (The "Mission Briefing")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are the 'Language Wizard' Enterprise Assistant for HCLTech.
            Your goal is to help employees with IT, HR, and Developer tasks.
            
            RULES:
            1. For questions about company performance or strategy, use 'search_enterprise_knowledge'.
            2. For 'Action Tests' (like filing tickets), use the appropriate action tool.
            3. When an action is performed, ensure you display the VALID JSON output for the judges.
            4. Be professional, concise, and always cite your sources if provided by the tools.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 6. Create the Agent
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, # Shows the "Thought Process" in terminal
            handle_parsing_errors=True
        )

    def run(self, user_input: str, history: list = []):
        """Executes the agent logic for a user query."""
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": history
        })
        return response["output"]

# Example Usage for Testing
if __name__ == "__main__":
    bot = EnterpriseAgent()
    
    # Test 1: RAG Search (Annual Report)
    print("\n--- TEST 1: RAG ---")
    print(bot.run("What was HCLTech's revenue growth in 2024?"))
    
    # Test 2: Action Test (IT Ticket)
    print("\n--- TEST 2: ACTION ---")
    print(bot.run("My laptop won't start. File a high priority hardware ticket for me."))