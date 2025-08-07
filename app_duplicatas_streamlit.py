
import pandas as pd
import unicodedata
import itertools
import streamlit as st

# Levenshtein
def levenshtein(a, b):
    m, n = len(a), len(b)
    if abs(m - n) > 3:
        return max(m, n)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
    return dp[m][n]

def normalizar(nome):
    nome = str(nome).strip().upper()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    return nome

def comparar(nomes, limite):
    pares_suspeitos = []
    for a, b in itertools.combinations(nomes, 2):
        if abs(len(a) - len(b)) <= 2:
            d = levenshtein(a, b)
            if 0 < d <= limite:
                pares_suspeitos.append((a, b, d))
    return pares_suspeitos

st.title("Verificador de Duplicatas por Levenshtein")

uploaded_file = st.file_uploader("Envie o arquivo Excel (.xlsx)", type="xlsx")
limite = st.slider("Distância máxima", 1, 5, 2)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Clientes Karita BLVD", skiprows=1)
        nomes_raw = df["nome"].dropna().unique().tolist()
        nomes = [normalizar(n) for n in nomes_raw]

        st.text("Analisando possíveis duplicatas...")
        resultado = comparar(nomes, limite)
        df_result = pd.DataFrame(resultado, columns=["nome_1", "nome_2", "distancia"])

        st.success(f"{len(df_result)} pares encontrados.")
        st.dataframe(df_result)

        csv = df_result.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar resultado CSV", csv, "duplicatas.csv", "text/csv")

    except Exception as e:
        st.error(f"Erro: {e}")
