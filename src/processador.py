import fitz  # PyMuPDF
import os
import streamlit as st
from PIL import Image
import io

class GeradorOS:
    def __init__(self, layout_pdf_path):
        """Inicializa o gerador com o caminho do layout base PDF."""
        self.layout_path = layout_pdf_path
        
        # --- CONFIGURAÇÃO DE COORDENADAS PDF (A4 padrão: 595 x 842 pontos) ---
        # Coordenadas X para as colunas
        self.x_col_esq_label = 50   # Onde começa o rótulo (ex: CLIENTE:)
        self.x_col_esq_valor = 120  # Onde começa o valor digitado
        self.x_col_dir_label = 320  
        self.x_col_dir_valor = 410  

        # Coordenadas Y para as linhas de texto (cabeçalho)
        # Ajustado para ficar dentro da área branca superior do seu layout
        self.y_linhas = [80, 105, 130, 155] 

        # Tamanho da fonte para o cabeçalho
        self.font_size = 10

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        """Gera a O.S. mesclando dados, imagem do produto e logo vetorial."""
        try:
            # 1. ABRE O LAYOUT BASE (Seu design da Plenitude em PDF vetorial)
            if not os.path.exists(self.layout_path):
                raise FileNotFoundError(f"Layout não encontrado: {self.layout_path}")
            
            doc = fitz.open(self.layout_path)
            page = doc[0] # Seleciona a primeira página

            # 2. INSERIR DADOS DO FORMULÁRIO (Texto Vetorial)
            # Usamos fontes nativas do PDF (Helvetica) para garantir qualidade vetorial e evitar erros de arquivo de fonte
            font_bold = "helv-bold" # Helvetica Bold
            font_reg = "helv"      # Helvetica Regular
            cor_texto = (0, 0, 0)   # Preto

            # --- PROCESSAMENTO DOS TEXTOS (CABEÇALHO) ---
            # Dados da Esquerda
            itens_esq = [
                ("CLIENTE:", dados.get('cliente', '')),
                ("VENDEDOR:", dados.get('vendedor', '')), 
                ("PRODUTO:", dados.get('produto', '')),
                ("QTD:", dados.get('quantidade', ''))
            ]
            for i, (label, valor) in enumerate(itens_esq):
                # Desenha o rótulo em Negrito
                page.insert_text((self.x_col_esq_label, self.y_linhas[i]), label, 
                                 fontsize=self.font_size, fontname=font_bold, color=cor_texto)
                # Desenha o valor em Regular (convertido para MAIÚSCULO)
                page.insert_text((self.x_col_esq_valor, self.y_linhas[i]), str(valor).upper(), 
                                 fontsize=self.font_size, fontname=font_reg, color=cor_texto)

            # Dados da Direita
            itens_dir = [
                ("COR:", dados.get('cor', '')),
                ("GRAVAÇÃO:", dados.get('gravacao', '')), 
                ("PANTONE:", dados.get('pantone', '-'))
            ]
            for i, (label, valor) in enumerate(itens_dir):
                # Nota: usamos 'i' aqui também para alinhar horizontalmente com a coluna da esquerda
                page.insert_text((self.x_col_dir_label, self.y_linhas[i]), label, 
                                 fontsize=self.font_size, fontname=font_bold, color=cor_texto)
                page.insert_text((self.x_col_dir_valor, self.y_linhas[i]), str(valor).upper(), 
                                 fontsize=self.font_size, fontname=font_reg, color=cor_texto)

            # --- PROCESSAMENTO DAS ARTES (IMAGENS E LOGO) ---
            
            # 3. INSERIR FOTO DO PRODUTO (Esquerda)
            # Define o retângulo (área) onde a foto do brinde vai ficar (x0, y0, x1, y1)
            # Ajuste esses números para posicionar corretamente no seu layout
            rect_produto = fitz.Rect(50, 200, 250, 450) 
            
            if file_produto:
                # SOLUÇÃO DEFINITIVA: Lê os bytes diretamente da memória do Streamlit
                # O parâmetro 'stream' é a chave para funcionar na nuvem sem precisar gravar arquivo
                # O fitz.insert_image() ajusta automaticamente a imagem dentro do retângulo mantendo a proporção.
                try:
                    page.insert_image(rect_produto, stream=file_produto.read())
                except Exception as e_img:
                    st.warning(f"Aviso: Não foi possível inserir a foto do produto. Erro: {e_img}")

            # 4. INSERIR LOGO DO CLIENTE (Direita - Preservando VETOR se for PDF)
            # Define o retângulo (área) onde a logo vai ficar (x0, y0, x1, y1)
            rect_logo = fitz.Rect(320, 200, 545, 450)
            
            if file_vetor:
                nome_vetor = file_vetor.name.lower()
                
                # SE FOR PDF (VETORIAL): Usamos show_pdf_page para mesclar os vetores
                if nome_vetor.endswith('.pdf'):
                    try:
                        # Abre o PDF da logo diretamente da memória
                        logo_doc = fitz.open(stream=file_vetor.read(), filetype="pdf")
                        # Insere a primeira página da logo dentro do retângulo definido na OS
                        # Isso preserva os nós e curvas do vetor original (perfeito para o Illustrator)
                        page.show_pdf_page(rect_logo, logo_doc, 0)
                        logo_doc.close()
                    except Exception as e_vetor:
                        st.warning(f"Aviso: Não foi possível processar o logo PDF vetorial. Erro: {e_vetor}")
                
                # SE FOR IMAGEM (PNG/JPG): Inserimos como imagem de alta qualidade
                elif nome_vetor.endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        # Reinicia o ponteiro do arquivo para garantir a leitura do início
                        file_vetor.seek(0)
                        page.insert_image(rect_logo, stream=file_vetor.read())
                    except Exception as e_logo_img:
                        st.warning(f"Aviso: Não foi possível inserir o logo como imagem. Erro: {e_logo_img}")
                else:
                    st.warning(f"Aviso: O formato do arquivo de logo '{file_vetor.name}' não é suportado para inserção direta.")

            # 5. SALVAR O ARQUIVO FINAL
            # Cria a pasta 'saida' se não existir (no ambiente local, na nuvem é opcional mas boa prática)
            if not os.path.exists("saida"): 
                os.makedirs("saida")
            
            output_path = f"saida/{nome_arquivo}.pdf"
            
            # SALVAMENTO OTIMIZADO:
            # garbage=4: Remove objetos duplicados e não utilizados (limpa o arquivo)
            # deflate=True: Comprime streams de dados (reduz tamanho sem perder vetor)
            # clean=True: Limpa e repara a estrutura do PDF
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            # Retorna o caminho do arquivo gerado para o app_web.py
            return output_path

        except Exception as e:
            # Captura qualquer erro crítico e exibe no Streamlit
            st.error(f"Erro Crítico no Processador: {e}")
            return None
