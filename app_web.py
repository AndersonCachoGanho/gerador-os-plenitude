import streamlit as st
from src.processador import GeradorOS
import os

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
    # Aceita formatos de imagem padrão e PDF para vetor
    upload_prod = st.file_uploader("Selecione a Foto do Produto (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    upload_veto = st.file_uploader("Selecione o Logo (PDF Vetorial, PNG, JPG)", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    st.info("Para máxima qualidade na impressão, prefira o logo do cliente em formato PDF vetorial.")

st.markdown("---")

# Botão de Ação
if st.button("🚀 GERAR ORDEM DE SERVIÇO", use_container_width=True):
    # Validação básica
    if not dados['cliente'] or not dados['produto']:
        st.error("Por favor, preencha pelo menos o nome do Cliente e o Produto.")
    else:
        with st.spinner('Gerando Ordem de Serviço vetorial...'):
            try:
                # Caminho do layout base no GitHub (assets/)
                layout_path = "assets/layout_base.pdf" 
                
                # Verificação Crítica: O arquivo de layout existe?
                if not os.path.exists(layout_path):
                    st.error(f"Erro Crítico: Arquivo de layout '{layout_path}' não encontrado na pasta 'assets' do GitHub.")
                    st.stop() # Interrompe a execução

                # Inicializa o processador com o caminho do layout
                gerador = GeradorOS(layout_path)
                
                # Prepara o nome do arquivo final (OS_NomeCliente_NomeProduto.pdf)
                # Remove espaços e caracteres especiais para evitar erros de download
                cliente_safe = "".join([c if c.isalnum() else "_" for c in dados['cliente']])
                produto_safe = "".join([c if c.isalnum() else "_" for c in dados['produto']])
                nome_base_pdf = f"OS_{cliente_safe}_{produto_safe}"

                # --- CHAMADA DO PROCESSADOR (PASSANDO OBJETOS DE MEMÓRIA) ---
                # Passamos diretamente upload_prod e upload_veto (que são objetos BytesIO/UploadedFile)
                pdf_gerado_path = gerador.gerar_os(dados, upload_prod, upload_veto, nome_base_pdf)
                
                if pdf_gerado_path and os.path.exists(pdf_gerado_path):
                    st.success(f"✅ Ordem de Serviço para '{dados['cliente']}' gerada com sucesso!")
                    
                    # Botão para baixar o PDF direto pelo navegador
                    with open(pdf_gerado_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Baixar O.S. Vetorial Completa",
                            data=pdf_file,
                            file_name=f"{nome_base_pdf}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.error("Erro interno ao gerar ou localizar o arquivo PDF final.")
            
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado no processamento: {e}")
