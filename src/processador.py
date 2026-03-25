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
            # 1. Abre o layout base
            if not os.path.exists(self.layout_path):
                st.error(f"Arquivo não encontrado: {self.layout_path}")
                return None
                
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # 2. DEFINIÇÃO DE FONTES PADRÃO (Sem arquivos externos .ttf)
            # 'helv' é o código interno do PDF para Helvetica. 
            # Como é uma "Base 14 font", o PyMuPDF não pede arquivo de fonte.
            f_bold = "helv-bold"
            f_reg = "helv"
            
            # --- Inserção de Textos ---
            # Dados Esquerda
            itens_esq = [("CLIENTE:", 'cliente'), ("VENDEDOR:", 'vendedor'), ("PRODUTO:", 'produto'), ("QTD:", 'quantidade')]
            for i, (label, key) in enumerate(itens_esq):
                # Usamos fontname em vez de fontfile
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_col_esq + 65, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # Dados Direita
            itens_dir = [("COR:", 'cor'), ("GRAVAÇÃO:", 'gravacao'), ("PANTONE:", 'pantone')]
            for i, (label, key) in enumerate(itens_dir):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_col_dir + 80, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # 3. INSERIR ARTES (Lendo direto da memória para evitar erros de disco)
            # Produto
            if file_produto:
                rect_prod = fitz.Rect(50, 220, 250, 450)
                page.insert_image(rect_prod, stream=file_produto.read())

            # Logo (Vetor ou Imagem)
            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 545, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    # Abre o PDF do logo em memória
                    logo_bytes = file_vetor.read()
                    with fitz.open(stream=logo_bytes, filetype="pdf") as logo_doc:
                        page.show_pdf_page(rect_logo, logo_doc, 0)
                else:
                    file_vetor.seek(0)
                    page.insert_image(rect_logo, stream=file_vetor.read())

            # 4. SALVAMENTO FINAL
            if not os.path.exists("saida"): 
                os.makedirs("saida")
                
            output_path = os.path.join("saida", f"{nome_arquivo}.pdf")
            
            # 'clean=True' ajuda a evitar erros de estrutura no PDF final
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            return output_path

        except Exception as e:
            st.error(f"Erro Crítico no Processador: {e}")
            return None
