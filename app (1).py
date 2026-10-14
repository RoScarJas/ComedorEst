import streamlit as st
import pandas as pd
from datetime import date
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de la página
st.set_page_config(page_title="Control de Deudas - Comedor", layout="wide")
st.title("🍴 Control de Cuentas y Deudas - Comedor Estudiantil")

# Inicializar el estado de la aplicación para persistir datos en la sesión
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = {}
if 'productos' not in st.session_state:
    st.session_state.productos = {
        "Almuerzo Completo": 2000.00,
        "Desayuno": 1200.00,
        "Bebida": 600.00,
        "Snack": 800.00
    }
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = []

# Función para generar PDF de adeudados
def generar_pdf_deudores(datos_estudiantes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo_style = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e3d59"),
        alignment=1 # Centrado
    )
    story.append(Paragraph("Reporte de Estudiantes Adeudados - Comedor", titulo_style))
    story.append(Spacer(1, 20))
    
    # Filtrar solo los que tienen deuda pendiente > 0
    deudores = [est for est in datos_estudiantes if est["Deuda Pendiente (₡)"] > 0]
    
    if len(deudores) == 0:
        story.append(Paragraph("No existen estudiantes con deudas pendientes actualmente.", styles['Normal']))
    else:
        # Encabezados de tabla
        tabla_datos = [["Estudiante", "Teléfono", "Consumido", "Pagado", "Deuda Pendiente"]]
        for d in deudores:
            tabla_datos.append([
                d["Estudiante"],
                d["Teléfono"],
                f"₡{d['Total Consumido (₡)']:,.2f}",
                f"₡{d['Total Pagado (₡)']:,.2f}",
                f"₡{d['Deuda Pendiente (₡)']:,.2f}"
            ])
        
        t = Table(tabla_datos, colWidths=[150, 100, 100, 100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3d59")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f5f5f5")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#dddddd")),
            ('FONTSIZE', (0,0), (-1,-1), 10),
        ]))
        story.append(t)
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# Sidebar para gestión de Estudiantes y Productos
with st.sidebar:
    st.header("⚙️ Configuración")

    # Sección Estudiantes
    st.subheader("👥 Registrar Estudiante")
    nuevo_estudiante = st.text_input("Nombre del Estudiante").strip()
    telefono_estudiante = st.text_input("Número de Teléfono (ej: 88887777)").strip()
    deuda_inicial = st.number_input("Deuda Inicial Pendiente (₡)", min_value=0.0, value=0.0, step=500.0)
    if st.button("Registrar Estudiante"):
        if nuevo_estudiante and telefono_estudiante:
            if nuevo_estudiante not in st.session_state.estudiantes:
                st.session_state.estudiantes[nuevo_estudiante] = {
                    "telefono": telefono_estudiante,
                    "consumido": deuda_inicial,
                    "pagado": 0.0
                }
                st.success(f"Estudiante {nuevo_estudiante} registrado con éxito.")
                st.rerun()
            else:
                st.error("El estudiante ya existe.")
        else:
            st.warning("Por favor, ingresa el nombre y el número de teléfono.")

    st.markdown("---")

    # Sección Productos
    st.subheader("🍔 Agregar/Actualizar Producto")
    nuevo_producto = st.text_input("Nombre del Producto").strip()
    precio_producto = st.number_input("Precio (₡)", min_value=1.0, value=1000.0, step=100.0)
    if st.button("Guardar Producto"):
        if nuevo_producto:
            st.session_state.productos[nuevo_producto] = precio_producto
            st.success(f"Producto {nuevo_producto} guardado a ₡{precio_producto:,.2f}")
            st.rerun()
        else:
            st.warning("Por favor, ingresa un nombre de producto válido.")

# Layout Principal
col1, col2 = st.columns([1, 1])

