import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador de Ganancias", page_icon="🎯", layout="wide")

st.title("Simulador de Ganancias — Máquina de Premios 🎯")

# --- Escenarios ---
escenarios = {
    "Normal": dict(precio=10, jn=15, jp=80, jdia=150, cn=40, cp=200, com=30),
    "Pesimista": dict(precio=8, jn=20, jp=100, jdia=80, cn=40, cp=200, com=35),
    "Bueno": dict(precio=15, jn=12, jp=60, jdia=280, cn=40, cp=200, com=25),
}

escenario = st.radio("Escenario rápido", list(escenarios.keys()), horizontal=True)
vals = escenarios[escenario]

# --- Sidebar ---
st.sidebar.header("⚙️ Configuración")

precio   = st.sidebar.slider("Precio por jugada ($)",          5,   50,  vals["precio"])
jn       = st.sidebar.slider("Jugadas → premio normal",         5,   60,  vals["jn"])
jp       = st.sidebar.slider("Jugadas → premio premium",       20,  200, vals["jp"], step=5)
jdia     = st.sidebar.slider("Jugadas por día",                20,  500, vals["jdia"], step=10)
cn       = st.sidebar.slider("Costo premio normal ($)",        10,  200, vals["cn"], step=5)
cp       = st.sidebar.slider("Costo premio premium ($)",       50,  800, vals["cp"], step=10)
com      = st.sidebar.slider("Comisión tienda (%)",             0,   60,  vals["com"])

# --- Cálculos ---
pct         = com / 100
net_normal  = jn * precio * (1 - pct) - cn
net_premium = jp * precio * (1 - pct) - cp
gan_dia     = (jdia / jn) * net_normal + (jdia / jp) * net_premium
gan_mes     = gan_dia * 30

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Ganancia diaria",   f"${gan_dia:,.2f}")
k2.metric("📅 Ganancia mensual",  f"${gan_mes:,.2f}")
k3.metric("🎁 Premio normal",     f"${net_normal:,.2f}")
k4.metric("🏆 Premio premium",    f"${net_premium:,.2f}")

st.divider()

# --- Datos por día de la semana ---
dias  = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
mult  = [1.0,   1.0,   1.0,   1.1,   1.2,   1.4,   1.3]

brutos, costos_tot, netos, gan_final = [], [], [], []
for m in mult:
    jd     = jdia * m
    bruto  = jd * precio
    costo  = (jd / jn) * cn + (jd / jp) * cp + bruto * pct
    neto   = bruto * (1 - pct)
    gan    = (jd / jn) * net_normal + (jd / jp) * net_premium
    brutos.append(round(bruto, 2))
    costos_tot.append(round(costo, 2))
    netos.append(round(neto, 2))
    gan_final.append(round(gan, 2))

col1, col2 = st.columns(2)

# Gráfica de barras
with col1:
    st.subheader("Proyección semanal")
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Ingreso bruto",     x=dias, y=brutos,     marker_color="#97C459"))
    fig_bar.add_trace(go.Bar(name="Ganancia neta",     x=dias, y=gan_final,  marker_color="#3B6D11"))
    fig_bar.add_trace(go.Bar(name="Costos + comisión", x=dias, y=costos_tot, marker_color="#E24B4A"))
    fig_bar.update_layout(
        barmode="group", height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=10, b=0, l=0, r=0),
        yaxis_tickprefix="$",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Gráfica de líneas
with col2:
    st.subheader("Flujo por día")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(name="Ingreso bruto",     x=dias, y=brutos,    mode="lines+markers", line=dict(color="#185FA5", width=2), fill="tozeroy", fillcolor="rgba(24,95,165,0.08)"))
    fig_line.add_trace(go.Scatter(name="Neto (sin costos)", x=dias, y=netos,     mode="lines+markers", line=dict(color="#3B6D11", width=2)))
    fig_line.add_trace(go.Scatter(name="Ganancia final",    x=dias, y=gan_final, mode="lines+markers", line=dict(color="#639922", width=2), fill="tozeroy", fillcolor="rgba(99,153,34,0.08)"))
    fig_line.update_layout(
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=10, b=0, l=0, r=0),
        yaxis_tickprefix="$",
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- Tabla detalle ---
st.divider()
st.subheader("📋 Detalle por día")
df = pd.DataFrame({
    "Día":              dias,
    "Jugadas":          [round(jdia * m) for m in mult],
    "Ingreso bruto":    [f"${v:,.2f}" for v in brutos],
    "Costos + comisión":[f"${v:,.2f}" for v in costos_tot],
    "Ganancia":         [f"${v:,.2f}" for v in gan_final],
})
st.dataframe(df, use_container_width=True, hide_index=True)

# --- Exportar ---
st.divider()
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Exportar tabla como CSV", csv, "ganancias.csv", "text/csv")