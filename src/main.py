import streamlit as st
from utils.openai_client import OpenAIClient
from agents.context_extractor import extract_context
from agents.blog_generator import generate_blog
from agents.seo_optimizer import generate_seo_metadata
from agents.visualization_generator import generate_visuals
import openai
from datetime import datetime
import textwrap
import os

def chunk_text(text, chunk_size=2000):
    """Split text into chunks of approximately equal size."""
    return textwrap.wrap(text, chunk_size, break_long_words=False, break_on_hyphens=False)

def process_chunk(chunk, previous_context="", system_prompt="", is_first_chunk=False):
    """Process individual chunks while maintaining context."""
    if is_first_chunk:
        context_prompt = chunk
    else:
        context_prompt = f"Previous content: {previous_context}\n\nContinue the blog post coherently without creating a new introduction. This is a continuation of the previous section. New content to process: {chunk}"

    client = OpenAIClient.get_instance()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context_prompt}
    ]
    
    response = client.create_chat_completion(
        messages=messages,
        max_tokens=2000,
        temperature=0.7
    )
    
    return response.choices[0].message['content']

def generate_blog_with_chunking(text, system_prompt):
    """Generate blog content using chunking approach."""
    chunks = chunk_text(text)
    full_content = ""
    previous_context = ""
    
    for i, chunk in enumerate(chunks):
        chunk_response = process_chunk(
            chunk, 
            previous_context, 
            system_prompt, 
            is_first_chunk=(i == 0)
        )
        
        # For subsequent chunks, remove any accidental headings that look like introductions
        if i > 0:
            lines = chunk_response.split('\n')
            filtered_lines = []
            for line in lines:
                if not (line.lower().startswith('# ') or 
                       'introduction' in line.lower() or 
                       'overview' in line.lower()):
                    filtered_lines.append(line)
            chunk_response = '\n'.join(filtered_lines)
        
        full_content += "\n" + chunk_response
        previous_context = chunk_response[-500:]
    
    # Clean up any double newlines and spaces
    full_content = '\n'.join(line for line in full_content.split('\n') if line.strip())
    return full_content.strip()

def save_as_readme(content):
    """Save the generated blog content as README.md"""
    # Ensure the content starts with a title
    if not content.startswith('#'):
        content = "# " + content
    
    # Clean up any multiple consecutive newlines
    content = '\n'.join(line for line in content.split('\n') if line.strip())
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

def main():
    st.set_page_config(
        page_title="Strategic Content Transformer",
        page_icon="📝",
        layout="wide"
    )
    
    st.sidebar.title("Configuration")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    
    if openai_api_key:
        OpenAIClient.initialize(openai_api_key)
    else:
        st.warning("Please enter your OpenAI API key to begin.")
        return
    
    st.title("Strategic Content Transformer")
    st.markdown("""
    Transform your newsletter into a comprehensive, SEO-optimized strategic blog post with 
    professional visualizations. Our AI agents work together to deliver exceptional content 
    that drives engagement and provides real business value.
    """)
    
    newsletter_input = st.text_area(
        "Newsletter Content",
        height=200,
        placeholder="Paste your newsletter content here..."
    )
    
    if st.button("Transform Content", type="primary"):
        if not newsletter_input.strip():
            st.error("Please provide newsletter content to transform.")
            return
        
        try:
            progress = st.progress(0)
            
            with st.spinner("Extracting strategic context..."):
                newsletter_context = extract_context(newsletter_input)
                progress.progress(25)
            if not newsletter_context:
                st.error("Failed to extract context from newsletter")
                return
            
            with st.spinner("Crafting strategic blog content..."):
                blog_text = generate_blog(newsletter_context)
                progress.progress(50)
            if not blog_text:
                st.error("Failed to generate blog content")
                return
            
            with st.spinner("Optimizing content for search visibility..."):
                seo_data = generate_seo_metadata(blog_text)
                progress.progress(75)
            
            with st.spinner("Creating strategic visualizations..."):
                visuals = generate_visuals(seo_data.get("seo_enhanced_content", blog_text))
                progress.progress(100)
            
            st.success("✨ Content Transformation Complete!")
            
            blog_tab, seo_tab, visual_tab = st.tabs([
                "Strategic Blog", "SEO Insights", "Visualizations"
            ])
            
            # with blog_tab:
            #     st.markdown("### Generated Blog Post")
            #     formatted_blog = seo_data.get("seo_enhanced_content", blog_text)
            #     st.markdown(formatted_blog)
            
            with seo_tab:
                st.subheader("Search Optimization Details")
                seo_display = {k: v for k, v in seo_data.items() if k != "seo_enhanced_content"}
                st.json(seo_display)
            
            with visual_tab:
                if visuals:
                    for idx, visual in enumerate(visuals, 1):
                        if isinstance(visual, dict):
                            st.subheader(f"Visualization {idx}")
                            if 'technical_explanation' in visual:
                                st.markdown("**Purpose & Explanation:**")
                                st.markdown(visual['technical_explanation'])
                            if 'mermaid_code' in visual:
                                st.markdown("**Diagram:**")
                                st.markdown(f"```mermaid\n{visual['mermaid_code']}\n```")
                                with st.expander("View Mermaid Code"):
                                    st.code(visual['mermaid_code'], language='mermaid')
                            st.markdown("---")
                else:
                    st.info("No visualizations were generated for this content")
            
            # Save as README.md
            save_as_readme(blog_text)
            
            # Download button
            st.download_button(
                label="Download Blog Content",
                data=blog_text,
                file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
            st.info("Please try again or contact support if the issue persists.")

if __name__ == "__main__":
    main() 