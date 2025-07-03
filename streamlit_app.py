
import streamlit as st
import base64
from openai import OpenAI


# 👉 Configura tu API Key
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# 👉 Título de la app
st.title("Analizador de estantes y productos")

# 👉 Sube la imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Mostrar la imagen
    st.image(uploaded_file, caption='Imagen subida', use_container_width=True)

    # Convertir a base64
    bytes_data = uploaded_file.read()
    encoded_string = base64.b64encode(bytes_data).decode("utf-8")

    # Prompt
    prompt_text = (
        "Analiza la imagen y devuelve la siguiente información en este formato exacto, sin agregar comentarios adicionales.\n\n"
        "Número de estantes: __\n\n"
        "(de izquierda a derecha)\n"
        "Estante #1:\n"
        "- Número de filas por estante: [__, __, __, ...]\n"
        "(de arriba hacia abajo)\n"
        "Fila 1:\n"
        "- Porcentaje de llenado: __%\n"
        "- Productos principales aproximados o categorías generales: __\n"
        "Fila 2:\n"
        "- Porcentaje de llenado: __%\n"
        "- Productos principales aproximados o categorías generales: __\n"
        "(Repite para todas las filas)\n\n"
        "Porcentaje de llenado global aproximado: __%\n\n"
        "Estante #2:\n"
        "- Número de filas por estante: [__, __, __, ...]\n"
        "(de arriba hacia abajo)\n"
        "Fila 1:\n"
        "- Porcentaje de llenado: __%\n"
        "- Productos principales aproximados o categorías generales: __\n"
        "Fila 2:\n"
        "- Porcentaje de llenado: __%\n"
        "- Productos principales aproximados o categorías generales: __\n"
        "(Repite para todas las filas)\n\n"
        "Porcentaje de llenado global aproximado: __%\n\n"
        "(Repite para todos los estantes que se vean en la imagen).\n\n"
        "No agregues explicaciones adicionales, ni saludos, ni comentarios, tampoco marcas, precios ni datos sensibles. Usa solo este formato exacto."
    )

    # Botón para analizar
    if st.button("Analizar estantes"):
        with st.spinner("Analizando imagen..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}
                        ]
                    }
                ]
            )
            result = response.choices[0].message.content
            print("result>", result)

            # Procesar y formatear
            lines = result.strip().split("\n")
            st.header("📄 Análisis del estante")
            st.info(lines[0])  # Número de estantes

            estante_indices = [i for i, line in enumerate(lines) if line.startswith("Estante")]

            for idx, start in enumerate(estante_indices):
                end = estante_indices[idx + 1] if idx + 1 < len(estante_indices) else len(lines)
                estante_lines = lines[start:end]

                with st.expander(f"🟢 {estante_lines[0]}"):
                    st.write(estante_lines[1])  # Número de filas

                    fila_actual = ""
                    for l in estante_lines[2:]:
                        if l.startswith("Fila"):
                            if fila_actual:
                                st.success(fila_actual)
                            fila_actual = f"**{l}**\n"
                        elif l.startswith("- Porcentaje"):
                            fila_actual += f"• {l}\n"
                        elif l.startswith("- Productos"):
                            fila_actual += f"• {l}\n"
                    if fila_actual:
                        st.success(fila_actual)

            # Mostrar porcentaje global final
            for l in lines:
                if l.startswith("Porcentaje de llenado global"):
                    st.warning(l)
