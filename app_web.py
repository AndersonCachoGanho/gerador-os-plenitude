import streamlit as st
from src.processador import GeradorOS
import os

st.set_page_config(page_title="Plenitude Brindes - Gerador de O.S.", layout="wide")
st.title("Gerador de Ordem de Serviço - Plenitude Brindes")

col_dados, col_files = st.columns([1, 1])

with col_dados:
    st.subheader("📝 Dados da Ordem")
    dados = {
        'cliente': st.text_input("Cliente (Empresa):"),
        'vendedor': st.text_input("Vendedor:"),
        'produto': st.text_input("Nome do Produto:"),
        'quantidade': st.text_input("Quantidade:"),
        'cor': st.text_input("Cor do Produto:"),
        'gravacao': st.text_input("Tipo de Gravação:"),
        'pantone': st.text_input("Pantone:", value="-")
    }

with col_files:
    st.subheader("🖼️ Imagens e Logos")
    # Agora aceitamos PDF como prioridade para o Vetor
    upload_prod = st.file_uploader("Foto do Produto (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    upload_veto = st.file_uploader("Logo do Cliente (PDF VETORIAL)", type=['pdf', 'png', 'jpg'])
    st.info("Para manter o VETOR, suba o logo em PDF.")

if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    if not dados['cliente'] or not dados['produto']:
        st.error("Preencha Cliente e Produto.")
    else:
        try:
            if not os.path.exists("uploads"): os.makedirs("uploads")
            
            # Garantir que os caminhos não sejam None (mesmo que vazios)
            p_path = ""
            v_path = ""
            
            if upload_prod:
                p_path = f"uploads/p_{upload_prod.name}"
                with open(p_path, "wb") as f: f.write(upload_prod.getbuffer())
            
            if upload_veto:
                v_path = f"uploads/v_{upload_veto.name}"
                with open(v_path, "wb") as f: f.write(upload_veto.getbuffer())

            # IMPORTANTE: O arquivo no GitHub deve ser .pdf agora!
            layout = "assets/layout_base.pdf" 
            
            if os.path.exists(layout):
                gerador = GeradorOS(layout)
                nome_pdf = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_")
                pdf_gerado = gerador.gerar_os(dados, p_path, v_path, nome_pdf)
                
                if pdf_gerado:
                    st.success("✅ Gerado com Sucesso!")
                    with open(pdf_gerado, "rb") as f:
                        st.download_button("📥 Baixar O.S. Vetorial", f, f"{nome_pdf}.pdf", "application/pdf")
            else:
                st.error(f"Arquivo não encontrado: {layout}. Suba o layout em PDF na pasta assets.")
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
