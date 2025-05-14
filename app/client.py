from fastmcp import Client
import asyncio
from fastmcp.client.transports import PythonStdioTransport

transport_explicit = PythonStdioTransport(
    script_path='firewall-server.py', # Path to the script
    python_cmd="python" # Specify python version
)

client = transport_explicit(Client)

async def main():
    async with Client("mcp") as client:
        tools = await client.tools()
        print(f"Connected via Python Stdio, found tools: {tools}")
