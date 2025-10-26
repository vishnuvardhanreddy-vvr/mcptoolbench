"""
MCP Client UI with Streamlit

This application connects to multiple MCP servers, loads all available tools,
and provides a unified dashboard to run any tool. Users can configure multiple
servers with transport type, customize theme, and share MCP configurations.

Features:
- Connect to multiple MCP servers (stdio / streamable_http)
- Auto-detect and run tools from all servers
- Unified tool list
- Dynamic input form generation based on tool schema
- Customizable theme and button color
"""
import json
import asyncio
import streamlit as st
from langchain_mcp_adapters.client import MultiServerMCPClient



# ------------------------
# Default Session State
# ------------------------
DEFAULTS = {
    "mcp_client": None,
    "tools_obj": {},
    "current_screen": "Dashboard",
    "theme": "light",
    "button_color": "#4CAF50",
    "connected": False,
    "servers": [
        {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable_http"}
    ],
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ------------------------
# Theme
# ------------------------
def apply_theme():
    """
    Apply the selected theme and button color dynamically to the Streamlit app.
    Supports 'light' and 'dark' themes and updates button styling.
    """
    button_color = st.session_state.button_color
    bg = "#111" if st.session_state.theme == "dark" else "#fff"
    fg = "#eee" if st.session_state.theme == "dark" else "#000"

    st.markdown(
        f"""
        <style>
        body {{ background-color: {bg}; color: {fg}; }}
        .stButton>button {{
            background-color: {button_color};
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
        }}
        .stButton>button:hover {{
            background-color: #3e8e41;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------
# Server Connection
# ------------------------
def connect_to_servers():
    """
    Connect to all configured MCP servers, fetch tools from each, and
    populate st.session_state.tools_obj with a unified tool list.
    Displays Streamlit messages for success, warnings, and errors.
    """
    servers_dict = {
        f"server_{i + 1}": {"url": s["url"], "transport": s["transport"]}
        for i, s in enumerate(st.session_state.servers)
    }

    client = MultiServerMCPClient(servers_dict)
    st.session_state.mcp_client = client

    all_tools = []
    for server_name in servers_dict.keys():
        try:
            tools = asyncio.run(client.get_tools())
            all_tools.extend(tools)
        except Exception as err:
            st.warning(f"⚠️ Failed to load tools from {servers_dict[server_name]['url']}: {err}")

    if not all_tools:
        st.error("No tools found from any MCP server.")
    else:
        st.session_state.tools_obj = {t.name: t for t in all_tools}
        st.session_state.connected = True
        st.session_state.current_screen = "Dashboard"
        st.success(f"✅ Connected to {len(servers_dict)} servers, total tools: {len(all_tools)}")
        st.rerun()


# ------------------------
# Dashboard
# ------------------------
def render_dashboard():
    """
    Render the main dashboard UI where users can:
    - Select a tool from the unified tool list
    - Enter input values dynamically based on the tool schema
    - Run the tool and view results
    """
    st.title("🧩 Dashboard")

    if st.session_state.tools_obj:
        tool_name = st.selectbox("Select MCP Tool", list(st.session_state.tools_obj.keys()))
        tool_obj = st.session_state.tools_obj[tool_name]

        st.markdown("### Tool Input Form")
        input_dict = {}
        properties = tool_obj.args_schema.get("properties", {})
        required_fields = tool_obj.args_schema.get("required", [])

        # Pretty display for input schema
        if properties:
            st.markdown("#### 🧾 Tool Input Fields:")
            cols = st.columns([2, 2, 1])
            cols[0].markdown("**Field Name**")
            cols[1].markdown("**Type**")
            cols[2].markdown("**Required**")
            for field, meta in properties.items():
                cols = st.columns([2, 2, 1])
                cols[0].write(field)
                cols[1].write(meta.get("type", "string"))
                cols[2].write("✅" if field in required_fields else "❌")

        st.markdown("---")

        # Dynamic input generation
        for field, meta in properties.items():
            field_type = meta.get("type", "string")
            default_value = "" if field_type == "string" else 0
            label = f"{field} ({field_type}) {'*' if field in required_fields else ''}"

            if field_type == "string":
                value = st.text_input(label, value=str(default_value))
            elif field_type == "integer":
                value = st.number_input(label, value=int(default_value), step=1)
            elif field_type == "number":
                value = st.number_input(label, value=float(default_value))
            elif field_type == "boolean":
                value = st.checkbox(label, value=False)
            else:
                value = st.text_input(label, value=str(default_value))
            input_dict[field] = value

        if st.button("Run Tool"):
            try:
                result = asyncio.run(tool_obj.ainvoke(input_dict))

                # Display results cleanly
                if isinstance(result, list) and all(isinstance(r, str) for r in result):
                    parsed_rows = []
                    for r in result:
                        try:
                            parsed_rows.append(json.loads(r))
                        except Exception:
                            parsed_rows.append({"raw": r})
                    st.dataframe(parsed_rows)
                elif isinstance(result, (dict, list)):
                    st.dataframe(result)
                else:
                    with st.expander("🧾 Tool Output", expanded=True):
                        st.text(str(result))
            except Exception as e:
                st.error(f"Error running tool: {e}")
    else:
        st.info("No tools found. Please check the MCP connection.")


# ------------------------
# About Screen
# ------------------------
def render_about():
    """
    Render the About screen with developer info and app features.
    """
    st.title("ℹ️ About")
    st.markdown(
        """
        **Developer:** Vishnu Vardhan Reddy  
        **App:** MCP Client UI  
        **Features:**
        - Connect to multiple MCP servers  
        - Choose transport type (`stdio` / `streamable_http`)  
        - Auto-detect & run tools from all servers  
        - Unified tool list  
        - Custom theme & color  
        """
    )


# ------------------------
# Settings Screen
# ------------------------
def render_settings():
    """
    Render the Settings screen for theme selection and button color customization.
    """
    st.title("⚙️ Settings")
    theme_option = st.radio("Theme", ["light", "dark"],
                            index=0 if st.session_state.theme == "light" else 1)
    st.session_state.theme = theme_option

    color = st.color_picker("Select button color", value=st.session_state.button_color)
    st.session_state.button_color = color
    apply_theme()
    st.success("Settings applied!")


# ------------------------
# Share URL Screen
# ------------------------
def render_share_url():
    """
    Render the Share URL screen showing MCP server URLs and transport types.
    All fields are disabled for copying purposes.
    """
    st.title("🔗 Share MCP Configurations")
    for i, server in enumerate(st.session_state.servers, start=1):
        st.text_input(f"Server {i} URL", value=server["url"], disabled=True)
        st.text_input(f"Server {i} Transport", value=server["transport"], disabled=True)
    st.info("Copy above configurations to share with others.")


# ------------------------
# Streamlit App
# ------------------------
def main():
    """
    Main Streamlit app execution function.
    Handles initial connection and screen rendering.
    """
    st.set_page_config(
        page_title="MCP UI - test your tools with simple UI",
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    apply_theme()

    if not st.session_state.connected:
        # Connection UI
        st.markdown("<div style='height:20vh;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>🖥️ Connect to MCP Servers</h2>",
                    unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="centered-box">', unsafe_allow_html=True)
            # Server input UI
            for i, server in enumerate(st.session_state.servers):
                st.markdown(f"#### Server {i + 1}")
                st.session_state.servers[i]["url"] = st.text_input(f"Server {i + 1} URL",
                                                    value=server["url"], key=f"server_url_{i}")
                st.session_state.servers[i]["transport"] = st.selectbox(
                    f"Server {i + 1} Transport Type",
                    options=["streamable_http", "stdio"],
                    index=0 if server["transport"] == "streamable_http" else 1,
                    key=f"server_transport_{i}",
                )
                if len(st.session_state.servers) > 1:
                    if st.button(f"❌ Remove Server {i + 1}", key=f"remove_server_{i}"):
                        st.session_state.servers.pop(i)
                        st.rerun()

            if st.button("➕ Add Another MCP Server"):
                st.session_state.servers.append({"url": "http://127.0.0.1:8000/mcp",
                                                 "transport": "streamable_http"})
                st.rerun()

            if st.button("Connect to All", key="connect_btn"):
                connect_to_servers()

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Sidebar menu
        with st.sidebar:
            st.markdown("## Menu")
            menu_items = ["Dashboard", "About", "Settings", "Share URL"]
            selected = st.radio("Navigation", menu_items,
                                index=menu_items.index(st.session_state.current_screen))
            st.session_state.current_screen = selected
            st.markdown("---")
            st.markdown("Developed by **Vishnu Vardhan Reddy**")

        # Render the selected screen
        screen_map = {
            "Dashboard": render_dashboard,
            "About": render_about,
            "Settings": render_settings,
            "Share URL": render_share_url,
        }
        screen_map.get(st.session_state.current_screen, render_dashboard)()

main()
