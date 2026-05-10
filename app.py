import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import uuid

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

def carregar_dados():

    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)

            if not df.empty:

                if "ID" not in df.columns:
                    df["ID"] = [str(uuid.uuid4())[:8] for _ in range(len(df))]

                df["Data Compra"] = pd.to_datetime(
                    df["Data Compra"]
                ).dt.date

                if "Data Venda" in df.columns:
                    df["Data Venda"] = pd.to_datetime(
                        df["Data Venda"],
                        errors="coerce"
                    ).dt.date

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
        }
    ]

    return pd.DataFrame(dados_iniciais)


def salvar_dados(df):
    try:
        backup_nome = f"backup_operacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if os.path.exists(DB_FILE):
            df.to_csv(backup_nome, index=False)

        df.to_csv(DB_FILE, index=False)

    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")


def calcular_dias_aberto(data_compra):
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

    duracoes_validas = ops_encerradas["Duração (Dias)"].dropna()

    if not duracoes_validas.empty:
        tempo_medio = round(duracoes_validas.mean(), 1)

# =========================================================
# RESUMO EXECUTIVO
# =========================================================

st.subheader("📌 Resumo Executivo")

col1, col2, col3, col4 = st.columns(4)

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
        "Tempo Médio até Venda",
        f"{tempo_medio} dias"
    )

with col4:
    st.metric(
        "Ciclos Concluídos",
        ciclos_concluidos
    )

# =========================================================
# ALERTA CAPITAL PARADO
# =========================================================

ops_lentas = []

for idx, row in ops_abertas.iterrows():

    dias = calcular_dias_aberto(row["Data Compra"])

    if dias > 45:
        ops_lentas.append(row["Ticker"])

if len(ops_lentas) > 0:
    st.warning(
        f"⚠️ {len(ops_lentas)} operação(ões) acima de 45 dias: "
        + ", ".join(ops_lentas)
    )

# =========================================================
# FORMULÁRIO NOVA OPERAÇÃO
# =========================================================

with st.expander("➕ Registrar Nova Operação", expanded=False):

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

        alvo = round(preco_compra * 1.03, 2)

        st.info(f"🎯 Alvo de Venda: R$ {alvo:.2f}")

    if st.button("Salvar Operação"):

        if ticker and estrategia_final:

            duplicada = (
                (df["Ticker"] == ticker) &
                (df["Status"] == "Aberta")
            ).any()

            if duplicada:
                st.warning(
                    "Já existe uma operação aberta para este ticker."
                )

            else:

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

                salvar_dados(st.session_state.operacoes)

                st.success(
                    f"Operação com {ticker} registrada!"
                )

                st.rerun()

        else:
            st.warning(
                "Preencha ticker e estratégia."
            )

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

            dias = calcular_dias_aberto(row["Data Compra"])

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

    colunas_exibir = [
        "Data Compra",
        "Ticker",
        "Qtd",
        "Preço Compra",
        "Alvo (3%)",
        "Estratégia",
        "Status",
        "Dias em Aberto",
        "Status Tempo"
    ]

    st.dataframe(
        tabela[colunas_exibir],
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
                (preco_venda - preco_compra)
                / preco_compra
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
            ] = round(resultado_pct, 2)

            st.session_state.operacoes.at[
                idx,
                "Resultado R$"
            ] = round(resultado_rs, 2)

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
    st.info("Nenhuma operação aberta.")

# =========================================================
# ABA ESTATÍSTICAS
# =========================================================

with st.expander("📈 Estatísticas", expanded=False):

    if not ops_encerradas.empty:

        resultado_total = ops_encerradas[
            "Resultado R$"
        ].sum()

        retorno_medio = ops_encerradas[
            "Resultado %"
        ].mean()

        melhor_trade = ops_encerradas.loc[
            ops_encerradas["Resultado %"].idxmax()
        ]

        pior_trade = ops_encerradas.loc[
            ops_encerradas["Resultado %"].idxmin()
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

        # =============================================
        # RANKING DE CICLOS
        # =============================================

        st.divider()

        st.subheader("🔄 Ranking de Ciclos por Ticker")

        ranking = (
            ops_encerradas
            .groupby("Ticker")
            .agg({
                "Ticker": "count",
                "Duração (Dias)": "mean",
                "Resultado %": "mean"
            })
            .rename(columns={
                "Ticker": "Ciclos",
                "Duração (Dias)": "Média Dias",
                "Resultado %": "Retorno Médio %"
            })
            .sort_values(
                by="Média Dias",
                ascending=True
            )
        )

        ranking["Média Dias"] = ranking[
            "Média Dias"
        ].round(1)

        ranking["Retorno Médio %"] = ranking[
            "Retorno Médio %"
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
# RECOMPRA RÁPIDA
# =========================================================

with st.expander("🔁 Recompra Rápida", expanded=False):

    if not ops_encerradas.empty:

        ultimas_encerradas = ops_encerradas.sort_values(
            by="Data Venda",
            ascending=False
        )

        opcoes_recompra = {
            idx: (
                f"{row['Ticker']} "
                f"(Última venda: {row['Data Venda']})"
            )
            for idx, row in ultimas_encerradas.iterrows()
        }

        idx_recompra = st.selectbox(
            "Escolha uma operação encerrada",
            options=list(opcoes_recompra.keys()),
            format_func=lambda x: opcoes_recompra[x]
        )

        if st.button("Criar Nova Operação Igual"):

            row = ultimas_encerradas.loc[idx_recompra]

            preco_compra = row["Preço Venda"]

            nova_op = {
                "ID": str(uuid.uuid4())[:8],
                "Data Compra": datetime.now().date(),
                "Ticker": row["Ticker"],
                "Qtd": row["Qtd"],
                "Preço Compra": preco_compra,
                "Alvo (3%)": round(preco_compra * 1.03, 2),
                "Estratégia": row["Estratégia"],
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
                f"Nova recompra criada para "
                f"{row['Ticker']}!"
            )

            st.rerun()

    else:
        st.info(
            "Nenhuma operação encerrada disponível."
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
