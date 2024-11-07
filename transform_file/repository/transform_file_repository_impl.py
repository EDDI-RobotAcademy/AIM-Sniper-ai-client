import pdfplumber
from bs4 import BeautifulSoup
from transform_file.repository.transform_file_repository import TransformRepository


class TransformRepositoryImpl(TransformRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def extract_overview_and_sales_table(self):
        with pdfplumber.open(self.file_path) as pdf:
            overview_text = ""
            sales_table_html = ""
            found_overview = False
            found_sales_table = False
            overview_to_products_text = ""

            for page in pdf.pages:
                page_text = page.extract_text()

                # "사업의 개요"부터 "주요 제품 및 서비스" 전까지의 텍스트 추출
                if not found_overview and "사업의 개요" in page_text:
                    overview_text = page_text
                    found_overview = True
                    overview_to_products_text += overview_text
                    if "주요 제품 및 서비스" in overview_to_products_text:
                        overview_to_products_text = overview_to_products_text.split("2. 주요 제품 및 서비스")[0]
                elif found_overview and "주요 제품 및 서비스" in page_text:
                    break
                elif found_overview:
                    overview_to_products_text += page_text

                # 테이블 추출
                tables = page.extract_tables()
                if tables:
                    if "주요 제품 및 서비스" in page_text:
                        for table in tables:
                            for row in table:
                                clean_row = [cell if cell is not None else "" for cell in row]
                                if any(keyword in "".join(clean_row) for keyword in ["매출", "매출액", "영업수익"]):
                                    soup = BeautifulSoup("<table></table>", "html.parser")
                                    table_tag = soup.find("table")
                                    for row in table:
                                        tr = soup.new_tag("tr")
                                        for cell in row:
                                            td = soup.new_tag("td")
                                            td.string = str(cell) if cell else ""
                                            tr.append(td)
                                        table_tag.append(tr)
                                    sales_table_html = str(soup)
                                    found_sales_table = True
                                    break
                            if found_sales_table:
                                break

                if found_overview and found_sales_table:
                    break

        return overview_to_products_text, sales_table_html
