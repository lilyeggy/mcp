import asyncio
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
import json

with open("config.json","r") as f:
    config = json.load(f)

api_key = config['api_key']
base_url = config['base_url']
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 配置你的 MCP Server 路径 (就是你刚才在 Inspector 里填的那两个)
server_params = StdioServerParameters(
    command="/Users/mac/anaconda3/envs/hugface/bin/python",
    args=["/Users/mac/Documents/mcp/mcp/stock_mcp_server.py"],
)


