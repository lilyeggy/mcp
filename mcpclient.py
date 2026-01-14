import asyncio
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

client = OpenAI(
    api_key="sk-m4Q9TMINyGQiKnxJPlMtfLkHzs6Td1OZqpQ8ibdpTMI7QEzJ",
    base_url="https://chat.intern-ai.org.cn/api/v1"
)


# 配置你的 MCP Server 路径 
server_params = StdioServerParameters(
    command="/Users/mac/miniconda3/envs/intern/bin/python", # 当前虚拟环境的 python 位置
    args=["/Users/mac/Documents/intern-s1/stock_mcp_server.py"], # mcp server 位置
)

async def main():
    # 启动并链接本地 MCP Server
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:
            # 初始化连接
            await session.initialize()

            # 获取server 里定义的 tools
            mcp_tools = await session.list_tools()

            # 将 MCP工具转化为大模型 API 能够识别的格式
            # 这个过程和单一让API 调用工具是一致的
            available_tools = [{
                "type":"function",
                "function":{
                    "name":tool.name,
                    "description":tool.description or "股票查询工具",
                    "parameters" :tool.inputSchema
                } 
            } for tool in mcp_tools.tools
            ]
            messages = [{
                "role":"user",
                "content":"帮我查一下贵州茅台的股票价格，并给出你的看法"
            }]

            response = client.chat.completions.create(
                model = "intern-s1",
                messages = messages,
                tools = available_tools
            )

            message = response.choices[0].message

            # 如果模型决定调用工具
            if message.tool_calls:
                messages.append(message)
                for tool_call in message.tool_calls:
                    tool_result = await session.call_tool(
                        tool_call.function.name,
                        eval(tool_call.function.arguments)
                    )
                    # 将运行结果存入对话历史
                    messages.append({
                        "role":"tool",
                        "tool_call_id":tool_call.id,
                        "content":str(tool_result.content)
                    })

                # 第二次请求，让模型根据工具结果给出回答
                final_response = client.chat.completions.create(
                    model = "intern-s1",
                    messages = messages
                )
                print(f"\nAI 的回答：\n{final_response.choices[0].message.content}")
            else:
                print(f"\nAI 的直接回答：\n{message.content}")

if __name__ == "__main__":
    asyncio.run(main())



