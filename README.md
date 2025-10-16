
# ansible-mcp-demo — "It's Not The Firewall"

Small demo that shows how to fetch firewall ACL data (via Ansible/AAP),
send that context to an LLM (OpenAI via LangChain), and expose a Streamlit
front-end for interactive questions about whether traffic is allowed.

## Contents

--------

- `fw_client.py` — MCP client + OpenAI prompt logic.
- `fe.py` — Streamlit frontend that accepts a natural-language query and displays the LLM's answer.
- `firewall-server.py` — a small FastMCP server that launches an Ansible Automation Platform (AAP) job template and returns ACL data as JSON via a tool named `acl_audit`.
- `openai_test.py` — pytest tests that mock the MCP client and OpenAI client.

## Requirements

--------

- Python 3.12
- Packages used:
  - fastmcp
  - langchain-openai
  - langgraph (optional for other frontends)
  - streamlit
  - pytest, pytest-asyncio

Install (example):

```bash
python -m pip install -r requirements.txt
# or install the packages directly:
python -m pip install fastmcp langchain-openai streamlit pytest pytest-asyncio
```

## Environment

--------

Create a `.env` in the project root (or set env vars in your container):

- `openai_key` — your OpenAI API key
- `AAP_TOKEN` — Ansible Automation Platform API token used by `firewall-server.py` to launch a playbook

## Usage

--------

Run the Streamlit frontend:

```bash
streamlit run app/fe.py
```

The UI includes a text area for your natural-language query (for example,
"Can host 192.168.2.100 reach google.com on port 80?"). The frontend calls
`fw_client.analyze_sync()` which runs the MCP tool to fetch ACLs, builds a
prompt, and asks the LLM.

## CLI

--------

You can also call the client directly from the command line:

```bash
python app/fw_client.py "can host 192.168.2.100 reach google.com on port 80"
```

## Testing

--------

Run the pytest tests (mocks are used — no network calls required):

```bash
pytest app/openai_test.py -v
```

## Notes & Troubleshooting

--------

- The Streamlit app calls a synchronous helper `analyze_sync()` which runs the async client under the hood. If you see errors about an existing event loop, `fe.py` contains a thread-based fallback.
- If `fw_client` reports `Client failed to connect`, ensure the path to `firewall-server.py` inside the `Client` config is correct for your environment and that your AAP credentials are valid.
- Keep your secrets out of source control — use `.env` and your container secret facilities.

## Development

--------

- Tests use `unittest.mock.AsyncMock` for async context managers and `call_tool()` mocking.
- The LLM prompt is kept simple—if you need structured output (JSON, verdict + explanation), update the prompt in `fw_client.py` and adapt the post-processing accordingly.

## License

--------

See the `LICENSE` in the repository.
