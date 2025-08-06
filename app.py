import streamlit as st
import json
from datetime import datetime

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

    # ⚠️ Alerta de emergencia si se detecta el comportamiento 5 (suicidio)
    if "5" in resultados:
        st.error("🚨 **Si estás teniendo pensamientos suicidas, por favor busca ayuda inmediata.**")
        st.markdown("### 📞 Líneas de ayuda emocional:")
        for e in ayuda["emergencia"]:
            st.write(f"- **{e['nombre']}**: {e['telefono']} — [Web]({e['web']})")
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

    # --- Botones de navegación ---
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🔄 Regresar a la encuesta", key="restart_btn"):
            st.session_state.finalizado = False
            st.rerun()

    with col2:
        if st.button("🗑️ Reiniciar todo", key="clear_all"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
