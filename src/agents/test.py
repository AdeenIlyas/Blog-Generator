import streamlit as st
from utils.openai_client import OpenAIClient
from config.prompts import BLOG_WRITER_PROMPT
import textwrap

def chunk_newsletter(newsletter_content: str, chunk_size: int = 2000) -> list:
    return textwrap.wrap(newsletter_content, chunk_size, break_long_words=False, break_on_hyphens=False)

def generate_blog(newsletter_context: str) -> str:
    client = OpenAIClient.get_client()
    chunks = chunk_newsletter(newsletter_context)
    full_blog_content = ""
    previous_content = ""

    for chunk_index, chunk in enumerate(chunks):
        if chunk_index == 0:
            # First chunk uses the original prompt structure with all instructions included
            user_message = (
                f"NEWSLETTER CONTENT PART {chunk_index + 1}:\n\n{chunk}\n\n"
                "INSTRUCTIONS:\n"
                "1. Write a COMPLETE blog post section based on the provided newsletter content.\n"
                "2. Start with an introduction of at least 300 words that is engaging and interesting, capturing the essence of the newsletter content.\n"
                "3. Expand each topic fully. The blog must include an Introduction, 4-5 detailed sections, and a comprehensive conclusion covering every aspect of the newsletter content.\n"
                "4. Do not use AI generated phrases or sentences. Present the blog as if you're explaining it to a colleague; avoid technical jargon and maintain an easy-to-understand tone.\n"
                "5. Use proper markdown formatting with clear headings and subheadings derived from the newsletter content.\n"
                "6. Do not summarize—create detailed content that expands on the information provided.\n"
                "7. Ensure there is no repetition of the same content.\n"
                "8. Avoid visualizations, diagrams, tables, bullet points, or numbering; instead, expand through well-developed paragraphs.\n"
                "9. Write detailed sentences for better clarity and understanding.\n"
                "10. Ensure each section is engaging and in-depth, with each section (including its heading and any subheadings) containing a minimum of 500 words.\n"
                "Note: This is part 1 of the newsletter; more content will follow."
            )
        else:
            # Subsequent chunks continue from previous content with all original instructions reinserted
            user_message = (
                # f"PREVIOUS BLOG CONTENT (last 500 characters for context):\n\n{previous_content[-500:]}\n\n"
                f"CONTINUE WITH NEWSLETTER PART {chunk_index + 1}:\n\n{chunk}\n\n"
                "INSTRUCTIONS:\n"
                "1. Continue the blog post coherently from the previous section, maintaining the same engaging style and depth.\n"
                "2. Maintain the same writing style and mirror the newsletter content to keep the blog engaging.\n"
                "3. Expand each topic fully with detailed paragraphs.\n"
                "4. Use proper markdown formatting with appropriate headings and subheadings derived from the newsletter content.\n"
                "5. Ensure smooth transition from the previous content.\n"
                "6. Write detailed paragraphs that fully explain the information without summarizing.\n"
                "7. Do not use AI generated phrases or sentences. Present the blog as if you're explaining it to a colleague, avoiding technical jargon.\n"
                "8. Use the headings and information from the newsletter content. Avoid short sentences; use longer, descriptive sentences that keep the audience engaged.\n"
                "9. Present the blog as if telling a story in an engaging way to establish a personal connection with the audience.\n"
                "10. Ensure each section is engaging and maintains the depth of the newsletter content.\n"
                "11. Each section of the blog must have a heading and subheadings (if necessary) derived from the newsletter content.\n"
                "12. Avoid bullet points and numbering; expand through well-structured paragraphs.\n"
                "13. Write detailed sentences for better understanding.\n"
                "14. Each section must have at least 500 words to thoroughly explain the information.\n"
                "15. The blog must have 5 sections in total.\n"
                "16. Visualizations, diagrams, or tables are not allowed; expand the information solely through paragraphs.\n"
                "17. The blog must include a comprehensive conclusion summarizing the newsletter content.\n"
                f"{'18. End with a comprehensive conclusion as this is the final part.' if chunk_index == len(chunks)-1 else ''}"
            )

        try:
            response = client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {"role": "system", "content": BLOG_WRITER_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=8000,
                presence_penalty=1.0,
                frequency_penalty=0.5
            )

            chunk_content = response.choices[0].message.content.strip()

            # Ensure the first chunk starts with a markdown header if not already present
            if chunk_index == 0 and not chunk_content.startswith('#'):
                chunk_content = "# " + chunk_content

            full_blog_content += "\n\n" + chunk_content
            previous_content = chunk_content

        except Exception as e:
            st.error(f"Blog generation error in chunk {chunk_index + 1}: {str(e)}")
            return ""

    # Final formatting to ensure proper markdown spacing
    formatted_content = full_blog_content.replace('\n#', '\n\n#').replace('\n##', '\n\n##')

    # Save to README.md
    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(formatted_content)
    except Exception as e:
        st.error(f"Error saving to README.md: {str(e)}")

    return formatted_content
























































# import streamlit as st
# from utils.openai_client import OpenAIClient
# from config.prompts import BLOG_WRITER_PROMPT
# import textwrap

# def chunk_newsletter(newsletter_content: str, chunk_size: int = 2000) -> list:
#     return textwrap.wrap(newsletter_content, chunk_size, break_long_words=False, break_on_hyphens=False)

