import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Encriptadora UMES Enigma", layout="wide")

# ESTILO
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; color: #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

st.title("Encriptador UMES Enigma")

# DEFINICIÓN DEL ALFABETO CON VALIDACIÓN
alfabeto_base = list("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ0123456789_.¡!:")
n = len(alfabeto_base)

if 'mapeo' not in st.session_state:
    st.session_state.mapeo = {char: i for i, char in enumerate(alfabeto_base)}

st.header("1. Configuración del Alfabeto")
with st.expander("Configurar Mapeo Manual"):
    cols = st.columns(6)
    temp_mapeo = {}
    duplicado = False
    valor_duplicado = None

    for i, char in enumerate(alfabeto_base):
        with cols[i % 6]:
            # Permitimos cualquier número, sin límite de n-1
            val = st.number_input(f"'{char}'", min_value=0,
                                  value=st.session_state.mapeo[char], 
                                  key=f"input_{char}")
            
            # Verificación de duplicados
            if val in temp_mapeo.values():
                duplicado = True
                valor_duplicado = val
            temp_mapeo[char] = val

    if duplicado:
        st.error(f"❌ Error: El valor **{valor_duplicado}** está repetido. Cada letra debe tener un número único.")
    else:
        st.session_state.mapeo = temp_mapeo
        st.success("✅ Mapeo único validado.")

# --- Solo procesar si el alfabeto es válido ---
if not duplicado:
    # CONFIGURACIÓN DE ROTORES
    st.header("2. Configuración de los Rotores")
    c1, c2, c3 = st.columns(3)
    with c1:
        s1 = st.number_input("Rotor 1 (Base)", value=100)
        with st.expander("Ver Matriz Base R1"):
            np.random.seed(s1); p_base = np.random.permutation(n)
            st.write(pd.DataFrame(np.eye(n)[p_base], columns=alfabeto_base, index=alfabeto_base))

    with c2:
        s2 = st.number_input("Rotor 2 (Base)", value=200)
        with st.expander("Ver Matriz Base R2"):
            np.random.seed(s2); p_base = np.random.permutation(n)
            st.write(pd.DataFrame(np.eye(n)[p_base], columns=alfabeto_base, index=alfabeto_base))

    with c3:
        s3 = st.number_input("Rotor 3 (Base)", value=300)
        with st.expander("Ver Matriz Base R3"):
            np.random.seed(s3); p_base = np.random.permutation(n)
            st.write(pd.DataFrame(np.eye(n)[p_base], columns=alfabeto_base, index=alfabeto_base))

    # ENCRIPTAR / DESENCRIPTAR 
    st.header("3. Procesamiento de Mensaje")
    modo = st.radio("Selecciona modo:", ["Encriptar", "Desencriptar"])
    texto_usuario = st.text_input("Ingresa el texto:").upper()

    def procesar(texto, modo_encriptar=True):
        res = ""
        pasos = []
        mapeo_inv = {v: k for k, v in st.session_state.mapeo.items()}
        
        for i, letra in enumerate(texto):
            if letra not in alfabeto_base: continue
            
            # Generar permutaciones del momento (Rotores girando)
            p = []
            for s, shift in zip([s1, s2, s3], [i, i//n, i//(n**2)]):
                np.random.seed(s + shift)
                p.append(np.random.permutation(n))
            
            if modo_encriptar:
                # Entrada -> Mapeo -> R1 -> R2 -> R3 -> Alfabeto
                v = st.session_state.mapeo[letra]
                # Aseguramos que el valor mapeado esté dentro del rango del rotor mediante módulo n
                idx_v = v % n 
                idx_v = p[2][p[1][p[0][idx_v]]] 
                letra_f = alfabeto_base[idx_v]
            else:
                # Alfabeto -> R3⁻¹ -> R2⁻¹ -> R1⁻¹ -> Mapeo Inverso
                idx_v = alfabeto_base.index(letra)
                idx_v = np.where(p[2] == idx_v)[0][0]
                idx_v = np.where(p[1] == idx_v)[0][0]
                idx_v = np.where(p[0] == idx_v)[0][0]
                
                # Para desencriptar, buscamos el valor original en el mapeo
                # Si el usuario usó números > n, usamos lógica de congruencia
                letra_f = mapeo_inv.get(idx_v, "?")
                
            res += letra_f
            pasos.append({"in": letra, "out": letra_f, "p": p})
        return res, pasos

    if texto_usuario:
        texto_usuario = texto_usuario.replace(" ", "_") #reemplazar espacios vacíos por guión
        resultado, detalle = procesar(texto_usuario, modo == "Encriptar")
        
        st.markdown(f"**Resultado:**")
        st.markdown(f'<p class="big-font">{resultado}</p>', unsafe_allow_html=True)

        # EXPLICACIÓN DE PASOS
        st.divider()
        st.subheader("Proceso de Encriptación")
        if detalle:
            idx = st.select_slider("Paso:", options=range(len(detalle)), format_func=lambda x: f"Letra {detalle[x]['in']}")
            d = detalle[idx]
            
            st.write(f"Para la letra **{d['in']}**, las matrices se generaron con configuración dinámica:")
            st.write(f"R1: {s1+idx} | R2: {s2+(idx//n)} | R3: {s3+(idx//(n**2))}")
            st.write(f"Nota: el R1 avanza cada vez un paso.")

            with st.expander("Ver matrices de este paso específico"):
                t1, t2, t3 = st.tabs(["Rotor 1", "Rotor 2", "Rotor 3"])
                with t1: st.dataframe(pd.DataFrame(np.eye(n)[d['p'][0]], alfabeto_base, alfabeto_base))
                with t2: st.dataframe(pd.DataFrame(np.eye(n)[d['p'][1]], alfabeto_base, alfabeto_base))
                with t3: st.dataframe(pd.DataFrame(np.eye(n)[d['p'][2]], alfabeto_base, alfabeto_base))
else:
    st.warning("⚠️ Configura el alfabeto con valores únicos para activar la máquina Enigma.")
