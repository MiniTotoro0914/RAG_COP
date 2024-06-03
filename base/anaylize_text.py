import docx2txt
import loguru
from os.path import exists, splitext, isdir, basename
from langchain.text_splitter import RecursiveCharacterTextSplitter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans

from sklearn.model_selection import GridSearchCV
from gensim.models import CoherenceModel

import util_file

# from gensim.models import CoherenceModel

file_path = "../data/0200-0-0_組織権限規程/0201-0-0-IDG_組織規程.docx"
dir_path = "../data/"

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4", chunk_size=2000, chunk_overlap=60
)

loguru.logger.add(
    "logs/lda_topics.log", rotation="1 MB"
)  # Rotate the log file after it reaches 1 MB


def clusetre_split(documents):
    # loguru.logger.debug(documents)
    textts = []
    files = []
    for docs in documents:
        textts.append(docs)
        # files.append(docs.metadata["source"] + " ：" + docs.metadata["chunk_index"])
    loguru.logger.debug(len(textts))
    # TF - IDFベクトル化
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textts)

    # LDAによるトピックモデル
    n_topics = 10  # トピック数
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=0)
    lda.fit(X)

    # トピックごとの上位10単語を出力
    n_top_words = 15
    tf_feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(lda.components_):
        loguru.logger.debug(f"Topic {topic_idx}:")
        loguru.logger.debug(
            " ".join(
                [tf_feature_names[i] for i in topic.argsort()[: -n_top_words - 1 : -1]]
            )
        )
    topic_distributions = lda.transform(X)
    for doc_idx, topic_dist in enumerate(topic_distributions):
        loguru.logger.debug(f"文書> {doc_idx} :トピック分布: {topic_dist}")

    search_params = {"n_components": [5, 10, 15, 20, 25, 30]}
    model = GridSearchCV(lda, param_grid=search_params)
    model.fit(X)
    # 最適なトピック数を取得
    best_lda_model = model.best_estimator_
    print(f"Best Model's Params: {model.best_params_}")
    print(f"Best Log Likelihood Score: {model.best_score_}")
    print(f"Model Perplexity: {best_lda_model.perplexity(X)}")

    # 各文書のトピック分布を表示
    # for idx, (topic, topic_dist) in enumerate(zip(lda.components_, lda.transform(X))):
    #     loguru.logger.debug(
    #         # f"Topic {idx}: {' '.join([vectorizer.get_feature_names_out()[i] for i in topic.argsort()[:-11:-1]])}"
    #         f"Topic {idx}: {' '.join([vectorizer.get_feature_names_out()[i] for i in topic.argsort()[:-11:-1]])}"
    #     )
    #     for i, prob in enumerate(topic_dist):
    #         # loguru.logger.debug(f"文書> {i} :元> {files[i]} のトピック分布: {prob}")
    #         loguru.logger.debug(f"文書> {i} :トピック分布: {prob}")

    # # k-meansクラスタリング
    # k = 5  # クラスタ数
    # kmeans = KMeans(n_clusters=k, random_state=0).fit(X)
    # logger.debug("文書のクラスタリング")
    # # 各文書のクラスタを表示
    # for i, cluster in enumerate(kmeans.labels_):
    #     logger.debug(f"文書> {i} :元> {files[i]} の Cluster> {cluster}")


def to_text(file_path):
    # lower→小文字
    texts = ""
    extension = splitext(file_path)[-1][1:].lower()
    if extension == "docx":
        texts = docx2txt.process(file_path)
        res = "dummy_ok"
    else:
        res = "dummy"

    return texts, res


all_text = []
for path in util_file.get_all_file_paths(dir_path):
    texts, res = to_text(path)
    tmp = text_splitter.split_text(texts)
    for txt in tmp:
        all_text.append(txt)

texts, res = to_text(file_path)


# print(len(text_splitter.split_text(texts)))
# print("set_1")
# print(text_splitter.split_text(texts))
# print("set_2_all")
# print(all_text)
clusetre_split(all_text)
