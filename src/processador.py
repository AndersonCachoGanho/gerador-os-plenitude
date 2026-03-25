from PIL import Image, ImageDraw, ImageFont
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

    def converter_pdf_para_img(self, pdf_path, max_w, max_h):
        """Converte PDF para imagem com DPI alto (renderização vetorial de alta qualidade)"""
        try:
            doc = fitz.open(pdf_path)
            pagina = doc.load_page(0)
            
            # --- CORREÇÃO DE QUALIDADE (VETOR) ---
            # Para manter a qualidade, renderizamos com DPI alto (ex: 300 ou 600 DPI)
            # Um zoom de 6x ou 8x gera uma imagem enorme do vetor, que depois o Pillow redimensiona
            # com suavização (suprimindo os serrilhados).
            dpi = 600 # Configura para 600 DPI
            # pix = pagina.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), alpha=True) # Alternativa direta
            pix = pagina.get_pixmap(matrix=fitz.Matrix(8, 8), alpha=True) # Super Zoom 8x

            img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
            doc.close()
            return img
        except Exception as e:
            st.error(f"Erro na renderização do vetor: {e}") 
            return None

    def gerar_os(self, dados, caminho_produto, caminho_vetor, nome_arquivo):
        # 1. Preparar Layout Base (A4 300DPI - 3508x2480px)
        # Se você subir o arquivo 'layout_base.png' na raiz, chame direto
        img = Image.open(self.layout_path).convert("RGB")
        # Mantemos o resize para garantir a resolução correta
        img = img.resize((3508, 2480), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        # --- AJUSTE DE FONTE (Aumentado de 55 para 110) ---
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

        # 3. Função de Colagem Otimizada com Alta Qualidade
        def colar_img_ajustada(caminho, pos_x, pos_y, max_w, max_h):
            if caminho and os.path.exists(caminho):
                extensao = caminho.lower().strip().split('.')[-1]
                
                temp = None
                
                # Tratamento por extensão
                if extensao == "pdf":
                    # --- AJUSTE DE QUALIDADE ---
                    # Passamos max_w e max_h para a função saber o espaço final
                    # e renderizar o PDF com zoom altíssimo proporcional àquele box.
                    temp = self.converter_pdf_para_img(caminho, max_w, max_h)
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
                    
                    # --- REDIMENSIONAMENTO COM ALTA QUALIDADE ---
                    # Usamos Image.Resampling.LANCZOS (o melhor algoritmo de suavização do Pillow)
                    # Quando a imagem original tem resolução alta (zoom 8x), o LANCZOS
                    # remove os serrilhados e mantém as linhas nítidas.
                    temp = temp.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    # Centraliza a imagem dentro do box definido
                    final_x = pos_x + (max_w - new_w) // 2
                    final_y = pos_y + (max_h - new_h) // 2
                    
                    # Usa o próprio temp como máscara se for RGBA (transparência)
                    mask = temp if temp.mode == 'RGBA' else None
                    img.paste(temp, (final_x, final_y), mask)

        # --- DISTRIBUIÇÃO HARMONIOSA ---
        # A logo não ficará achatada porque o Pillow recalcula a proporção (ratio).
        # A qualidade será máxima porque renderizamos o PDF com DPI alto.
        
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
        # Mantemos a resolução de 300.0 DPI no PDF final
        img.save(output, "PDF", resolution=300.0)
        return output
