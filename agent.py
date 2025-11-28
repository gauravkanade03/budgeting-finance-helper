import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# load api keys from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    print("oops! GEMINI_API_KEY missing in .env")  
    raise ValueError("GEMINI_API_KEY not found. Please set it in .env")
if not tavily_key: 
    raise ValueError("TAVILY_API_KEY not found. Please set it in .env")

# using gemini flash model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)

# global list to store expenses 
expenses = []

def add_expense(amount, category, desc):
    """add new expense - basic error checking"""
    try:
        amount = float(amount)  # convert to number
    except:
        return "❌ Error: Amount must be a number."
    
    if not category:  
        return "❌ Error: Category cannot be empty."
    
    expenses.append({"amount": amount, "category": category, "desc": desc or ""})
    return f"✅ Added ₹{amount} to '{category}'"  

def budget_analyzer():
    """my custom function to analyze spending - hackathon requirement!"""
    if not expenses:
        return "No expenses yet. Add some first."
    
    total = sum(e["amount"] for e in expenses)  # total spending
    by_cat = {}
    
    # group by category 
    for e in expenses:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]
    
    # flag overspending if >500 
    overspending = [c for c, v in by_cat.items() if v > 500]
    
    lines = [f"Total spent: ₹{total:.0f}"]
    lines.append("By category:")
    
    for c, v in by_cat.items():
        lines.append(f"   - {c}: ₹{v:.0f}")
    
    if overspending:
        lines.append(f"Overspending: {', '.join(overspending)}")
    else:
        lines.append("No overspending detected!")
    
    return "\n".join(lines)

# tavily search setup 
tavily_search = TavilySearchResults(max_results=1, api_key=tavily_key)

# langchain tools 
@tool
def get_budget_summary() -> str:
    """Tool 1: my budget analysis tool"""
    return budget_analyzer()

@tool
def web_search_tool(query: str) -> str:
    """Tool 2: search web for saving tips"""
    return tavily_search.run(query)

# main agent function - combines tools + ai
def savings_advisor():
    if not expenses:
        return "No expenses yet. Add some first."
    
    # call tools 
    budget_info = get_budget_summary.invoke("") or budget_analyzer()
    
    search_query = "simple ways to save money on groceries rent transport"
    raw_web_result = web_search_tool.invoke(search_query) or "Web search unavailable"
    web_str = str(raw_web_result)
    web_tips = (web_str[:300] + "...") if len(web_str) > 50 else web_str

    # prompt template for gemini 
    template = """
    You are a helpful finance buddy.

    Here is my budget info:
    {budget_info}
    
    And some tips I found online:
    {web_tips}
    
    Please suggest 3 to 5 easy and practical money-saving tips related to my spending.

    """
    
    prompt = PromptTemplate(input_variables=["budget_info", "web_tips"], template=template)
    response = llm.invoke(prompt.format(budget_info=budget_info, web_tips=web_tips))
    
    # return formatted result
    return f"""
**Budget:** {budget_info}

**Web Research:** {web_tips}

**💡 Saving Tips:** {response.content}
"""

def qa_tool(question: str):
    """simple q&a - bonus feature"""
    if not question:
        return "Please ask a question."
    
    template = """
    You are a friendly finance helper.
    
    Answer this question clearly and briefly:
    {question}
    
    Explain in simple terms, like talking to a friend.
    Give one practical tip if possible.
    """
    prompt = PromptTemplate(input_variables=["question"], template=template)
    response = llm.invoke(prompt.format(question=question))
    return response.content
