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


# 配置你的 MCP Server 路径 
server_params = StdioServerParameters(
    command="/Users/mac/anaconda3/envs/hugface/bin/python", # 当前虚拟环境的 python 位置
    args=["/Users/mac/Documents/mcp/mcp/stock_mcp_server.py"], # mcp server 位置
)

async def main():
    # 启动并链接本地 MCP Server
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:
            # 初始化连接
            await session.initialize()

            # 获取server 里定义的 tools
            mcp_tools = await session.list_tools()
            print("\n" + "="*30)
            print("🛡️  当前已加载的 MCP 工具清单:")
            print("="*30)

            for tool in mcp_tools.tools:
                print(f"🔧 工具名称: {tool.name}")
                print(f"📝 功能描述: {tool.description}")
                print(f"📊 输入参数: {tool.inputSchema.get('properties', {}).keys()}")
                print("-" * 30)

            # 将 MCP工具转化为大模型 API 能够识别的格式
            # 这个过程和单一让API 调用工具是一致的
            available_tools = [{
                "type":"function",
                "function":{
                    "name":tool.name,
                    "description":tool.description, # 这里获取的tool.description就是 tool 的注释
                    "parameters" :tool.inputSchema
                } 
            } for tool in mcp_tools.tools
            ]
            messages = [{
                "role":"user",
                "content":"帮我查一下比亚迪的股票价格，并给出你的看法"
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
                    args = json.loads(tool_call.function.arguments)
                    tool_result = await session.call_tool(
                        tool_call.function.name,
                        args
                    )
                    tool_output = "".join([
                        content.text 
                        for content in tool_result.content 
                        if hasattr(content, 'text')
                    ])
                    print(f"DEBUG - 发给模型的结果内容: {tool_output}")
                    print(f"\n🤖 模型决策：调用工具 [{tool_call.function.name}]")
                    print(f"📥 提取参数：{tool_call.function.arguments}")
                    # 将运行结果存入对话历史
                    messages.append({
                        "role":"tool",
                        "tool_call_id":tool_call.id,
                        "content":tool_output
                    })

                # 第二次请求，让模型根据工具结果给出回答
                final_response = client.chat.completions.create(
                    model = "intern-s1",
                    messages = messages,
                    tools = available_tools, 
                    tool_choice = "auto"
                )
                print(f"\nAI 的回答：\n{final_response.choices[0].message.content}")
            else:
                print(f"\nAI 的直接回答：\n{message.content}")

if __name__ == "__main__":
    asyncio.run(main())



