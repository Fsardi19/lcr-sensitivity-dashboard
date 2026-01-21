import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Sensibilidad Nota Convertible | LCR",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1e293b 0%, #312e81 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .accent { color: #0ea5e9; }
    .accent2 { color: #8b5cf6; }
</style>
""", unsafe_allow_html=True)

# Constants
PRE_MONEY_CAP = 40_000_000
DESCUENTO = 0.20
TASA_INTERES = 0.06
PCT_ARLEN = 0.0160  # 1.60% cada uno
ARLEN_EN_LCR = 0.5232  # Arlen tiene 52.32% de LCR Corp
PCT_EFECTIVO_INICIAL = PCT_ARLEN * ARLEN_EN_LCR  # 0.84% efectivo

def format_currency(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:.0f}"

def format_pct(val):
    return f"{val*100:.2f}%"

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Sensibilidad Conversión Nota Convertible</h1>
    <p>Análisis para P-11 (Laura Escobar) y P-12 (Camilo Reyes) en LCR</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Note Terms
st.sidebar.header("⚙️ Términos de la Nota")
monto_nota = st.sidebar.number_input("Monto Total Nota (USD)",
                                      min_value=1_000_000,
                                      max_value=20_000_000,
                                      value=5_500_000,
                                      step=100_000,
                                      format="%d")

meses_interes = st.sidebar.slider("Meses desde Inversión",
                                   min_value=6,
                                   max_value=36,
                                   value=18)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Términos Fijos:**
- Pre-Money Cap: **$40M**
- Tasa Interés: **6% E.A.**
- Descuento: **20%**
""")

# Calculate interest
intereses = monto_nota * TASA_INTERES * (meses_interes / 12)
total_convertir = monto_nota + intereses

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Intereses Capitalizables ({meses_interes}m):** {format_currency(intereses)}

**Total a Convertir:** {format_currency(total_convertir)}
""")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Posición Actual P-11 & P-12")

    st.markdown("""
    | Persona | % en Arlen | Arlen en LCR | % Efectivo LCR |
    |---------|------------|--------------|----------------|
    | **P-11 (Laura)** | 1.60% | 52.32% | **0.84%** |
    | **P-12 (Camilo)** | 1.60% | 52.32% | **0.84%** |
    | **Combinado** | 3.20% | - | **1.68%** |
    """)

with col2:
    st.subheader("💰 Resumen Nota Convertible")

    c1, c2, c3 = st.columns(3)
    c1.metric("Principal", format_currency(monto_nota))
    c2.metric("Intereses", format_currency(intereses))
    c3.metric("Total", format_currency(total_convertir))

# Valuation slider
st.markdown("---")
st.subheader("🎯 Simulador de Valoración")

valoracion_ronda = st.slider(
    "Valoración LCR en Ronda de Conversión",
    min_value=20_000_000,
    max_value=70_000_000,
    value=55_000_000,
    step=1_000_000,
    format="$%d"
)

# Calculations
val_efectiva = min(valoracion_ronda, PRE_MONEY_CAP)
val_con_descuento = val_efectiva * (1 - DESCUENTO)
post_money = val_con_descuento + total_convertir
pct_nota = total_convertir / post_money
dilution_factor = 1 - pct_nota

pct_efectivo_antes = PCT_EFECTIVO_INICIAL
pct_efectivo_despues = PCT_EFECTIVO_INICIAL * dilution_factor

valor_antes = pct_efectivo_antes * valoracion_ronda
valor_despues = pct_efectivo_despues * (valoracion_ronda + total_convertir)
cambio_valor = valor_despues - valor_antes

# Display results
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Antes de Conversión")
    st.metric("Valoración LCR", format_currency(valoracion_ronda))
    st.metric("% P-11 + P-12 Efectivo", format_pct(pct_efectivo_antes * 2))
    st.metric("Valor Combinado", format_currency(valor_antes * 2))

with col2:
    st.markdown("### Después de Conversión")
    st.metric("Post-Money Valoración", format_currency(valoracion_ronda + total_convertir))
    st.metric("% P-11 + P-12 (Diluido)", format_pct(pct_efectivo_despues * 2),
              delta=f"{(pct_efectivo_despues - pct_efectivo_antes) * 2 * 100:.2f} pp")
    st.metric("Valor Combinado", format_currency(valor_despues * 2),
              delta=format_currency(cambio_valor * 2))

# Conversion details
st.markdown("---")
st.subheader("📐 Detalle del Cálculo")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Paso 1: Monto a Convertir**")
    st.markdown(f"""
    - Principal: {format_currency(monto_nota)}
    - Intereses ({meses_interes}m al 6%): {format_currency(intereses)}
    - **Total: {format_currency(total_convertir)}**
    """)

with col2:
    st.markdown("**Paso 2: Precio de Conversión**")
    cap_aplicado = "✓ CAP APLICADO" if valoracion_ronda > PRE_MONEY_CAP else ""
    st.markdown(f"""
    - Valoración Ronda: {format_currency(valoracion_ronda)}
    - Val Efectiva: {format_currency(val_efectiva)} {cap_aplicado}
    - Con Descuento 20%: **{format_currency(val_con_descuento)}**
    """)

st.markdown(f"""
**Paso 3: % Nota Holders**

