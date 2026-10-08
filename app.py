import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control de Créditos - Comedor", layout="wide")
st.title("🍴 Control de Créditos - Comedor Estudiantil")

# Inicializar el estado de la aplicación para persistir datos en la sesión
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = {}
if 'productos' not in st.session_state:
    st.session_state.productos = {
        "Almuerzo Completo": 3.50,
        "Desayuno": 2.00,
        "Bebida": 1.00,
        "Snack": 1.50
    }
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = []

# Sidebar para gestión de Estudiantes y Productos
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Sección Estudiantes
    st.subheader("👥 Agregar Estudiante")
    nuevo_estudiante = st.text_input("Nombre del Estudiante").strip()
    credito_inicial = st.number_input("Crédito Inicial ($)", min_value=0.0, value=10.0, step=1.0)
    if st.button("Registrar Estudiante"):
        if nuevo_estudiante:
            if nuevo_estudiante not in st.session_state.estudiantes:
                st.session_state.estudiantes[nuevo_estudiante] = credito_inicial
                st.success(f"Estudiante {nuevo_estudiante} registrado con ${credito_inicial:.2f}")
                st.rerun()
            else:
                st.error("El estudiante ya existe.")
        else:
            st.warning("Por favor, ingresa un nombre válido.")

    st.markdown("---")
    
    # Sección Productos
    st.subheader("🍔 Agregar/Actualizar Producto")
    nuevo_producto = st.text_input("Nombre del Producto").strip()
    precio_producto = st.number_input("Precio ($)", min_value=0.01, value=1.0, step=0.5)
    if st.button("Guardar Producto"):
        if nuevo_producto:
            st.session_state.productos[nuevo_producto] = precio_producto
            st.success(f"Producto {nuevo_producto} guardado a ${precio_producto:.2f}")
            st.rerun()
        else:
            st.warning("Por favor, ingresa un nombre de producto válido.")

# Layout Principal
col1, col2 = st.columns([1, 1])

with col1:
    st.header("💸 Registrar Consumo (Cobro de Crédito)")
    if not st.session_state.estudiantes:
        st.info("Registra estudiantes en el panel lateral para comenzar.")
    elif not st.session_state.productos:
        st.info("Registra productos con sus precios para poder cobrar.")
    else:
        with st.form("form_consumo"):
            estudiante_sel = st.selectbox("Selecciona Estudiante", list(st.session_state.estudiantes.keys()))
            producto_sel = st.selectbox("Selecciona Producto", list(st.session_state.productos.keys()))
            cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1)
            
            precio_unitario = st.session_state.productos[producto_sel]
            total_cobrar = precio_unitario * cantidad
            st.write(f"**Total a cobrar:** ${total_cobrar:.2f}")
            
            submit_cobro = st.form_submit_button("Confirmar Consumo")
            
            if submit_cobro:
                credito_actual = st.session_state.estudiantes[estudiante_sel]
                if credito_actual >= total_cobrar:
                    st.session_state.estudiantes[estudiante_sel] -= total_cobrar
                    st.session_state.transacciones.append({
                        "Estudiante": estudiante_sel,
                        "Producto": producto_sel,
                        "Cantidad": cantidad,
                        "Total ($)": total_cobrar,
                        "Tipo": "Consumo"
                    })
                    st.success(f"¡Consumo registrado! Nuevo saldo de {estudiante_sel}: ${st.session_state.estudiantes[estudiante_sel]:.2f}")
                    st.rerun()
                else:
                    st.error(f"Saldo insuficiente. Crédito actual de {estudiante_sel}: ${credito_actual:.2f}")

    st.header("💵 Recargar Crédito")
    if st.session_state.estudiantes:
        with st.form("form_recarga"):
            estudiante_recarga = st.selectbox("Selecciona Estudiante para Recarga", list(st.session_state.estudiantes.keys()))
            monto_recarga = st.number_input("Monto a Recargar ($)", min_value=0.5, value=5.0, step=1.0)
            submit_recarga = st.form_submit_button("Realizar Recarga")
            
            if submit_recarga:
                st.session_state.estudiantes[estudiante_recarga] += monto_recarga
                st.session_state.transacciones.append({
                    "Estudiante": estudiante_recarga,
                    "Producto": "Recarga de Saldo",
                    "Cantidad": 1,
                    "Total ($)": monto_recarga,
                    "Tipo": "Recarga"
                })
                st.success(f"Recarga exitosa. Nuevo saldo de {estudiante_recarga}: ${st.session_state.estudiantes[estudiante_recarga]:.2f}")
                st.rerun()

with col2:
    st.header("📋 Estado de Cuentas")
    if st.session_state.estudiantes:
        df_estudiantes = pd.DataFrame(list(st.session_state.estudiantes.items()), columns=["Estudiante", "Crédito Disponible ($)"])
        st.dataframe(df_estudiantes, use_container_width=True)
    else:
        st.write("No hay estudiantes registrados.")

    st.header("🏷️ Lista de Precios")
    df_productos = pd.DataFrame(list(st.session_state.productos.items()), columns=["Producto", "Precio ($)"])
    st.dataframe(df_productos, use_container_width=True)

# Mostrar Historial de Transacciones
st.header("📝 Historial de Transacciones Recientes")
if st.session_state.transacciones:
    df_trans = pd.DataFrame(st.session_state.transacciones)
    st.dataframe(df_trans.iloc[::-1], use_container_width=True) # Mostrar las más recientes primero
else:
    st.info("No se han realizado transacciones aún.")
