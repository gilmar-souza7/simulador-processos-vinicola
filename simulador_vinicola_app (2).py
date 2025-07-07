import streamlit as st
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go

# Título e descrição do app
st.set_page_config(page_title="Simulador de Vinícola", layout="centered")
st.title("🍷 Simulador de Produção de Vinho")
st.markdown("Este app simula as etapas básicas da produção de vinho, da recepção das uvas ao engarrafamento.")

st.header("🍇 1. Recepção das Uvas")
input_mode_uvas = st.radio("Modo de entrada - Uvas (kg):", ["Deslizador", "Entrada manual"], key="uvas")
if input_mode_uvas == "Deslizador":
    uvas_kg = st.slider("Quantidade de uvas recebidas (kg)", 1000, 20000, 15000)
else:
    uvas_kg = st.number_input("Digite a quantidade de uvas recebidas (kg)", min_value=100.0, max_value=50000.0, value=15000.0, step=100.0)

temperatura_uvas = st.slider("Temperatura das uvas (°C)", 10, 35, 25)

rendimento_mosto = 0.65
mosto_litros = uvas_kg * rendimento_mosto

st.metric("Mosto gerado (L)", f"{mosto_litros:.1f}")

st.header("🧪 2. Fermentação Alcoólica")
tipo_vinho = st.selectbox("Tipo de vinho", ["Tinto", "Branco"])
temperatura_fermentacao = 28 if tipo_vinho == "Tinto" else 16

input_mode_fermentacao = st.radio("Modo de entrada - Volume em fermentação (L):", ["Deslizador", "Entrada manual"], key="fermentacao")
if input_mode_fermentacao == "Deslizador":
    fermentacao_litros = st.slider("Volume em fermentação (L)", 1000, int(mosto_litros), int(mosto_litros * 0.9))
else:
    fermentacao_litros = st.number_input("Digite o volume em fermentação (L)", min_value=500.0, max_value=mosto_litros, value=mosto_litros * 0.9, step=100.0)

st.write(f"Fermentação a aproximadamente **{temperatura_fermentacao}°C**.")

# Simulação da fermentação
st.subheader("🔬 Simulação da Fermentação")
input_mode_acucar = st.radio("Modo de entrada - Açúcar (g/L):", ["Deslizador", "Entrada manual"], key="acucar")
if input_mode_acucar == "Deslizador":
    conc_acucar_inicial = st.slider("Concentração inicial de açúcar (g/L)", 150, 250, 200)
else:
    conc_acucar_inicial = st.number_input("Digite a concentração de açúcar (g/L)", min_value=100.0, max_value=300.0, value=200.0, step=10.0)

# Modelo cinético da fermentação

def modelo_fermentacao(y, t, μmax, Ks, Pmax, Yxs, Yps):
    X, S, P = y
    μ = μmax * S / (Ks + S) * (1 - P / Pmax)
    dXdt = μ * X
    dSdt = -(1 / Yxs) * dXdt
    dPdt = Yps * (-dSdt)
    return [dXdt, dSdt, dPdt]

# Parâmetros do modelo
μmax = 0.4
Ks = 1.0
Pmax = 80.0
Yxs = 0.5
Yps = 0.45

# Condições iniciais
y0 = [0.1, conc_acucar_inicial, 0.0]  # [X0, S0, P0]
t = np.linspace(0, 48, 300)

# Integração das equações diferenciais
resultado = odeint(modelo_fermentacao, y0, t, args=(μmax, Ks, Pmax, Yxs, Yps))
X, S, P = resultado.T

# Gráfico com Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=X, mode='lines', name='Biomassa (g/L)', line=dict(color='green')))
fig.add_trace(go.Scatter(x=t, y=S, mode='lines', name='Açúcar (g/L)', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=t, y=P, mode='lines', name='Etanol (g/L)', line=dict(color='purple')))

fig.update_layout(title='Simulação da Fermentação Alcoólica',
                  xaxis_title='Tempo (h)',
                  yaxis_title='Concentração (g/L)',
                  template='plotly_white',
                  width=800, height=500)

st.plotly_chart(fig)

st.header("🧼 3. Clarificação e Estabilização")
input_mode_perda = st.radio("Modo de entrada - Perda na estabilização (%):", ["Deslizador", "Entrada manual"], key="estabilizacao")
if input_mode_perda == "Deslizador":
    perda_estabilizacao = st.slider("Perda na estabilização (%)", 0, 10, 5)
else:
    perda_estabilizacao = st.number_input("Digite a perda (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

volume_pos_estabilizacao = fermentacao_litros * (1 - perda_estabilizacao / 100)

st.metric("Volume após estabilização (L)", f"{volume_pos_estabilizacao:.1f}")

st.header("🛢️ 4. Maturação")
maturacao_premium = st.checkbox("Linha Premium (maturação em barrica)")
volume_maturacao = volume_pos_estabilizacao * 0.3 if maturacao_premium else 0

st.write(f"Volume destinado à maturação: **{volume_maturacao:.1f} L**")

st.header("🍾 5. Engarrafamento")
volume_garrafa = st.selectbox("Volume por garrafa (L)", [0.375, 0.75, 1.5])
volume_engarrafado = volume_pos_estabilizacao - volume_maturacao
n_garrafas = int(volume_engarrafado / volume_garrafa)

st.metric("Garrafas produzidas", n_garrafas)

st.header("📦 6. Armazenamento Final")
temperatura_armazenamento = 15
volume_final = volume_engarrafado
st.write(f"Volume armazenado: **{volume_final:.1f} L** a **{temperatura_armazenamento}°C**")

# Resultado final
st.success(f"✅ Produção total: {n_garrafas} garrafas de {volume_garrafa} L")
