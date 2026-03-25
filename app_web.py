import streamlit as st
import fitz  # PyMuPDF
import os

# --- MOTOR DE GERAÇÃO INTEGRADO ---
class GeradorOS:
    def __init__(self, layout_pdf_path):
        self.layout_path = layout_pdf_path
        # Coordenadas ajustadas para o padrão A4 PDF (595x842)
        self.x_col_esq = 60
        self.x_val_esq = 135
        self.x_col_dir = 320
        self.x_val_dir = 430
        self.y_linhas = [85, 110, 135, 160] 

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        try:
            doc = fitz.open(self.layout_path)
            page = doc[0]
            f_bold, f_reg = "helv-bold", "helv"
            
            # Dados Esquerda
            itens_esq = [("CLIENTE:", 'cliente'), ("VENDEDOR:", 'vendedor'), 
                         ("PRODUTO:", 'produto'), ("QTD:", 'quantidade')]
            for i, (label, key) in enumerate(itens_esq):
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_val_esq, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # Dados Direita
            itens_dir = [("COR:", 'cor'), ("GRAVAÇÃO:", 'gravacao'), ("PANTONE:", 'pantone')]
            for i, (label, key) in enumerate(itens_dir):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_val_dir, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # Imagem do Produto
            if file_produto:
                page.insert_image(fitz.Rect(50, 220, 270, 450), stream=file_produto.read())

            # Logo (Vetor ou Imagem)
            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 540, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    logo_doc = fitz.open(stream=file_vetor.read(), filetype="pdf")
                    page.show_pdf_page(rect_logo, logo_doc, 0)
                else:
                    file_vetor.seek(0)
                    page.insert_image(rect_logo, stream=file_vetor.read())

            if not os.path.exists("saida"): os.makedirs("saida")
            output_path = f"saida/{nome_arquivo}.pdf"
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            return output_path
        except Exception as e:
            st.error(f"Erro interno: {e}")
            return None

# --- INTERFACE ---
st.set_page_config(page_title="Plenitude Brindes - Gerador", layout="wide")
st.title("Gerador de O.S. - Plenitude Brindes")

col1, col2 = st.columns(2)
with col1:
    dados = {
        'cliente': st.text_input("Cliente:"),
        'vendedor': st.text_input("Vendedor:"),
        'produto': st.text_input("Produto:"),
        'quantidade': st.text_input("Quantidade:"),
        'cor': st.text_input("Cor:"),
        'gravacao': st.text_input("Gravação:"),
        'pantone': st.text_input("Pantone:", value="-")
    }
with col2:
    up_prod = st.file_uploader("Foto do Produto", type=['png', 'jpg', 'jpeg'])
    up_veto = st.file_uploader("Logo (PDF ou Imagem)", type=['pdf', 'png', 'jpg'])

if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    path_layout = "assets/layout_base.pdf"
    if os.path.exists(path_layout):
        gerador = GeradorOS(path_layout)
        nome_os = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_")
        res = gerador.gerar_os(dados, up_prod, up_veto, nome_os)
        if res:
            with open(res, "rb") as f:
                st.download_button("📥 Baixar O.S.", f, f"{nome_os}.pdf")
    else:
        st.error("Arquivo layout_base.pdf não encontrado na pasta assets.")
