"""
    文档向量化与存储：core/vector_store.py
"""
from base.config import config
from base.logger import logger
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# 导入 BGE-M3 嵌入函数，用于生成文档和查询的向量表示
from milvus_model.hybrid import BGEM3EmbeddingFunction
# 导入 Milvus 相关类，用于操作向量数据库
from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker
# 导入 Document 类，用于创建文档对象
from langchain_core.documents import Document
# 导入 CrossEncoder，用于重排序和 NLI 判断
from sentence_transformers import CrossEncoder
# 导入 hashlib 模块，用于生成唯一 ID 的哈希值
import hashlib


# # 定义 VectorStore 类，封装向量存储和检索功能
class VectorStore:
    # 初始化方法，设置向量存储的基本参数
    def __init__(self,
                 collection_name=config.MILVUS_COLLECTION_NAME,
                 host=config.MILVUS_HOST,
                 port=config.MILVUS_PORT,
                 database=config.MILVUS_DATABASE_NAME):
        # 设置 Milvus 集合名称
        self.collection_name = collection_name
        # 设置 Milvus 主机地址
        self.host = host
        # 设置 Milvus 端口号
        self.port = port
        # 设置 Milvus 数据库名称
        self.database = database
        # 设置日志记录器
        self.logger = logger
        # 设置重排序模型路径
        rerank_model_path = os.path.join(config.MODELS_DIR, 'bge-reranker-large')
        # 初始化 BGE-Reranker 模型，用于重排序检索结果
        # device代表设备： mps:m1系列的mac/ cpu: cpu / cuda: nvidia的gpu。和操作系统无关
        self.reranker = CrossEncoder(rerank_model_path, device='cpu')
        # 初始化 BGE-M3 嵌入函数，使用 CPU 设备，不启用 FP16
        bge_m3_model_path = os.path.join(config.MODELS_DIR, 'bge-m3')
        self.embedding_function = BGEM3EmbeddingFunction(
            model_name_or_path=bge_m3_model_path,
            # 在CPU上，FP32往往更稳定、兼容性更好。关闭FP16以保证检索和排序的准确性。
            use_f16=False,
            device='cpu'
        )
        # 获取稠密向量的维度
        self.dense_dim = self.embedding_function.dim["dense"]
        # 初始化 Milvus 客户端，连接到指定主机和数据库
        self.client = MilvusClient(uri=f'http://{self.host}:{self.port}', db_name=self.database)
        # 调用方法创建或加载 Milvus 集合
        self._create_or_load_collection()

    # 定义私有方法，创建或加载 Milvus 集合
    def _create_or_load_collection(self):
        # 检查指定集合是否已存在
        if not self.client.has_collection(self.collection_name):
            # 创建集合 Schema，禁用自动 ID，启用动态字段
            schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
            # 添加 ID 字段，作为主键，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=100)
            # 添加文本字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            # 添加稠密向量字段，FLOAT_VECTOR 类型，维度由嵌入函数指定
            schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=self.dense_dim)
            # 添加稀疏向量字段，SPARSE_FLOAT_VECTOR 类型
            schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
            # 添加父块 ID 字段，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="parent_id", datatype=DataType.VARCHAR, max_length=100)
            # 添加父块内容字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="parent_content", datatype=DataType.VARCHAR, max_length=65535)
            # 添加业务板块类别字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=50)
            # 添加时间戳字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="timestamp", datatype=DataType.VARCHAR, max_length=50)

            # 创建索引参数对象
            index_params = self.client.prepare_index_params()
            # 为稠密向量字段添加 IVF_FLAT 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="dense_vector",
                index_name="dense_index",
                index_type="IVF_FLAT",
                metric_type="IP",
                params={"nlist": 128}
            )
            # 为稀疏向量字段添加 SPARSE_INVERTED_INDEX 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="sparse_vector",
                index_name="sparse_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="IP",
                params={"drop_ratio_build": 0.2}
            )

            # 创建 Milvus 集合，应用定义的 Schema 和索引参数
            self.client.create_collection(collection_name=self.collection_name, schema=schema,
                                          index_params=index_params)
            # 记录创建集合的日志
            logger.info(f"已创建集合 {self.collection_name}")
        # 如果集合已存在
        else:
            # 记录加载集合的日志
            logger.info(f"已加载集合 {self.collection_name}")
        # 将集合加载到内存，确保可立即查询
        self.client.load_collection(self.collection_name)

    def add_documents(self, documents):
        # collection中一条数据
        data = []
        # 提取文档内容
        texts = [doc.page_content for doc in documents]
        # BGM-M3 生成嵌入【向量化】
        embeddings = self.embedding_function(texts)
        # 遍历文档
        for i, doc in enumerate(documents):
            text_hash = hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()
            # 初始化稀疏向量字典
            sparse_vector = {}
            try:
                # 新版本 milvus-model 使用 coo_array 格式
                row = embeddings["sparse"][i]
                # 获取非零元素的列索引数组
                if hasattr(row, 'col'):  # coo_array 格式，新版Milvus
                    indices = row.col
                else:  # csr_matrix 格式
                    indices = row.indices
            except Exception as e:
                # 兼容旧版本 milvus-model
                row = embeddings["sparse"].getrow(0)
                indices = row.indices
            # 获取稀疏向量的非零值
            values = row.data
            # logger.info(f"稀疏向量的非零索引：{indices}:{values}")
            # logger.info("=" * 100)
            for idx, value in zip(indices, values):
                sparse_vector[idx] = value
            # 构建数据记录
            data.append({
                "id": text_hash,
                "text": doc.page_content,
                "dense_vector": embeddings["dense"][i],
                "sparse_vector": sparse_vector,
                "parent_id": doc.metadata["parent_id"],
                "parent_content": doc.metadata["parent_content"],
                # 无法获取到source数据，则当空串处理
                "source": doc.metadata.get("source", ""),
                "timestamp": doc.metadata.get("timestamp", "")
            })

        if data:
            self.client.upsert(collection_name=self.collection_name, data=data)
            logger.info(f"存储 {len(documents)} 个文档到向量数据库...")
        else:
            logger.error("没有加载到数据")

    # 定义方法，执行混合检索并重排序
    def hybrid_search_with_rerank(self, query, k=config.RETRIEVAL_K, source_filter=None):
        # 使用 BGE-M3 嵌入函数生成查询的嵌入
        query_embeddings = self.embedding_function([str(query)])
        # 获取查询的稠密向量
        dense_query_vector = query_embeddings["dense"][0]
        # 初始化查询的稀疏向量字典，存储非零值   索引:值。非零项表示文档中出现的词及其权重。
        sparse_query_vector = {}
        try:
            # 新版本 milvus-model 使用 coo_array 格式
            row = query_embeddings["sparse"][0]
            if hasattr(row, 'col'):  # coo_array 格式
                indices = row.col
            else:  # csr_matrix 格式
                indices = row.indices
        except Exception as e:
            # 兼容旧版本 milvus-model
            row = query_embeddings["sparse"].getrow(0)
            indices = row.indices
        # 获取稀疏向量的非零值
        values = row.data
        # 将索引和值配对，填充稀疏向量字典
        for idx, value in zip(indices, values):
            sparse_query_vector[idx] = value

        # 初始化过滤表达式，默认不过滤
        filter_expr = f"source == '{source_filter}'" if source_filter else ""
        logger.debug(f"source查询条件: {filter_expr}")
        # 创建稠密向量搜索请求
        dense_request = AnnSearchRequest(
            data=[dense_query_vector],
            anns_field="dense_vector",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=k,
            expr=filter_expr
        )
        # 创建稀疏向量搜索请求
        sparse_request = AnnSearchRequest(
            data=[sparse_query_vector],
            anns_field="sparse_vector",
            param={"metric_type": "IP", "params": {}},
            limit=k,
            expr=filter_expr
        )

        # 创建加权排序器，稠密向量权重 1.0，稀疏向量权重 0.7
        ranker = WeightedRanker(1.0, 0.7)
        # 执行混合搜索，返回 Top-K 结果
        results = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[dense_request, sparse_request],
            ranker=ranker,
            limit=k,
            output_fields=["id", "text", "parent_id", "parent_content", "source", "timestamp"]
        )[0]
        # print(results)
        # 将搜索结果转换为 Document 对象列表
        sub_chunks = [self._doc_from_hit(hit["entity"]) for hit in results]
        # print(f'子文档数量-->{len(sub_chunks)}')
        # 从子块中提取去重的父文档
        parent_docs = self._get_unique_parent_docs(sub_chunks)
        # print(f'去重后父文档数量-->{len(parent_docs)}')
        # 如果只有1个文档，直接返回跳过重排序
        if len(parent_docs) < 2:
            return parent_docs[:config.CANDIDATE_M]
            # 如果有父文档，进行重排序
        if parent_docs:
            # 创建问题与文档内容的配对列表
            pairs = [[query, doc.page_content] for doc in parent_docs]
            # 使用 BGE-Reranker 计算每个问题及文档内容配对的得分
            scores = self.reranker.predict(pairs)
            # 将分值与文档内容配对后，根据得分从高到低排序文档
            ranked_parent_docs = [doc for _, doc in sorted(zip(scores, parent_docs), reverse=True)]
        # 如果没有父文档，返回空列表
        else:
            ranked_parent_docs = []

        # 返回前 k 个重排序后的文档
        return ranked_parent_docs[:config.CANDIDATE_M]

    # 定义私有方法，将搜索结果转换为 Document 对象
    def _doc_from_hit(self, hit):
        return Document(
            page_content=hit["text"],
            metadata={
                "id": hit["id"],
                "parent_id": hit["parent_id"],
                "parent_content": hit["parent_content"],
                "source": hit["source"],
                "timestamp": hit["timestamp"]
            }
        )

    # 定义私有方法，从子块中提取去重的父文档，里面只有内容
    def _get_unique_parent_docs(self, child_chunks):
        parent_contents = set()
        for chunk in child_chunks:
            parent_contents.add(chunk.metadata.get('parent_content', chunk.page_content))
        return [Document(page_content=content) for content in parent_contents]


# 测试
if __name__ == '__main__':
    vector_store = VectorStore()
    from rag_qa.core.document_processor import process_documents
    # 处理安保执勤板块文档
    test_dir = config.DATA_DIR
    if os.path.exists(test_dir):
        docs = process_documents(test_dir)
        vector_store.add_documents(docs)
        vector_store.hybrid_search_with_rerank("武装押运流程是什么", k=10, source_filter="security_duty")
    else:
        logger.warning(f"测试目录不存在: {test_dir}")
