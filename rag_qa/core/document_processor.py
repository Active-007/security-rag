"""
    文档处理器：rag_qa/core/document_processor.py
"""
import os
from base.config import config
from base.logger import logger
from datetime import datetime
from rag_qa.document_loaders.doc_loader import OCRDOCLoader
from rag_qa.document_loaders.img_loader import OCRIMGLoader
from rag_qa.document_loaders.pdf_loader import OCRPDFLoader
from rag_qa.document_loaders.ppt_loader import OCRPPTLoader

from rag_qa.text_spliter.chinese_recursive_text_splitter import ChineseRecursiveTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownTextSplitter

# 定义支持的文件类型及其对应的加载器字典
document_loaders = {
    # 文本文件使用 TextLoader
    ".txt": TextLoader,
    # PDF 文件使用 OCRPDFLoader
    ".pdf": OCRPDFLoader,
    # Word 文件使用 OCRDOCLoader
    ".docx": OCRDOCLoader,
    # PPT 文件使用 OCRPPTLoader
    ".ppt": OCRPPTLoader,
    # PPTX 文件使用 OCRPPTLoader
    ".pptx": OCRPPTLoader,
    # JPG 文件使用 OCRIMGLoader
    ".jpg": OCRIMGLoader,
    # PNG 文件使用 OCRIMGLoader
    ".png": OCRIMGLoader,
    # Markdown 文件使用 UnstructuredMarkdownLoader
    ".md": UnstructuredMarkdownLoader
}


# 定义函数，从指定文件夹加载多种类型的文件，并添加元数据
def load_documents_from_directory(directory_path):
    # 初始化空列表，用于存储加载后的文档
    documents = []

    # 获取支持的文件列表扩展名
    supported_extensions = document_loaders.keys()
    # 从目录中提取业务板块类别 (security_duty_data  -->  security_duty)
    source = os.path.basename(directory_path).replace("_data", "")

    # 遍历指定目录及子目录中的所有文件
    '''
        参数：
            root:  当前正在遍历的目录路径（字符串）
            _   :  当前目录下的子目录列表（列表）
            files:  当前目录下的文件列表（列表）
        os.walk:  这是一个生成器函数，会递归遍历目录树
    '''
    for root, _, files in os.walk(directory_path):
        # 遍历当前目录下的所有的文件
        for file in files:
            # 拼接文件的完整路径
            file_path = os.path.join(root, file)
            # 获取文件的扩展名
            file_extension = os.path.splitext(file)[1]
            if file_extension in supported_extensions:
                try:
                    # 获取文件的加载器
                    load_class = document_loaders[file_extension]
                    # 如果是txt文件，则只需要指定编码格式
                    if file_extension == ".txt":
                        loader = load_class(file_path, encoding="utf-8")
                    else:
                        loader = load_class(file_path)
                    # 获取文档的内容
                    load_docs = loader.load()
                    for doc in load_docs:
                        # 添加文档的元数据，业务板块、文件路径，创建时间
                        doc.metadata["source"] = source
                        doc.metadata["file_path"] = file_path
                        doc.metadata["timestamp"] = datetime.now().isoformat()

                    # 将文档添加到总列表中
                    documents.extend(load_docs)
                    logger.info(f"加载文件 {file_path} 成功")
                except Exception as e:
                    logger.error(f"加载文件 {file_path} 失败: {str(e)}")
            else:
                logger.warning(f"不支持的文件类型 {file_extension}")

    return documents


# 处理文档并进行分层拆分，返回子块结果
def process_documents(directory_path,
                      parent_chunk_size=config.PARENT_CHUNK_SIZE,
                      child_chunk_size=config.CHILD_CHUNK_SIZE,
                      parent_chunk_overlap=config.PARENT_CHUNK_OVERLAP,
                      child_chunk_overlap=config.CHILD_CHUNK_OVERLAP):
    # 从指定目录加载文档
    documents = load_documents_from_directory(directory_path)
    # 记录加载的文档的总数
    logger.info(f"加载了 {len(documents)} 个文档")
    # 初始化父块和子块的分割器
    parent_splitter = ChineseRecursiveTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=parent_chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(chunk_size=child_chunk_size, chunk_overlap=child_chunk_overlap)
    # 初始化markdown分割器
    markdown_parent_splitter = MarkdownTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=parent_chunk_overlap)
    markdown_child_splitter = MarkdownTextSplitter(chunk_size=child_chunk_size, chunk_overlap=child_chunk_overlap)

    # 初始化空列表，用于存储子块
    child_chunks = []

    # 遍历文档 带索引
    for i, doc in enumerate(documents):
        # 获取文档的扩展名
        file_extension = os.path.splitext(doc.metadata.get("file_path", ""))[1].lower()
        # 选择分割器
        is_markdown = (file_extension == ".md")
        parent_splitter_to_use = markdown_parent_splitter if is_markdown else parent_splitter
        child_splitter_to_use = markdown_child_splitter if is_markdown else child_splitter
        logger.info(
            f"处理文档: {doc.metadata['file_path']}, 使用切分器: {'Markdown' if is_markdown else 'ChineseRecursive'}")

        # 使用父块分割器进行分割
        parent_docs = parent_splitter_to_use.split_documents([doc])
        # 遍历父块，带上索引
        for j, parent_doc in enumerate(parent_docs):
            # 为每个父块生成唯一id,格式为：doc_i_parent_j
            parent_id = f'doc_{i}_parent_{j}'
            # 将父块id添加到元数据中
            parent_doc.metadata["parent_id"] = parent_id
            # 将父块内容添加到元数据中
            parent_doc.metadata["parent_content"] = parent_doc.page_content

            # 使用子块分割器进行分割
            child_docs = child_splitter_to_use.split_documents([parent_doc])
            # 遍历子块，带上索引
            for k, child_doc in enumerate(child_docs):
                # 为子块添加到父块id到元数据中
                child_doc.metadata["parent_id"] = parent_id
                # 添加父块的内容到元数据中
                child_doc.metadata["parent_content"] = parent_doc.page_content
                # 为每个子块生成唯一id,格式为：parent_id_child_k
                child_id = f'{parent_id}_child_{k}'
                child_doc.metadata["id"] = child_id
                child_chunks.append(child_doc)

        # 记录子块总数日志
        logger.info(f"父文档: {doc.metadata.get('file_path', '')}，子块数量: {len(child_chunks)}")
    # 返回所有子块列表
    return child_chunks


if __name__ == "__main__":
    # chunks = load_documents_from_directory(f"{config.DATA_DIR}")
    # print(chunks)
    chunks = process_documents(f"{config.DATA_DIR}")
    print(chunks)