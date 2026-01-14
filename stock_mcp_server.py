from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("StockAssistant")
@mcp.tool()
def query_stock_price(symbol:str) -> str:
    prefix = "sh" if symbol.startswith('6') else "sz"
    full_code = f"{prefix}{symbol}"
    url = f"http://qt.gtimg.cn/q={full_code}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
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
    
if __name__ == "__main__":
    mcp.run()