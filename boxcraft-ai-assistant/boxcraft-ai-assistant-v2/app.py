import os
import sqlite3
import json
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# 載入 .env 檔案
load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "https://www.iai.nkust.edu.tw/aihub/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "Furen-large")
API_KEY = os.getenv("API_KEY", "")

# 初始化客戶端
client = OpenAI(
    base_url=LLM_API_URL,
    api_key=API_KEY
)

# 1. 初始化 SQLite 資料庫
def init_db():
    conn = sqlite3.connect("packaging.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            quote_id TEXT PRIMARY KEY,
            company TEXT,
            dimensions TEXT,
            quantity INTEGER,
            total_price REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 2. 定義真實 Python 工具函式 (Tool Calling)
def calculate_box_price(length: float, width: float, height: float, flute: str, quantity: int):
    """計算瓦楞紙箱單價與總額，並套用大量階梯折扣"""
    sqm = ((float(length) * 2 + float(width) * 2 + 5) * (float(width) + float(height) + 3)) / 10000.0
    base_rate = 25.0 if "AB" in str(flute).upper() else 18.0
    unit_price = round(sqm * base_rate, 1)
    discount = 0.9 if quantity >= 1000 else 1.0
    final_unit = round(unit_price * discount, 1)
    total = round(final_unit * quantity)
    return {
        "dimensions": f"{length}x{width}x{height} cm",
        "flute": flute,
        "quantity": quantity,
        "unit_price": final_unit,
        "total_price": total,
        "discount_applied": "10% off" if discount < 1.0 else "None"
    }

def save_quote_to_db(company: str, dimensions: str, quantity: int, total_price: float):
    """將確認的報價單資訊存入工廠 SQLite 資料庫 quotes 表格中"""
    quote_id = "Q-202611-04"
    conn = sqlite3.connect("packaging.db")
    conn.cursor().execute("INSERT OR REPLACE INTO quotes VALUES (?, ?, ?, ?, ?)",
                          (quote_id, company, dimensions, quantity, total_price))
    conn.commit()
    conn.close()
    return {"status": "success", "quote_id": quote_id, "message": f"報價單 {quote_id} 已成功入庫"}

def check_order_status(order_id: str):
    """查詢工廠訂單生產與出貨進度"""
    if order_id == "ORD-1001":
        return {"order_id": order_id, "status": "生產中", "stage": "模切成型", "eta": "週五前出貨"}
    return {"order_id": order_id, "status": "查無記錄", "message": f"系統中不存在訂單編號 {order_id}"}

# 讀取 RAG 規範手冊
policy_text = ""
if os.path.exists("factory_policy.md"):
    with open("factory_policy.md", "r", encoding="utf-8") as f:
        policy_text = f.read()

# 3. 定義 Tools 清單
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_box_price",
            "description": "計算紙箱單價與總額。當使用者提供長寬高、楞型或數量詢問報價時調用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "length": {"type": "number", "description": "紙箱長度 (cm)"},
                    "width": {"type": "number", "description": "紙箱寬度 (cm)"},
                    "height": {"type": "number", "description": "紙箱高度 (cm)"},
                    "flute": {"type": "string", "description": "瓦楞種類，如 'B' 或 'AB'"},
                    "quantity": {"type": "integer", "description": "訂購數量"}
                },
                "required": ["length", "width", "height", "flute", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_quote_to_db",
            "description": "儲存報價單記錄至工廠資料庫。當客戶確認並要求建檔/儲存報價時調用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "客戶公司名稱或抬頭"},
                    "dimensions": {"type": "string", "description": "紙箱尺寸 (如 40x30x20 cm)"},
                    "quantity": {"type": "integer", "description": "數量"},
                    "total_price": {"type": "number", "description": "總金額"}
                },
                "required": ["company", "dimensions", "quantity", "total_price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "查詢歷史訂單生產狀態與出貨進度。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "訂單編號，如 ORD-1001"}
                },
                "required": ["order_id"]
            }
        }
    }
]

SYSTEM_PROMPT = f"""你是由高科大開發的 BoxCraft 工業包裝紙箱智慧助理。
你的任務是協助 B2B 企業客戶進行紙箱規格諮詢、精準算價（呼叫工具）與報價單入庫存檔。

【嚴格遵守規範】
1. 嚴禁自行口算紙箱面積與價格！只要遇到詢問尺寸價格，必須調用 `calculate_box_price` 工具計算。
2. 客戶確認建檔報價時，調用 `save_quote_to_db` 將資料儲存入庫。
3. 查詢訂單時調用 `check_order_status`。若回報查無紀錄，老實告知查無此訂單，嚴禁胡謅編造。
4. 專業範疇限制：你僅限回答瓦楞紙箱包裝、報價、工廠政策與訂單事宜。若使用者詢問天氣、閒聊等無關問題，請嚴格拒絕回答。

【工廠知識庫 (RAG Source)】
{policy_text}
"""

def chat_with_agent(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "calculate_box_price":
                tool_result = calculate_box_price(**function_args)
            elif function_name == "save_quote_to_db":
                tool_result = save_quote_to_db(**function_args)
            elif function_name == "check_order_status":
                tool_result = check_order_status(**function_args)
            else:
                tool_result = {"error": "未定義的工具"}
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(tool_result, ensure_ascii=False)
            })
        
        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        return response_message.content

demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="BoxCraft AI: B2B 工業包裝紙箱智慧報價助理 (真正 API 驅動版)",
    examples=[
        "我想詢問 1000 個 5 層 AB 楞紙箱的報價，尺寸是長 40 cm、寬 30 cm、高 20 cm。",
        "請幫我用公司名稱「Apex Logistics」確認並儲存這筆正式報價單。",
        "幫我查一下歷史訂單 #ORD-99999 的進度，順便告訴我明天高雄天氣如何？"
    ]
)

if __name__ == "__main__":
    demo.launch()
