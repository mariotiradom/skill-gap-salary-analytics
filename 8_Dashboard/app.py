# Ejecutar:  pip install streamlit plotly pandas openpyxl  &&  streamlit run app.py
import pandas as pd, plotly.express as px, streamlit as st

st.set_page_config(page_title="Brechas formativas", layout="wide")
st.title("Analítica web: habilidades laborales y mallas universitarias")

@st.cache_data
def cargar():
    r = lambda f, **k: pd.read_csv(f, **k)
    of = pd.read_excel("ofertas_limpias_skills.xlsx")
    return (of, r("skill_influencia.csv"), r("skill_peso.csv"), r("icc_carrera.csv", index_col=0),
            r("cobertura_skill_carrera.csv", index_col=0), r("icc_curso.csv"), r("brechas.csv"),
            r("modelos_metricas.csv"), r("clusters.csv"), r("cluster_resumen.csv"))
of, inf, peso, icc, cov, icc_curso, brechas, met, cl, cl_res = cargar()

t1, t2, t3 = st.tabs(["Mercado laboral", "Diagnóstico curricular", "Modelos"])

with t1:
    c1, c2 = st.columns(2)
    n = c1.slider("Top N habilidades", 5, 40, 15)
    metrica = c1.selectbox("Ordenar por", ["I", "pagerank", "authority", "grado_ofertas"])
    top = inf.sort_values(metrica, ascending=False).head(n)
    c1.plotly_chart(px.bar(top, x=metrica, y="habilidad", orientation="h").update_yaxes(autorange="reversed"), use_container_width=True)
    sen = c2.multiselect("Seniority", sorted(of.seniority.dropna().unique()), default=None)
    d = of[of.sal_mid.notna() & (of.seniority.isin(sen) if sen else True)]
    c2.plotly_chart(px.histogram(d[d.sal_mid < d.sal_mid.quantile(0.98)], x="sal_mid", nbins=25,
                                 labels={"sal_mid": "Salario mensual (S/)"}, title="Distribución salarial"), use_container_width=True)
    st.subheader("Prima salarial por habilidad (S)")
    st.dataframe(peso.sort_values("S", ascending=False)[["habilidad", "prima", "S", "w"]], use_container_width=True)

with t2:
    st.plotly_chart(px.bar(icc.reset_index(), x="index", y="ICC", labels={"index": "Carrera"}, title="ICC por carrera"), use_container_width=True)
    k = st.selectbox("Carrera", icc.index)
    c1, c2 = st.columns(2)
    cc = icc_curso[icc_curso.carrera == k].sort_values("aporte", ascending=False)
    c1.subheader("Aporte por asignatura"); c1.dataframe(cc, use_container_width=True)
    c2.subheader("Brechas prioritarias (peso alto, sin cobertura)")
    c2.dataframe(brechas[brechas.carrera == k].head(15), use_container_width=True)
    topw = peso.sort_values("w", ascending=False).head(25).habilidad
    st.plotly_chart(px.imshow(cov.loc[topw], aspect="auto", color_continuous_scale="Blues",
                              title="Mapa de cobertura: top 25 habilidades por peso x carrera"), use_container_width=True)

with t3:
    st.subheader("Clasificación de bandas salariales")
    st.dataframe(met.round(3), use_container_width=True)
    st.subheader("Clustering de ofertas (K-Means ponderado por I)")
    st.plotly_chart(px.scatter(cl, x="pc1", y="pc2", color=cl.cluster.astype(str), hover_data=["titulo"]), use_container_width=True)
    st.dataframe(cl_res, use_container_width=True)
