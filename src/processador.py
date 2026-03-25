import fitz  # PyMuPDF
import os
import streamlit as st

class GeradorOS:
    def __init__(self, layout_pdf_path):
        self.layout_path = layout_pdf_path
        # Coordenadas em Pontos PDF (A4: 595 x 842)
        self.x_col_esq = 60
        self.x_col_dir = 320
        self.y_linhas = [85, 110, 135, 160] 

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        try:
            # Abre o layout base PDF
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # 1. TEXTOS (Usando fontes nativas que não dependem de arquivos externos)
            f_bold = "helv-bold"
            f_reg = "helv"
            
            # Dados Esquerda
            itens_esq = [("CLIENTE:", 'cliente'), ("VENDEDOR:", 'vendedor'), ("PRODUTO:", 'produto'), ("QTD:", 'quantidade')]
            for i, (label, key) in enumerate(itens_esq):
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_col_esq + 65, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # Dados Direita
            itens_dir = [("COR:", 'cor'), ("GRAVAÇÃO:", 'gravacao'), ("PANTONE:", 'pantone')]
            for i, (label, key) in enumerate(itens_dir):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_col_dir + 80, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # 2. INSERIR FOTO DO PRODUTO
            if file_produto:
                rect_prod = fitz.Rect(50, 220, 250, 450)
                # O read() pega os bytes do Streamlit e o fitz cola no PDF
                page.insert_image(rect_prod, stream=file_produto.read())

            # 3. INSERIR LOGO (VETOR SE FOR PDF)
            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 545, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    logo_bytes = file_vetor.read()
                    with fitz.open(stream=logo_bytes, filetype="pdf") as logo_doc:
                        page.show_pdf_page(rect_logo, logo_doc, 0)
                else:
                    file_vetor.seek(0)
                    page.insert_image(rect_logo, stream=file_vetor.read())

            # 4. SALVAMENTO FINAL
            if not os.path.exists("saida"): os.makedirs("saida")
            output_path = f"saida/{nome_arquivo}.pdf"
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            return output_path

        except Exception as e:
            st.error(f"Erro Crítico no Processador: {e}")
            return None
