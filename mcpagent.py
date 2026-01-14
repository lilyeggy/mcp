import asyncio
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

client = OpenAI(
    api_key="sk-m4Q9TMINyGQiKnxJPlMtfLkHzs6Td1OZqpQ8ibdpTMI7QEzJ",
    base_url="https://chat.intern-ai.org.cn/api/v1"
)

# 配置你的 MCP Server 路径 (就是你刚才在 Inspector 里填的那两个)
server_params = StdioServerParameters(
    command="/Users/mac/anaconda3/envs/hugface/bin/python",
    args=["/Users/mac/Documents/mcp/mcp/stock_mcp_server.py"],
)
