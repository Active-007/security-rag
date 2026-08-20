# 全新克隆恢复指南

这份指南的目标是：本地项目删除后，仅凭 GitHub 仓库和明确列出的外部模型来源，能够重建可运行环境。

## 1. 克隆并创建 Python 环境

建议使用 Python 3.10（当前开发环境为 Python 3.10.20）。

```powershell
git clone https://github.com/Active-007/security-rag.git
cd security_rag
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux/macOS 激活命令为 `source .venv/bin/activate`。

## 2. 恢复配置

```powershell
Copy-Item config.ini.example config.ini
```

编辑 `config.ini`，填入 MySQL、Redis、Milvus 和 LLM 的真实连接信息。`config.ini` 和 `.env` 含密钥，必须保持在 Git 之外。

## 3. 恢复公开模型

```powershell
python scripts/download_models.py
```

脚本会恢复以下公开模型：

| 本地目录 | 上游来源 |
|---|---|
| `rag_qa/models/bert-base-chinese/` | `google-bert/bert-base-chinese` |
| `rag_qa/models/bge-m3/` | `BAAI/bge-m3` |
| `rag_qa/models/bge-reranker-large/` | `BAAI/bge-reranker-large` |
| `rag_qa/models/nlp_bert_document-segmentation_chinese-base/` | `damo/nlp_bert_document-segmentation_chinese-base` |

这些公开模型合计数 GB，不应直接写入普通 Git 历史。下载时需要访问 Hugging Face 和 ModelScope。

## 4. 恢复定制查询分类模型

`rag_qa/models/bert_query_classifier/` 是本项目训练产物，不属于公开上游模型。可选择以下一种方式：

1. 从单独的可信备份恢复该目录；或
2. 在公开模型下载完成后，用仓库内训练集重新训练：

```powershell
python -m rag_qa.core.query_classifier
```

训练会读取 `security_rag/classify_data/model_generic_5000.json`，并将最终模型保存到 `rag_qa/models/bert_query_classifier/`。训练检查点写入 `rag_qa/core/bert_results/`，不需要备份。

## 5. 恢复知识库文档

原始 Word/PDF/PPT/图片默认被 `.gitignore` 排除，以防企业资料意外进入公开仓库。当前项目的 8 份 Word 文档位于：

- `rag_qa/data/armed_escort_data/`
- `rag_qa/data/security_duty_data/`

如果 GitHub 仓库是私有仓库并确认这些文档可以上传，应只显式纳入经过确认的文件。如果仓库公开，应将这些文档保存到加密备份或私有对象存储，并在删除本地项目前验证备份可下载。没有这些文档仍可查询已经写入 Milvus 的数据，但无法从零重建知识库。

## 6. 外部服务和数据库

运行前需要 MySQL、Redis 和 Milvus。应用会自动创建 `conversations` 表；`security_qa` 表及初始 CSV 数据可用以下命令初始化。仓库跟踪了 `mysql_qa/data/安保集团知识问答.csv`。

```powershell
python -m mysql_qa.db.mysql_client
```

Milvus 向量集合由代码自动创建。恢复原始知识库文档后，运行以下命令处理文档并写入 Milvus：

```powershell
python rag_qa/rag_main.py --data-processing --data-dir ./rag_qa/data
```

## 7. 恢复验收

```powershell
python scripts/verify_restore.py
python -m compileall -q app.py new_main.py base mysql_qa rag_qa security_rag scripts
python app.py
```

看到恢复检查通过、Python 编译检查无错误，并能访问 `http://localhost:8003/health` 后，才算恢复完成。

## 删除本地文件前的最终检查

1. GitHub 默认分支上的最新提交与本地准备发布的提交一致。
2. 在一个新的临时目录执行一次全新克隆，不复用当前工作区。
3. 全新克隆中能安装依赖、下载模型、恢复定制分类模型和知识库文档。
4. `config.ini` 中的真实密钥已经另行安全保存，且泄露过的 Key 已撤销。
5. 仅在上述检查全部通过后删除本地目录。
