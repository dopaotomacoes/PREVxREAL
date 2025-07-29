'''curl -s https://app.omie.com.br/api/v1/financas/caixa/ \
 -H 'Content-type: application/json' \
 -d '{"call":"ListarOrcamentos","param":[{"nAno":2024,"nMes":5}],"app_key":"#APP_KEY#","app_secret":"#APP_SECRET#"}'''

from credenciais import Config
import requests
import pandas as pd
from pandas import json_normalize
from credenciais import Config  # seu jeito original de pegar credenciais
import streamlit as st
import plotly.express as px
from datetime import datetime
import time

st.set_page_config(layout="wide")

unidades_servicos = [("pinheirinho", "cartao")]


def listar_orcamentos(localidade, servico, ano, mes, tentativas=3):
    app_keys = Config.get_app_keys(localidade, servico)
    if not app_keys:
        st.error(f"Credenciais não encontradas para {localidade} / {servico}")
        return pd.DataFrame()

    url = "https://app.omie.com.br/api/v1/financas/caixa/"
    payload = {
        "call": "ListarOrcamentos",
        "param": [{"nAno": ano, "nMes": mes}],
        "app_key": app_keys.app_key,
        "app_secret": app_keys.app_secret
    }

    for tentativa in range(1, tentativas + 1):
        time.sleep(4 * tentativa)  # delay progressivo

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            dados = response.json()
            if "faultcode" in dados and "8020" in dados["faultcode"]:
                st.warning(
                    f"Tentativa {tentativa}: outra requisição em execução para {localidade} / {servico}. Aguardando...")
                continue  # tenta novamente

            lista = dados.get("ListaOrcamentos", [])
            if lista:
                df = json_normalize(lista)
                df["ano"] = ano
                df["mes"] = str(mes).zfill(2)
                df["localidade"] = localidade
                df["servico"] = servico
                return df
            else:
                return pd.DataFrame()

        else:
            st.error(
                f"Erro {response.status_code} - {response.text} para {localidade} / {servico}")
            return pd.DataFrame()

    st.error(
        f"Erro: Limite de tentativas excedido para {localidade} / {servico}")
    return pd.DataFrame()


localidade = st.sidebar.selectbox(
    "Localidade", sorted(set([u[0] for u in unidades_servicos])))
servicos_disponiveis = sorted(
    set([u[1] for u in unidades_servicos if u[0] == localidade]))
servico = st.sidebar.selectbox("Serviço", servicos_disponiveis)

ano_atual = datetime.now().year
ano = st.sidebar.selectbox("Ano", list(
    range(2018, ano_atual + 1)), index=ano_atual-2018)
mes = st.sidebar.selectbox("Mês", list(range(1, 13)),
                           index=datetime.now().month-1)

# Botão para buscar dados

if st.sidebar.button("Buscar dados"):
    df = listar_orcamentos(localidade, servico, ano, mes)
    time.sleep(1)
    if df.empty:
        st.warning("Nenhum dado retornado para o filtro selecionado.")
    else:
        # Conversões de tipo
        df["ano"] = df["ano"].astype(str)
        df["mes"] = df["mes"].astype(str).str.zfill(2)
        df["localidade"] = df["localidade"].astype(str)
        df["servico"] = df["servico"].astype(str)
        df["cDesCateg"] = df["cDesCateg"].astype(str)
        df["nValorPrevisto"] = df["nValorPrevisto"].round(2).astype(float)
        df["nValorRealizado"] = df["nValorRealizado"].round(2).astype(float)
        df.rename(columns={"nValorPrevisto": "Previsto", "nValorRealizado": "Realizado" , "cDesCateg": "Categoria"}, inplace=True)
        


        # Filtrar só linhas com valores positivos
        df_filtrado = df[(df["Previsto"] > 0) | (df["Realizado"] > 0)]

        if not df_filtrado.empty:
            st.markdown("""
            # PREVISTOS X REALIZADOS  
            """)

            fig = px.bar(
                df_filtrado,
                y="Categoria",
                x=["Previsto", "Realizado"],
                barmode="group",
                text_auto=True,
                orientation="h",
                title=f"{servico} - {localidade} - {str(mes).zfill(2)}/{ano}"
            )

            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=40 * len(df),
                xaxis_title="Valor (R$)",
                yaxis_title="Categoria",
                margin=dict(l=20, r=20, t=40, b=20),
                title_font_size=20
            )

            

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Não há valores positivos para exibir no gráfico.")
            
