import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import matplotlib.pyplot as plt #Visualizacion grafica
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Se usa para integrar matplotlib en tkinter
import tkinter as tk # Para construir la interfaz
from tkinter import ttk, messagebox

# Función para realizar web scraping
def scrap(año, mes, tipo_cotizacion):
    # Construir la URL basado en el tipo de cotización
    if tipo_cotizacion == 'blue':
        url = 'https://www.cotizacion-dolar.com.ar/dolar-blue-historico-' + str(año) + '.php'
    elif tipo_cotizacion == 'oficial':
        url = 'https://www.cotizacion-dolar.com.ar/dolar-historico-' + str(año) + '.php'
    else:
        raise ValueError("Tipo de cotización no válido")

    # Intentar obtener la página web para cada día del mes
    for i in range(1, 7):
        try:        
            fecha = datetime.datetime(año, mes, i)
            data = {'fecha': fecha.strftime('%d-%m-%y')}
            resp = requests.post(url, data=data)
            soup = BeautifulSoup(resp.text, "html.parser")
            break
        except:
            print('Falló en ', i)

    # Encontrar las filas de datos en la página
    filas = soup.find_all('td', {'style': 'padding: 1%'})
    return filas

# Función para procesar los datos obtenidos
def parsear(filas):
    mensual = pd.DataFrame() 
    for i in range(1, int(len(list(filas))/3)):
        dic = {}
        # Extrae los valores
        dic['fecha'] = filas[3*i].text
        dic['bid'] = filas[3*i+1].text
        dic['ask'] = filas[3*i+2].text
        rueda = pd.DataFrame.from_dict(dic, orient='index').transpose().set_index('fecha')
        rueda.index = pd.to_datetime(rueda.index, format='%d-%m-%y ')
        mensual = pd.concat([mensual,rueda], axis=0)
    return mensual

# Función para descargar datos de todo un año
def downloadAño(año, num_cotizaciones, tipo_cotizacion):
    tablaAnual = pd.DataFrame()
    for i in range(1, 13):
         # Obtiene las filas de datos para el mes actual
        filas = scrap(año=año, mes=i, tipo_cotizacion=tipo_cotizacion)
        # Procesa los datos y los agrega a la tabla anual
        tabla = parsear(filas)
        tablaAnual = pd.concat([tablaAnual, tabla], axis=0)
        print('mes', i, 'listo')
    
    # Mostrar el gráfico con los datos descargados
    mostrar_grafico(tablaAnual, num_cotizaciones, año, tipo_cotizacion)

# Función para mostrar el gráfico
def mostrar_grafico(tablaAnual, num_cotizaciones, año, tipo_cotizacion):
    tablaAnual = tablaAnual.tail(num_cotizaciones)  # Selecciona la cantidad de cotizaciones ingresada
    # Crea una figura y ejes para el gráfico
    fig, ax = plt.subplots(figsize=(13, 9))
    # Agrega líneas al gráfico para los valores de compra y venta
    ax.plot(tablaAnual.index, tablaAnual['bid'], label='Compra')
    ax.plot(tablaAnual.index, tablaAnual['ask'], label='Venta')

    # CConfiguracion del título, etiquetas y otras cosas del gráfico
    if tipo_cotizacion == 'blue':
        titulo_cotizacion = 'Dólar Blue'
    elif tipo_cotizacion == 'oficial':
        titulo_cotizacion = 'Dólar Oficial'
    else:
        titulo_cotizacion = 'Cotización Desconocida'

    ax.set_title(f'Últimas {num_cotizaciones} Cotizaciones del {titulo_cotizacion} en Argentina ({año})')
    ax.set_xlabel('Fechas')
    ax.set_ylabel('Valor del Dólar')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)

    # Actualiza la interfaz gráfica con el nuevo gráfico cuando cambiamos los parametros
    if hasattr(app, 'canvas_widget'):
        app.canvas_widget.destroy()  # Elimina el gráfico anterior si existe

    canvas = FigureCanvasTkAgg(fig, master=app)
    app.canvas_widget = canvas.get_tk_widget()
    app.canvas_widget.pack()

# Función para obtener los datos ingresados por el usuario
def obtener_datos():
    # Obtine los datos que ingresamos 
    input_año = año_var.get()
    input_fechas = fechas_var.get()
    tipo_cotizacion = tipo_cotizacion_var.get()

     # Verifica si los campos están vacíos
    if not input_año or not input_fechas or not tipo_cotizacion:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return
    
    año = int(input_año)
    num_cotizaciones = int(input_fechas)

    # Verifica si los datos que ingresamos son correctos
    if tipo_cotizacion not in ['blue', 'oficial']:
        messagebox.showerror("Error", "Por favor, seleccione un tipo de cotización válido.")
        return

    # Verifica si el año que ingresamos es valido
    if año < 2015 or año > datetime.datetime.now().year:
        messagebox.showerror("Error", "Por favor, ingrese un año válido.")
        return
    if num_cotizaciones <= 0:
        messagebox.showerror("Error", "Por favor, ingrese una cantidad de fechas válida.")
        return

    # Descarga y visualizar los datos en el gráfico
    downloadAño(año, num_cotizaciones, tipo_cotizacion)
    messagebox.showinfo("Listo", "Datos extraídos y visualizados exitosamente.")

# Configura la interfaz grafica
app = tk.Tk()
app.title("Web Scraping y Visualización de Datos")

# Variables para almacenar los valores ingresados por el usuario
año_var = tk.StringVar()
fechas_var = tk.StringVar()
tipo_cotizacion_var = tk.StringVar()

# Inputs, radio button y boton para ingresar los datos para mostrar el grafico
label_año = ttk.Label(app, text="Ingrese el año:")
label_año.pack(padx=10, pady=5)

año_entry = ttk.Entry(app, textvariable=año_var)
año_entry.pack(padx=10, pady=5)

label_fechas = ttk.Label(app, text="Ingrese la cantidad de cotizaciones a visualizar:")
label_fechas.pack(padx=10, pady=5)

fechas_entry = ttk.Entry(app, textvariable=fechas_var)
fechas_entry.pack(padx=10, pady=5)

label_tipo_cotizacion = ttk.Label(app, text="Seleccione el tipo de cotización:")
label_tipo_cotizacion.pack(padx=10, pady=5)

blue_radio = ttk.Radiobutton(app, text="Dólar Blue", variable=tipo_cotizacion_var, value="blue")
blue_radio.pack(padx=10, pady=5)

oficial_radio = ttk.Radiobutton(app, text="Dólar Oficial", variable=tipo_cotizacion_var, value="oficial")
oficial_radio.pack(padx=10, pady=5)

obtener_button = ttk.Button(app, text="Obtener Datos", command=obtener_datos)
obtener_button.pack(padx=10, pady=10)

app.mainloop()