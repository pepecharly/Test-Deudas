import streamlit as st
import json
from datetime import datetime
from fpdf import FPDF
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

try:
    comportamientos, preguntas, evaluacion, ayuda = cargar_datos()
except FileNotFoundError as e:
    st.error(f"No se encontró el archivo: {e.filename}")
    st.stop()

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

    # --- Botones de acción ---
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("📥 Descargar Reporte en PDF", key="pdf_btn"):
            pdf = FPDF()
            pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("DejaVu", size=12)

            pdf.cell(0, 10, "Reporte Personalizado: ¿Por qué tienes deudas?", ln=True, align="C")
            pdf.set_font("DejaVu", size=10)
            pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
            pdf.ln(10)

            def split_text(text, max_width=180):
                words = text.split(' ')
                lines = []
                current_line = ""
                for word in words:
                    if len(word) > 30:
                        while len(word) > 30:
                            lines.append(word[:30])
                            word = word[30:]
                        if word:
                            current_line = word + " "
                    else:
                        test_line = current_line + word + " "
                        try:
                            if pdf.get_string_width(test_line) < max_width:
                                current_line = test_line
                            else:
                                lines.append(current_line)
                                current_line = word + " "
                        except:
                            lines.append(current_line)
                            current_line = word + " "
                if current_line.strip():
                    lines.append(current_line)
                return lines

            if resultados:
                for num, data in resultados.items():
                    pdf.set_font("DejaVu", size=12, style="B")
                    pdf.cell(0, 8, data["titulo"], ln=True)
                    pdf.set_font("DejaVu", size=10)
                    for line in split_text(f"Descripción: {data['descripcion']}"):
                        try:
                            pdf.cell(0, 5, line)
                            pdf.ln(5)
                        except:
                            pass
                    for line in split_text(f"Síntomas: {data['sintomas']}"):
                        try:
                            pdf.cell(0, 5, line)
                            pdf.ln(5)
                        except:
                            pass
                    for line in split_text(f"Solución: {data['solucion']}"):
                        try:
                            pdf.cell(0, 5, line)
                            pdf.ln(5)
                        except:
                            pass
                    pdf.ln(4)
            else:
                for line in split_text("No se detectaron comportamientos de riesgo significativos."):
                    try:
                        pdf.cell(0, 5, line)
                        pdf.ln(5)
                    except:
                        pass

            pdf.ln(8)
            pdf.set_font("DejaVu", size=12, style="B")
            pdf.cell(0, 10, "Recomendación Final", ln=True)
            pdf.set_font("DejaVu", size=10)
            rec_text = recomendacion if resultados else "No se detectaron comportamientos de riesgo."
            for line in split_text(rec_text):
                try:
                    pdf.cell(0, 5, line)
                    pdf.ln(5)
                except:
                    pass

            pdf.ln(10)
            pdf.set_font("DejaVu", size=12, style="B")
            pdf.cell(0, 10, "Recursos de Apoyo", ln=True)
            pdf.set_font("DejaVu", size=10)
            for e in ayuda["emergencia"]:
                text = f"🚨 {e['nombre']}: {e['telefono']} - {e['web']}"
                for line in split_text(text):
                    try:
                        pdf.cell(0, 6, line)
                        pdf.ln(6)
                    except:
                        pass
            for f in ayuda["financiero"]:
                text = f"💼 {f['nombre']} ({f['pais']}): {f['web']}"
                for line in split_text(text):
                    try:
                        pdf.cell(0, 6, line)
                        pdf.ln(6)
                    except:
                        pass
            for t in ayuda["terapia"]:
                text = f"🧠 {t['nombre']}: {t['web']}"
                for line in split_text(text):
                    try:
                        pdf.cell(0, 6, line)
                        pdf.ln(6)
                    except:
                        pass

            try:
                pdf_output = pdf.output(dest="S").encode("latin1")
            except Exception as e:
                st.error("No se pudo generar el PDF.")
                st.stop()

            st.download_button(
                "💾 Descargar PDF",
                data=pdf_output,
                file_name=f"reporte_financiero_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="download_pdf"
            )

    with col2:
        if st.button("🔄 Regresar a la encuesta", key="restart_btn"):
            st.session_state.finalizado = False
            st.rerun()

    # Reiniciar todo
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Reiniciar todo"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Recursos de ayuda
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
