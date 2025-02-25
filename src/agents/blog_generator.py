import streamlit as st
from utils.openai_client import OpenAIClient
from config.prompts import BLOG_WRITER_PROMPT
import textwrap

def chunk_newsletter(newsletter_content: str, chunk_size: int = 2000) -> list:
    return textwrap.wrap(newsletter_content, chunk_size, break_long_words=False, break_on_hyphens=False)

def calculate_tokens(text: str) -> int:
    """Rough estimation of tokens based on words (1 token ≈ 0.75 words)"""
    return len(text.split()) * 4 // 3

def generate_blog(newsletter_context: str) -> str:
    client = OpenAIClient.get_client()
    chunks = chunk_newsletter(newsletter_context)
    full_blog_content = ""
    previous_content = ""

    for chunk_index, chunk in enumerate(chunks):
        # Calculate dynamic max_tokens based on chunk size
        chunk_tokens = calculate_tokens(chunk)
        max_output_tokens = min(8000, max(2000, chunk_tokens * 2))  # Dynamic allocation between 2000-5000

        if chunk_index == 0:
            user_message = (
                f"NEWSLETTER CONTENT PART {chunk_index + 1}:\n\n{chunk}\n\n"
                "INSTRUCTIONS:\n"
                "<Introduction>"
                "- Start the introduction of the blog with a heading. The heading must be from the newsletter.\n" 
                "-From the newsletter content, Generate the blog mirroring the newsletter effectively. Extract the introductory content of the newsletter and start with a strong Introduction of 300-400 words\n."
                 "- Keep the tone conversational and engaging.\n"
                 "- Do not use AI generated phrases or words.\n"
                 "- Avoid using bullet points, numbering or visualizations such as table , diagrams.\n"
                 "- Ensure all the information is covered from the newsletter. Including heading , subheadings , titles , paragraphs etc.\n"
                 "- Write the paragraph in a detailed way to make the content easy to understand.\n"
                 "- Present the blog as a story to establish connection with the audience.\n"
                 "- Avoid using jargons.\n"
                 "- If the content of the newsletter is covered then the introduction has ended </introduction>, move onto the next chunk to process new information.\n"
                "10. IMPORTANT: Only write about information present in the newsletter. Stop when the content is exhausted.\n"
                f"Note: You have {max_output_tokens} tokens available for this section."
            )
        else:
            user_message = (
                f"CONTINUE WITH NEWSLETTER PART {chunk_index + 1}:\n\n{chunk}\n\n"
                "<body>"
                "INSTRUCTIONS:\n"
                "-. Use proper markdown formatting with appropriate headings and subheadings from the newsletter content.\n"
                "1. Present the blog as if you're explaining it to a colleague, avoiding technical jargon and try to mirror the newsletter.\n"
                "2. Continue the blog post coherently from the previous section.\n"
                "3. Maintain the same writing style and depth as of the newsletter.\n"
                "4. Write atleast 5-6 sections of the blog. Each section must be explained in detail for ease of understanding.\n"
                "5. Ensure all the information from the newsletter being processed is covered.\n"
                "6. Keep the information accurate and consistent with the newsletter.\n"
                "7. For each section, generate detailed explanations/paragraphs upto (600 words). Expand on the keypoints of each section and use information from the newsletter to make the user learn effectively.\n"
                "<Restrictions>"
                "- Do not use phrases like In this newsletter, or In this blog.\n" 
                "- Do not use AI generated phrases or sentences." 
                "- Do not use short concise sentences."
                "- Each section must be fully explained with detailed information while also maintaining the smooth flow of the blog."
                "- Do not explain the sections in 2-3 lines of paragraphs. Expand on it and keep it engaging by following the newsletter content."
                "- Do not use bullet points numbering or any visuals that hinders information."
                "- Do not add any information that is not mentioned in the newsletter."
                "</Restrictions>"
                "8. Stop writing when you've covered all the new information.\n"
                "</body>"
                "<Conclusion>"
                f"{'10. Once all the newsletter content has been covered, End with a comprehensive conclusion of 200-300 words that ties together the key points.' if chunk_index == len(chunks)-1 else ''}\n"
                "</Conclusion>"
                f"Note: You have {max_output_tokens} tokens available for this section."
            )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a precise blog writer who ONLY uses information from the provided newsletter content. Stop writing when you've covered all the information."},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=max_output_tokens,
                presence_penalty=0.0,
                frequency_penalty=1.0
            )

            chunk_content = response.choices[0].message.content.strip()

            if chunk_index == 0 and not chunk_content.startswith('#'):
                chunk_content = "# " + chunk_content

            full_blog_content += "\n\n" + chunk_content
            previous_content = chunk_content

        except Exception as e:
            st.error(f"Blog generation error in chunk {chunk_index + 1}: {str(e)}")
            return ""

    # Final formatting
    formatted_content = full_blog_content.replace('\n#', '\n\n#').replace('\n##', '\n\n##')
    
    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(formatted_content)
    except Exception as e:
        st.error(f"Error saving to README.md: {str(e)}")

    return formatted_content
