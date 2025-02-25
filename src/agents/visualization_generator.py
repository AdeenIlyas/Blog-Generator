import json
import streamlit as st
from utils.openai_client import OpenAIClient
from config.prompts import VISUALIZATION_EXPERT_PROMPT

def generate_visuals(blog_text: str) -> list:
    client = OpenAIClient.get_client()
    try:
        user_message = (f"Create 2-3 strategic visualizations using Mermaid.js for the following blog content. "
                        f"Explain the Mermaid.js code briefly."
                       f"Return a valid JSON response containing the diagrams and a brief code explanations.\n\n"
                       f"Content:\n{blog_text}")
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": VISUALIZATION_EXPERT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        visuals_str = response.choices[0].message.content.strip()
        visuals_str = visuals_str.replace('```json', '').replace('```', '').strip()
        try:
            visuals_data = json.loads(visuals_str)
            if isinstance(visuals_data, dict) and "diagrams" in visuals_data:
                return visuals_data["diagrams"]
            elif isinstance(visuals_data, list):
                return visuals_data
            else:
                st.warning("Unexpected visuals format. Using empty list.")
                return []
        except json.JSONDecodeError:
            st.error("Invalid JSON response from visuals agent")
            return []
    except Exception as e:
        st.error(f"Error generating visuals: {str(e)}")
        return [] 