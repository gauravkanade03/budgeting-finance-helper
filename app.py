import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from agent import add_expense, budget_analyzer, savings_advisor, qa_tool, expenses

st.set_page_config(page_title="Budgeting & Finance Helper", layout="centered")

st.title("💰 Budgeting & Finance Helper")

st.write(
    "Track expenses, analyze your simple budget, get saving tips, and ask finance questions."
)

st.header("1. Add Expense")

with st.form("add_expense_form"):
    col1, col2 = st.columns(2)
    with col1:
        amount = st.text_input("Amount (₹)", "")
    with col2:
        category = st.text_input("Category (e.g., Food, Rent, Travel)", "")

    description = st.text_input("Description (optional)", "")
    submitted = st.form_submit_button("Add")

    if submitted:
        msg = add_expense(amount, category, description)
        if msg.startswith("Error"):
            st.error(msg)
        else:
            st.success(msg)

st.header("2. Budget Analyzer")

if st.button("Analyze Budget"):
    summary = budget_analyzer()
    st.text(summary)

st.header("3. Savings Advisor")
if st.button("🚀 Get AI Saving Tips"):
    with st.spinner("Agent thinking... using tools..."):
        tips = savings_advisor()
    st.markdown(tips)

st.header("4. Finance Q&A")

question = st.text_input("Ask a finance question (e.g., How can I save more on food?)")
if st.button("Get Answer"):
    answer = qa_tool(question)
    st.write(answer)

st.header("5. Dashboard")

if expenses:
    df = pd.DataFrame(expenses)
    st.subheader("Expense Table")
    st.dataframe(df)

    st.subheader("Spending by Category")
    by_cat = df.groupby("category")["amount"].sum().reset_index()

    fig, ax = plt.subplots()
    ax.bar(by_cat["category"], by_cat["amount"])
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Expenses by Category")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("No expenses added yet. Add some expenses to see the dashboard.")
