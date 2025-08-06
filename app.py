import streamlit as st
import json
from datetime import datetime
from weasyprint import HTML
from jinja2 import Template
import os

# --- Configuración ---
st.set_page_config(page_title="Test: ¿Por qué tienes deudas?", layout="centered")

# --- Cargar datos ---
@st.cache_data
def cargar_datos():
    with open("comportamientos.json", "r", encoding="utf-8") as f:
        comportamientos = json.load(f)
    with open("preguntas.json", "r", encoding="utf-8") as f:
        preguntas = json.load(f)
    with open("evaluacion.json", "r", encoding="utf-8") as f:
        evaluacion = json.load(f)
    with open("ayuda.json", "r", encoding="utf-8") as f:
        ayuda = json.load(f)
    return comportamientos, preguntas, evaluacion, ayuda

comportamientos, preguntas, evaluacion, ayuda = cargar_datos()

# --- Estado de la app ---
if "respuestas" not in st.session_state:
    st.session_state.respuestas = {}
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False

# --- Título ---
st.title("🔍 Test: ¿Por qué tienes deudas y no logras salir?")
st.markdown("Responde con honestidad. Este test identifica comportamientos emocionales que podrían estar frenándote.")

# --- Cuestionario ---
if not st.session_state.finalizado:
    st.subheader("📌 Preguntas")

    for pregunta in preguntas:
        idx = str(pregunta["id"])
        respuesta = st.radio(
            pregunta["texto"],
            options=["No", "Sí"],
            key=f"q_{idx}",
            index=0
        )
        st.session_state.respuestas[idx] = (respuesta == "Sí")

    # Botón para resultados
    if st.button("📊 Mostrar Resultados"):
        st.session_state.finalizado = True
        st.rerun()

# --- Mostrar resultados ---
else:
    # Detectar comportamientos
    resultados = {}
    for pregunta_id, fue_si in st.session_state.respuestas.items():
        if fue_si and pregunta_id in evaluacion:
            for num in evaluacion[pregunta_id]:
                key = str(num)
                if key in comportamientos:
                    resultados[key] = comportamientos[key]

    # Alerta de emergencia si se detecta el comportamiento 5
    if "5" in resultados:
        st.error("🚨 **Si estás teniendo pensamientos suicidas, por favor busca ayuda inmediata.**")
        emergencia_list = "\n".join([f"- {e['nombre']}: {e['teléfono']} ({e['web']})" for e in ayuda["emergencia"]])
        st.markdown(f"""
        **Líneas de ayuda:**
        {emergencia_list}
        """)
        st.stop()

    # Mostrar reporte
    st.header("📋 Tu Reporte Personalizado")

    if resultados:
        st.success(f"Se detectaron **{len(resultados)} comportamientos** clave.")

        html_parts = ""
        for num, data in resultados.items():
            with st.expander(f"⚠️ {data['titulo']}"):
                st.markdown(f"**Descripción:** {data['descripcion']}")
                st.markdown(f"**Síntomas:** {data['sintomas']}")
                st.markdown(f"**Solución:** {data['solucion']}")

            # Agregar al HTML del PDF
            html_parts += f"""
            <div class="comportamiento">
                <h3>{data['titulo']}</h3>
                <p><strong>Descripción:</strong> {data['descripcion']}</p>
                <p><strong>Síntomas:</strong> {data['sintomas']}</p>
                <div class="solucion"><strong>Solución:</strong> {data['solucion']}</div>
            </div>
            """

        # Recomendación final
        if len(resultados) <= 2:
            recomendacion = "Estás en buen camino. Trabaja en los comportamientos detectados con pequeños pasos."
        elif len(resultados) <= 5:
            recomendacion = "Tienes varios patrones emocionales que afectan tu salud financiera. Considera apoyo profesional."
        else:
            recomendacion = "Tu relación con el dinero está fuertemente influenciada por emociones. Buscar ayuda es un acto de valentía."

        st.markdown("---")
        st.markdown("### 💡 Recomendación Final")
        st.markdown(recomendacion)

    else:
        st.balloons()
        st.markdown("### 🎉 ¡Felicidades!")
        st.markdown("No se detectaron comportamientos de riesgo. Tu relación con el dinero es consciente y equilibrada.")

    # --- Botón para descargar PDF ---
    if st.button("📥 Descargar Reporte en PDF"):
        fecha = datetime.now().strftime("%d/%m/%Y")
        emergencia = ", ".join([e["teléfono"] for e in ayuda["emergencia"][:1]])
        financiero_nombre = ayuda["financiero"][0]["nombre"]
        financiero_web = ayuda["financiero"][0]["web"]

        with open("reporte_template.html", "r", encoding="utf-8") as f:
            template_str = f.read()
        template = Template(template_str)

        html_final = template.render(
            fecha=fecha,
            comportamientos_html=html_parts if html_parts else "<p>No se detectaron comportamientos.</p>",
            recomendacion=recomendacion if resultados else "No se detectaron comportamientos de riesgo.",
            emergencia=emergencia,
            financiero_nombre=financiero_nombre,
            financiero_web=financiero_web
        )

        # Generar PDF
        pdf = HTML(string=html_final).write_pdf()

        st.download_button(
            "💾 Descargar PDF",
            data=pdf,
            file_name=f"reporte_financiero_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

    # --- Recursos de ayuda ---
    st.markdown("---")
    st.markdown("### 🆘 Recursos de Apoyo")
    with st.expander("📞 Líneas de emergencia emocional"):
        for e in ayuda["emergencia"]:
            st.write(f"**{e['nombre']}**: {e['teléfono']} — [Web]({e['web']})")

    with st.expander("💼 Asesoría financiera"):
        for f in ayuda["financiero"]:
            st.write(f"**{f['nombre']}** ({f['país']}) — [Ir al sitio]({f['web']})")

    with st.expander("🧠 Terapia y salud mental"):
        for t in ayuda["terapia"]:
            st.write(f"**{t['nombre']}** — [Sitio web]({t['web']})")

    # --- Reiniciar test ---
    if st.button("🔄 Reiniciar Test"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()