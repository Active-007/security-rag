"""下载 Security RAG 运行所需的公开上游模型。"""

from pathlib import Path

from huggingface_hub import snapshot_download as hf_snapshot_download
from modelscope import snapshot_download as ms_snapshot_download


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "rag_qa" / "models"


def download_huggingface_model(repo_id: str, directory_name: str) -> None:
    target = MODELS_DIR / directory_name
    print(f"下载 {repo_id} -> {target}")
    hf_snapshot_download(repo_id=repo_id, local_dir=target)


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    download_huggingface_model("google-bert/bert-base-chinese", "bert-base-chinese")
    download_huggingface_model("BAAI/bge-m3", "bge-m3")
    download_huggingface_model("BAAI/bge-reranker-large", "bge-reranker-large")

    segmentation_target = MODELS_DIR / "nlp_bert_document-segmentation_chinese-base"
    print(
        "下载 damo/nlp_bert_document-segmentation_chinese-base"
        f" -> {segmentation_target}"
    )
    ms_snapshot_download(
        "damo/nlp_bert_document-segmentation_chinese-base",
        local_dir=str(segmentation_target),
    )

    print("公开模型下载完成。定制分类模型请按 docs/RESTORE.md 重建或恢复备份。")


if __name__ == "__main__":
    main()
