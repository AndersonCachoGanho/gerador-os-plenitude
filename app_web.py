import streamlit as st
import os
from src.processador import GeradorOS

# 1. Configuração da página (Deve ser a primeira linha do Streamlit)
st.set_page_config(page_title="Plenitude Brindes - Gerador", layout="wide")

st.title("Gerador de O.S. - Plenitude Brindes")

# 2. Interface de Colunas
col_dados, col_files = st.columns([1, 1])

with col_dados:
    st.subheader("Dados da Ordem")
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
    st.subheader("Arquivos")
    upload_prod = st.file_uploader("Foto Produto", type=['png', 'jpg', 'jpeg'], key="prod")
    upload_veto = st.file_uploader("Logo (PDF Vetor/Imagem)", type=['pdf', 'png', 'jpg'], key="veto")

st.divider()

# 3. Lógica de Geração
if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    if not dados['cliente'] or not dados['produto']:
        st.error("❌ Erro: Preencha os campos 'Cliente' e 'Produto'.")
    else:
        try:
            # Caminho absoluto para evitar erros no servidor Linux do Streamlit
            layout = os.path.join("assets", "layout_base.pdf")
            
            if os.path.exists(layout):
                # Garantir que a pasta de saída existe
                if not os.path.exists("saida"):
                    os.makedirs("saida")

                gerador = GeradorOS(layout)
                
                # Nome do arquivo sanitizado (sem espaços problemáticos)
                nome_base = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_").replace("/", "-")
                
                # Processamento
                pdf_path = gerador.gerar_os(dados, upload_prod, upload_veto, nome_base)
                
                if pdf_path and os.path.exists(pdf_path):
                    st.success("✅ O.S. Gerada com Sucesso!")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Baixar O.S. Vetorial",
                            data=f,
                            file_name=f"{nome_base}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.error("❌ O processador não conseguiu gerar o PDF. Verifique os logs.")
            else:
                st.error(f"❌ Layout não encontrado em: {layout}. Verifique se o arquivo está na pasta 'assets' do GitHub.")
        
        except Exception as e:
            st.error(f"⚠️ Ocorreu um erro inesperado: {e}")
