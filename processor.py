import fitz  # PyMuPDF
import os
import streamlit as st

class GeradorOS:
    def __init__(self, layout_path):
        self.layout_path = layout_path
        
        # --- CONFIGURAÇÃO DE COORDENADAS (Pontos PDF) ---
        # No PDF A4 (595x842), as coordenadas são menores que em pixels 300DPI
        self.x_col_esq = 60
        self.x_val_esq = 130
        self.x_col_dir = 320
        self.x_val_dir = 430
        self.y_linhas = [85, 110, 135, 160] # Espaçamento vertical

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        try:
            # 1. Abrir o Layout Base
            if not os.path.exists(self.layout_path):
                st.error(f"Layout não encontrado: {self.layout_path}")
                return None
            
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # 2. Configurar Fontes Nativas (Não precisam de arquivo .ttf)
            # 'helv' = Helvetica (Padrão universal do PDF)
            f_bold = "helv-bold"
            f_reg = "helv"
            size = 10

            # 3. Escrita dos Dados (Lado Esquerdo)
            itens_esq = [
                ("CLIENTE:", dados.get('cliente', '')),
                ("VENDEDOR:", dados.get('vendedor', '')), 
                ("PRODUTO:", dados.get('produto', '')),
                ("QTD:", dados.get('quantidade', ''))
            ]
            for i, (label, valor) in enumerate(itens_esq):
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, fontsize=size, fontname=f_bold)
                page.insert_text((self.x_val_esq, self.y_linhas[i]), str(valor).upper(), fontsize=size, fontname=f_reg)

            # 4. Escrita dos Dados (Lado Direito)
            itens_dir = [
                ("COR:", dados.get('cor', '')),
                ("GRAVAÇÃO:", dados.get('gravacao', '')), 
                ("PANTONE:", dados.get('pantone', '-'))
            ]
            for i, (label, valor) in enumerate(itens_dir):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, fontsize=size, fontname=f_bold)
                page.insert_text((self.x_val_dir, self.y_linhas[i]), str(valor).upper(), fontsize=size, fontname=f_reg)

            # 5. Inserção de Imagens (Produto e Logo)
            
            # PRODUTO (Lado Esquerdo) - Rect(x0, y0, x1, y1)
            if file_produto:
                rect_prod = fitz.Rect(50, 220, 270, 450)
                # O stream lê direto do upload do Streamlit
                page.insert_image(rect_prod, stream=file_produto.read())

            # LOGO/VETOR (Lado Direito)
            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 540, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    # MANTÉM O VETOR: Abre o PDF do logo e sobrepõe no layout
                    logo_doc = fitz.open(stream=file_vetor.read(), filetype="pdf")
                    page.show_pdf_page(rect_logo, logo_doc, 0)
                    logo_doc.close()
                else:
                    # Se for imagem (PNG/JPG), cola normal
                    file_vetor.seek(0) # Reseta ponteiro do arquivo
                    page.insert_image(rect_logo, stream=file_vetor.read())

            # 6. Salvar o arquivo final
            if not os.path.exists("saida"):
                os.makedirs("saida")
                
            output_path = f"saida/{nome_arquivo}.pdf"
            # garbage=4 e deflate=True reduzem o tamanho do arquivo
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            return output_path

        except Exception as e:
            st.error(f"Erro Crítico no Processor: {e}")
            return None
