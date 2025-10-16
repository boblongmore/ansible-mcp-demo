#!/usr/bin/python3
# pylint: disable=line-too-long

# Python mcp client using mcp and openai
# This client calls the firewall-server tool and uses that context to ask
# openai whether a ruleset allows or disallows traffic

import asyncio
import logging
import os
from fastmcp import Client
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # noqa: E501
logger = logging.getLogger(__name__)

# input_data = "can host 192.168.2.100 reach google.com on port 80"


load_dotenv()  # load environment variables from .env


async def main(input_data):
    """calling mcp tools as defined in config"""

    try:
        openai_api_key = os.getenv('openai_key')
        model = ChatOpenAI(temperature=0.7, api_key=openai_api_key) # type: ignore
        # define tools
        config = {
            "mcpServers": {
                "acl_audit": {
                    # local firewall-server using stdio
                    "transport": "stdio",
                    "command": "python",
                    "args": ["/workspaces/ansible-mcp-demo/app/firewall-server.py"]  # noqa: E501
                }
            }
        }
        client = Client(config)
        async with client:
            # Get firewall rules from MCP server
            result = await client.call_tool("acl_audit")

            # Create a system message that defines the assistant's role
            system_message = SystemMessage(content=(
                "You are a network security assistant that analyzes firewall rules. "  # noqa: E501
                "Your task is to analyze the provided firewall configuration and "  # noqa: E501
                "determine if specific traffic flows are allowed or blocked. "
                "Base your answers on the actual firewall rules provided."
            ))

            # Create a human message with the query and context
            human_message = HumanMessage(content=(
                f"Based on these firewall rules:\n{result}\n\n"
                f"Please analyze: {input_data}\n\n"
                "Provide a clear explanation of whether the traffic is allowed or "  # noqa: E501
                "blocked, and which specific rule applies."
            ))

            # Get response from OpenAI
            messages = [system_message, human_message]
            response = model.invoke(messages)

            # Return the analysis so callers (frontends/tests) can use it
            return response.content

    except Exception:
        logging.exception("main failed")

if __name__ == "__main__":
    # Allow running the script from the command line. If no argument is
    # provided, use a simple default example query.
    import sys

    if len(sys.argv) > 1:
        cli_input = " ".join(sys.argv[1:])
    else:
        cli_input = "can host 192.168.2.100 reach google.com on port 80"

    asyncio.run(main(cli_input))


def analyze_sync(input_data: str) -> str:
    """Synchronous helper for callers that don't want to manage asyncio.

    Example: in Streamlit you can call `from fw_client import analyze_sync` and
    then `result = analyze_sync(user_input)`.
    """
    return asyncio.run(main(input_data))  # type: ignore
