# ==================================================
# LIBRERÍAS
# ==================================================
import pandas as pd
from dash import Dash, html, dcc
from dash import Input, Output
import plotly.graph_objects as go


# ==================================================
# PALETA COBOCE
# ==================================================
COBOCE = {
    "verde": "#006c40",
    "verde_claro": "#2FA66A",
    "verde_claro_2": "#007e47",
    "gris": "#6B6B6B",
    "gris_claro": "#F4F6F5",
    "gris_claro_2": "#9c9495",
    "ladrillo": "#b8190d",
    "azul": "#1f77b4"
}


# ==================================================
# CARGA DE DATOS
# ==================================================
df = pd.read_excel("Modelo 202509.xlsx", sheet_name="Dash")

df["fecha_dt"] = pd.to_datetime(df["fecha"], dayfirst=True)
df["año"] = df["fecha_dt"].dt.year
df["mes"] = df["fecha_dt"].dt.month

# Gestión industrial Abr–Mar
df["gestion_ind"] = df.apply(
    lambda x: x["año"] + 1 if x["mes"] >= 4 else x["año"], axis=1
)

orden_meses = [4,5,6,7,8,9,10,11,12,1,2,3]
nombres = {
    4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",
    10:"Oct",11:"Nov",12:"Dic",1:"Ene",2:"Feb",3:"Mar"
}

df["mes_nombre"] = df["mes"].map(nombres)
df["mes_orden"] = df["mes"].apply(lambda x: orden_meses.index(x))

COL_GASTOS = {
    "Administración": "gastos administracion",
    "Comercialización": "gastos comercializacion",
    "Otros": "otros gastos/ingresos",
    "Financieros": "gastos financieros",
    "Tributarios": "gastos tributarios"
}


# ==================================================
# APP
# ==================================================
app = Dash(__name__)

app.layout = html.Div(style={"backgroundColor": "white", "padding": "20px"}, children=[

    html.H1(
        "Dashboard – Desempeño Financiero",
        style={"textAlign": "center", "color": COBOCE["verde"]}
    ),

    # ---------------------------
    # FILTRO
    # ---------------------------
    html.Div([
        dcc.Dropdown(
            id="gestion",
            options=[
                {"label": str(g), "value": g}
                for g in sorted(df["gestion_ind"].unique(), reverse=True)
            ],
            value=int(df["gestion_ind"].max()),
            clearable=False
        )
    ], style={"width": "220px", "margin": "auto"}),

    html.Br(),

    # ===========================
    # KPIs
    # ===========================
    html.Div(style={
        "display": "flex",
        "justifyContent": "space-around",
        "marginBottom": "20px"
    }, children=[

        html.Div(id="kpi_ventas", style={
            "backgroundColor": COBOCE["gris_claro"],
            "padding": "10px",
            "borderRadius": "8px",
            "width": "20%",
            "textAlign": "center"
        }),

        html.Div(id="kpi_margen", style={
            "backgroundColor": COBOCE["gris_claro"],
            "padding": "10px",
            "borderRadius": "8px",
            "width": "20%",
            "textAlign": "center"
        }),

        html.Div(id="kpi_pct", style={
            "backgroundColor": COBOCE["gris_claro"],
            "padding": "10px",
            "borderRadius": "8px",
            "width": "20%",
            "textAlign": "center"
        }),
    ]),

    html.Hr(),

    # ===========================
    # VENTAS
    # ===========================
    dcc.Graph(id="ventas_mensuales"),

    html.Hr(),

    # ===========================
    # MÁRGENES + GASTOS (2 COLUMNAS)
    # ===========================
    html.Div(style={"display": "flex", "gap": "30px"}, children=[

        # ---------- MÁRGENES ----------
        html.Div(style={"width": "60%"}, children=[
            dcc.Graph(id="grafico_margenes")
        ]),

        # ---------- GASTOS ----------
        html.Div(style={"width": "40%"}, children=[
            dcc.Graph(id="grafico_gastos")
        ])
    ])
])


