# app.py

import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import gspread
from google.oauth2.service_account import Credentials

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Gerenciador de Operações Buy Side",
    layout="wide"
)

st.title("📊 Gerenciador de Operações - Buy Side")

# =========================================================
# GOOGLE SHEETS
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "1F96th5Cu0Px4eFWrPfwBIiBpohEtgGk-Gc0O199mnaM"

ABA_NOME = "operacoes"

# =========================================================
# CONEXÃO
# =========================================================

@st.cache_resource
def conectar_planilha():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    planilha = client.open_by_key(SHEET_ID)

    aba = planilha.worksheet(ABA_NOME)

    return aba


# =========================================================
# FUNÇÕES NUMÉRICAS
def converter_numero(valor):

    if valor is None:
        return None

    if valor == "":
        return None

    try:

        # Se já for número
        if isinstance(valor, (int, float)):
            return float(valor)

        texto = str(valor).strip()

        texto = texto.replace("R$", "")
        texto = texto.replace("%", "")
        texto = texto.replace(" ", "")

        # =================================================
        # CASO 1:
        # 1.234,56  -> 1234.56
        # =================================================

        if "," in texto and "." in texto:

            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")

        # =================================================
        # CASO 2:
        # 1,93 -> 1.93
        # =================================================

        elif "," in texto:

            texto = texto.replace(",", ".")

        # =================================================
        # CASO 3:
        # 951.10 -> mantém
        # =================================================

        return float(texto)

    except Exception:

        return None

# =========================================================
# GARANTIR COLUNAS
# =========================================================

def garantir_colunas(df):

    colunas_necessarias = {
        "ID": "",
        "Data Compra": None,
        "Ticker": "",
        "Qtd": 0,
        "Preço Compra": 0.0,
        "Alvo (3%)": 0.0,
        "Estratégia": "",
        "Preço Venda": None,
        "Data Venda": None,
        "Duração (Dias)": None,
        "Resultado %": None,
        "Resultado R$": None,
        "Status": "Aberta"
    }

    for coluna, valor_padrao in colunas_necessarias.items():

        if coluna not in df.columns:
            df[coluna] = valor_padrao

    return df

# =========================================================
# CARREGAR DADOS
# =========================================================

def carregar_dados():

    try:

        aba = conectar_planilha()

        dados = aba.get_all_records(
            numericise_ignore=['all']
        )

        if len(dados) == 0:

            df_vazio = pd.DataFrame()

            df_vazio = garantir_colunas(df_vazio)

            salvar_dados(df_vazio)

            return df_vazio

        df = pd.DataFrame(dados)

        df = garantir_colunas(df)

        # =================================================
        # DATAS
        # =================================================

        if "Data Compra" in df.columns:

            df["Data Compra"] = pd.to_datetime(
                df["Data Compra"],
                errors="coerce"
            ).dt.date

        if "Data Venda" in df.columns:

            df["Data Venda"] = pd.to_datetime(
                df["Data Venda"],
                errors="coerce"
            ).dt.date

        # =================================================
        # NÚMEROS
        # =================================================

        colunas_numericas = [
            "Qtd",
            "Preço Compra",
            "Alvo (3%)",
            "Preço Venda",
            "Duração (Dias)",
            "Resultado %",
            "Resultado R$"
        ]

        for coluna in colunas_numericas:

            if coluna in df.columns:

                df[coluna] = df[coluna].apply(
                    converter_numero
                )

        # =================================================
        # IDs
        # =================================================

        ids_vazios = (
            df["ID"].isna() |
            (df["ID"] == "")
        )

        quantidade_ids = ids_vazios.sum()

        if quantidade_ids > 0:

            novos_ids = [
                str(uuid.uuid4())[:8]
                for _ in range(quantidade_ids)
            ]

            df.loc[ids_vazios, "ID"] = novos_ids

        return df

    except Exception as e:

        st.error(f"Erro ao carregar dados: {e}")

    dados_iniciais = []

    df = pd.DataFrame(dados_iniciais)

    return garantir_colunas(df)

# =========================================================
# SALVAR DADOS
# =========================================================

