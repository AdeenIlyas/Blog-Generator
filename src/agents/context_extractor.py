import streamlit as st
from utils.openai_client import OpenAIClient
from config.prompts import NEWSLETTER_CONTEXT_PROMPT

def extract_context(newsletter: str) -> str:
    client = OpenAIClient.get_client()
    try:
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": NEWSLETTER_CONTEXT_PROMPT},
                {"role": "user", "content": f"Process this newsletter and extract its complete context:\n\n{newsletter}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Context extraction error: {str(e)}")
        return "" 