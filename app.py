import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from agent import add_expense, budget_analyzer, savings_advisor, qa_tool   # removed: , expenses
from image_agent import qa_image_tool

if "expenses" not in st.session_state:
    st.session_state.expenses = []

st.set_page_config(page_title="BudgetNest", layout="centered")
st.title("🪺BudgetNest")
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
            # also store in session so dashboard uses per-session data
            st.session_state.expenses.append(
                {"amount": float(amount), "category": category, "desc": description}
            )

# 2. Budget Analyzer
st.header("2. Budget Analyzer")

if st.button("Analyze Budget"):
    summary = budget_analyzer(st.session_state.expenses)
    st.text(summary)

st.header("3. Savings Advisor")
if st.button("🚀 Get AI Saving Tips"):
    with st.spinner("Agent thinking... using tools..."):
        tips = savings_advisor(st.session_state.expenses)
    st.markdown(tips)

st.header("4. Finance Q&A")

qa_question = st.text_input(
    "Ask a finance question (you can also upload a bill / statement image below)"
)

qa_image = st.file_uploader(
    "Optional: Upload bill / statement image (PNG / JPG)",
    type=["png", "jpg", "jpeg"],
)

if st.button("Get Answer"):
    if not qa_question:
        st.warning("Please type your question first.")
    else:
        if qa_image is not None:
            img_bytes = qa_image.getvalue()
            with st.spinner("Analyzing image..."):
                answer = qa_image_tool(qa_question, img_bytes)
                st.image(qa_image, caption="Uploaded image", width=500)
        else:
            answer = qa_tool(qa_question)

        st.write("**Question:**", qa_question)
        st.write("**Answer:**")
        st.write(answer)

st.header("5. Dashboard")

if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
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