def salvar_dados(df):

    try:

        aba = conectar_planilha()

        df_salvar = df.copy()

        # =================================================
        # DATAS
        # =================================================

        for coluna in ["Data Compra", "Data Venda"]:

            if coluna in df_salvar.columns:

                df_salvar[coluna] = df_salvar[
                    coluna
                ].astype(str)

        # =================================================
        # NÚMEROS
        # =================================================

        colunas_numericas = [
            "Qtd",
            "Preço Compra",
            "Alvo (3%)",
            "Preço Venda",
            "Duração (Dias)",
            "Resultado %",
            "Resultado R$"
        ]

        for coluna in colunas_numericas:

            if coluna in df_salvar.columns:

                df_salvar[coluna] = pd.to_numeric(
                    df_salvar[coluna],
                    errors="coerce"
                )

        df_salvar = df_salvar.fillna("")

        dados = [
            df_salvar.columns.tolist()
        ] + df_salvar.values.tolist()

        aba.clear()

        aba.update(dados)

    except Exception as e:

        st.error(f"Erro ao salvar dados: {e}")

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def calcular_dias_aberto(data_compra):

    if pd.isnull(data_compra):
        return 0

    return (date.today() - data_compra).days

def classificar_tempo(dias):

    if dias <= 15:
        return "🟢 Saudável"

    elif dias <= 45:
        return "🟡 Atenção"

    else:
        return "🔴 Capital Parado"

# =========================================================
# SESSION STATE
# =========================================================

if "operacoes" not in st.session_state:

    st.session_state.operacoes = carregar_dados()

st.session_state.operacoes = garantir_colunas(
    st.session_state.operacoes
)

df = st.session_state.operacoes

# =========================================================
# CÁLCULOS
# =========================================================

ops_abertas = df[df["Status"] == "Aberta"]

ops_encerradas = df[df["Status"] == "Encerrada"]

capital_alocado = 0

if not ops_abertas.empty:

    capital_alocado = (
        ops_abertas["Qtd"].fillna(0)
        *
        ops_abertas["Preço Compra"].fillna(0)
    ).sum()

ciclos_concluidos = len(ops_encerradas)

tempo_medio = 0

if not ops_encerradas.empty:

    duracoes_validas = ops_encerradas[
        "Duração (Dias)"
    ].dropna()

    if not duracoes_validas.empty:

        tempo_medio = round(
            duracoes_validas.mean(),
            1
        )

lucro_total = 0

if not ops_encerradas.empty:

    lucro_total = ops_encerradas[
        "Resultado R$"
    ].fillna(0).sum()

# =========================================================
# RESUMO EXECUTIVO
# =========================================================

st.subheader("📌 Resumo Executivo")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Operações Abertas",
        len(ops_abertas)
    )

with col2:

    st.metric(
        "Capital Alocado",
        f"R$ {capital_alocado:,.2f}"
    )

with col3:

    st.metric(
        "Tempo Médio",
        f"{tempo_medio} dias"
    )

with col4:

    st.metric(
        "Ciclos",
        ciclos_concluidos
    )

with col5:

    st.metric(
        "Lucro Total",
        f"R$ {lucro_total:,.2f}"
    )

# =========================================================
# ALERTA CAPITAL PARADO
# =========================================================

ops_lentas = []

for idx, row in ops_abertas.iterrows():

    dias = calcular_dias_aberto(
        row["Data Compra"]
    )

    if dias > 45:

        ops_lentas.append(
            row["Ticker"]
        )

if len(ops_lentas) > 0:

    st.warning(
        f"⚠️ {len(ops_lentas)} operação(ões) acima de 45 dias: "
        + ", ".join(ops_lentas)
    )

# =========================================================
# FORMULÁRIO NOVA OPERAÇÃO
# =========================================================

