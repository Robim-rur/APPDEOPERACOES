import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="Gerenciador de Operações Buy Side", layout="wide")

st.title("📊 Gerenciador de Operações - Buy Side")

DB_FILE = 'operacoes.csv'

# Função para carregar dados e incluir os lançamentos iniciais
def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not df.empty:
                df['Data Compra'] = pd.to_datetime(df['Data Compra']).dt.date
            return df
        except:
            pass
    
    # Dados iniciais baseados no seu histórico
    dados_iniciais = [
        {"Data Compra": datetime(2026, 5, 11).date(), "Ticker": "NVDC34", "Qtd": 5, "Preço Compra": 22.07, "Alvo (3%)": 22.73, "Estratégia": "SAZONALIDADE/bdrsetfspullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 11).date(), "Ticker": "KNSC11", "Qtd": 10, "Preço Compra": 9.17, "Alvo (3%)": 9.45, "Estratégia": "SAZONALIDADE", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 11).date(), "Ticker": "ITUB4", "Qtd": 2, "Preço Compra": 40.70, "Alvo (3%)": 41.92, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "CPFE3F", "Qtd": 2, "Preço Compra": 49.79, "Alvo (3%)": 51.27, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "ABEV3F", "Qtd": 6, "Preço Compra": 16.69, "Alvo (3%)": 17.18, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "AVGO34", "Qtd": 1, "Preço Compra": 30.60, "Alvo (3%)": 31.52, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "VIVT3F", "Qtd": 2, "Preço Compra": 39.77, "Alvo (3%)": 40.95, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "PETR4F", "Qtd": 2, "Preço Compra": 46.68, "Alvo (3%)": 48.06, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "SBSP3F", "Qtd": 3, "Preço Compra": 33.23, "Alvo (3%)": 34.23, "Estratégia": "auvppullback", "Status": "Aberta"},
        {"Data Compra": datetime(2026, 5, 6).date(), "Ticker": "TIM3F", "Qtd": 4, "Preço Compra": 26.35, "Alvo (3%)": 27.13, "Estratégia": "auvppullback", "Status": "Aberta"}
    ]
    
    df_inicial = pd.DataFrame(dados_iniciais)
    df_inicial["Data Venda"] = None
    df_inicial["Duração (Dias)"] = None
    return df_inicial

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

if 'operacoes' not in st.session_state:
    st.session_state.operacoes = carregar_dados()

# --- FORMULÁRIO DE ENTRADA ---
with st.expander("➕ Registrar Nova Operação", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        data_compra = st.date_input("Data da Compra", datetime.now().date())
        ticker = st.text_input("Ticker (Ex: PETR4F)").upper()
    with col2:
        qtd = st.number_input("Quantidade", min_value=1, step=1)
        preco_compra = st.number_input("Preço de Compra (R$)", min_value=0.01, format="%.2f")
    with col3:
        # Lógica para permitir digitar nova estratégia
        opcoes_estrat = ["auvppullback", "SAZONALIDADE", "SAZONALIDADE/bdrsetfspullback", "Outra (Digitar...)"]
        selecao = st.selectbox("Estratégia / App Origem", opcoes_estrat)
        
        if selecao == "Outra (Digitar...)":
            estrategia_final = st.text_input("Digite o nome da Estratégia/App")
        else:
            estrategia_final = selecao
            
        alvo = preco_compra * 1.03
        st.info(f"🎯 Alvo de Venda (3%): R$ {alvo:.2f}")

    if st.button("Salvar Operação"):
        if ticker and estrategia_final:
            nova_op = {"Data Compra": data_compra, "Ticker": ticker, "Qtd": qtd, "Preço Compra": preco_compra, "Alvo (3%)": round(alvo, 2), "Estratégia": estrategia_final, "Data Venda": None, "Duração (Dias)": None, "Status": "Aberta"}
            st.session_state.operacoes = pd.concat([st.session_state.operacoes, pd.DataFrame([nova_op])], ignore_index=True)
            salvar_dados(st.session_state.operacoes)
            st.success(f"Operação com {ticker} registrada!")
            st.rerun()
        else:
            st.warning("Por favor, preencha o Ticker e a Estratégia.")

# --- VISUALIZAÇÃO E EDIÇÃO ---
st.subheader("📝 Histórico de Operações")
if not st.session_state.operacoes.empty:
    st.dataframe(st.session_state.operacoes, use_container_width=True)

    st.divider()
    st.subheader("🏁 Registrar Encerramento (Venda)")
    ops_abertas = st.session_state.operacoes[st.session_state.operacoes['Status'] == 'Aberta']
    
    if not ops_abertas.empty:
        col_sel, col_data, col_btn = st.columns([2, 1, 1])
        with col_sel:
            opcoes = {idx: f"{row['Ticker']} (Compra: {row['Data Compra']})" for idx, row in ops_abertas.iterrows()}
            id_op = st.selectbox("Selecione a operação", options=list(opcoes.keys()), format_func=lambda x: opcoes[x])
        with col_data:
            data_venda = st.date_input("Data da Venda", datetime.now().date())
        with col_btn:
            st.write("")
            st.write("") 
            if st.button("Confirmar Venda"):
                idx = id_op
                dt_compra = st.session_state.operacoes.at[idx, "Data Compra"]
                if isinstance(dt_compra, str):
                    dt_compra = datetime.strptime(dt_compra, '%Y-%m-%d').date()
                duracao = (data_venda - dt_compra).days
                st.session_state.operacoes.at[idx, "Data Venda"] = data_venda
                st.session_state.operacoes.at[idx, "Duração (Dias)"] = duracao
                st.session_state.operacoes.at[idx, "Status"] = "Encerrada"
                salvar_dados(st.session_state.operacoes)
                st.success(f"Venda de {st.session_state.operacoes.at[idx, 'Ticker']} registrada!")
                st.rerun()
    else:
        st.info("Nenhuma operação aberta para encerrar.")

    st.sidebar.subheader("Configurações")
    csv = st.session_state.operacoes.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Baixar Excel (CSV)", csv, "historico_operacoes.csv", "text/csv")
else:
    st.info("Aguardando registro.")