with col1:
    st.header("💸 Registrar Consumo (Anotar a Cuenta)")
    if not st.session_state.estudiantes:
        st.info("Registra estudiantes en el panel lateral para comenzar.")
    elif not st.session_state.productos:
        st.info("Registra productos con sus precios para poder cobrar.")
    else: 
        with st.form("form_consumo"):
            estudiante_sel = st.selectbox("Selecciona Estudiante", list(st.session_state.estudiantes.keys()))
            producto_sel = st.selectbox("Selecciona Producto", list(st.session_state.productos.keys()))
            cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1)
            
            # Selección de fecha del consumo
            fecha_consumo = st.date_input("Fecha del Reporte", value=date.today())

            precio_unitario = st.session_state.productos[producto_sel]
            total_cobrar = precio_unitario * cantidad
            st.write(f"**Monto a sumar a la deuda:** ₡{total_cobrar:,.2f}")

            submit_cobro = st.form_submit_button("Confirmar Venta / Consumo")

            if submit_cobro:
                st.session_state.estudiantes[estudiante_sel]["consumido"] += total_cobrar
                st.session_state.transacciones.append({
                    "Fecha": fecha_consumo.strftime("%Y-%m-%d"),
                    "Estudiante": estudiante_sel,
                    "Detalle": f"{producto_sel} (x{cantidad})",
                    "Monto (₡)": total_cobrar,
                    "Tipo": "Consumo"
                })
                total_deuda = st.session_state.estudiantes[estudiante_sel]["consumido"] - st.session_state.estudiantes[estudiante_sel]["pagado"]
                st.success(f"¡Consumo anotado! Nueva deuda total de {estudiante_sel}: ₡{total_deuda:,.2f}")
                st.rerun()

    st.header("💵 Registrar Pago (Abono a Cuenta)")
    if st.session_state.estudiantes:
        with st.form("form_pago"):
            estudiante_pago = st.selectbox("Selecciona Estudiante que Paga", list(st.session_state.estudiantes.keys()))
            monto_pago = st.number_input("Monto Pagado (₡)", min_value=1.0, value=1000.0, step=500.0)
            fecha_pago = st.date_input("Fecha del Pago", value=date.today())
            submit_pago = st.form_submit_button("Registrar Pago")

            if submit_pago:
                st.session_state.estudiantes[estudiante_pago]["pagado"] += monto_pago
                st.session_state.transacciones.append({
                    "Fecha": fecha_pago.strftime("%Y-%m-%d"),
                    "Estudiante": estudiante_pago,
                    "Detalle": "Abono / Pago de Cuenta",
                    "Monto (₡)": monto_pago,
                    "Tipo": "Pago"
                })
                total_deuda = st.session_state.estudiantes[estudiante_pago]["consumido"] - st.session_state.estudiantes[estudiante_pago]["pagado"]
                st.success(f"Pago registrado de ₡{monto_pago:,.2f}. Deuda restante de {estudiante_pago}: ₡{total_deuda:,.2f}")
                st.rerun()

with col2:
    st.header("📋 Estado de Cuentas")
    datos_estudiantes = []
    if st.session_state.estudiantes:
        for nombre, valores in st.session_state.estudiantes.items():
            deuda_total = valores["consumido"] - valores["pagado"]
            datos_estudiantes.append({
                "Estudiante": nombre,
                "Teléfono": valores.get("telefono", "No registrado"),
                "Total Consumido (₡)": valores["consumido"],
                "Total Pagado (₡)": valores["pagado"],
                "Deuda Pendiente (₡)": deuda_total
            })
        df_estudiantes = pd.DataFrame(datos_estudiantes)
        st.dataframe(df_estudiantes.style.format({
            "Total Consumido (₡)": "₡{:,.2f}",
            "Total Pagado (₡)": "₡{:,.2f}",
            "Deuda Pendiente (₡)": "₡{:,.2f}"
        }), use_container_width=True)
        
        # Botón para descargar reporte de deudores en PDF
        pdf_data = generar_pdf_deudores(datos_estudiantes)
        st.download_button(
            label="📥 Descargar Deudores en PDF",
            data=pdf_data,
            file_name=f"reporte_adeudados_{date.today().strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )
    else:
        st.write("No hay estudiantes registrados.")

    st.header("🏷️ Lista de Precios")
    df_productos = pd.DataFrame(list(st.session_state.productos.items()), columns=["Producto", "Precio (₡)"])
    st.dataframe(df_productos.style.format({"Precio (₡)": "₡{:,.2f}"}), use_container_width=True)

# Mostrar Historial de Transacciones
st.header("📝 Historial de Transacciones Recientes")
if st.session_state.transacciones:
    df_trans = pd.DataFrame(st.session_state.transacciones)
    # Mostrar columnas en orden óptimo
    columnas_ordenadas = ["Fecha", "Estudiante", "Detalle", "Monto (₡)", "Tipo"]
    df_trans = df_trans[columnas_ordenadas]
    st.dataframe(df_trans.iloc[::-1].style.format({"Monto (₡)": "₡{:,.2f}"}), use_container_width=True)
else:
    st.info("No se han realizado transacciones aún.")
