# RAG_COP
RAGのあれこれ
docker build -t rag_sample . && docker run -d --name 001_rag_container rag_sample

# redis-serverがダメなとき・・・これで認証してからやるとできる
# local-redis-serverは任意の名称
docker exec -it local-redis-server redis-cli