% Nota = {format_currency(total_convertir)} / ({format_currency(val_con_descuento)} + {format_currency(total_convertir)}) = **{format_pct(pct_nota)}**
""")

# Sensitivity Table
st.markdown("---")
st.subheader("📊 Tabla de Sensibilidad Completa")

valoraciones = [20_000_000, 25_000_000, 30_000_000, 35_000_000, 40_000_000,
                45_000_000, 50_000_000, 55_000_000, 60_000_000, 65_000_000, 70_000_000]

sensitivity_data = []
for val in valoraciones:
    ve = min(val, PRE_MONEY_CAP)
    vd = ve * (1 - DESCUENTO)
    pm = vd + total_convertir
    pn = total_convertir / pm
    df = 1 - pn
    pe = PCT_EFECTIVO_INICIAL * df
    vf = pe * (val + total_convertir)

    sensitivity_data.append({
        "Valoración": format_currency(val),
        "Val Efectiva": format_currency(ve) + (" (Cap)" if val > PRE_MONEY_CAP else ""),
        "% Nota Holders": format_pct(pn),
        "% P-11+P-12": format_pct(pe * 2),
        "Valor P-11": format_currency(vf),
        "Valor P-12": format_currency(vf),
        "Combinado": format_currency(vf * 2)
    })

df_sensitivity = pd.DataFrame(sensitivity_data)
st.dataframe(df_sensitivity, use_container_width=True, hide_index=True)

# Serie A Section
st.markdown("---")
st.subheader("🚀 Serie A - Marzo 2027 (Proyección)")

col1, col2 = st.columns(2)

with col1:
    serie_a_valoracion = st.slider(
        "Valoración Pre-Money Serie A",
        min_value=40_000_000,
        max_value=150_000_000,
        value=80_000_000,
        step=5_000_000,
        format="$%d"
    )

    serie_a_monto = st.slider(
        "Monto a Levantar Serie A",
        min_value=10_000_000,
        max_value=15_000_000,
        value=12_000_000,
        step=500_000,
        format="$%d"
    )

# Serie A Calculations
serie_a_post_money = serie_a_valoracion + serie_a_monto
pct_nuevos = serie_a_monto / serie_a_post_money
serie_a_dilution = 1 - pct_nuevos
pct_post_nota = pct_efectivo_despues * 2
pct_post_serie_a = pct_post_nota * serie_a_dilution
valor_post_serie_a = pct_post_serie_a * serie_a_post_money

with col2:
    st.markdown("### Impacto Serie A")
    st.metric("% Post-Nota (antes Serie A)", format_pct(pct_post_nota))
    st.metric("% Nuevos Inversionistas", format_pct(pct_nuevos))
    st.metric("% P-11+P-12 Post Serie A", format_pct(pct_post_serie_a),
              delta=f"{(pct_post_serie_a - pct_post_nota) * 100:.2f} pp")
    st.metric("Valor Final P-11+P-12", format_currency(valor_post_serie_a),
              delta=format_currency(valor_post_serie_a - valor_antes * 2))

# Evolution waterfall chart
st.markdown("### Evolución de Participación")

fig = go.Figure(go.Waterfall(
    name="% Participación",
    orientation="v",
    x=["Inicial<br>(Hoy)", "Dilución<br>Nota", "Post-Nota<br>(2026)", "Dilución<br>Serie A", "Final<br>(Mar 2027)"],
    y=[PCT_EFECTIVO_INICIAL * 2 * 100,
       (pct_post_nota - PCT_EFECTIVO_INICIAL * 2) * 100,
       0,
       (pct_post_serie_a - pct_post_nota) * 100,
       0],
    measure=["absolute", "relative", "total", "relative", "total"],
    text=[f"{PCT_EFECTIVO_INICIAL * 2 * 100:.2f}%",
          f"{(pct_post_nota - PCT_EFECTIVO_INICIAL * 2) * 100:.2f}%",
          f"{pct_post_nota * 100:.2f}%",
          f"{(pct_post_serie_a - pct_post_nota) * 100:.2f}%",
          f"{pct_post_serie_a * 100:.2f}%"],
    textposition="outside",
    connector={"line": {"color": "#334155"}},
    increasing={"marker": {"color": "#10b981"}},
    decreasing={"marker": {"color": "#ef4444"}},
    totals={"marker": {"color": "#8b5cf6"}}
))

fig.update_layout(
    title="Evolución % P-11 + P-12",
    showlegend=False,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e2e8f0')
)

st.plotly_chart(fig, use_container_width=True)

# Evolution table
st.markdown("### Tabla de Evolución")

valor_inicial = PCT_EFECTIVO_INICIAL * 2 * valoracion_ronda
valor_post_nota = pct_post_nota * (valoracion_ronda + total_convertir)

evolution_data = [
    {
        "Etapa": "Inicial (Hoy)",
        "Fecha": "Ene 2026",
        "% P-11+P-12": format_pct(PCT_EFECTIVO_INICIAL * 2),
        "Valoración": format_currency(valoracion_ronda),
        "Valor USD": format_currency(valor_inicial),
        "Cambio": "-"
    },
    {
        "Etapa": "Post Conversión Nota",
        "Fecha": "2026",
        "% P-11+P-12": format_pct(pct_post_nota),
        "Valoración": format_currency(valoracion_ronda + total_convertir),
        "Valor USD": format_currency(valor_post_nota),
        "Cambio": format_currency(valor_post_nota - valor_inicial)
    },
    {
        "Etapa": "Post Serie A",
        "Fecha": "Mar 2027",
        "% P-11+P-12": format_pct(pct_post_serie_a),
        "Valoración": format_currency(serie_a_post_money),
        "Valor USD": format_currency(valor_post_serie_a),
        "Cambio": format_currency(valor_post_serie_a - valor_inicial)
    }
]

df_evolution = pd.DataFrame(evolution_data)
st.dataframe(df_evolution, use_container_width=True, hide_index=True)

# Conclusion
cambio_total = valor_post_serie_a - valor_inicial
if cambio_total >= 0:
    st.success(f"""
    **Conclusión:** A pesar de diluirse de {format_pct(PCT_EFECTIVO_INICIAL * 2)} a {format_pct(pct_post_serie_a)},
    el valor de P-11+P-12 aumentaría de {format_currency(valor_inicial)} a {format_currency(valor_post_serie_a)}
    (**+{format_currency(cambio_total)}**) gracias al aumento de valoración.
    """)
else:
    st.warning(f"""
    **Conclusión:** Con esta valoración, P-11+P-12 se diluirían de {format_pct(PCT_EFECTIVO_INICIAL * 2)} a {format_pct(pct_post_serie_a)},
    y su valor disminuiría de {format_currency(valor_inicial)} a {format_currency(valor_post_serie_a)}
    (**{format_currency(cambio_total)}**).
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem;">
    Dashboard Sensibilidad Nota Convertible | LCR | P-11 & P-12<br>
    Versión Streamlit 1.0
</div>
""", unsafe_allow_html=True)
