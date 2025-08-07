
import pandas as pd
import unicodedata
import itertools
import streamlit as st

# Levenshtein
def levenshtein(a, b):
    m, n = len(a), len(b)
    if abs(m - n) > 6:
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

# Jaccard com bigramas
def jaccard_bigrams(a, b):
    def bigramas(s):
        return set([s[i:i+2] for i in range(len(s) - 1)])
    a_bi = bigramas(a)
    b_bi = bigramas(b)
    inter = len(a_bi & b_bi)
    union = len(a_bi | b_bi)
    return inter / union if union != 0 else 0

# Normalizar nome
def normalizar(nome):
    nome = str(nome).strip().upper()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = nome.replace(" ", "")
    return nome

# Combinar heurísticas
def comparar_com_barra(nomes, limite_lev, limite_jaccard):
    pares_suspeitos = []
    total = len(nomes) * (len(nomes) - 1) // 2
    progresso = st.progress(0, text="Analisando pares de nomes...")
    count = 0

    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            a, b = nomes[i], nomes[j]
            lev = levenshtein(a, b)
            jac = jaccard_bigrams(a, b)
            if 0 < lev <= limite_lev and jac >= limite_jaccard:
                pares_suspeitos.append((a, b, lev, round(jac, 2)))
            count += 1
            if count % 100 == 0 or count == total:
                progresso.progress(count / total, text=f"Processando... ({count}/{total})")
    progresso.empty()
    return pares_suspeitos

# Interface
st.title("🔍 Verificador Inteligente de Duplicatas (Levenshtein + Jaccard)")

uploaded_file = st.file_uploader("Envie o arquivo Excel (.xlsx)", type="xlsx")
limite_lev = st.slider("Distância máxima de Levenshtein", 1, 6, 3)
limite_jaccard = st.slider("Similaridade mínima de Jaccard (bigrams)", 0.0, 1.0, 0.6, step=0.05)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Clientes Karita BLVD", skiprows=1)
        nomes_raw = df["nome"].dropna().unique().tolist()
        nomes = [normalizar(n) for n in nomes_raw]

        resultado = comparar_com_barra(nomes, limite_lev, limite_jaccard)
        df_result = pd.DataFrame(resultado, columns=["nome_1", "nome_2", "levenshtein", "jaccard"])

        st.success(f"{len(df_result)} possíveis duplicatas encontradas.")
        st.dataframe(df_result)

        csv = df_result.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar resultado CSV", csv, "duplicatas.csv", "text/csv")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
