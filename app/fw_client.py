#!/usr/bin/python3
# pylint: disable=line-too-long

# Python mcp client using mcp and openai
# This client calls the firewall-server tool and uses that context to ask openai whether a ruleset allows or disallows traffic

import asyncio
import logging
import os
from fastmcp import Client
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # noqa: E501
logger = logging.getLogger(__name__)

input_data = "can host 192.168.2.100 reach google.com on port 80"


load_dotenv()  # load environment variables from .env


async def main():
    """calling mcp tools as defined in config"""

    try:
        openai_api_key = os.getenv('openai_key')
        model = ChatOpenAI(temperature=0.7, api_key=openai_api_key)
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

            # Print the analysis
            print("\nFirewall Analysis:")
            print(response.content)

    except Exception:
        logging.exception("main failed")

asyncio.run(main())
