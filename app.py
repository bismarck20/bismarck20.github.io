# ==================================================
# LIBRERÍAS
# ==================================================
import pandas as pd
from dash import Dash, html, dcc, dash_table
from dash import Input, Output, State, callback_context
import plotly.graph_objects as go

# ==================================================
# PALETA COBOCE
# ==================================================
COBOCE = {
    "verde": "#006c40",
    "verde_claro": "#2FA66A",
    "verde_claro_2": "#007e47",
    "gris": "#6B6B6B",
    "gris_oscuro": "#404040",
    "gris_claro": "#F4F6F5",
    "gris_claro_2": "#9c9495",
    "ladrillo": "#b8190d",
    "blanco": "#ffffff",
    "azul_gris": "#4A6FA5"
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

orden_meses_fiscal = [4,5,6,7,8,9,10,11,12,1,2,3]
nombres = {
    4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",
    10:"Oct",11:"Nov",12:"Dic",1:"Ene",2:"Feb",3:"Mar"
}

df["mes_nombre"] = df["mes"].map(nombres)
df["mes_orden"] = df["mes"].apply(lambda x: orden_meses_fiscal.index(x))

# Columnas de gastos
COL_GASTOS = {
    "Administración": "gastos administracion",
    "Comercialización": "gastos comercializacion",
    "Otros": "otros gastos/ingresos",
    "Financieros": "gastos financieros",
    "Tributarios": "gastos tributarios"
}

# ==================================================
# APP & LAYOUT
# ==================================================
app = Dash(__name__)

app.layout = html.Div(style={"backgroundColor": "white", "fontFamily": "Segoe UI, sans-serif", "paddingBottom": "50px"}, children=[

    # ---------------------------
    # ENCABEZADO CON LOGO
    # ---------------------------
    html.Div(style={"position": "relative", "paddingTop": "20px", "height": "80px"}, children=[
        html.Img(
            src=app.get_asset_url("logotipo.png"),
            style={
                "height": "65px",
                "position": "absolute",
                "left": "40px",
                "top": "15px"
            }
        ),
        html.H1(
            "Dashboard – Desempeño Financiero",
            style={
                "textAlign": "center", 
                "color": COBOCE["verde"], 
                "margin": "0",
                "lineHeight": "65px"
            }
        ),
    ]),

    # ---------------------------
    # FILTRO GESTIÓN
    # ---------------------------
    html.Div([
        dcc.Dropdown(
            id="gestion",
            options=[
                {"label": str(g), "value": g}
                for g in sorted(df["gestion_ind"].unique(), reverse=True)
            ],
            value=int(df["gestion_ind"].max()),
            clearable=False,
            style={"fontSize": "18px"}
        )
    ], style={"width": "220px", "margin": "0 auto 20px auto"}),

    # ===========================
    # KPIs SUPERIORES
    # ===========================
    html.Div(
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "marginBottom": "30px",
            "maxWidth": "1400px",
            "margin": "0 auto 30px auto"
        },
        children=[
            html.Div(id="kpi_ventas", style={"backgroundColor": COBOCE["gris_claro"], "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),
            html.Div(id="kpi_costo", style={"backgroundColor": COBOCE["gris_claro"], "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),
            html.Div(id="kpi_bruto", style={"backgroundColor": COBOCE["gris_claro"], "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),
            html.Div(id="kpi_neto", style={"backgroundColor": COBOCE["gris_claro"], "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),
        ]
    ),

    html.Hr(style={"borderTop": "1px solid #eee"}),

    # ===========================
    # GRÁFICO 1: VENTAS MENSUALES
    # ===========================
    html.Div([
        dcc.Graph(id="ventas_mensuales")
    ], style={"maxWidth": "1500px", "margin": "auto"}),
    
    html.Hr(style={"borderTop": "1px solid #eee", "margin": "30px 0"}),

    # ===========================
    # SECCIÓN INFERIOR: TRES COLUMNAS (Horizontal)
    # ===========================
    html.Div(
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "maxWidth": "1550px",
            "margin": "auto",
            "justifyContent": "space-between",
            "alignItems": "flex-start"
        },
        children=[
            # --- COLUMNA 1: VENTAS HISTÓRICAS ---
            html.Div(
                style={"width": "25%", "paddingRight": "10px"},
                children=[
                    dcc.Graph(id="ventas_anuales")
                ]
            ),

            # --- COLUMNA 2: EVOLUCIÓN MÁRGENES ---
            html.Div(
                style={"width": "45%", "paddingRight": "10px"},
                children=[
                    html.H3("Evolución de Márgenes", 
                            style={"textAlign": "center", "color": COBOCE["gris_oscuro"], "fontSize": "16px", "marginBottom": "5px"}),
                    dcc.Graph(id="grafico_margenes")
                ]
            ),

            # --- COLUMNA 3: TABLA GASTOS ---
            html.Div(
                style={"width": "28%"},
                children=[
                    html.H3("Desglose de Gastos", style={"color": COBOCE["verde"], "fontSize": "16px", "textAlign": "center", "marginBottom": "10px"}),
                    
                    html.Button("← Volver", id="btn_volver", 
                                n_clicks=0, style={"display": "none", "marginBottom": "5px", "cursor": "pointer", "fontSize": "12px"}),

                    html.Div(
                        style={
                            "height": "300px",
                            "overflowY": "auto",
                            "border": "1px solid #ddd",
                            "borderRadius": "8px",
                            "backgroundColor": "white"
                        },
                        children=[
                            dash_table.DataTable(
                                id="tabla_gastos",
                                columns=[
                                    {"name": "Concepto", "id": "concepto"},
                                    {"name": "Monto", "id": "monto", "type": "numeric", "format": {"specifier": ",.2f"}},
                                    {"name": "% s/Ventas", "id": "pct_str"}
                                ],
                                style_cell={
                                    "padding": "8px", 
                                    "cursor": "pointer", 
                                    "fontSize": "12px", 
                                    "fontFamily": "Segoe UI",
                                    "textAlign": "left"
                                },
                                style_header={
                                    "fontWeight": "bold", 
                                    "backgroundColor": COBOCE["verde"], 
                                    "color": "white", 
                                    "textAlign": "center",
                                    "position": "sticky", "top": "0", "zIndex": "100",
                                    "fontSize": "12px"
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
                                style_as_list_view=True,
                                page_action="none"
                            )
                        ]
                    ),
                    html.Div(id="nivel_gastos", children="total", style={"display": "none"}),
                ]
            )
        ]
    )
])


# ==================================================
# CALLBACK PRINCIPAL
# ==================================================
@app.callback(
    Output("kpi_ventas", "children"),
    Output("kpi_costo", "children"),
    Output("kpi_bruto", "children"),
    Output("kpi_neto", "children"),
    Output("ventas_mensuales", "figure"),
    Output("ventas_anuales", "figure"),
    Output("grafico_margenes", "figure"),
    Output("tabla_gastos", "data"),
    Output("nivel_gastos", "children"),
    Output("btn_volver", "style"),
    Output("tabla_gastos", "active_cell"),
    Input("gestion", "value"),
    Input("tabla_gastos", "active_cell"),
    Input("btn_volver", "n_clicks"),
    State("nivel_gastos", "children")
)
def update_dashboard(gestion, active_cell, n_back, nivel):
    
    df_act = df[df["gestion_ind"] == int(gestion)].copy()
    df_prev = df[df["gestion_ind"] == int(gestion) - 1].copy()

    # ---------------------------
    # KPIs
    # ---------------------------
    ventas = df_act["ventas"].sum() / 1_000_000
    costo_v = df_act["costo de ventas"].sum() / 1_000_000
    pct_costo = (costo_v / ventas * 100) if ventas else 0
    margen_b = df_act["margen bruto"].sum() / 1_000_000
    pct_bruto = (margen_b / ventas * 100) if ventas else 0
    margen_n = df_act["margen neto"].sum() / 1_000_000
    pct_neto = (margen_n / ventas * 100) if ventas else 0

    kpi_ventas = [html.Div("Ventas Acumuladas", style={"fontSize": "14px", "color": COBOCE["gris"]}), html.Div(f"{ventas:.1f} MM Bs", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"})]
    kpi_costo = [html.Div("Costo de Ventas", style={"fontSize": "14px", "color": COBOCE["gris"]}), html.Div(f"{costo_v:.1f} MM Bs", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"}), html.Div(f"({pct_costo:.1f} % s/Ventas)", style={"fontSize": "13px", "fontWeight": "bold", "color": COBOCE["ladrillo"]})]
    kpi_bruto = [html.Div("Margen Bruto", style={"fontSize": "14px", "color": COBOCE["gris"]}), html.Div(f"{margen_b:.1f} MM Bs", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"}), html.Div(f"({pct_bruto:.1f} % s/Ventas)", style={"fontSize": "13px", "fontWeight": "bold", "color": COBOCE["azul_gris"]})]
    kpi_neto = [html.Div("Resultado Neto", style={"fontSize": "14px", "color": COBOCE["gris"]}), html.Div(f"{margen_n:.1f} MM Bs", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"}), html.Div(f"({pct_neto:.1f} % s/Ventas)", style={"fontSize": "13px", "fontWeight": "bold", "color": COBOCE["verde"]})]

    # ---------------------------
    # GRÁFICO HORIZONTAL: VENTAS HISTÓRICAS
    # ---------------------------
    df_anual = df.groupby("gestion_ind")["ventas"].sum().reset_index()
    df_anual["ventas_mm"] = df_anual["ventas"] / 1_000_000
    df_anual["variacion"] = df_anual["ventas"].pct_change() * 100
    
    gestiones_plot = [int(gestion)-2, int(gestion)-1, int(gestion)]
    df_anual_plot = df_anual[df_anual["gestion_ind"].isin(gestiones_plot)].copy()

    fig_anual = go.Figure()

    if not df_anual_plot.empty:
        y_vals = df_anual_plot["gestion_ind"].astype(str).tolist()
        x_vals = df_anual_plot["ventas_mm"].tolist()
        
        colores_bar = []
        textos_monto = []
        textos_var = []
        colores_var = []

        for idx, row in df_anual_plot.iterrows():
            g = int(row["gestion_ind"])
            val = row["ventas_mm"]
            var = row["variacion"]
            
            # Color Barra
            if g == int(gestion):
                colores_bar.append(COBOCE["verde"])
            else:
                colores_bar.append(COBOCE["gris_claro_2"])

            # Texto Monto (BLANCO)
            textos_monto.append(f"<b>{val:.1f} MM</b>")

            # Texto Variación
            if pd.isna(var):
                textos_var.append("")
                colores_var.append("black")
            else:
                simbolo = "▲" if var >= 0 else "▼"
                txt = f"{simbolo} {var:.1f}%"
                textos_var.append(f"<b>{txt}</b>")
                colores_var.append(COBOCE["verde_claro_2"] if var >= 0 else COBOCE["ladrillo"])

        # Barras
        fig_anual.add_trace(go.Bar(
            y=y_vals,
            x=x_vals,
            text=textos_monto,
            textposition="inside",
            textfont=dict(color="white"),
            marker_color=colores_bar,
            orientation='h',
            width=0.6,
            hoverinfo="x+y"
        ))

        # Texto Variación (Scatter invisible)
        fig_anual.add_trace(go.Scatter(
            y=y_vals,
            x=x_vals,
            text=textos_var,
            mode="text",
            textposition="middle right",
            textfont=dict(size=11, color=colores_var),
            hoverinfo="skip"
        ))

        max_val = max(x_vals) if x_vals else 0
        fig_anual.update_layout(
            title=dict(text="Ventas Históricas", font=dict(size=16, color=COBOCE["verde"])),
            template="simple_white",
            xaxis=dict(showgrid=False, showticklabels=False, range=[0, max_val * 1.35]),
            yaxis=dict(type='category', tickfont=dict(size=14, color="#333")),
            height=320,
            margin=dict(l=5, r=10, t=40, b=10),
            showlegend=False,
            bargap=0.4
        )
    else:
        fig_anual.update_layout(title="Sin datos", height=320)

    # ---------------------------
    # DATOS MENSUALES
    # ---------------------------
    df_act["precio_prom"] = df_act[["precio de venta (IP-40)", "precio de venta (IP-30)"]].mean(axis=1, skipna=True)
    df_prev["precio_prom"] = df_prev[["precio de venta (IP-40)", "precio de venta (IP-30)"]].mean(axis=1, skipna=True)

    g_act = df_act.groupby(["mes_orden", "mes_nombre"]).agg(
        ventas_mm=("ventas", lambda x: x.sum()/1_000_000),
        precio=("precio_prom", "mean"),
        m_bruto=("margen bruto", lambda x: x.sum()/1_000_000),
        m_oper=("margen operativo", lambda x: x.sum()/1_000_000),
        m_neto=("margen neto", lambda x: x.sum()/1_000_000),
    ).reset_index()

    g_prev = df_prev.groupby(["mes_orden", "mes_nombre"]).agg(
        ventas_mm=("ventas", lambda x: x.sum()/1_000_000)
    ).reset_index()

    esqueleto = pd.DataFrame({"mes_orden": range(12)})
    nombres_fiscal = [nombres[orden_meses_fiscal[i]] for i in range(12)]
    esqueleto["mes_nombre"] = nombres_fiscal

    p_act = pd.merge(esqueleto, g_act, on=["mes_orden", "mes_nombre"], how="left").fillna(0)
    p_prev = pd.merge(esqueleto, g_prev, on=["mes_orden", "mes_nombre"], how="left").fillna(0)

    def procesar_etiquetas(df_temp, gestion_objetivo):
        def calcular(row):
            idx = int(row["mes_orden"])
            año_real = gestion_objetivo - 1 if idx <= 8 else gestion_objetivo
            eje = f"{row['mes_nombre']}-{str(año_real)[-2:]}"
            return pd.Series([eje, eje])
        df_temp[["mes_label_eje", "label_tooltip"]] = df_temp.apply(calcular, axis=1)
        return df_temp

    p_act = procesar_etiquetas(p_act, int(gestion))
    p_prev = procesar_etiquetas(p_prev, int(gestion) - 1)
    p_prev["mes_label_eje"] = p_act["mes_label_eje"]

    p_act_plot = p_act[p_act["ventas_mm"] > 0].copy()

    # GRÁFICO VENTAS MENSUALES
    fig_ventas = go.Figure()
    fig_ventas.add_bar(
        x=p_prev["mes_label_eje"], y=p_prev["ventas_mm"],
        name=f"Ventas {int(gestion)-1}",
        marker_color=COBOCE["gris_claro_2"],
        text=p_prev["ventas_mm"], texttemplate="%{text:.1f} Mill.", textposition="outside",
        customdata=p_prev["label_tooltip"], hovertemplate="<b>%{customdata}</b><br>Ventas: Bs. %{y:.2f} Mill.<extra></extra>"
    )
    fig_ventas.add_bar(
        x=p_act["mes_label_eje"], y=p_act["ventas_mm"],
        name=f"Ventas {gestion}",
        marker_color=COBOCE["verde_claro_2"],
        text=p_act["ventas_mm"], texttemplate="%{text:.1f} Mill.", textposition="outside",
        customdata=p_act["label_tooltip"], hovertemplate="<b>%{customdata}</b><br>Ventas: Bs. %{y:.2f} Mill.<extra></extra>"
    )
    if not p_act_plot.empty:
        fig_ventas.add_trace(go.Scatter(
            x=p_act_plot["mes_label_eje"], y=p_act_plot["precio"],
            mode="lines+markers", name="Precio Promedio",
            line=dict(color=COBOCE["ladrillo"], width=3),
            marker=dict(size=8, line=dict(width=2, color='white')), 
            yaxis="y2", customdata=p_act_plot["label_tooltip"], hovertemplate="<b>%{customdata}</b><br>Precio: Bs. %{y:.2f}<extra></extra>"
        ))
    fig_ventas.update_layout(
        title=dict(text="Ventas Mensuales (MM Bs) vs Precio Promedio", font=dict(size=16, color=COBOCE["verde"])),
        template="simple_white", barmode="group",
        yaxis=dict(title="Ventas (MM Bs)", showgrid=True, gridcolor="#f0f0f0"),
        yaxis2=dict(title="Precio (Bs)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=-0.2), height=380, 
        margin=dict(l=40, r=40, t=50, b=50),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Segoe UI")
    )

    # GRÁFICO MÁRGENES
    fig_margenes = go.Figure()
    if not p_act_plot.empty:
        fig_margenes.add_trace(go.Scatter(
            x=p_act_plot["mes_label_eje"], y=p_act_plot["m_bruto"],
            mode="lines+markers", name="M. Bruto",
            line=dict(color=COBOCE["gris_oscuro"], width=2),
            marker=dict(size=6, line=dict(width=1, color='white')), 
            customdata=p_act_plot["label_tooltip"], hovertemplate="<b>%{customdata}</b><br>Bruto: %{y:.1f} M<extra></extra>"
        ))
        fig_margenes.add_trace(go.Scatter(
            x=p_act_plot["mes_label_eje"], y=p_act_plot["m_oper"],
            mode="lines+markers", name="M. Oper",
            line=dict(color=COBOCE["ladrillo"], width=2),
            marker=dict(size=6, line=dict(width=1, color='white')), 
            customdata=p_act_plot["label_tooltip"], hovertemplate="<b>%{customdata}</b><br>Oper: %{y:.1f} M<extra></extra>"
        ))
        fig_margenes.add_trace(go.Scatter(
            x=p_act_plot["mes_label_eje"], y=p_act_plot["m_neto"],
            mode="lines+markers+text", name="M. Neto",
            line=dict(color=COBOCE["verde"], width=3),
            marker=dict(size=8, line=dict(width=2, color='white')), 
            text=p_act_plot["m_neto"], texttemplate="<b>%{text:.1f}</b>", textposition="top center",
            textfont=dict(size=10), customdata=p_act_plot["label_tooltip"], hovertemplate="<b>%{customdata}</b><br>Neto: %{y:.1f} M<extra></extra>"
        ))
    fig_margenes.update_layout(
        template="simple_white",
        yaxis=dict(title="MM Bs", showgrid=True, gridcolor="#f0f0f0", zeroline=True, zerolinecolor="black"),
        legend=dict(orientation="h", y=1.1, font=dict(size=11)), height=320, 
        margin=dict(l=30, r=10, t=30, b=30),
        hovermode="x unified", hoverlabel=dict(bgcolor="white", font_size=12, font_family="Segoe UI")
    )

    # ---------------------------
    # TABLA + LÓGICA DE RETORNO (CORREGIDO)
    # ---------------------------
    total_gastos = df_act[list(COL_GASTOS.values())].sum().sum() / 1_000_000
    
    # IMPORTANTE: Definimos trigger aquí
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

    def calc_pct_str(monto_gasto):
        val = (monto_gasto / ventas * 100) if ventas else 0
        return f"{val:.1f}%"

    data_total = [{"concepto": "Total Gastos", "monto": total_gastos, "pct_str": calc_pct_str(total_gastos)}]
    detalle = [{"concepto": k, "monto": df_act[v].sum() / 1_000_000, "pct_str": calc_pct_str(df_act[v].sum() / 1_000_000)} for k, v in COL_GASTOS.items()]

    if trigger == "btn_volver":
        return kpi_ventas, kpi_costo, kpi_bruto, kpi_neto, fig_ventas, fig_anual, fig_margenes, data_total, "total", {"display": "none"}, None
    if trigger == "tabla_gastos" and nivel == "total" and active_cell:
        return kpi_ventas, kpi_costo, kpi_bruto, kpi_neto, fig_ventas, fig_anual, fig_margenes, detalle, "detalle", {"display": "inline-block", "marginBottom": "5px", "fontSize": "12px"}, None
    if nivel == "detalle":
        return kpi_ventas, kpi_costo, kpi_bruto, kpi_neto, fig_ventas, fig_anual, fig_margenes, detalle, "detalle", {"display": "inline-block", "marginBottom": "5px", "fontSize": "12px"}, None

    return kpi_ventas, kpi_costo, kpi_bruto, kpi_neto, fig_ventas, fig_anual, fig_margenes, data_total, "total", {"display": "none"}, None


# ==================================================
# SERVER
# ==================================================
server = app.server

if __name__ == "__main__":
    app.run(debug=True)