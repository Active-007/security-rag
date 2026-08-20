"""检查一次全新克隆是否已具备运行所需的本地资产。"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "本地配置": PROJECT_ROOT / "config.ini",
    "BERT 基础模型": PROJECT_ROOT / "rag_qa/models/bert-base-chinese/pytorch_model.bin",
    "查询分类模型": PROJECT_ROOT / "rag_qa/models/bert_query_classifier/model.safetensors",
    "BGE-M3": PROJECT_ROOT / "rag_qa/models/bge-m3/pytorch_model.bin",
    "BGE-M3 稀疏层": PROJECT_ROOT / "rag_qa/models/bge-m3/sparse_linear.pt",
    "BGE-M3 ColBERT 层": PROJECT_ROOT / "rag_qa/models/bge-m3/colbert_linear.pt",
    "BGE 重排序模型": PROJECT_ROOT / "rag_qa/models/bge-reranker-large/pytorch_model.bin",
    "文档分割模型": (
        PROJECT_ROOT
        / "rag_qa/models/nlp_bert_document-segmentation_chinese-base/pytorch_model.bin"
    ),
}

SUPPORTED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"}


def main() -> int:
    missing = [f"{label}: {path.relative_to(PROJECT_ROOT)}" for label, path in REQUIRED_FILES.items() if not path.is_file()]

    data_dir = PROJECT_ROOT / "rag_qa" / "data"
    documents = [
        path
        for path in data_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_DOCUMENT_EXTENSIONS
    ] if data_dir.exists() else []
    if not documents:
        missing.append("知识库文档: rag_qa/data/ 下没有支持的文档")

    if missing:
        print("恢复检查未通过：")
        for item in missing:
            print(f"- {item}")
        print("请按 docs/RESTORE.md 补齐后再次运行本脚本。")
        return 1

    print(f"恢复检查通过：配置、5 组模型和 {len(documents)} 份知识库文档均已就绪。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
