# Mermaid Diagram Generator

Mermaid Diagram Generator is an interactive web application built with Streamlit that allows users to create and visualize diagrams using the Mermaid.js syntax. It integrates with the Groq API to generate Mermaid code from user prompts, enabling the creation of flowcharts, sequence diagrams, and more.

## Features

- **Interactive Mermaid Diagram Rendering**: Enter prompts and get diagrams rendered in real time.
- **Model Selection**: Choose from a variety of pre-defined AI models for code generation.
- **Diagram Download Options**: Export diagrams as HTML or SVG files.
- **Retry Mechanism**: Automatically attempts to fix syntax errors in generated Mermaid code.
- **Examples Sidebar**: Provides sample prompts to help you get started.

## Installation

To run the application, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/mermaid-diagram-generator.git
   cd mermaid-diagram-generator
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`.

## Usage

1. **Model Selection**: Choose a model from the dropdown in the app to generate Mermaid code.
2. **Enter a Prompt**: Use the text area to input a description of the desired diagram. Start prompts with `Generate mermaid code`.
3. **Generate Diagram**: Click the "Generate Mermaid Diagram" button.
4. **View and Download**: View the generated code and diagram. Use the download button to save the diagram as an HTML or SVG file.

## Example Prompts

### Flowchart Example
```plaintext
Generate mermaid code to create a flowchart:
- User logs in
- Checks logs
- If logs > 3GB, clear them
- Else, allocate space
- Notify OC team
- End flow
```

### Sequence Diagram Example
```plaintext
Generate mermaid code to create a sequence diagram:
- User logs in
- Reviews logs
- Deletes logs if size > 3GB
- Allocates space otherwise
- Sends email to OC team
- Ends process
```

## Code Explanation

### Key Libraries

- **Streamlit**: For building the web interface.
- **streamlit_mermaid**: For rendering Mermaid diagrams.
- **requests**: For interacting with the Groq API.
- **re**: For extracting code blocks from API responses.

### Application Workflow

1. **Prompt Input**: Users enter a description of the desired diagram.
2. **API Request**: The app sends the prompt to the Groq API, specifying the selected model and sampling parameters.
3. **Code Extraction**: The response is parsed to extract Mermaid code.
4. **Diagram Rendering**: Mermaid code is rendered, and syntax errors are retried up to three times.
5. **Download Options**: The rendered diagram is embedded in HTML for download, with an option to save as SVG.

### Mermaid Rendering Logic

The `render_mermaid_diagram` function uses `st_mermaid` to display diagrams and handles syntax errors by retrying up to a defined limit.

### File Generation

The `generate_mermaid_html_with_download` function creates an HTML file containing the diagram and a button for SVG download.

## API Configuration

- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **API Key**: Replace the placeholder in the code with your valid Groq API key.
- **Models**: Supported models include:
  - `gemma2-9b-it`
  - `mixtral-8x7b-32768`
  - `llama-3.1-8b-instant`
  - `llama3-70b-8192`
  - `llama3-8b-8192`

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License.

---

Happy diagramming!

