import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import base64
from langchain_core.messages import HumanMessage

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

vision_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  
    google_api_key=api_key,
)

def qa_image_tool(question: str, image_bytes: bytes):
    """q&a over bill / bank statement image"""
    if not question:
        return "Please ask a question about the image."
    if not image_bytes:
        return "No image received."

    prompt = (
    "You are a finance helper. "
    "Look at this bill or bank statement image and answer the question briefly:\n"
    f"{question}"
)


    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    msg = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                },
            },
        ]
    )

    resp = vision_llm.invoke([msg])
    return resp.content
