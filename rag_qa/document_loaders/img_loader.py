from typing import Iterator
from rag_qa.document_loaders.ocr import get_ocr
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader


class OCRIMGLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, img_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            img_path: The path to the img to load.
        """
        self.img_path = img_path

    def lazy_load(self) -> Iterator[Document]:
        # <-- Does not take any arguments
        """A lazy loader that reads a file line by line.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """

        line = self.img2text()
        yield Document(page_content=line, metadata={"source": self.img_path})

    def img2text(self):
        resp = ""
        ocr = get_ocr()
        result, _ = ocr(self.img_path)
        if result:
            ocr_result = [line[1] for line in result]
            resp += "\n".join(ocr_result)
        return resp


if __name__ == '__main__':
    from base.config import config
    import os
    # 使用安保业务板块的图片进行测试（需自行放置图片测试文件）
    test_dir = os.path.join(config.DATA_DIR, 'security_duty_data')
    test_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.png'))] if os.path.exists(test_dir) else []
    if test_files:
        img_loader = OCRIMGLoader(img_path=os.path.join(test_dir, test_files[0]))
        doc = img_loader.load()
        print(doc)
    else:
        print(f"未找到图片测试文档: {test_dir}")