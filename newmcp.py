from openai import OpenAI
import requests
import base64

API_KEY = "sk-m4Q9TMINyGQiKnxJPlMtfLkHzs6Td1OZqpQ8ibdpTMI7QEzJ"
url = "https://chat.intern-ai.org.cn/api/v1"

client = OpenAI(
    api_key=API_KEY,
    base_url=url
)

# 传输图像(url)
MODEL_NAME = "intern-s1"
IMAGE_URL = "https://pic1.imgdb.cn/item/6964d432c02d09d8013ec3b6.png"

# 传输本地图像
def encode_image(image_path):
    with open(image_path,"rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
image_path = "horse.jpeg"
base64_image = encode_image(image_path)


def get_stock_status(symbol:str):
    prefix = "sh" if symbol.startswith('6') else "sz"
    full_code = f"{prefix}{symbol}"

    url = f"http://qt.gtimg.cn/q={full_code}"

    try:
        # 模拟浏览器 header，防止被拦截
        headers = {'User-Agent':'Mozilla/5.0'}
        response = requests.get(url,headers=headers,timeout=5)

        # 腾讯财经返回的是GBK 编码
        response.encoding = 'gbk'
        text = response.text

        # 腾讯财经返回的字符串格式示例：
        # v_sh600519="1~贵州茅台~600519~1600.00~"
        parts = text.split('~')

        if len(parts) < 10 :
            return f"查询失败：接口未返回{symbol}的有效数据"
        
        name = parts[1]
        price = parts[3]
        percent = parts[32] # 涨跌幅
        
        return f"{name}({symbol})当前价格：{price} 元，今日涨跌幅:{percent}%"
    
    except Exception as e:
        return f"查询过程中出错:{str(e)}"


tools = [{
    "type":"function",
    "function":{
        "name":"get_stock_status",
        "description":"获取股票动态",
        "parameters":{
            "type":"object",
            "properties":{
                "symbol":{
                    "type":"string",
                    "description":"对应股票的代码",
                }, 
            },
            "required":["symbol"]
        }
    }
}]


response = client.chat.completions.create(
    model = "intern-s1",
    messages=[
        {"role":"user",
         "content":"600519股票的情况如何"
        }
    ],
    tools=tools,
    extra_body={"thinking_mode":True},
)

print(response.choices[0].message.tool_calls)