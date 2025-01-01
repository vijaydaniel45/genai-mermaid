import re
import requests
import streamlit as st
from streamlit_mermaid import st_mermaid  # Mermaid rendering component

# Groq API settings
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"

# Available models for selection
MODEL_OPTIONS = [
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-guard-3-8b",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "distil-whisper-large-v3-en",
    "whisper-large-v3",
    "whisper-large-v3-turbo"
]

# Initialize session state
if "extracted_code" not in st.session_state:
    st.session_state.extracted_code = ""
if "api_error" not in st.session_state:
    st.session_state.api_error = ""
if "retry_count" not in st.session_state:
    st.session_state.retry_count = 0

RETRY_LIMIT = 3

def main():
    st.title("Welcome to Vijay's GenAI App")
    st.markdown(
        """
        ### Generate Mermaid Diagrams
        Enter a prompt to generate and render Mermaid diagrams.
        You can download the diagram as an HTML or SVG file.
        """
    )

    # Model selection dropdown
    selected_model = st.selectbox("Select Model", MODEL_OPTIONS)

    # Sampling options
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.05)

    # User input for the prompt
    user_prompt = st.text_area("Enter your prompt (e.g., Generate a Data Flow Diagram):")

    # Button to trigger Mermaid code generation
    if st.button("Generate Mermaid Diagram"):
        if user_prompt:
            st.session_state.retry_count = 0
            process_with_groq_api(user_prompt, selected_model, temperature, top_p)
        else:
            st.warning("Please enter a prompt.")

    # Display extracted Mermaid code and render diagram
    if st.session_state.extracted_code:
        st.write("### Extracted Mermaid Code")
        st.code(st.session_state.extracted_code, language="mermaid")

        render_mermaid_diagram(st.session_state.extracted_code)

        # Generate downloadable HTML with SVG button
        html_content_with_download = generate_mermaid_html_with_download(st.session_state.extracted_code)
        st.download_button(
            label="Download Diagram with SVG Option",
            data=html_content_with_download,
            file_name="diagram_with_svg.html",
            mime="text/html",
        )

    # Display any API error messages
    if st.session_state.api_error:
        st.error(f"API Error: {st.session_state.api_error}")

def process_with_groq_api(user_prompt, selected_model, temperature, top_p):
    """Send user prompt to Groq API and extract Mermaid code."""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": selected_model,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": temperature,
            "top_p": top_p,
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            response_content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            mermaid_code = extract_code_from_response(response_content)
            if mermaid_code:
                st.session_state.extracted_code = mermaid_code
                st.session_state.api_error = ""
            else:
                st.error("No valid Mermaid code found in the response.")
        else:
            st.session_state.api_error = response.text
    except Exception as e:
        st.session_state.api_error = str(e)

def extract_code_from_response(response):
    """Extract the first block of code wrapped in triple backticks."""
    match = re.search(r"```(?:[a-zA-Z]*)?\n(.*?)```", response, re.DOTALL)
    return match.group(1).strip() if match else response.strip()

def render_mermaid_diagram(mermaid_code):
    """Render Mermaid diagram and retry if syntax error detected."""
    try:
        st_mermaid(mermaid_code)
        st.session_state.retry_count = 0  # Reset retry count on successful render
    except Exception as e:
        if "Syntax error in text" in str(e) and st.session_state.retry_count < RETRY_LIMIT:
            st.session_state.retry_count += 1
            st.warning(f"Syntax error detected. Retrying... ({st.session_state.retry_count}/{RETRY_LIMIT})")
            process_with_groq_api(
                user_prompt=st.session_state.extracted_code,
                selected_model=st.session_state.selected_model,
                temperature=1.0,
                top_p=1.0
            )
        else:
            st.error(f"Error rendering Mermaid diagram: {e}")

def generate_mermaid_html_with_download(mermaid_code):
    """Generate an HTML file with embedded Mermaid diagram and a button to download it as SVG."""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f9f9f9;
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
        mermaid.initialize({{ startOnLoad: true }});
        function downloadSVG() {{
            const svg = document.querySelector('svg');
            const serializer = new XMLSerializer();
            const source = serializer.serializeToString(svg);
            const blob = new Blob([source], {{ type: 'image/svg+xml' }});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'diagram.svg';
            a.click();
        }}
        </script>
    </head>
    <body>
        <div>
            <div class="mermaid">
                {mermaid_code}
            </div>
            <br>
            <button onclick="downloadSVG()">Download as SVG</button>
        </div>
    </body>
    </html>
    """
    return html_template

if __name__ == "__main__":
    main()
