import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import uuid
import shutil

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Gerenciador de Operações Buy Side",
    layout="wide"
)

st.title("📊 Gerenciador de Operações - Buy Side")

DB_FILE = "operacoes.csv"

# =========================================================
# FUNÇÕES
# =========================================================

def garantir_colunas(df):

    colunas_necessarias = {
        "ID": "",
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


def carregar_dados():

    if os.path.exists(DB_FILE):

        try:

            df = pd.read_csv(DB_FILE)

            df = garantir_colunas(df)

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

            st.error(f"Erro ao carregar arquivo: {e}")

    # =====================================================
    # DADOS INICIAIS
    # =====================================================

    dados_iniciais = [

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 11).date(),
            "Ticker": "NVDC34",
            "Qtd": 5,
            "Preço Compra": 22.07,
            "Alvo (3%)": 22.73,
            "Estratégia": "SAZONALIDADE/bdrsetfspullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 11).date(),
            "Ticker": "KNSC11",
            "Qtd": 10,
            "Preço Compra": 9.17,
            "Alvo (3%)": 9.45,
            "Estratégia": "SAZONALIDADE",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 11).date(),
            "Ticker": "ITUB4",
            "Qtd": 2,
            "Preço Compra": 40.70,
            "Alvo (3%)": 41.92,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "CPFE3F",
            "Qtd": 2,
            "Preço Compra": 49.79,
            "Alvo (3%)": 51.27,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "ABEV3F",
            "Qtd": 6,
            "Preço Compra": 16.69,
            "Alvo (3%)": 17.18,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "AVGO34",
            "Qtd": 1,
            "Preço Compra": 30.60,
            "Alvo (3%)": 31.52,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "VIVT3F",
            "Qtd": 2,
            "Preço Compra": 39.77,
            "Alvo (3%)": 40.95,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "PETR4F",
            "Qtd": 2,
            "Preço Compra": 46.68,
            "Alvo (3%)": 48.06,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "SBSP3F",
            "Qtd": 3,
            "Preço Compra": 33.23,
            "Alvo (3%)": 34.23,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        },

        {
            "ID": str(uuid.uuid4())[:8],
            "Data Compra": datetime(2026, 5, 6).date(),
            "Ticker": "TIM3F",
            "Qtd": 4,
            "Preço Compra": 26.35,
            "Alvo (3%)": 27.13,
            "Estratégia": "auvppullback",
            "Preço Venda": None,
            "Data Venda": None,
            "Duração (Dias)": None,
            "Resultado %": None,
            "Resultado R$": None,
            "Status": "Aberta"
        }
    ]

    return pd.DataFrame(dados_iniciais)


