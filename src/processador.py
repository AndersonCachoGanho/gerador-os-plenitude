import fitz
import os
import streamlit as st

class GeradorOS:
    def __init__(self, layout_pdf_path):
        self.layout_path = layout_pdf_path
        # Coordenadas em Pontos (A4: 595 x 842)
        self.x_col_esq = 120
        self.x_col_dir = 360
        self.y_linhas = [70, 95, 120, 145]
        
        # Caminhos das fontes na pasta assets
        self.font_reg = "assets/arial.ttf"
        self.font_bold = "assets/arialbd.ttf"

    def gerar_os(self, dados, caminho_produto, caminho_vetor, nome_arquivo):
        try:
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # 1. Inserção de Textos usando os arquivos TTF da pasta assets
            for i, (label, key) in enumerate([("CLIENTE:", 'cliente'), ("VENDEDOR:", 'vendedor'), ("PRODUTO:", 'produto'), ("QTD:", 'quantidade')]):
                # Rótulo em Negrito
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, 
                                 fontsize=9, fontfile=self.font_bold)
                # Valor em Regular
                page.insert_text((self.x_col_esq + 60, self.y_linhas[i]), str(dados.get(key, '')).upper(), 
                                 fontsize=9, fontfile=self.font_reg)

            for i, (label, key) in enumerate([("COR:", 'cor'), ("GRAVAÇÃO:", 'gravacao'), ("PANTONE:", 'pantone')]):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, 
                                 fontsize=9, fontfile=self.font_bold)
                page.insert_text((self.x_col_dir + 75, self.y_linhas[i]), str(dados.get(key, '')).upper(), 
                                 fontsize=9, fontfile=self.font_reg)

            # 2. Inserir Logo (VETOR)
            if caminho_vetor and os.path.exists(caminho_vetor):
                if caminho_vetor.lower().endswith(".pdf"):
                    with fitz.open(caminho_vetor) as logo_doc:
                        rect_logo = fitz.Rect(350, 220, 550, 420) 
                        page.show_pdf_page(rect_logo, logo_doc, 0)
                else:
                    page.insert_image(fitz.Rect(350, 220, 550, 420), filename=caminho_vetor)

            # 3. Inserir Foto do Produto
            if caminho_produto and os.path.exists(caminho_produto):
                page.insert_image(fitz.Rect(50, 220, 250, 420), filename=caminho_produto)

            if not os.path.exists("saida"): os.makedirs("saida")
            output_path = f"saida/{nome_arquivo}.pdf"
            
            # Salva preservando vetores e comprimindo o que for imagem
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            return output_path
            
        except Exception as e:
            st.error(f"Erro Crítico no Processador: {e}")
            return None
