import streamlit as st
import pandas as pd
import PyPDF2
import ollama 

# Full screen layout
st.set_page_config(page_title="Xavier - Your Finance Assistant", layout="wide")

# App Header with name, description & tagline
st.markdown(
    """
<div style="text-align: center; padding: 20px;">
    <h1 style="font-size: 52px; margin:0;">
         <span style="color: #B8860B;">X@v</span>
        🤖<span style="color: #000000;">Ier</span>
    </h1>
    <h3 style="color:#566573; font-weight: normal;">
        Your intelligent financial assistant – upload documents, ask questions, and get instant insights.
    </h3>
    <p style="font-style: italic; color: #7B7D7D; margin-top: 10px;">
        "Empowering decisions with clarity." – created by <b>Rajesh Kumar Maurya</b>
    </p>
</div>


    """,
    unsafe_allow_html=True
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

# Upload section in a nice card
st.markdown("### 📂 Upload Your Document")
uploaded_file = st.file_uploader("Upload a financial document (PDF or Excel)", type=["pdf", "xlsx"])

doc_content = ""

if uploaded_file is not None:
    st.success(f"✅ Uploaded file: {uploaded_file.name}")

    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        st.markdown("**Preview of your Excel data:**")
        st.dataframe(df.head(), use_container_width=True)
        doc_content = df.to_string()

    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        st.markdown("**📄 Extracted text from PDF:**")
        st.text_area("PDF Content", pdf_text, height=300)
        doc_content = pdf_text

# --- Chat Interface ---
if doc_content:
    st.markdown("### 💬 Ask Questions about Your Document")

    with st.form("qa_form", clear_on_submit=True):
        user_question = st.text_input("Type your question here:", key="question_input")
        submitted = st.form_submit_button("Ask")

    if submitted and user_question:
        with st.spinner("🤖 Thinking... please wait!"):
            prompt = f"""
            You are a financial assistant. Answer the user’s question based on the document below:

            Document:
            {doc_content}

            Question: {user_question}
            """
            try:
                response = ollama.chat(
                    model="gemma3:latest",
                    messages=[{"role": "user", "content": prompt}]
                )

                if hasattr(response, "message") and hasattr(response.message, "content"):
                    answer_text = response.message.content
                elif isinstance(response, list):
                    answer_text = "\n".join([msg.message.content for msg in response])
                else:
                    answer_text = str(response)

            except Exception as e:
                answer_text = f"⚠️ Error generating response: {e}"

        st.session_state.chat_history.append((user_question, answer_text))

    # --- Display chat history (latest first) ---
    for q, a in reversed(st.session_state.chat_history):
        st.markdown(
            f"""
            <div style="background-color:#E8F6F3; padding:12px; border-radius:10px; margin-bottom:20px;">
                <b>🧑 You asked:</b> {q}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="background-color:#F4F6F7; padding:12px; border-radius:10px; margin-bottom:20px;">
                {a}
            </div>
            """,
            unsafe_allow_html=True,
        )
