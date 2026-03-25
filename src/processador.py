from PIL import Image, ImageDraw, ImageFont
import os
import fitz  # PyMuPDF

class GeradorOS:
    def __init__(self, layout_path):
        self.layout_path = layout_pathfrom PIL import Image, ImageDraw, ImageFont
import os
import fitz  # PyMuPDF
import streamlit as st  # Import necessário para st.warning e st.error

class GeradorOS:
    def __init__(self, layout_path):
        self.layout_path = layout_path
        
        # --- CONFIGURAÇÃO DE TEXTOS AJUSTADA PARA ALTA VISIBILIDADE (X, Y) ---
        # Aumentamos o espaçamento para a esquerda para não grudar na borda azul
        self.x_label_esq = 550      # Posição X para o rótulo (ex: "CLIENTE:")
        self.x_value_esq = 1100     # Posição X para o valor digitado (ex: "EMPRESA X")
        self.x_label_dir = 2000     # Posição X para a coluna da direita (rótulo)
        self.x_value_dir = 2650     # Posição X para o valor da direita

        # --- AJUSTE CRÍTICO DE ALTURA (Y) ---
        # Desci as linhas para começar em 350px (abaixo do logo e da borda superior)
        # e aumentei o espaçamento entre as linhas para 160px para não embolar.
        self.y_linhas = [350, 510, 670, 830]

    def converter_pdf_para_img(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            pagina = doc.load_page(0)
            # Alta definição (Zoom 4x para 300 DPI)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=True)
            img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
            doc.close()
            return img
        except Exception as e:
            st.error(f"Erro na conversão do PDF: {e}") # Usando st.error
            return None

    def gerar_os(self, dados, caminho_produto, caminho_vetor, nome_arquivo):
        # 1. Preparar Layout Base (A4 300DPI - 3508x2480px)
        img = Image.open(self.layout_path).convert("RGB")
        # Mantemos o resize para garantir a resolução correta
        img = img.resize((3508, 2480), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        # --- AJUSTE DE FONTE (Dobrei o tamanho de 55 para 110) ---
        try:
            # Carrega as fontes arial da pasta assets (que você subiu)
            f_bold = ImageFont.truetype("assets/arialbd.ttf", 110)
            f_reg = ImageFont.truetype("assets/arial.ttf", 110)
        except:
            # Se não achar, tenta carregar as fontes padrão ou dá erro
            try:
                f_bold = ImageFont.truetype("arialbd.ttf", 110)
                f_reg = ImageFont.truetype("arial.ttf", 110)
            except Exception as font_e:
                st.warning(f"Aviso: Fontes Arial não encontradas em 'assets'. Usando fonte padrão minúscula. Erro: {font_e}")
                st.info("Para corrigir, suba 'arial.ttf' e 'arialbd.ttf' para a pasta 'assets' no GitHub.")
                f_bold = f_reg = ImageFont.load_default()

        # 2. Escrita dos Dados (Cabeçalho)
        # Coluna da Esquerda
        itens_esq = [
            ("CLIENTE:", dados.get('cliente', '')),
            ("VENDEDOR:", dados.get('vendedor', '')), 
            ("PRODUTO:", dados.get('produto', '')),
            ("QUANTIDADE:", dados.get('quantidade', ''))
        ]
        for i, (label, valor) in enumerate(itens_esq):
            # Desenha o rótulo em Negrito
            draw.text((self.x_label_esq, self.y_linhas[i]), label, fill="black", font=f_bold)
            # Desenha o valor digitado (convertido para MAIÚSCULO) em Regular
            draw.text((self.x_value_esq, self.y_linhas[i]), str(valor).upper(), fill="black", font=f_reg)

        # Coluna da Direita
        itens_dir = [
            ("COR DO PRODUTO:", dados.get('cor', '')),
            ("GRAVAÇÃO:", dados.get('gravacao', '')), 
            ("PANTONE:", dados.get('pantone', '-'))
        ]
        for i, (label, valor) in enumerate(itens_dir):
            # Nota: usamos 'i' aqui também para alinhar horizontalmente com a coluna da esquerda
            # Desenha o rótulo da direita em Negrito
            draw.text((self.x_label_dir, self.y_linhas[i]), label, fill="black", font=f_bold)
            # Desenha o valor da direita em Regular
            draw.text((self.x_value_dir, self.y_linhas[i]), str(valor).upper(), fill="black", font=f_reg)

        # 3. Função de Colagem com Inteligência de Espaço (Sem alterações aqui)
        def colar_img_ajustada(caminho, pos_x, pos_y, max_w, max_h):
            if caminho and os.path.exists(caminho):
                extensao = caminho.lower().strip().split('.')[-1]
                
                temp = None
                
                # Tratamento por extensão
                if extensao == "pdf":
                    temp = self.converter_pdf_para_img(caminho)
                elif extensao in ["png", "jpg", "jpeg"]:
                    temp = Image.open(caminho).convert("RGBA")
                elif extensao == "ai":
                    # Formato .ai não é suportado nativamente pelo Pillow
                    st.warning(f"O arquivo de logo '{os.path.basename(caminho)}' está no formato .ai, que não é suportado diretamente. Para manter a qualidade, por favor, peça ao cliente um arquivo PDF ou gere um PNG de alta resolução (300 DPI) com fundo transparente.")
                    return # Sai da função sem colar nada
                else:
                    st.error(f"Formato de arquivo não suportado: .{extensao}")
                    return

                if temp:
                    # Cálculo de proporção (aspect ratio)
                    w_orig, h_orig = temp.size
                    ratio = min(max_w / w_orig, max_h / h_orig)
                    new_w = int(w_orig * ratio)
                    new_h = int(h_orig * ratio)
                    
                    temp = temp.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    # Centraliza a imagem dentro do box definido
                    final_x = pos_x + (max_w - new_w) // 2
                    final_y = pos_y + (max_h - new_h) // 2
                    
                    # Usa o próprio temp como máscara se for RGBA (transparência)
                    mask = temp if temp.mode == 'RGBA' else None
                    img.paste(temp, (final_x, final_y), mask)

        # --- DISTRIBUIÇÃO DAS IMAGENS (Ajustada para o novo tamanho de cabeçalho) ---
        
        # PRODUTO (Esquerda): Box de 1000x1000
        # Posicionado para não bater no cabeçalho (Desci para Y=1000)
        colar_img_ajustada(caminho_produto, 500, 1000, 1000, 1000)

        # VETOR (Direita): Box de 1000x1000 para manter simetria
        # Posicionado na área técnica da direita
        colar_img_ajustada(caminho_vetor, 2150, 1000, 1000, 1000)

        # 4. Salvar PDF
        if not os.path.exists("saida"): 
            os.makedirs("saida")
        output = f"saida/{nome_arquivo}.pdf"
        # Mantemos a resolução de 300.0 DPI
        img.save(output, "PDF", resolution=300.0)
        return output
        
        # --- CONFIGURAÇÃO DE TEXTOS (X, Y) ---
        self.x_label_esq = 750    
        self.x_value_esq = 1300   
        self.x_label_dir = 2100   
        self.x_value_dir = 2750   
        self.y_linhas = [75, 160, 245, 330]

    def converter_pdf_para_img(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            pagina = doc.load_page(0)
            # Alta definição (Zoom 4x para 300 DPI)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=True)
            img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
            doc.close()
            return img
        except Exception as e:
            print(f"Erro na conversão do PDF: {e}")
            return None

    def gerar_os(self, dados, caminho_produto, caminho_vetor, nome_arquivo):
        # 1. Preparar Layout Base (A4 300DPI)
        img = Image.open(self.layout_path).convert("RGB")
        img = img.resize((3508, 2480), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        try:
            f_bold = ImageFont.truetype("arialbd.ttf", 55)
            f_reg = ImageFont.truetype("arial.ttf", 55)
        except:
            f_bold = f_reg = ImageFont.load_default()

        # 2. Escrita dos Dados (Cabeçalho)
        itens_esq = [
            ("CLIENTE:", dados.get('cliente', '')),
            ("VENDEDOR:", dados.get('vendedor', '')), 
            ("PRODUTO:", dados.get('produto', '')),
            ("QUANTIDADE:", dados.get('quantidade', ''))
        ]
        for i, (label, valor) in enumerate(itens_esq):
            draw.text((self.x_label_esq, self.y_linhas[i]), label, fill="black", font=f_bold)
            draw.text((self.x_value_esq, self.y_linhas[i]), str(valor).upper(), fill="black", font=f_reg)

        itens_dir = [
            ("COR DO PRODUTO:", dados.get('cor', '')),
            ("GRAVAÇÃO:", dados.get('gravacao', '')), 
            ("PANTONE:", dados.get('pantone', '-'))
        ]
        for i, (label, valor) in enumerate(itens_dir):
            draw.text((self.x_label_dir, self.y_linhas[i]), label, fill="black", font=f_bold)
            draw.text((self.x_value_dir, self.y_linhas[i]), str(valor).upper(), fill="black", font=f_reg)

        # 3. Função de Colagem com Inteligência de Espaço
        def colar_img_ajustada(caminho, pos_x, pos_y, max_w, max_h):
            if caminho and os.path.exists(caminho):
                extensao = caminho.lower().strip().split('.')[-1]
                
                temp = None
                
                # Tratamento por extensão
                if extensao == "pdf":
                    temp = self.converter_pdf_para_img(caminho)
                elif extensao in ["png", "jpg", "jpeg"]:
                    temp = Image.open(caminho).convert("RGBA")
                elif extensao == "ai":
                    # Formato .ai não é suportado nativamente pelo Pillow
                    print(f"Aviso: O arquivo .ai '{caminho}' não é suportado nativamente. Por favor, converta para PDF ou PNG de alta resolução.")
                    st.warning(f"O arquivo de logo '{os.path.basename(caminho)}' está no formato .ai, que não é suportado diretamente. Para manter a qualidade, por favor, peça ao cliente um arquivo PDF ou gere um PNG de alta resolução (300 DPI) com fundo transparente.")
                    return # Sai da função sem colar nada
                else:
                    st.error(f"Formato de arquivo não suportado: .{extensao}")
                    return

                if temp:
                    # Cálculo de proporção (aspect ratio)
                    w_orig, h_orig = temp.size
                    ratio = min(max_w / w_orig, max_h / h_orig)
                    new_w = int(w_orig * ratio)
                    new_h = int(h_orig * ratio)
                    
                    temp = temp.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    # Centraliza a imagem dentro do box definido
                    final_x = pos_x + (max_w - new_w) // 2
                    final_y = pos_y + (max_h - new_h) // 2
                    
                    # O segredo: usa o próprio temp como máscara se for RGBA (transparência)
                    mask = temp if temp.mode == 'RGBA' else None
                    img.paste(temp, (final_x, final_y), mask)

        # --- DISTRIBUIÇÃO HARMONIOSA ---
        
        # PRODUTO (Esquerda): Box de 1000x1000
        # Posicionado para não bater no cabeçalho (Y=550)
        colar_img_ajustada(caminho_produto, 500, 850, 1000, 1000)

        # VETOR (Direita): Box de 1000x1000 para manter simetria
        # Posicionado na área técnica da direita
        colar_img_ajustada(caminho_vetor, 2150, 850, 1000, 1000)

        # 4. Salvar PDF
        if not os.path.exists("saida"): os.makedirs("saida")
        output = f"saida/{nome_arquivo}.pdf"
        img.save(output, "PDF", resolution=300.0)
        return output
