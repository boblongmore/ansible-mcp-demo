# pylint: disable=redefined-outer-name
# pylint: disable=missing-function-docstring
# noqa: F811

from unittest.mock import Mock, patch, AsyncMock
import pytest
from fw_client import main


@pytest.fixture
def mock_firewall_rules():
    return (
        "Security Rules:\n"
        "- rule1: allow inbound tcp/80 from 192.168.2.0/24 to any\n"
        "- rule2: deny inbound any from any to any\n"
    )


@pytest.fixture
def mock_mcp_client():
    with patch('fw_client.Client') as mock_client:
        mock_instance = Mock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.call_tool = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_openai():
    with patch('fw_client.ChatOpenAI') as mock_chat:
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Traffic is allowed by rule1"
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_firewall_analysis(
    mock_mcp_client, mock_openai, mock_firewall_rules
):
    mock_mcp_client.call_tool.return_value = mock_firewall_rules
    input_text = "can host 192.168.2.100 reach google.com on port 80"
    await main(input_text)
    mock_mcp_client.call_tool.assert_called_once_with("acl_audit")
    calls = mock_openai.invoke.call_args_list
    assert len(calls) == 1
    messages = calls[0][0][0]
    assert len(messages) == 2
    assert mock_firewall_rules in messages[1].content


@pytest.mark.asyncio
async def test_mcp_client_error(mock_mcp_client):
    mock_mcp_client.call_tool.side_effect = Exception(
        "MCP connection failed"
    )
    input_text = "can host 192.168.2.100 reach google.com on port 80"
    await main(input_text)
    mock_mcp_client.call_tool.assert_called_once_with("acl_audit")


@pytest.mark.asyncio
async def test_input_in_prompt(
    mock_mcp_client, mock_openai, mock_firewall_rules
):
    mock_mcp_client.call_tool.return_value = mock_firewall_rules
    input_text = "can host 192.168.2.100 reach google.com on port 80"
    await main(input_text)
    calls = mock_openai.invoke.call_args_list
    messages = calls[0][0][0]
    human_message = messages[1].content
    assert "192.168.2.100" in human_message
    assert "google.com" in human_message
    assert "port 80" in human_message
