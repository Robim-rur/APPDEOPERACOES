import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="Gerenciador de Operações Buy Side", layout="wide")[cite: 1]

st.title("📊 Gerenciador de Operações - Buy Side")[cite: 1]

# Nome do arquivo para persistência local de dados (CSV)
DB_FILE = 'operacoes.csv'[cite: 1]

# Função para carregar dados salvos
def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Converte colunas de data de string para objeto date
            if not df.empty:
                df['Data Compra'] = pd.to_datetime(df['Data Compra']).dt.date
            return df
        except:
            pass
    return pd.DataFrame(columns=[
        "Data Compra", "Ticker", "Qtd", "Preço Compra", "Alvo (3%)", "Estratégia", "Data Venda", "Duração (Dias)", "Status"
    ])[cite: 1]

# Função para salvar dados no CSV
def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)[cite: 1]

# Inicialização do estado da sessão
if 'operacoes' not in st.session_state:
    st.session_state.operacoes = carregar_dados()[cite: 1]

# --- FORMULÁRIO DE ENTRADA ---
with st.expander("➕ Registrar Nova Operação", expanded=True):[cite: 1]
    col1, col2, col3 = st.columns(3)[cite: 1]
    
    with col1:
        data_compra = st.date_input("Data da Compra", datetime.now().date())[cite: 1]
        ticker = st.text_input("Ticker (Ex: PETR4F)").upper()[cite: 1]
    
    with col2:
        qtd = st.number_input("Quantidade", min_value=1, step=1)[cite: 1]
        preco_compra = st.number_input("Preço de Compra (R$)", min_value=0.01, format="%.2f")[cite: 1]
    
    with col3:
        # Lista de estratégias baseada nos seus dados
        estrategia = st.selectbox("Estratégia / App Origem", [
            "auvppullback",
            "SAZONALIDADE",
            "SAZONALIDADE/bdrsetfspullback", 
            "Outros"
        ])[cite: 1]
        # Cálculo automático do alvo de 3%
        alvo = preco_compra * 1.03[cite: 1]
        st.info(f"🎯 Alvo de Venda (3%): R$ {alvo:.2f}")[cite: 1]

    if st.button("Salvar Operação"):[cite: 1]
        if ticker:
            nova_op = {
                "Data Compra": data_compra,
                "Ticker": ticker,
                "Qtd": qtd,
                "Preço Compra": preco_compra,
                "Alvo (3%)": round(alvo, 2),
                "Estratégia": estrategia,
                "Data Venda": None,
                "Duração (Dias)": None,
                "Status": "Aberta"
            }
            # Adiciona ao DataFrame e salva
            st.session_state.operacoes = pd.concat([st.session_state.operacoes, pd.DataFrame([nova_op])], ignore_index=True)
            salvar_dados(st.session_state.operacoes)
            st.success(f"Operação com {ticker} registrada!")
            st.rerun()
        else:
            st.error("Por favor, preencha o Ticker.")[cite: 1]

# --- VISUALIZAÇÃO E EDIÇÃO ---
st.subheader("📝 Histórico de Operações")[cite: 1]

if not st.session_state.operacoes.empty:[cite: 1]
    # Exibição da tabela principal
    st.dataframe(st.session_state.operacoes, use_container_width=True)[cite: 1]

    # Lógica para registrar a venda (Encerramento)
    st.divider()
    st.subheader("🏁 Registrar Encerramento (Venda)")[cite: 1]
    
    # Filtrar apenas operações que ainda estão abertas
    ops_abertas = st.session_state.operacoes[st.session_state.operacoes['Status'] == 'Aberta'][cite: 1]
    
    if not ops_abertas.empty:
        col_sel, col_data, col_btn = st.columns([2, 1, 1])[cite: 1]
        with col_sel:
            opcoes = {idx: f"{row['Ticker']} (Compra: {row['Data Compra']})" for idx, row in ops_abertas.iterrows()}
            id_op = st.selectbox("Selecione a operação", options=list(opcoes.keys()), format_func=lambda x: opcoes[x])[cite: 1]
        
        with col_data:
            data_venda = st.date_input("Data da Venda", datetime.now().date())[cite: 1]
        
        with col_btn:
            st.write("") # Alinhamento
            st.write("") 
            if st.button("Confirmar Venda"):
                idx = id_op
                dt_compra = st.session_state.operacoes.at[idx, "Data Compra"]
                if isinstance(dt_compra, str):
                    dt_compra = datetime.strptime(dt_compra, '%Y-%m-%d').date()
                
                # Cálculo da duração
                duracao = (data_venda - dt_compra).days[cite: 1]
                
                # Atualiza os campos
                st.session_state.operacoes.at[idx, "Data Venda"] = data_venda
                st.session_state.operacoes.at[idx, "Duração (Dias)"] = duracao
                st.session_state.operacoes.at[idx, "Status"] = "Encerrada"
                
                salvar_dados(st.session_state.operacoes)
                st.success(f"Venda de {st.session_state.operacoes.at[idx, 'Ticker']} registrada!")
                st.rerun()
    else:
        st.info("Nenhuma operação aberta para encerrar no momento.")[cite: 1]

    # Exportação e Limpeza
    st.sidebar.subheader("Configurações")
    csv = st.session_state.operacoes.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Baixar Excel (CSV)", csv, "meu_historico_buyside.csv", "text/csv")[cite: 1]
    
    if st.sidebar.button("⚠️ Limpar Tudo"):
        if st.sidebar.checkbox("Confirmar exclusão de TODOS os dados?"):
            st.session_state.operacoes = pd.DataFrame(columns=st.session_state.operacoes.columns)
            salvar_dados(st.session_state.operacoes)
            st.rerun()[cite: 1]
else:
    st.info("Aguardando o registro da primeira operação.")[cite: 1]
