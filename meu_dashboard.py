import streamlit as st
import pandas as pd

# ---------------------------------------------------------------
# Fase 1: Estrutura Básica e Otimização de Desempenho
# ---------------------------------------------------------------
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")
st.title('Dashboard de Vendas')


@st.cache_data
def carregar_dados():
    df = pd.read_csv('vendas.csv')
    df['Data'] = pd.to_datetime(df['Data'])
    return df


df = carregar_dados()

# ---------------------------------------------------------------
# Fase 2: Layout e Filtros Laterais (Interatividade)
# ---------------------------------------------------------------
st.sidebar.title('Filtros')

lista_de_categorias = sorted(df['Categoria'].unique())
categorias_selecionadas = st.sidebar.multiselect(
    'Selecione as Categorias',
    options=lista_de_categorias,
    default=lista_de_categorias
)

data_min, data_max = df['Data'].min(), df['Data'].max()
intervalo_datas = st.sidebar.date_input(
    'Período',
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

# Regra de ouro: usar o retorno do widget para filtrar o DataFrame
df_filtrado = df[df['Categoria'].isin(categorias_selecionadas)]

if isinstance(intervalo_datas, tuple) and len(intervalo_datas) == 2:
    inicio, fim = pd.to_datetime(intervalo_datas[0]), pd.to_datetime(intervalo_datas[1])
    df_filtrado = df_filtrado[(df_filtrado['Data'] >= inicio) & (df_filtrado['Data'] <= fim)]

# ---------------------------------------------------------------
# Fase 3: Métricas em Destaque e Visualização de Dados
# ---------------------------------------------------------------
col1, col2 = st.columns([1, 1])

receita_calculada = df_filtrado['Receita'].sum()
total_pedidos = len(df_filtrado)

with col1:
    st.metric(label='Receita Total', value=f"R$ {receita_calculada:,.2f}")

with col2:
    st.metric(label='Total de Pedidos', value=total_pedidos)

aba1, aba2 = st.tabs(['Evolução Mensal', 'Tabela de Dados'])

with aba1:
    if df_filtrado.empty:
        st.warning('Nenhum dado para os filtros selecionados.')
    else:
        dados_agrupados = (
            df_filtrado
            .set_index('Data')
            .resample('M')['Receita']
            .sum()
        )
        dados_agrupados.index = dados_agrupados.index.strftime('%Y-%m')
        st.area_chart(dados_agrupados)

with aba2:
    st.dataframe(df_filtrado, use_container_width=True)

    csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Baixar CSV filtrado',
        data=csv_export,
        file_name='vendas_filtrado.csv',
        mime='text/csv'
    )
