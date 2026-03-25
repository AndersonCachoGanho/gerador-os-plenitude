import streamlit as st
from processador import GeradorOS
import os
from PIL import Image

# Configuração da Página
st.set_page_config(page_title="Plenitude Brindes - Gerador de O.S.", layout="wide")

st.title("Gerador de Ordem de Serviço - Plenitude Brindes")
st.markdown("---")

# Criando duas colunas: uma para dados e outra para instruções/arquivos
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
    upload_prod = st.file_uploader("Selecione a Foto do Produto", type=['png', 'jpg', 'jpeg'])
    upload_veto = st.file_uploader("Selecione o Logo (Vetor/Alta)", type=['png', 'jpg', 'pdf', 'ai', 'svg'])
    
    st.info("O sistema manterá a qualidade original dos arquivos para impressão.")

st.markdown("---")

# Botão de Ação
if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    if not dados['cliente'] or not dados['produto']:
        st.error("Por favor, preencha pelo menos o Cliente e o Produto.")
    else:
        try:
            # Caminhos temporários para processamento
            p_path = None
            v_path = None
            
            # Criar pastas se não existirem
            if not os.path.exists("uploads"): os.makedirs("uploads")
            
            if upload_prod:
                p_path = f"uploads/temp_prod_{upload_prod.name}"
                with open(p_path, "wb") as f:
                    f.write(upload_prod.getbuffer())
            
            if upload_veto:
                v_path = f"uploads/temp_veto_{upload_veto.name}"
                with open(v_path, "wb") as f:
                    f.write(upload_veto.getbuffer())

            # Chamar o processador reconstruído
            layout = "assets/layout_base.png"
            if os.path.exists(layout):
                gerador = GeradorOS(layout)
                nome_pdf = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_")
                pdf_gerado = gerador.gerar_os(dados, p_path, v_path, nome_pdf)
                
                st.success(f"✅ O.S. Gerada com Sucesso! Arquivo: {pdf_gerado}")
                
                # Botão para baixar o PDF direto pelo navegador
                with open(pdf_gerado, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Baixar PDF Agora",
                        data=pdf_file,
                        file_name=f"{nome_pdf}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("Erro: Layout base não encontrado em 'assets/layout_base.png'")
        
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
