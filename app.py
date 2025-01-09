import re
import requests
import streamlit as st
from streamlit_mermaid import st_mermaid  # Mermaid rendering component
from transformers import pipeline  # For sentiment analysis

# Groq API settings
GROQ_API_URL = st.secrets["GROQ_API"]["GROQ_API_URL"]
GROQ_API_KEY = st.secrets["GROQ_API"]["GROQ_API_KEY"]

# Available models for selection
MODEL_OPTIONS = [
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192"
]

# Initialize session state
if "extracted_code" not in st.session_state:
    st.session_state.extracted_code = ""
if "api_error" not in st.session_state:
    st.session_state.api_error = ""
if "retry_count" not in st.session_state:
    st.session_state.retry_count = 0
if "selected_model" not in st.session_state:
    st.session_state.selected_model = MODEL_OPTIONS[0]
if "temperature" not in st.session_state:
    st.session_state.temperature = 1.0  # default temperature

RETRY_LIMIT = 3

# Initialize sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis")

# Feedback file path
FEEDBACK_FILE_PATH = "feedback.txt"

def main():
    st.title("Mermaid Diagram Generator")
    st.markdown(
        """
        ### Generate Mermaid Diagrams
        Enter a prompt to generate and render Mermaid diagrams.
        You can download the diagram as an HTML or SVG file.
        """
    )

    # Sidebar for examples
    with st.sidebar:
        st.header("Examples")
        st.markdown("**Example 1:**")
        st.text(
            """Generate mermaid code for the following:
1. User logs in
2. User checks logs
3. If logs > 3GB, clear them
4. Else, allocate space
5. Notify OC team
6. End flow"""
        )
        st.markdown("**Example 2:**")
        st.text(
            """Generate mermaid code to create a sequence diagram:
- User logs into the system
- Reviews dumped logs
- Deletes logs if size > 3GB
- Expands space otherwise
- Sends completion email to OC
- Ends process"""
        )
        st.markdown("**Example 3:**")
        st.text(
            """Generate mermaid code to crate a flowchart:
- Login -> Check logs -> Size check
- If > 3GB: Clear logs
- Else: Allocate space
- Notify OC team -> End"""
        )
        st.markdown("Feel free to modify these examples or create your own and make sure you starts with **Generate mermaid code**!")

    # Model selection dropdown
    st.session_state.selected_model = st.selectbox("Select Model", MODEL_OPTIONS)

    # Sampling options
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=st.session_state.temperature, step=0.1)
    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.05)

    # User input for the prompt
    user_prompt = st.text_area("Enter your prompt:", "Generate mermaid code for ...")

    # Button to trigger Mermaid code generation
    if st.button("Generate Mermaid Diagram"):
        if user_prompt:
            st.session_state.retry_count = 0
            process_with_groq_api(user_prompt, temperature, top_p)
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

    # Feedback Section
    feedback = st.text_area("Provide feedback on the generated code:")
    if st.button("Submit Feedback"):
        if feedback:
            save_feedback(feedback)
            analyze_feedback(feedback)  # Automatically analyze and adjust based on feedback
            st.info("Feedback submitted and used for learning!")
        else:
            st.warning("Please provide feedback before submitting.")

def process_with_groq_api(user_prompt, temperature, top_p):
    """Send user prompt to Groq API and extract Mermaid code."""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": st.session_state.selected_model,
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
            render_mermaid_diagram(mermaid_code)  # Retry rendering
        else:
            st.error(f"Error rendering Mermaid diagram: {e}")

def generate_mermaid_html_with_download(mermaid_code):
    """Generate an HTML file with embedded Mermaid diagram and a button to download it as SVG."""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
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
        <div class="mermaid">
            {mermaid_code}
        </div>
        <button onclick="downloadSVG()">Download as SVG</button>
    </body>
    </html>
    """
    return html_template

def save_feedback(feedback):
    """Save feedback to the feedback file."""
    try:
        with open(FEEDBACK_FILE_PATH, "a") as f:
            f.write(f"Feedback: {feedback}\n")
        st.success("Feedback saved!")
    except Exception as e:
        st.error(f"Error saving feedback: {e}")

def analyze_feedback(feedback):
    """Analyze feedback using sentiment analysis and adjust generation parameters."""
    try:
        # Perform sentiment analysis using Hugging Face's sentiment-analysis pipeline
        sentiment = sentiment_analyzer(feedback)[0]  # Get the first result from the response
        label = sentiment["label"]

        # Adjust parameters based on sentiment
        if label == "POSITIVE":
            st.session_state.temperature = 1.5  # Increase temperature for more creative responses
        elif label == "NEGATIVE":
            st.session_state.temperature = 0.5  # Decrease temperature for more structured responses
        else:
            st.session_state.temperature = 1.0  # Keep neutral for balanced responses

        st.session_state.feedback_sentiment = label
        st.info(f"Feedback sentiment: {label}. Adjusting response generation parameters.")
    except Exception as e:
        st.error(f"Error analyzing feedback: {e}")

if __name__ == "__main__":
    main()

