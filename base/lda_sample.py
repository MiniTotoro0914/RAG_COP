import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# サンプルテキストデータ
textts = [
    "自然言語処理は楽しい",
    "機械学習は強力です",
    "データサイエンスは重要な分野です",
    "深層学習は未来を変えます",
    "人工知能は興味深い",
]

# TF-IDFベクトライザを使ってテキストデータをベクトル化
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(textts)

# LDAによるトピックモデルの適用
n_topics = 5  # トピック数
lda = LatentDirichletAllocation(n_components=n_topics, random_state=0)
lda.fit(X)


# トピックごとの上位の単語を出力
def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print(f"Topic {topic_idx}:")
        print(
            " ".join(
                [feature_names[i] for i in topic.argsort()[: -n_top_words - 1 : -1]]
            )
        )


# トピックごとの上位10単語を出力
n_top_words = 10
tf_feature_names = vectorizer.get_feature_names_out()
print_top_words(lda, tf_feature_names, n_top_words)
