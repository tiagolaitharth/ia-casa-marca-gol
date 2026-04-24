import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

ARQUIVO = r'C:\Users\Pichau\OneDrive\BASE DE DADOS.xlsx'


def rodar_modelo():
    print("Lendo base...")
    df = pd.read_excel(ARQUIVO, header=9)

    df.columns = [c.strip() for c in df.columns]

    colunas_base = [
        'ODD CASA',
        'ODD FORA',
        'MÉDIA CHUTES NO GOL CASA',
        'MÉDIA GOL A FAVOR CASA',
        '% Marca Gol Casa',
        'MÉDIA GOLS CONTRA CASA',
        'MÉDIA GOLS CONTRA FORA',
        'MÉDIA GOLS TOTAL CASA',
        'MÉDIA GOLS TOTAL FORA'
    ]

    def limpar(v):
        try:
            return float(str(v).replace(',', '.'))
        except:
            return 0

    for c in colunas_base:
        df[c] = df[c].apply(limpar)

    # =========================
    # TARGET
    # =========================

    def extrair_alvo(placar):
        try:
            gols = int(str(placar).split('x')[0].strip())
            return 1 if gols > 0 else 0
        except:
            return None  # importante

    df['ALVO'] = df['Placar'].apply(extrair_alvo)

    # =========================
    # SEPARAÇÃO (CORREÇÃO)
    # =========================

    df_passado = df[df['Placar'] != "-"].copy()
    df_futuro = df[df['Placar'] == "-"].copy()

    # =========================
    # FEATURES
    # =========================

    for base in [df_passado, df_futuro]:
        base['FORCA_ATAQUE_CASA'] = base['MÉDIA GOL A FAVOR CASA'] * base['% Marca Gol Casa']
        base['FRAGILIDADE_DEFESA_FORA'] = base['MÉDIA GOLS CONTRA FORA']
        base['INDICE_GOL_CASA'] = base['FORCA_ATAQUE_CASA'] - base['FRAGILIDADE_DEFESA_FORA']
        base['JOGO_TRAVADO'] = base['MÉDIA GOLS TOTAL CASA'] + base['MÉDIA GOLS TOTAL FORA']
        base['PRESSAO_VISITANTE'] = 1 / base['ODD FORA']

    colunas = colunas_base + [
        'FORCA_ATAQUE_CASA',
        'FRAGILIDADE_DEFESA_FORA',
        'INDICE_GOL_CASA',
        'JOGO_TRAVADO',
        'PRESSAO_VISITANTE'
    ]

    # =========================
    # TREINO (SÓ PASSADO)
    # =========================

    X_train = df_passado[colunas].fillna(0)
    y_train = df_passado['ALVO']

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    print("Treinando modelo...")

    modelo = MLPClassifier(
        hidden_layer_sizes=(20, 10),
        max_iter=1500,
        random_state=42
    )

    modelo.fit(X_train_scaled, y_train)

    # =========================
    # PREVISÃO (TODOS)
    # =========================

    X_all = df[colunas].fillna(0)
    X_all_scaled = scaler.transform(X_all)

    df['Probabilidade'] = modelo.predict_proba(X_all_scaled)[:, 1]

    # =========================
    # RESULTADO FINAL
    # =========================

    df_resultado = df[[
        'Liga',
        'Data',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Probabilidade'
    ]]

    df_resultado.to_excel("resultado_modelo.xlsx", index=False)

    print("Arquivo gerado com sucesso!")


if __name__ == "__main__":
    rodar_modelo()