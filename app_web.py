import streamlit as st
import fitz  # PyMuPDF
import os

# --- CLASSE DO PROCESSADOR (Integrada para evitar erro de importação) ---
class GeradorOS:
    def __init__(self, layout_pdf_path):
        self.layout_path = layout_pdf_path
        # Coordenadas em Pontos PDF (A4: 595 x 842)
        self.x_col_esq = 60
        self.x_col_dir = 320
        self.y_linhas = [85, 110, 135, 160] 

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        try:
            if not os.path.exists(self.layout_path):
                return None
            
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # Fontes Nativas (Não precisam de arquivos .ttf)
            f_bold, f_reg = "helv-bold", "helv"
            
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

            # Inserir Artes
            if file_produto:
                page.insert_image(fitz.Rect(50, 220, 250, 450), stream=file_produto.read())

            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 545, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    with fitz.open(stream=file_vetor.read(), filetype="pdf") as logo_doc:
                        page.show_pdf_page(rect_logo, logo_doc, 0)
                else:
                    file_vetor.seek(0)
                    page.insert_image(rect_logo, stream=file_vetor.read())

            if not os.path.exists("saida"): os.makedirs("saida")
            output_path = os.path.join("saida", f"{nome_arquivo}.pdf")
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            return output_path
        except Exception as e:
            st.error(f"Erro no Processador: {e}")
            return None

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Plenitude Brindes - Gerador", layout="wide")
st.title("Gerador de O.S. - Plenitude Brindes")

col_dados, col_files = st.columns([1, 1])

with col_dados:
    dados = {
        'cliente': st.text_input("Cliente:"),
        'vendedor': st.text_input("Vendedor:"),
        'produto': st.text_input("Produto:"),
        'quantidade': st.text_input("Quantidade:"),
        'cor': st.text_input("Cor:"),
        'gravacao': st.text_input("Gravação:"),
        'pantone': st.text_input("Pantone:", value="-")
    }

with col_files:
    upload_prod = st.file_uploader("Foto Produto", type=['png', 'jpg', 'jpeg'])
    upload_veto = st.file_uploader("Logo (PDF Vetor/Imagem)", type=['pdf', 'png', 'jpg'])

if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    if not dados['cliente'] or not dados['produto']:
        st.error("Preencha os campos obrigatórios.")
    else:
        layout = "assets/layout_base.pdf"
        if os.path.exists(layout):
            gerador = GeradorOS(layout)
            nome_base = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_")
            pdf_path = gerador.gerar_os(dados, upload_prod, upload_veto, nome_base)
            
            if pdf_path:
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Baixar O.S. Vetorial", f, f"{nome_base}.pdf", "application/pdf")
        else:
            st.error("Layout não encontrado em assets/layout_base.pdf")
