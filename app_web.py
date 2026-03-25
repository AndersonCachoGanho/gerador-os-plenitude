import streamlit as st
import fitz  # PyMuPDF
import os

# --- MOTOR DE GERAÇÃO (TUDO EM UM ARQUIVO SÓ) ---
class GeradorOS:
    def __init__(self, layout_pdf_path):
        self.layout_path = layout_pdf_path
        # Coordenadas em Pontos PDF (A4 padrão é 595 x 842)
        # Se o texto sair do lugar, basta ajustar esses números abaixo
        self.x_col_esq = 60
        self.x_val_esq = 135
        self.x_col_dir = 320
        self.x_val_dir = 430
        self.y_linhas = [85, 110, 135, 160] 

    def gerar_os(self, dados, file_produto, file_vetor, nome_arquivo):
        try:
            # Abre o layout base PDF
            doc = fitz.open(self.layout_path)
            page = doc[0]

            # FONTES NATIVAS (Não precisam de arquivo .ttf, por isso não dão erro)
            f_bold, f_reg = "helv-bold", "helv"
            
            # 1. Dados da Esquerda
            itens_esq = [
                ("CLIENTE:", dados.get('cliente', '')),
                ("VENDEDOR:", dados.get('vendedor', '')), 
                ("PRODUTO:", dados.get('produto', '')),
                ("QTD:", dados.get('quantidade', ''))
            ]
            for i, (label, valor) in enumerate(itens_esq):
                page.insert_text((self.x_col_esq, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_val_esq, self.y_linhas[i]), str(valor).upper(), fontsize=10, fontname=f_reg)

            # 2. Dados da Direita
            itens_dir = [
                ("COR:", dados.get('cor', '')),
                ("GRAVAÇÃO:", dados.get('gravacao', '')), 
                ("PANTONE:", dados.get('pantone', '-'))
            ]
            for i, (label, valor) in enumerate(itens_dir):
                page.insert_text((self.x_col_dir, self.y_linhas[i]), label, fontsize=10, fontname=f_bold)
                page.insert_text((self.x_val_dir, self.y_linhas[i]), str(valor).upper(), fontsize=10, fontname=f_reg)

            # 3. Inserir Foto do Produto (Lendo da memória)
            if file_produto:
                rect_prod = fitz.Rect(50, 220, 270, 450)
                page.insert_image(rect_prod, stream=file_produto.read())

            # 4. Inserir Logo (VETOR SE FOR PDF)
            if file_vetor:
                rect_logo = fitz.Rect(320, 220, 540, 450)
                if file_vetor.name.lower().endswith('.pdf'):
                    # Abre o PDF do logo e sobrepõe no layout (Mantém a qualidade máxima)
                    logo_doc = fitz.open(stream=file_vetor.read(), filetype="pdf")
                    page.show_pdf_page(rect_logo, logo_doc, 0)
                else:
                    file_vetor.seek(0)
                    page.insert_image(rect_logo, stream=file_vetor.read())

            # 5. Salvar na pasta temporária do Streamlit
            if not os.path.exists("saida"): os.makedirs("saida")
            output_path = f"saida/{nome_arquivo}.pdf"
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            return output_path
        except Exception as e:
            st.error(f"Erro no Processador: {e}")
            return None

# --- INTERFACE DE USUÁRIO ---
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
    up_veto = st.file_uploader("Logo (Vetor PDF ou Imagem)", type=['pdf', 'png', 'jpg'])

if st.button("🚀 GERAR O.S.", use_container_width=True):
    path_layout = "assets/layout_base.pdf"
    if os.path.exists(path_layout):
        gerador = GeradorOS(path_layout)
        nome_os = f"OS_{dados['cliente']}_{dados['produto']}".replace(" ", "_")
        resultado = gerador.gerar_os(dados, up_prod, up_veto, nome_os)
        
        if resultado:
            with open(resultado, "rb") as f:
                st.download_button("📥 Baixar O.S. Agora", f, f"{nome_os}.pdf")
    else:
        st.error("Erro: Coloque o arquivo 'layout_base.pdf' dentro da pasta 'assets' no seu GitHub.")
