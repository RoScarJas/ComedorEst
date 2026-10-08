import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Control de Deudas - Comedor", layout="wide")
st.title("🍴 Control de Cuentas y Deudas - Comedor Estudiantil")

# Inicializar el estado de la aplicación para persistir datos en la sesión
# Guardamos una estructura de diccionario para cada estudiante: {'consumido': X, 'pagado': Y}
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
    st.subheader("👥 Registrar Estudiante")
    nuevo_estudiante = st.text_input("Nombre del Estudiante").strip()
    deuda_inicial = st.number_input("Deuda Inicial Pendiente ($)", min_value=0.0, value=0.0, step=1.0)
    if st.button("Registrar Estudiante"):
        if nuevo_estudiante:
            if nuevo_estudiante not in st.session_state.estudiantes:
                st.session_state.estudiantes[nuevo_estudiante] = {
                    "consumido": deuda_inicial,
                    "pagado": 0.0
                }
                st.success(f"Estudiante {nuevo_estudiante} registrado con deuda inicial de ${deuda_inicial:.2f}")
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
    st.header("💸 Registrar Consumo (Anotar a Cuenta/Deuda)")
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
            st.write(f"**Monto a sumar a la deuda:** ${total_cobrar:.2f}")
            
            submit_cobro = st.form_submit_button("Confirmar Venta / Consumo")
            
            if submit_cobro:
                st.session_state.estudiantes[estudiante_sel]["consumido"] += total_cobrar
                st.session_state.transacciones.append({
                    "Estudiante": estudiante_sel,
                    "Detalle": f"{producto_sel} (x{cantidad})",
                    "Monto ($)": total_cobrar,
                    "Tipo": "Consumo"
                })
                total_deuda = st.session_state.estudiantes[estudiante_sel]["consumido"] - st.session_state.estudiantes[estudiante_sel]["pagado"]
                st.success(f"¡Consumo anotado! Nueva deuda total de {estudiante_sel}: ${total_deuda:.2f}")
                st.rerun()

    st.header("💵 Registrar Pago (Abono a Cuenta)")
    if st.session_state.estudiantes:
        with st.form("form_pago"):
            estudiante_pago = st.selectbox("Selecciona Estudiante que Paga", list(st.session_state.estudiantes.keys()))
            monto_pago = st.number_input("Monto Pagado ($)", min_value=0.1, value=10.0, step=1.0)
            submit_pago = st.form_submit_button("Registrar Pago")
            
            if submit_pago:
                st.session_state.estudiantes[estudiante_pago]["pagado"] += monto_pago
                st.session_state.transacciones.append({
                    "Estudiante": estudiante_pago,
                    "Detalle": "Abono / Pago de Cuenta",
                    "Monto ($)": monto_pago,
                    "Tipo": "Pago"
                })
                total_deuda = st.session_state.estudiantes[estudiante_pago]["consumido"] - st.session_state.estudiantes[estudiante_pago]["pagado"]
                st.success(f"Pago registrado de ${monto_pago:.2f}. Deuda restante de {estudiante_pago}: ${total_deuda:.2f}")
                st.rerun()

with col2:
    st.header("📋 Estado de Cuentas")
    if st.session_state.estudiantes:
        datos_estudiantes = []
        for nombre, valores in st.session_state.estudiantes.items():
            deuda_total = valores["consumido"] - valores["pagado"]
            datos_estudiantes.append({
                "Estudiante": nombre,
                "Total Consumido ($)": valores["consumido"],
                "Total Pagado ($)": valores["pagado"],
                "Deuda Pendiente ($)": deuda_total
            })
        df_estudiantes = pd.DataFrame(datos_estudiantes)
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
    st.dataframe(df_trans.iloc[::-1], use_container_width=True)
else:
    st.info("No se han realizado transacciones aún.")