# def generate_blog(newsletter_context: str) -> str:
#     client = OpenAIClient.get_client()
#     chunks = chunk_newsletter(newsletter_context)
#     full_blog_content = ""
#     previous_content = ""

#     for chunk_index, chunk in enumerate(chunks):
#         if chunk_index == 0:
#             user_message = (
#                 f"NEWSLETTER CONTENT PART {chunk_index + 1}:\n\n{chunk}\n\n"
#                 "INSTRUCTIONS:\n"
#                 "1. Write a blog post section using ONLY the information provided in the newsletter content.\n"
#                 "2. Start with an engaging introduction (300 words) that summarizes the key points from the newsletter.\n"
#                 "3. Create sections ONLY for topics that are explicitly mentioned in the newsletter.\n"
#                 "4. IMPORTANT: Do not add any information, examples, or elaborations that are not directly from the newsletter.\n"
#                 "5. Use proper markdown formatting with headings from the newsletter content.\n"
#                 "6. Write in a natural, conversational tone while staying strictly focused on the newsletter content.\n"
#                 "7. If a section's information is complete, move to the next section. Do not add filler content.\n"
#                 "8. STRICTLY PROHIBITED:\n"
#                 "   - Adding AI-generated phrases or adjective/verb lists\n"
#                 "   - Creating examples not from the newsletter\n"
#                 "   - Adding hypothetical scenarios\n"
#                 "   - Using repetitive or synonymous words\n"
#                 "9. Each paragraph must directly relate to specific information from the newsletter.\n"
#                 "10. Explain the sections in detail. Do not use short or concise paragraph."
#                 "11. The paragraphs must cover the depth of the newsletter and must be easy to understand for the reader."
#                 "Note: Focus on quality over quantity. Only write what the newsletter content supports."
#             )
#         else:
#             user_message = (
#                 f"PREVIOUS BLOG CONTENT (for context):\n\n{previous_content[-500:]}\n\n"
#                 f"CONTINUE WITH NEWSLETTER PART {chunk_index + 1}:\n\n{chunk}\n\n"
#                 "INSTRUCTIONS:\n"
#                 "1. Continue the blog using ONLY the new newsletter content provided.\n"
#                 "2. Maintain continuity with the previous section without repeating information.\n"
#                 "3. IMPORTANT: Do not add any content that isn't explicitly in the newsletter.\n"
#                 "4. If this chunk doesn't contain new information for a section, move to the next topic.\n"
#                 "5. STRICTLY PROHIBITED:\n"
#                 "   - Adding filler content or AI-generated phrases\n"
#                 "   - Creating lists of synonyms or related words\n"
#                 "   - Adding speculative or hypothetical content\n"
#                 "   - Repeating information from previous sections\n"
#                 "6. Each new paragraph must be based on specific newsletter content.\n"
#                 "7. If all newsletter content has been covered, conclude the blog naturally.\n"
#                 "8. Focus on clear, direct communication of the newsletter information.\n"
            
#                 "Note: Quality and accuracy are important factors in the blog."
#             )

#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4",  # Changed to standard GPT-4
#                 messages=[
#                     {"role": "system", "content": "You are a precise blog writer who ONLY uses information directly from the provided newsletter content. Never add information, examples, or elaborations that aren't explicitly in the newsletter."},
#                     {"role": "user", "content": user_message}
#                 ],
#                 temperature=0.3,  # Reduced for more focused output
#                 max_tokens=5000,
#                 presence_penalty=0.0,  # Reduced to prevent creative additions
#                 frequency_penalty=1.0  # Increased to prevent word repetition
#             )

#             chunk_content = response.choices[0].message.content.strip()
            
#             # Validate content doesn't contain common filler patterns
#             if any(pattern in chunk_content.lower() for pattern in [
#                 "undeniably", "unquestionably", "indisputably",
#                 "groundbreaking", "revolutionary", "paradigm-shifting",
#                 "clearly", "obviously", "evidently"
#             ]):
#                 # Retry with stricter prompt
#                 response = client.chat.completions.create(
#                     model="gpt-4",
#                     messages=[
#                         {"role": "system", "content": "Write using ONLY the newsletter content. No embellishments."},
#                         {"role": "user", "content": user_message + "\nIMPORTANT: Write using ONLY the facts and information provided. No filler words or phrases."}
#                     ],
#                     temperature=0.2,
#                     max_tokens=4000,
#                     presence_penalty=0.0,
#                     frequency_penalty=1.0
#                 )
#                 chunk_content = response.choices[0].message.content.strip()

#             if chunk_index == 0 and not chunk_content.startswith('#'):
#                 chunk_content = "# " + chunk_content

#             full_blog_content += "\n\n" + chunk_content
#             previous_content = chunk_content

#         except Exception as e:
#             st.error(f"Blog generation error in chunk {chunk_index + 1}: {str(e)}")
#             return ""

#     # Final formatting
#     formatted_content = full_blog_content.replace('\n#', '\n\n#').replace('\n##', '\n\n##')
    
#     try:
#         with open("README.md", "w", encoding="utf-8") as f:
#             f.write(formatted_content)
#     except Exception as e:
#         st.error(f"Error saving to README.md: {str(e)}")

#     return formatted_content