with st.expander(
    "➕ Registrar Nova Operação",
    expanded=False
):

    col1, col2, col3 = st.columns(3)

    with col1:

        data_compra = st.date_input(
            "Data da Compra",
            datetime.now().date()
        )

        ticker = st.text_input(
            "Ticker"
        ).upper()

    with col2:

        qtd = st.number_input(
            "Quantidade",
            min_value=1,
            step=1
        )

        preco_compra = st.number_input(
            "Preço de Compra (R$)",
            min_value=0.01,
            format="%.2f"
        )

    with col3:

        opcoes_estrat = [
            "auvppullback",
            "SAZONALIDADE",
            "SAZONALIDADE/bdrsetfspullback",
            "Outra (Digitar...)"
        ]

        selecao = st.selectbox(
            "Estratégia / App Origem",
            opcoes_estrat
        )

        if selecao == "Outra (Digitar...)":

            estrategia_final = st.text_input(
                "Digite o nome da Estratégia/App"
            )

        else:

            estrategia_final = selecao

        alvo = round(
            preco_compra * 1.03,
            2
        )

        st.info(
            f"🎯 Alvo de Venda: R$ {alvo:.2f}"
        )

    if st.button("Salvar Operação"):

        if ticker and estrategia_final:

            nova_op = {
                "ID": str(uuid.uuid4())[:8],
                "Data Compra": data_compra,
                "Ticker": ticker,
                "Qtd": qtd,
                "Preço Compra": preco_compra,
                "Alvo (3%)": alvo,
                "Estratégia": estrategia_final,
                "Preço Venda": None,
                "Data Venda": pd.NaT,
                "Duração (Dias)": None,
                "Resultado %": None,
                "Resultado R$": None,
                "Status": "Aberta"
            }

            st.session_state.operacoes = pd.concat(
                [
                    st.session_state.operacoes,
                    pd.DataFrame([nova_op])
                ],
                ignore_index=True
            )

            salvar_dados(
                st.session_state.operacoes
            )

            st.success(
                f"Operação com {ticker} registrada!"
            )

            st.rerun()

# =========================================================
# TABELA PRINCIPAL
# =========================================================

st.subheader("📝 Operações")

