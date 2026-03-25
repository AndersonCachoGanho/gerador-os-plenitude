import fitz  # PyMuPDF
import os
import streamlit as st

class GeradorOS:
    def __init__(self, layout_pdf_path):
        # O layout agora DEVE ser um arquivo .pdf para preservar os vetores da sua marca
        self.layout_path = layout_pdf_path
        
        # --- CONFIGURAÇÃO DE COORDENADAS (Pontos PDF - A4: 595 x 842) ---
        # No PDF, as medidas são menores que em pixels.
        self.x_col_esq = 120
        self.x_col_dir = 350
        self.y_linhas = [65, 95, 125, 155] # Ajustado para o cabeçalho superior

    def gerar_os(self, dados, caminho_produto, caminho_vetor, nome_arquivo):
        try:
            # 1. Abre o Layout Base (VETORIAL)
            doc = fitz.open(self.layout_path)
            page = doc[0] # Seleciona a primeira página

            # 2. Inserir Dados do Formulário (Texto Vetorial)
            # Definindo uma fonte padrão do sistema para garantir que não falhe
            font_bold = "helv" # Helvetica Bold (Nativa do PDF, sempre vetor)
            font_reg = "helv"
            
            # Coluna Esquerda
            labels_esq = ["CLIENTE:", "VENDEDOR:", "PRODUTO:", "QTD:"]
            valores_esq = [dados.get('cliente', ''), dados.get('vendedor', ''), 
                          dados.get('produto', ''), dados.get('quantidade', '')]
            
            for i in range(len(labels_esq)):
                # Rótulo
                page.insert_text((self.x_col_esq, self.y_linhas[i]), labels_esq[i], 
                                 fontsize=10, fontname=font_bold, color=(0, 0, 0))
                # Valor (Deslocado 60 pontos para a direita do rótulo)
                page.insert_text((self.x_col_esq + 60, self.y_linhas[i]), str(valores_esq[i]).upper(), 
                                 fontsize=10, fontname=font_reg, color=(0, 0, 0))

            # Coluna Direita
            labels_dir = ["COR:", "GRAVAÇÃO:", "PANTONE:"]
            valores_dir = [dados.get('cor', ''), dados.get('gravacao', ''), dados.get('pantone', '-')]
            
            for i in range(len(labels_dir)):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), labels_dir[i], 
                                 fontsize=10, fontname=font_bold, color=(0, 0, 0))
                page.insert_text((self.x_col_dir + 70, self.y_linhas[i]), str(valores_dir[i]).upper(), 
                                 fontsize=10, fontname=font_reg, color=(0, 0, 0))

            # 3. INSERIR O LOGO DO CLIENTE (PRESERVANDO VETOR)
            if caminho_vetor:
                ext = caminho_vetor.lower()
                # Se for PDF, fazemos o "Overlay" (Vetor sobre Vetor)
                if ext.endswith(".pdf"):
                    logo_doc = fitz.open(caminho_vetor)
                    # Define o retângulo onde a logo vai entrar (x0, y0, x1, y1)
                    # Ajuste esses números para caber no seu quadro da direita
                    rect_logo = fitz.Rect(380, 250, 550, 450) 
                    page.show_pdf_page(rect_logo, logo_doc, 0)
                # Se for imagem, o fitz insere com alta qualidade
                else:
                    rect_logo = fitz.Rect(380, 250, 550, 450)
                    page.insert_image(rect_logo, filename=caminho_vetor)

            # 4. INSERIR FOTO DO PRODUTO
            if caminho_produto:
                # Retângulo da esquerda para a foto do brinde
                rect_prod = fitz.Rect(50, 250, 250, 450)
                page.insert_image(rect_prod, filename=caminho_produto)

            # 5. SALVAR O ARQUIVO FINAL
            if not os.path.exists("saida"): 
                os.makedirs("saida")
            
            output_path = f"saida/{nome_arquivo}.pdf"
            
            # 'garbage=4' limpa objetos duplicados, 'deflate=True' compacta sem perder vetor
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            return output_path

        except Exception as e:
            st.error(f"Erro Crítico no Processador: {e}")
            return None
