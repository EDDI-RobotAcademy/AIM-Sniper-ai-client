from abc import ABC,abstractmethod
import os
from tkinter import filedialog

from transform_file.repository.transform_file_repository import TransformRepository
from transform_file.repository.transform_file_repository_impl import TransformRepositoryImpl
from transform_file.service.transform_file_service import TransformService


class TransformServiceImpl(TransformService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__TransformRepository = TransformRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    @abstractmethod
    def select_pdf_file(self):
        file_path = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf")]
        )
        return file_path


    @abstractmethod
    def save_html(self, file_path, overview_text, sales_table_html):
        output_file_name = os.path.splitext(os.path.basename(file_path))[0] + "_overview_sales.html"

        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(f"<h1>사업의 개요 페이지</h1><p>{overview_text.replace('\n', '<br>')}</p>")
            if sales_table_html:
                f.write(f"<h1>매출, 매출액, 영업수익 포함 테이블</h1>{sales_table_html}")
            else:
                f.write(f"<h1>매출, 매출액, 영업수익 테이블을 찾을 수 없습니다.</h1>")

        print(f"HTML 파일로 변환 완료! 파일명: {output_file_name}")

    @abstractmethod
    def process_pdf(self):
        file_path = self.select_pdf_file()
        if file_path:
            # PdfRepository 사용하여 데이터 추출
            pdf_repo = self.__TransformRepository.file_path(file_path)
            overview_text, sales_table_html = pdf_repo.extract_overview_and_sales_table()

            # 추출된 데이터를 HTML 파일로 저장
            self.save_html(file_path, overview_text, sales_table_html)
        else:
            print("PDF 파일이 선택되지 않았습니다.")