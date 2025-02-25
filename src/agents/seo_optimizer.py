import json
import streamlit as st
from utils.openai_client import OpenAIClient
from config.prompts import SEO_EXPERT_PROMPT

def generate_seo_metadata(blog_text: str) -> dict:
    client = OpenAIClient.get_client()
    try:
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": SEO_EXPERT_PROMPT},
                {"role": "user", "content": f"Optimize this content and generate SEO metadata:\n\n{blog_text}"}
            ],
            temperature=0.3
        )
        seo_json_str = response.choices[0].message.content.strip()
        seo_json_str = seo_json_str.replace('```json', '').replace('```', '').strip()
        try:
            seo_metadata = json.loads(seo_json_str)
            required_fields = [
                "seo_enhanced_content",
                "page_title",
                "meta_title",
                "meta_description",
                "focus_keywords",
                "url_slug"
            ]
            missing_fields = [field for field in required_fields if field not in seo_metadata]
            if missing_fields:
                raise ValueError(f"Missing fields: {', '.join(missing_fields)}")
            return seo_metadata
        except json.JSONDecodeError:
            st.error("Invalid JSON response from SEO agent")
            return {
                "seo_enhanced_content": blog_text,
                "page_title": blog_text.split('\n')[0][:50] + "...",
                "meta_title": blog_text.split('\n')[0][:50] + "...",
                "meta_description": blog_text[:150] + "...",
                "focus_keywords": ["blog", "article"],
                "url_slug": blog_text.split('\n')[0].lower().replace(' ', '-')[:50]
            }
    except Exception as e:
        st.error(f"Error in SEO optimization: {str(e)}")
        return {"seo_enhanced_content": blog_text} 