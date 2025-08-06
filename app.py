import streamlit as st
import json
from datetime import datetime
from fpdf import FPDF

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

# --- Estado ---
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

    if st.button("📊 Mostrar Resultados"):
        st.session_state.finalizado = True
        st.rerun()

# --- Resultados ---
else:
    # Detectar comportamientos
    resultados = {}
    for pregunta_id, fue_si in st.session_state.respuestas.items():
        if fue_si and pregunta_id in evaluacion:
            for num in evaluacion[pregunta_id]:
                key = str(num)
                if key in comportamientos:
                    resultados[key] = comportamientos[key]

    # ⚠️ Alerta de emergencia si se detecta el comportamiento 5
    if "5" in resultados:
        st.error("🚨 **Si estás teniendo pensamientos suicidas, por favor busca ayuda inmediata.**")
        for e in ayuda["emergencia"]:
            st.write(f"📞 **{e['nombre']}**: {e['telefono']} — [Web]({e['web']})")
        st.stop()

    # Mostrar reporte
    st.header("📋 Tu Reporte Personalizado")

    if resultados:
        st.success(f"Se detectaron **{len(resultados)} comportamientos** clave.")

        for num, data in resultados.items():
            with st.expander(f"⚠️ {data['titulo']}"):
                st.markdown(f"**Descripción:** {data['descripcion']}")
                st.markdown(f"**Síntomas:** {data['sintomas']}")
                st.markdown(f"**Solución:** {data['solucion']}")

        # Recomendación
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
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Reporte Personalizado: ¿Por qué tienes deudas?", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(10)

        # Agregar comportamientos detectados
        if resultados:
            for num, data in resultados.items():
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, data["titulo"], ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, f"Descripción: {data['descripcion']}")
                pdf.multi_cell(0, 5, f"Síntomas: {data['sintomas']}")
                pdf.multi_cell(0, 5, f"Solución: {data['solucion']}")
                pdf.ln(4)
        else:
            pdf.multi_cell(0, 6, "No se detectaron comportamientos de riesgo significativos.")

        # Recomendación
        pdf.ln(8)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recomendación Final", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, recomendacion if resultados else "No se detectaron comportamientos de riesgo.")

        # Recursos
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recursos de Apoyo", ln=True)
        pdf.set_font("Arial", "", 10)
        for e in ayuda["emergencia"]:
            pdf.cell(0, 6, f"🚨 {e['nombre']}: {e['telefono']} - {e['web']}", ln=True)
        for f in ayuda["financiero"]:
            pdf.cell(0, 6, f"💼 {f['nombre']} ({f['pais']}): {f['web']}", ln=True)
        for t in ayuda["terapia"]:
            pdf.cell(0, 6, f"🧠 {t['nombre']}: {t['web']}", ln=True)

        # Generar PDF en memoria
        pdf_output = pdf.output(dest="S").encode("latin1")

        # Botón de descarga
        st.download_button(
            "💾 Descargar PDF",
            data=pdf_output,
            file_name=f"reporte_financiero_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

    # --- Recursos de ayuda ---
    st.markdown("---")
    st.markdown("### 🆘 Recursos de Apoyo")
    with st.expander("📞 Líneas de emergencia emocional"):
        for e in ayuda["emergencia"]:
            st.write(f"**{e['nombre']}**: {e['telefono']} — [Web]({e['web']})")

    with st.expander("💼 Asesoría financiera"):
        for f in ayuda["financiero"]:
            st.write(f"**{f['nombre']}** ({f['pais']}) — [Ir al sitio]({f['web']})")

    with st.expander("🧠 Terapia y salud mental"):
        for t in ayuda["terapia"]:
            st.write(f"**{t['nombre']}** — [Sitio web]({t['web']})")

    # --- Reiniciar test ---
    if st.button("🔄 Reiniciar Test"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