def salvar_dados(df):

    try:

        # =================================================
        # BACKUP AUTOMÁTICO
        # =================================================

        if os.path.exists(DB_FILE):

            backup_dir = "backups"

            os.makedirs(
                backup_dir,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            backup_file = os.path.join(
                backup_dir,
                f"operacoes_backup_{timestamp}.csv"
            )

            shutil.copy(
                DB_FILE,
                backup_file
            )

        df.to_csv(
            DB_FILE,
            index=False
        )

    except Exception as e:

        st.error(f"Erro ao salvar dados: {e}")


def calcular_dias_aberto(data_compra):

    if pd.isnull(data_compra):
        return 0

    return (date.today() - data_compra).days


def classificar_tempo(dias):

    if dias <= 30:
        return "🟢 Saudável"

    elif dias <= 60:
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
        ops_abertas["Qtd"] *
        ops_abertas["Preço Compra"]
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
# ALERTAS
# =========================================================

ops_atencao = []
ops_criticas = []

for idx, row in ops_abertas.iterrows():

    dias = calcular_dias_aberto(
        row["Data Compra"]
    )

    if dias > 60:

        ops_criticas.append(
            row["Ticker"]
        )

    elif dias > 30:

        ops_atencao.append(
            row["Ticker"]
        )

if len(ops_atencao) > 0:

    st.warning(
        "🟡 Operações acima de 30 dias: "
        + ", ".join(ops_atencao)
    )

if len(ops_criticas) > 0:

    st.error(
        "🔴 Operações acima de 60 dias: "
        + ", ".join(ops_criticas)
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
                "Data Venda": None,
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

    if "Resultado R$" not in tabela.columns:
        tabela["Resultado R$"] = None

    tabela_exibir = tabela.copy()

    tabela_exibir["Resultado R$"] = tabela_exibir[
        "Resultado R$"
    ].apply(
        lambda x: (
            f"R$ {x:,.2f}"
            if pd.notnull(x)
            else "-"
        )
    )

    colunas_exibir = [
        "Data Compra",
        "Ticker",
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
# ENCERRAMENTO
# =========================================================

st.divider()

st.subheader("🏁 Registrar Venda")

ops_abertas = st.session_state.operacoes[
    st.session_state.operacoes["Status"] == "Aberta"
]

if not ops_abertas.empty:

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        opcoes = {
            idx: (
                f"{row['Ticker']} "
                f"(Compra: {row['Data Compra']})"
            )
            for idx, row in ops_abertas.iterrows()
        }

        id_op = st.selectbox(
            "Selecione a operação",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x]
        )

    with col2:

        data_venda = st.date_input(
            "Data da Venda",
            datetime.now().date()
        )

    with col3:

        preco_venda = st.number_input(
            "Preço de Venda",
            min_value=0.01,
            format="%.2f"
        )

    with col4:

        st.write("")
        st.write("")

        if st.button("Confirmar Venda"):

            idx = id_op

            preco_compra = st.session_state.operacoes.at[
                idx,
                "Preço Compra"
            ]

            qtd = st.session_state.operacoes.at[
                idx,
                "Qtd"
            ]

            dt_compra = st.session_state.operacoes.at[
                idx,
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

            st.session_state.operacoes.at[
                idx,
                "Preço Venda"
            ] = preco_venda

            st.session_state.operacoes.at[
                idx,
                "Data Venda"
            ] = data_venda

            st.session_state.operacoes.at[
                idx,
                "Duração (Dias)"
            ] = duracao

            st.session_state.operacoes.at[
                idx,
                "Resultado %"
            ] = round(
                resultado_pct,
                2
            )

            st.session_state.operacoes.at[
                idx,
                "Resultado R$"
            ] = round(
                resultado_rs,
                2
            )

            st.session_state.operacoes.at[
                idx,
                "Status"
            ] = "Encerrada"

            salvar_dados(
                st.session_state.operacoes
            )

            st.success(
                "Venda registrada com sucesso!"
            )

            st.rerun()

else:

    st.info(
        "Nenhuma operação aberta."
    )

# =========================================================
# ESTATÍSTICAS
# =========================================================

with st.expander(
    "📈 Estatísticas",
    expanded=False
):

    if not ops_encerradas.empty:

        resultado_total = ops_encerradas[
            "Resultado R$"
        ].fillna(0).sum()

        retorno_medio = ops_encerradas[
            "Resultado %"
        ].fillna(0).mean()

        melhor_trade = ops_encerradas.loc[
            ops_encerradas[
                "Resultado %"
            ].idxmax()
        ]

        pior_trade = ops_encerradas.loc[
            ops_encerradas[
                "Resultado %"
            ].idxmin()
        ]

        st.write(
            f"💰 Resultado acumulado: "
            f"R$ {resultado_total:,.2f}"
        )

        st.write(
            f"📊 Retorno médio: "
            f"{retorno_medio:.2f}%"
        )

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

        # =================================================
        # RANKING POR TICKER
        # =================================================

        st.divider()

        st.subheader(
            "🏆 Ranking de Eficiência"
        )

        ranking = (
            ops_encerradas
            .groupby("Ticker")
            .agg({
                "Ticker": "count",
                "Duração (Dias)": "mean",
                "Resultado R$": "sum"
            })
            .rename(columns={
                "Ticker": "Ciclos",
                "Duração (Dias)": "Média Dias",
                "Resultado R$": "Lucro Total"
            })
            .sort_values(
                by="Média Dias",
                ascending=True
            )
        )

        ranking["Média Dias"] = ranking[
            "Média Dias"
        ].round(1)

        ranking["Lucro Total"] = ranking[
            "Lucro Total"
        ].round(2)

        st.dataframe(
            ranking,
            use_container_width=True
        )

    else:

        st.info(
            "Ainda não existem operações encerradas."
        )

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