# ==================================================
# CALLBACK
# ==================================================
@app.callback(
    Output("kpi_ventas", "children"),
    Output("kpi_margen", "children"),
    Output("kpi_pct", "children"),
    Output("ventas_mensuales", "figure"),
    Output("grafico_margenes", "figure"),
    Output("grafico_gastos", "figure"),
    Input("gestion", "value")
)
def update_dashboard(gestion):

    df_act = df[df["gestion_ind"] == int(gestion)]
    df_prev = df[df["gestion_ind"] == int(gestion) - 1]

    # ===========================
    # KPIs
    # ===========================
    ventas = df_act["ventas"].sum() / 1_000_000
    margen_neto = df_act["margen neto"].sum() / 1_000_000
    pct = margen_neto / ventas * 100 if ventas else 0

    kpi_ventas = [
        html.Div("Ventas acumuladas", style={"fontSize": "13px"}),
        html.Div(f"{ventas:.1f} MM Bs", style={"fontSize": "26px", "fontWeight": "bold"})
    ]

    kpi_margen = [
        html.Div("Resultado neto", style={"fontSize": "13px"}),
        html.Div(f"{margen_neto:.1f} MM Bs", style={"fontSize": "26px", "fontWeight": "bold"})
    ]

    kpi_pct = [
        html.Div("Margen neto (%)", style={"fontSize": "13px"}),
        html.Div(f"{pct:.1f} %", style={
            "fontSize": "26px",
            "fontWeight": "bold",
            "color": COBOCE["verde"]
        })
    ]

    # ===========================
    # VENTAS
    # ===========================
    p_act = df_act.groupby(["mes_orden","mes_nombre"])["ventas"].sum().reset_index()
    p_prev = df_prev.groupby(["mes_orden","mes_nombre"])["ventas"].sum().reset_index()

    fig_ventas = go.Figure()
    fig_ventas.add_bar(
        x=p_prev["mes_nombre"],
        y=p_prev["ventas"]/1_000_000,
        name=str(int(gestion)-1),
        marker_color=COBOCE["gris_claro_2"]
    )
    fig_ventas.add_bar(
        x=p_act["mes_nombre"],
        y=p_act["ventas"]/1_000_000,
        name=str(gestion),
        marker_color=COBOCE["verde_claro_2"]
    )
    fig_ventas.update_layout(
        title="Ventas mensuales comparadas",
        barmode="group",
        template="simple_white",
        yaxis_title="Mill. Bs"
    )

    # ===========================
    # MÁRGENES – 3 LÍNEAS
    # ===========================
    m = (
        df_act
        .groupby(["mes_orden","mes_nombre"])
        .agg({
            "margen bruto":"sum",
            "margen operativo":"sum",
            "margen neto":"sum"
        })
        .reset_index()
    )

    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(
        x=m["mes_nombre"], y=m["margen bruto"]/1_000_000,
        mode="lines+markers", name="Margen bruto",
        line=dict(color=COBOCE["verde"])
    ))
    fig_m.add_trace(go.Scatter(
        x=m["mes_nombre"], y=m["margen operativo"]/1_000_000,
        mode="lines+markers", name="Margen operativo",
        line=dict(color=COBOCE["azul"])
    ))
    fig_m.add_trace(go.Scatter(
        x=m["mes_nombre"], y=m["margen neto"]/1_000_000,
        mode="lines+markers", name="Margen neto",
        line=dict(color=COBOCE["ladrillo"])
    ))

    fig_m.update_layout(
        title="Evolución mensual de márgenes",
        template="simple_white",
        yaxis_title="Mill. Bs",
        legend=dict(orientation="h", y=-0.25)
    )

    # ===========================
    # GASTOS – BARRAS HORIZONTALES
    # ===========================
    gastos = {
        k: df_act[v].sum()/1_000_000
        for k,v in COL_GASTOS.items()
    }

    fig_g = go.Figure()
    fig_g.add_bar(
        x=list(gastos.values()),
        y=list(gastos.keys()),
        orientation="h",
        marker_color=COBOCE["gris"],
        text=[f"{v:.1f} MM" for v in gastos.values()],
        textposition="outside"
    )

    fig_g.update_layout(
        title="Gastos acumulados por concepto",
        template="simple_white",
        xaxis_title="Mill. Bs"
    )

    return (
        kpi_ventas,
        kpi_margen,
        kpi_pct,
        fig_ventas,
        fig_m,
        fig_g
    )


# ==================================================
# SERVER
# ==================================================
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
