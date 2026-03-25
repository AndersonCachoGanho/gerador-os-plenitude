import streamlit as st
import fitz  # PyMuPDF
import os

# --- LÓGICA DO PROCESSADOR INTEGRADA ---
class GeradorOS:
    def __init__(self, layout_pdf_path):
        self.layout_path = layout_pdf_path
        # Coordenadas em Pontos PDF (A4 padrão: 595 x 842)
        self.x_col_esq = 60
        self.x_val_esq = 135
        self.x_col_dir = 320
        self.x_val_dir = 430
        self.y_linhas = [85, 110, 135, 160] 

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        try:
            if not os.path.exists(self.layout_path):
                return None
            
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # Fontes Nativas (Garante que NÃO dê erro de 'font file')
            f_bold, f_reg = "helv-bold", "helv"
            
            # 1. Dados da Esquerda
            itens_esq = [("CLIENTE:", 'cliente'), ("VENDEDOR:", 'vendedor'), 
                         ("PRODUTO:", 'produto'), ("QTD:", 'quantidade')]
            for i, (label, key) in enumerate(itens_esq):
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_val_esq, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # 2. Dados da Direita
            itens_dir = [("COR:", 'cor'), ("GRAVAÇÃO:", 'gravacao'), ("PANTONE:", 'pantone')]
            for i, (label, key) in enumerate(itens_dir):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_val_dir, self.y_linhas[i]), str(dados.get(key, '')).upper(), fontsize=10, fontname=f_reg)

            # 3. Imagem do Produto
            if file_produto:
                rect_prod = fitz.Rect(50, 220, 270, 450)
                page.insert_image(rect_prod, stream=file_produto.read())

            # 4. Logo (Mantém Vetor se for PDF)
            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 540, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    logo_doc = fitz.open(stream=file_vetor.read(), filetype="pdf")
                    page.show_pdf_page(rect_logo, logo_doc, 0)
                    logo_doc.close()
                else:
                    file_vetor.seek(0)
                    page.insert_image(rect_logo, stream=file_vetor.read())

            # 5. Salvar PDF
            if not os.path.exists("saida"): os.makedirs("saida")
            output_path = os.path.join("saida", f"{nome_arquivo}.pdf")
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            return output_path
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
            return None

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Plenitude Brindes - Gerador", layout="wide")
st.title("Gerador de O.S. - Plenitude Brindes")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Informações")
    dados_input = {
        'cliente': st.text_input("Cliente:"),
        'vendedor': st.text_input("Vendedor:"),
        'produto': st.text_input("Produto:"),
        'quantidade': st.text_input("Quantidade:"),
        'cor': st.text_input("Cor:"),
        'gravacao': st.text_input("Gravação:"),
        'pantone': st.text_input("Pantone:", value="-")
    }

with col2:
    st.subheader("Arquivos")
    up_prod = st.file_uploader("Foto Produto", type=['png', 'jpg', 'jpeg'])
    up_veto = st.file_uploader("Logo (PDF ou Imagem)", type=['pdf', 'png', 'jpg'])

if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    path_layout = "assets/layout_base.pdf"
    if os.path.exists(path_layout):
        gerador = GeradorOS(path_layout)
        nome_os = f"OS_{dados_input['cliente']}_{dados_input['produto']}".replace(" ", "_")
        resultado = gerador.gerar_os(dados_input, up_prod, up_veto, nome_os)
        
        if resultado:
            st.success("✅ Gerado!")
            with open(resultado, "rb") as f:
                st.download_button("📥 Baixar O.S.", f, f"{nome_os}.pdf", "application/pdf")
    else:
        st.error(f"Layout não encontrado em: {path_layout}")
