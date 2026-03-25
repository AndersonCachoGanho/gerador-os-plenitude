import streamlit as st
from src.processador import GeradorOS
import os

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
        try:
            layout = "assets/layout_base.pdf" 
            if os.path.exists(layout):
                gerador = GeradorOS(layout)
                nome_base = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_")
                # Passa os arquivos carregados diretamente
                pdf_path = gerador.gerar_os(dados, upload_prod, upload_veto, nome_base)
                
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button("📥 Baixar O.S. Vetorial", f, f"{nome_base}.pdf", "application/pdf")
            else:
                st.error("Layout 'assets/layout_base.pdf' não encontrado no GitHub.")
        except Exception as e:
            st.error(f"Erro: {e}")
