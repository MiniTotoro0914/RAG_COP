import time
import tiktoken
from typing import TYPE_CHECKING
from threading import Lock
from dataclasses import dataclass, field
from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter


from langchain.text_splitter import NLTKTextSplitter
from langchain.vectorstores.redis import Redis

lock = Lock()
init_lock = Lock()


class RedisConnectionError(RuntimeError):
    """Redisの接続問題がある場合は発生される"""


class IncorrectSettingsException(RuntimeError):
    """設定ファイルの必須な値が設定されていない場合"""


class NoFilesInFoldersException(RuntimeError):
    """フォルダ内にファイルがない場合"""


class NoDocumentsAvaiableException(RuntimeError):
    """Redisに登録されている文章がない場合"""


class HeaderTooLongException(RuntimeError):
    """ヘッダーの長さがトーケン数より長い場合"""


class FileContentsEmpty(RuntimeError):
    """ファイルの内容が空の場合"""


class DocumentSearchFailed(RuntimeError):
    """Redisの検索文字列か検索のほかの部分が失敗した場合"""


@dataclass
class DataContainer:
    """ダウンロードしたデータを格納する
    Args:
        data_parent_directory (list[str]): ダウンロードしたデータのパス
        available_directories (set): ダウンロードしたデータのフォルダ
        available_files (set): ダウンロードしたデータのファイル
        documents (list): ダウンロードしたデータのテキスト
    """

    data_parent_directory: list[str]
    available_directories: set[str] = field(default_factory=set)
    available_files: set[str] = field(default_factory=set)
    file_ids: dict[str : list[str]] = field(default_factory=dict)


@dataclass
class ChunkingParameters:
    """文章を分けるためのパラメーター

    Args:
        chunk_length (int): 文章の最大長さ
        chunk_overlap (int): 文章の重複部分
        pre_chunk_length (int): 文章の前の部分
        post_chunk_length (int): 文章の後ろの部分
        chunk_separator (str): 文章の分ける文字
    """

    chunk_length: int = 500
    chunk_overlap: int = 60
    pre_chunk_length: int = 0
    post_chunk_length: int = 0
    chunk_separator: str = "\n\n"

    def __post_init__(self):
        self.chunk_separator = self.chunk_separator.replace("\\n", "\n")


class DocumentDatabase:
    """
    テキスト抽出
    """

    data: DataContainer = None

    @classmethod
    def init(
        cls,
        model: str,
        embedding: "Embeddings",
        redis_url: str,
        *,
        force=False,
        data_directory: str = "data",
        chunk_settings: ChunkingParameters = None,
    ):
        """Redisへの接続を初期化する、データフォルダーの内容を追加する

        Args:
            model (str): 対処チャットモデルのモデル名
            embedding (Embeddings): LangchainのEmbeddingオブジェクト
            redis_url (str): 例：redis://conci-docs:6379
            force (bool, optional): Falseの場合は、既に存在するデータベースを再初期化しない. Defaults to False.
            data_directory (str, optional): データが入っている親フォルダー（会社コード上のフォルダー）. Defaults to 'data'.
            chunk_settings (ChunkingParameters, optional): 文章を分けるためのパラメーター. Defaults to None.
        """
        if force or not cls.data:
            with init_lock:
                if force or not cls.data:
                    cls._init(
                        model,
                        embedding,
                        redis_url,
                        data_directory=data_directory,
                        chunk_settings=chunk_settings,
                    )

    @classmethod
    def _init(
        cls,
        model: str,
        embedding: "Embeddings",
        redis_url: str,
        *,
        data_directory: str = "data",
        chunk_settings: ChunkingParameters = None,
    ):
        """Not Threadsafe. Use init(...) instead!"""
        if not redis_url or len(redis_url) < 3:
            raise IncorrectSettingsException("unset_redis_url")

        if not data_directory:
            raise IncorrectSettingsException("unset_data_path")

        cls.embedding = embedding
        cls.model = model
        cls.redis_docsearch: Redis = None
        cls.index_name = "conci_dokuji_data"
        cls.schema_file_name = "redis_schema.yaml"
        cls.redis_url = redis_url

        cls.chunk_param = chunk_settings or ChunkingParameters()
        cls.data = DataContainer(data_directory)

        cls.encoder = tiktoken.encoding_for_model(model)
        cls.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name=cls.model,
            chunk_size=cls.chunk_param.chunk_length,
            chunk_overlap=cls.chunk_param.chunk_overlap,
            keep_separator=True,
            # separators=[cls.chunk_separator.replace('\\n', '\n')],
        )

        try:
            cls._connect_redis()
        except (ValueError, FileNotFoundError) as ex:
            logger.info("redis_connection_failed_1" + ex)
            doc_path_compss = collect_local_document_path_comps(
                cls.data.data_parent_directory
            )
            if not doc_path_compss:
                logger.error("no_files_available_but_dokuji_enabled")
                # ファイル見つかっていないことの詳細を渡す必要はありません
                # pylint: disable=W0707
                raise NoDocumentsAvaiableException(
                    "no_redis_database_or_local_files_found"
                )
                # pylint: enable=W0707
            cls._initialize_redis_with_documents(doc_path_compss)
        else:
            try:
                cls._fetch_file_list()
            except Exception as ex:  # pylint: disable=W0718:
                logger.exception(tr("redis_connected_but_file_fetching_failed_1", ex))
            else:
                if not (cls.data.available_directories and cls.data.available_files):
                    logger.info("reddis_connected_but_no_documents")
        logger.info("redis_setup_and_connection_done")