if not df.empty:

    tabela = df.copy()

    dias_aberto_lista = []

    status_tempo_lista = []

    for idx, row in tabela.iterrows():

        if row["Status"] == "Aberta":

            dias = calcular_dias_aberto(
                row["Data Compra"]
            )

            dias_aberto_lista.append(dias)

            status_tempo_lista.append(
                classificar_tempo(dias)
            )

        else:

            dias_aberto_lista.append(
                row["Duração (Dias)"]
            )

            status_tempo_lista.append("—")

    tabela["Dias em Aberto"] = dias_aberto_lista

    tabela["Status Tempo"] = status_tempo_lista

    tabela_exibir = tabela.copy()

    tabela_exibir["Resultado R$"] = tabela_exibir[
        "Resultado R$"
    ].apply(
        lambda x: (
            f"R$ {float(x):,.2f}"
            if pd.notnull(x)
            else "-"
        )
    )

    colunas_exibir = [
        "Ticker",
        "Data Compra",
        "Qtd",
        "Preço Compra",
        "Alvo (3%)",
        "Estratégia",
        "Status",
        "Dias em Aberto",
        "Status Tempo",
        "Resultado R$"
    ]

    st.dataframe(
        tabela_exibir[colunas_exibir],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# GERENCIAR OPERAÇÕES
# =========================================================

st.divider()

st.subheader("🛠️ Gerenciar Operações")

df_ops = st.session_state.operacoes.copy()

if not df_ops.empty:

    opcoes_operacoes = {
        row["ID"]: (
            f"{row['Ticker']} | "
            f"{row['Data Compra']} | "
            f"{row['Status']}"
        )
        for _, row in df_ops.iterrows()
    }

    operacao_id = st.selectbox(
        "Selecione uma operação",
        options=list(opcoes_operacoes.keys()),
        format_func=lambda x: opcoes_operacoes[x],
        key="selecionar_operacao"
    )

    linha = df_ops[df_ops["ID"] == operacao_id].iloc[0]

    # =====================================================
    # DETALHES DA OPERAÇÃO
    # =====================================================

    st.info(
        f"""
📌 Ticker: {linha['Ticker']}

📅 Data Compra: {linha['Data Compra']}

📦 Quantidade: {linha['Qtd']}

💰 Preço Compra: R$ {linha['Preço Compra']:.2f}

🎯 Alvo: R$ {linha['Alvo (3%)']:.2f}
     colb1, colb2, colb3 = st.columns(3)

    # =====================================================
    # SALVAR EDIÇÃO
    # =====================================================

    with colb1:
📊 Status: {linha['Status']}

🧠 Estratégia: {linha['Estratégia']}
"""
    )

    st.markdown("### ✏️ Editar Operação")

colb1, colb2, colb3 = st.columns(3)

with colb1:

    if st.button("💾 Salvar Alterações"):

        idx_real = st.session_state.operacoes[
            st.session_state.operacoes["ID"] == operacao_id
        ].index[0]

        st.session_state.operacoes.loc[
            idx_real, "Data Compra"
        ] = editar_data

        st.session_state.operacoes.loc[
            idx_real, "Ticker"
        ] = editar_ticker

        st.session_state.operacoes.loc[
            idx_real, "Qtd"
        ] = editar_qtd

        st.session_state.operacoes.loc[
            idx_real, "Preço Compra"
        ] = editar_preco

        st.session_state.operacoes.loc[
            idx_real, "Alvo (3%)"
        ] = novo_alvo

        st.session_state.operacoes.loc[
            idx_real, "Estratégia"
        ] = editar_estrategia

        salvar_dados(st.session_state.operacoes)

        st.success("Operação atualizada!")
        st.rerun()

    # =====================================================
    # EXCLUIR
    # =====================================================

    with colb2:

        if st.button("🗑️ Excluir Operação"):

            st.session_state.operacoes = (
                st.session_state.operacoes[
                    st.session_state.operacoes["ID"] != operacao_id
                ]
            )

            salvar_dados(
                st.session_state.operacoes
            )

            st.success(
                "Operação excluída!"
            )

            st.rerun()

    # =====================================================
    # REGISTRAR VENDA
    # =====================================================

    if linha["Status"] == "Aberta":

        st.markdown("### 🏁 Registrar Venda")

        colv1, colv2 = st.columns(2)

        with colv1:

            data_venda = st.date_input(
                "Data Venda",
                datetime.now().date(),
                key="data_venda"
            )

        with colv2:

           preco_venda = st.number_input(
    f"Preço Venda (Compra: R$ {linha['Preço Compra']:.2f})",
    min_value=0.01,
    value=float(linha["Alvo (3%)"]),
    format="%.2f",
    key="preco_venda"
)

        if st.button("✅ Confirmar Venda"):

            idx_real = st.session_state.operacoes[
                st.session_state.operacoes["ID"] == operacao_id
            ].index[0]

            preco_compra = float(
                st.session_state.operacoes.loc[
                    idx_real,
                    "Preço Compra"
                ]
            )

            qtd = float(
                st.session_state.operacoes.loc[
                    idx_real,
                    "Qtd"
                ]
            )

            dt_compra = st.session_state.operacoes.loc[
                idx_real,
                "Data Compra"
            ]

            if isinstance(dt_compra, str):

                dt_compra = datetime.strptime(
                    dt_compra,
                    "%Y-%m-%d"
                ).date()

            duracao = (
                data_venda - dt_compra
            ).days

            resultado_pct = (
                (
                    preco_venda - preco_compra
                ) / preco_compra
            ) * 100

            resultado_rs = (
                preco_venda - preco_compra
            ) * qtd

            st.session_state.operacoes.loc[
                idx_real,
                "Preço Venda"
            ] = preco_venda

            st.session_state.operacoes.loc[
                idx_real,
                "Data Venda"
            ] = pd.Timestamp(data_venda)

            st.session_state.operacoes.loc[
                idx_real,
                "Duração (Dias)"
            ] = duracao

            st.session_state.operacoes.loc[
                idx_real,
                "Resultado %"
            ] = round(
                resultado_pct,
                2
            )

            st.session_state.operacoes.loc[
                idx_real,
                "Resultado R$"
            ] = round(
                resultado_rs,
                2
            )

            st.session_state.operacoes.loc[
                idx_real,
                "Status"
            ] = "Encerrada"

            salvar_dados(
                st.session_state.operacoes
            )

            st.success(
                "Venda registrada!"
            )

            st.rerun()

    else:

        st.success(
            "Operação já encerrada."
        )

else:

    st.info(
        "Nenhuma operação encontrada."
    )

# =========================================================
# ESTATÍSTICAS
# =========================================================

with st.expander(
    "📈 Estatísticas",
    expanded=False
):

    ops_encerradas = st.session_state.operacoes[
        st.session_state.operacoes["Status"] == "Encerrada"
    ]

    if not ops_encerradas.empty:

        resultado_total = ops_encerradas[
            "Resultado R$"
        ].fillna(0).sum()

        retorno_medio = ops_encerradas[
            "Resultado %"
        ].fillna(0).mean()

        st.write(
            f"💰 Resultado acumulado: "
            f"R$ {resultado_total:,.2f}"
        )

        st.write(
            f"📊 Retorno médio: "
            f"{retorno_medio:.2f}%"
        )

        resultado_pct_validos = ops_encerradas.dropna(
            subset=["Resultado %"]
        )

        if not resultado_pct_validos.empty:

            melhor_trade = resultado_pct_validos.loc[
                resultado_pct_validos[
                    "Resultado %"
                ].idxmax()
            ]

            pior_trade = resultado_pct_validos.loc[
                resultado_pct_validos[
                    "Resultado %"
                ].idxmin()
            ]

            st.write(
                f"🏆 Melhor ciclo: "
                f"{melhor_trade['Ticker']} "
                f"({melhor_trade['Resultado %']:.2f}%)"
            )

            st.write(
                f"📉 Pior ciclo: "
                f"{pior_trade['Ticker']} "
                f"({pior_trade['Resultado %']:.2f}%)"
            )

        st.divider()

        st.subheader("🏅 Ranking por Ticker")

        ranking = (
            ops_encerradas
            .groupby("Ticker")
            .agg({
                "Resultado R$": "sum",
                "Resultado %": "mean",
                "Duração (Dias)": "mean"
            })
            .rename(columns={
                "Resultado R$": "Lucro Total R$",
                "Resultado %": "Retorno Médio %",
                "Duração (Dias)": "Média Dias"
            })
            .sort_values(
                by="Lucro Total R$",
                ascending=False
            )
        )

        st.dataframe(
            ranking,
            use_container_width=True
        )

    else:

        st.info(
            "Ainda não existem operações encerradas."
        )
    operacao_id = st.selectbox(
        "Selecione uma operação",
        options=list(opcoes_operacoes.keys()),
        format_func=lambda x: opcoes_operacoes[x]
    )

    linha = df_ops[df_ops["ID"] == operacao_id].iloc[0]

    # =====================================================
    # DETALHES DA OPERAÇÃO
    # =====================================================

    st.info(
        f"""
📌 Ticker: {linha['Ticker']}

📅 Data Compra: {linha['Data Compra']}

📦 Quantidade: {linha['Qtd']}

💰 Preço Compra: R$ {float(linha['Preço Compra']):.2f}

🎯 Alvo: R$ {float(linha['Alvo (3%)']):.2f}

📊 Status: {linha['Status']}

🧠 Estratégia: {linha['Estratégia']}
"""
    )

    st.markdown("### ✏️ Editar Operação")

    col1, col2, col3 = st.columns(3)

    with col1:

        editar_data = st.date_input(
            "Data Compra",
            value=linha["Data Compra"],
            key="editar_data"
        )

        editar_ticker = st.text_input(
            "Ticker",
            value=linha["Ticker"],
            key="editar_ticker"
        ).upper()

    with col2:

        editar_qtd = st.number_input(
            "Quantidade",
            min_value=1,
            value=int(linha["Qtd"]) if pd.notnull(linha["Qtd"]) else 1,
            key="editar_qtd"
        )

        editar_preco = st.number_input(
            "Preço Compra",
            min_value=0.01,
            value=float(linha["Preço Compra"]) if pd.notnull(linha["Preço Compra"]) else 0.01,
            format="%.2f",
            key="editar_preco"
        )

    with col3:

        editar_estrategia = st.text_input(
            "Estratégia",
            value=str(linha["Estratégia"]),
            key="editar_estrategia"
        )

        novo_alvo = round(
            editar_preco * 1.03,
            2
        )

        st.info(
            f"🎯 Novo alvo: R$ {novo_alvo:.2f}"
        )

    colb1, colb2, colb3 = st.columns(3)
# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.subheader("⚙️ Utilidades")

csv = st.session_state.operacoes.to_csv(
    index=False
).encode("utf-8")

st.sidebar.download_button(
    "📥 Baixar Histórico CSV",
    csv,
    "historico_operacoes.csv",
    "text/csv"
)

st.sidebar.info(
    "Modelo operacional:\n\n"
    "• Gain alvo: 3%\n"
    "• Sem stop loss\n"
    "• Foco em ativos carregáveis\n"
    "• Controle por ciclos"
)
