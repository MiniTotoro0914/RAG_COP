import loguru
import os

from langchain.prompts import PromptTemplate

# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import (
    OpenAIEmbeddings,
    AzureOpenAIEmbeddings,
    ChatOpenAI,
    AzureChatOpenAI,
)

# from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain, LLMChain
from langchain_community.vectorstores import Redis
from langchain.docstore.document import Document


class RedisConnectionError(RuntimeError):
    """Redisの接続問題がある場合は発生される"""


sample_text = """
以下のメッセージを出力してください
{text_one}
"""

dir_path = "../data"
files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

redis_url = "redis://redis2:6379/0"
# redis_url = "redis://conci-docs:6379"

api_key = 


embeddings = OpenAIEmbeddings(
    openai_api_key=api_key,
    model="text-embedding-3-small",
    # model="text-embedding-3-small",
    # deployment="text-embedding-ada-002",  # デプロイ名(≠モデル名)
    chunk_size=1000,  # Embeddingのバッチサイズは1にする
)
# models = ChatOpenAI(openai_api_key=api_key, model="gtp-4", temparature=0)

send = PromptTemplate(input_variables=["text_one"], template=sample_text)

# print(send.invoke({"text_one": "アクセス"}))

# embeddings = OpenAIEmbeddings(
#     openai_api_key=api_key,
#     model="gtp-4",
#     # deployment="text-embedding-ada-002",  # デプロイ名(≠モデル名)
#     chunk_size=1000,  # Embeddingのバッチサイズは1にする
# )
doc = [
    Document(
        page_content="関係会社管理規程\n（株式会社ＩＤホールディングス）\n\t\t\n\t\t\n（目\u3000的）\n\u3000この規程は、関係会社に対する管理手続を定め、その指導・育成をはかるとともに相互 の協調・発展に資することを目的とする。\n\t\t（関係会社の定義）\n\u3000この規程で定める関係会社とは、当社と経営上緊密な 関係を有し、発行済株式の過半数を当社が直接または間接に保有するなど、該社の議決権や意思決定機関を実質的に支配している「 子会社」を対象とする。\n\u3000\u3000\u3000\u3000\u3000その他、実質的な支配権を有しない関連会社（直接または間接に議決権 の20％以上50％以下の保有）に関しては、原則、株主総会付議事項に関する事前の報告、了解を求めることとし、当関係会社管理規 程の対象外とする。\n\t\t\n\t\t（疑義の措置）\n\u3000この規程に定めない事項およびこの規程に関する疑義については、社長の 承認を得て経営企画所管部署がこれを裁定する。\n\t\t\n\t\t（管理機構）\n\u3000関係会社に関する業務については、国内関係会 社（除く海外支店）については経営企画所管部署、海外\n関係会社（含む海外支店）については海外関係会社所管部署（以下、当該2部署をまとめて「関係会社所管部署」という）の所管業務とする。\n２．前項にかかわらず、関係会社所管部署は関係会社の事業内 容と当社組織との関連度を勘案し、必要と認めるときは、社長の決裁を得て、当該関係会社に関する業務の全部または一部を他の部 署または関係会社に委嘱することができる。\n\t\t\n\t\t（関係会社業務）\n\u3000関係会社業務とは次の業務をいう。\n（１）関 係会社の設立、合併、解散\n（２）関係会社の株式の取得、処分\n（３）関係会社に対する資金の貸付ならびに関係会社からの資金 調達\n（４）関係会社に対する担保の提供、債務の保証\n（５）関係会社との間の固定資産の譲渡、賃貸借",
        metadata={
            "source": "1011/社内規程/test_tanitsu/0204-0-0-IDHD_関係会社管理規程.docx",
            "category": "test_tanitsu",
            "extension": "docx",
            "parent": "3dd9c0995d54c0abd51a90f1_79f7214b4637127aeee5c1a8_3c6d0766bce0354fe22f7f99_6cb0b0fe7aafb532d5742eb2",
            "full_path_index": "3dd9c0995d54c0abd51a90f1_79f7214b4637127aeee5c1a8_3c6d0766bce0354fe22f7f99_6cb0b0fe7aafb532d5742eb20",
            "chunk_index": "0",
            "pre_chunk": "",
            "post_chunk": "",
        },
    )
]

try:
    redis_docsearch = Redis.from_documents(
        documents=doc,
        embedding=embeddings,  # or FakeEmbeddings(size=1536),
        index_name="test",
        redis_url=redis_url,
    )
except ValueError as ex:
    raise RedisConnectionError("接続エラー" + ex) from ex

print("登録後")
print(redis_docsearch.client.keys())
