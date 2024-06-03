import openai

# from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain_openai import OpenAI
from langchain.memory import SimpleMemory
import json

openai.api_key = 

# LLMの初期化
llm = OpenAI(model="text-embedding-ada-002", openai_api_key=openai.api_key)


# データ構造を文字列に変換
def format_data(parsed_data):
    return json.dumps(parsed_data, indent=2, ensure_ascii=False)


# HTML解析用のプロンプトテンプレート
html_prompt_template = PromptTemplate(
    input_variables=["html_content"],
    template="""
    次のHTMLコンテンツを解析して、テーブルデータを抽出してください:
    {html_content}
    """,
)

# HTML解析チェーンの作成
html_chain = LLMChain(llm=llm, prompt=html_prompt_template, output_key="parsed_data")


# データ保存関数
def save_to_memory(parsed_data):
    formatted_data = format_data(parsed_data)
    memory.save_context({}, {"parsed_data": formatted_data})
    return {"parsed_data": formatted_data}


# 回答生成用のプロンプトテンプレート
answer_prompt_template = PromptTemplate(
    input_variables=["user_input", "parsed_data"],
    template="""
    以下のデータに基づいてユーザーの質問に回答してください:
    データ:
    {parsed_data}

    質問: {user_input}
    """,
)

# メモリの初期化
memory = SimpleMemory()

# 回答生成チェーンの作成
answer_chain = LLMChain(llm=llm, prompt=answer_prompt_template, memory=memory)

# SimpleSequentialChainの作成
sequential_chain = SimpleSequentialChain(
    chains=[html_chain, answer_chain], verbose=True
)

# テスト用HTMLデータ
html_content = """
<table>
    <tr><th>Name</th><th>Age</th></tr>
    <tr><td>Alice</td><td>24</td></tr>
    <tr><td>Bob</td><td>30</td></tr>
</table>
"""

# ユーザインプット
user_input = "Aliceの年齢は？"

# HTML解析の実行
parsed_data = html_chain.run({"html_content": html_content})
formatted_data = save_to_memory(parsed_data)

# 回答生成の実行
response = answer_chain.run(
    {"user_input": user_input, "parsed_data": formatted_data["parsed_data"]}
)

print(response)
