from mcp.server.fastmcp import FastMCP
import requests
import asyncio
import httpx

mcp = FastMCP("StockAssistant")
@mcp.tool()
def query_stock_price(symbol:str) -> str:
    """查询指定股票代码的实时价格和涨跌幅。参数 symbol 是 6 位数字代码。"""
    prefix = "sh" if symbol.startswith('6') else "sz"
    full_code = f"{prefix}{symbol}"
    url = f"http://qt.gtimg.cn/q={full_code}"
    
    try:
        # 模拟浏览器header  防止被拦截
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        # 腾讯财经的编码方式是gbk
        response.encoding = 'gbk'
        text = response.text

        # 腾讯财经接口解析
        parts = text.split('~')
        
        if len(parts) < 10:
            return f"错误：未找到股票代码 {symbol} 的数据，请确认代码是否正确。"

        name = parts[1]      # 股票名称
        price = parts[3]     # 当前价格
        change = parts[32]    # 涨跌幅
        high = parts[33]      # 今日最高
        low = parts[34]       # 今日最低

        # 返回字符串给 AI 模型，AI 会根据这些信息组织语言回答用户
        return (f"【{name} ({symbol})】\n"
                f"当前价格: {price} 元\n"
                f"今日涨跌: {change}%\n"
                f"最高/最低: {high}/{low}")

    except Exception as e:
        return f"接口请求失败: {str(e)}"
    

# 多增加一个工具
@mcp.tool()
async def get_weather(city:str)->str:
    """获取指定城市的实时天气预报，包括气温。"""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh&format=json"
    async with httpx.AsyncClient() as client:
        geo_res = await client.get(geo_url)
        geo_data = geo_res.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"找不到城市{city}"
        
        location = geo_data["results"][0]
        lat,lon = location["latitude"],location["longitude"]
        city_full_name = location.get("name", city)

        # 2. 根据经纬度查询实时天气
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        weather_res = await client.get(weather_url)
        w_data = weather_res.json()
        
        temp = w_data["current"]["temperature_2m"]
        return f"{city_full_name} 当前气温为 {temp}°C。"

if __name__ == "__main__":
    mcp.run()