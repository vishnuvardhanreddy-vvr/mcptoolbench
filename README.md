# mcptoolbench

**mcptoolbench** is a Streamlit-based UI for connecting to multiple MCP servers. It provides a unified dashboard to explore and run all available tools from your MCP servers, dynamically generates input forms based on tool schemas, and allows easy theme customization and configuration sharing.

## Features

- Connect to multiple MCP servers (stdio / streamable_http)
- Unified tool list from all servers
- Dynamic input form generation based on tool schema
- Run tools and view results interactively
- Customizable theme and button color
- Share server configurations with others

## Folder Structure

mcptoolbench/
│
├─ MCP/                 # Your MCP server (if included in repo)
├─ mcp_ui.py            # Streamlit UI app
├─ requirements.txt     # Python dependencies
└─ Dockerfile           # Docker configuration for deployment

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/mcptoolbench.git
cd mcptoolbench
```

Install dependencies:

```bash
pip install -r requirements.txt
```


## Running the App
```bash
streamlit run mcp_ui.py
```

The app will open in your default browser, allowing you to add MCP servers, explore tools, and run them interactively.

## Docker Deployment

Build Docker image:

```bash
docker build -t mcptoolbench
```

Run Docker container:
```bash
docker run -p 8501:8501 mcptoolbench
```

Your Streamlit app will be available at ```http://localhost:8501```.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to enhance the UI, add features, or improve documentation.
