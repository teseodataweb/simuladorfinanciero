#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo de Riesgo Crediticio para Terrenos
=========================================

Este script implementa el modelo de riesgo crediticio utilizado en el simulador web,
permitiendo visualizar y manipular los factores de ponderación y sus efectos en:
- Cálculo de riesgo
- Tasas de interés
- Enganche mínimo requerido
- Monto máximo de préstamo

Autor: Manus
Fecha: Mayo 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

# Configuración de visualización
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 12

# Definir colores personalizados para riesgo
colors = [(0.0, 'green'), (0.5, 'yellow'), (1.0, 'red')]
cmap_riesgo = LinearSegmentedColormap.from_list('RiesgoColormap', colors)

# Factores de ponderación para el cálculo de riesgo
PONDERACIONES = {
    # Factores demográficos y financieros (40%)
    'edad': {
        '18-22': 8,
        '23-27': 6,
        '28-32': 4,
        '33-37': 2,
        '38-42': 0,
        '43-47': 2,
        '48-52': 4,
        '53-57': 6,
        '58-62': 8,
        '63-67': 10,
        '68-72': 12,
        '73-77': 14,
        '75+': 16
    },
    'rangoIngresos': {
        'Menos de 10K': 15,
        '10-15K': 12,
        '15-20K': 9,
        '20-25K': 6,
        '25-30K': 4,
        '30-35K': 3,
        '35-40K': 2,
        '40-45K': 1,
        '45-50K': 0,
        '50-55K': 0,
        '55-60K': 0,
        '60-65K': 0,
        '65-70K': 0,
        '70-75K': 0,
        'Más de 75K': 0
    },
    'tipoIngreso': {
        'Comprobable 100%': 0,
        'Comprobable 75%': 3,
        'Comprobable 50%': 6,
        'Comprobable 25%': 9,
        'Informal': 12
    },
    
    # Factores del crédito (35%)
    'plazoAnios': {
        1: 0,
        5: 2,
        10: 4,
        15: 6,
        20: 8,
        25: 10,
        30: 12
    },
    'enganchePorcentaje': {
        10: 12,
        15: 8,
        20: 4,
        25: 2,
        30: 0,
        40: 0,
        50: 0
    },
    
    # Factores del terreno (25%)
    'zonaLote': {
        'Premium': 0,
        'Intermedia': 3,
        'Estándar': 6
    },
    'tipoCredito': {
        'FOVISSSTE': 0,
        'IMSS': 2,
        'Hipotecario': 4,
        'Otro': 6
    },
    'codigoPostal': {
        # Esto sería un mapeo de códigos postales a puntajes de riesgo
        # basado en datos históricos o valoraciones de zona
        # Por defecto usamos un valor neutro de 3
        'default': 3
    }
}

# Umbrales de riesgo y sus efectos
UMBRALES_RIESGO = {
    'Bajo': {
        'max_score': 20,
        'tasa_base': 0.08,  # 8%
        'enganche_minimo': 0.12,  # 12%
        'prestamo_maximo': 7000000
    },
    'Medio': {
        'max_score': 40,
        'tasa_base': 0.13,  # 13%
        'enganche_minimo': 0.15,  # 15%
        'prestamo_maximo': 5000000
    },
    'Alto': {
        'max_score': 100,
        'tasa_base': 0.18,  # 18%
        'enganche_minimo': 0.25,  # 25%
        'prestamo_maximo': 3000000
    }
}

def calcular_puntaje_riesgo(datos):
    """
    Calcula el puntaje de riesgo basado en los datos proporcionados.
    
    Args:
        datos (dict): Diccionario con los datos del solicitante y del crédito
        
    Returns:
        int: Puntaje de riesgo (0-100, donde mayor es más riesgo)
    """
    puntaje = 0
    
    # Factores demográficos y financieros
    if datos['edad'] in PONDERACIONES['edad']:
        puntaje += PONDERACIONES['edad'][datos['edad']]
    
    if datos['rangoIngresos'] in PONDERACIONES['rangoIngresos']:
        puntaje += PONDERACIONES['rangoIngresos'][datos['rangoIngresos']]
    
    if datos['tipoIngreso'] in PONDERACIONES['tipoIngreso']:
        puntaje += PONDERACIONES['tipoIngreso'][datos['tipoIngreso']]
    
    # Factores del crédito
    # Para plazo, encontramos el valor más cercano
    plazos = list(PONDERACIONES['plazoAnios'].keys())
    plazo_cercano = min(plazos, key=lambda x: abs(x - datos['plazoAnios']))
    puntaje += PONDERACIONES['plazoAnios'][plazo_cercano]
    
    # Para enganche, encontramos el valor más cercano
    enganches = list(PONDERACIONES['enganchePorcentaje'].keys())
    enganche_cercano = min(enganches, key=lambda x: abs(x - datos['enganchePorcentaje']))
    puntaje += PONDERACIONES['enganchePorcentaje'][enganche_cercano]
    
    # Factores del terreno
    if datos['zonaLote'] in PONDERACIONES['zonaLote']:
        puntaje += PONDERACIONES['zonaLote'][datos['zonaLote']]
    
    if datos['tipoCredito'] in PONDERACIONES['tipoCredito']:
        puntaje += PONDERACIONES['tipoCredito'][datos['tipoCredito']]
    
    # Código postal (si está disponible)
    if datos['codigoPostal'] and datos['codigoPostal'] in PONDERACIONES['codigoPostal']:
        puntaje += PONDERACIONES['codigoPostal'][datos['codigoPostal']]
    else:
        puntaje += PONDERACIONES['codigoPostal']['default']
    
    return puntaje

def determinar_nivel_riesgo(puntaje):
    """
    Determina el nivel de riesgo basado en el puntaje.
    
    Args:
        puntaje (int): Puntaje de riesgo
        
    Returns:
        str: Nivel de riesgo ('Bajo', 'Medio', 'Alto')
    """
    if puntaje <= UMBRALES_RIESGO['Bajo']['max_score']:
        return 'Bajo'
    elif puntaje <= UMBRALES_RIESGO['Medio']['max_score']:
        return 'Medio'
    else:
        return 'Alto'

def calcular_tasa_interes(nivel_riesgo, puntaje):
    """
    Calcula la tasa de interés basada en el nivel de riesgo y el puntaje.
    
    Args:
        nivel_riesgo (str): Nivel de riesgo ('Bajo', 'Medio', 'Alto')
        puntaje (int): Puntaje de riesgo
        
    Returns:
        float: Tasa de interés anual (decimal)
    """
    # Obtenemos la tasa base según el nivel de riesgo
    tasa_base = UMBRALES_RIESGO[nivel_riesgo]['tasa_base']
    
    # Calculamos un ajuste adicional basado en la posición dentro del rango de puntaje
    if nivel_riesgo == 'Bajo':
        rango_min = 0
        rango_max = UMBRALES_RIESGO['Bajo']['max_score']
    elif nivel_riesgo == 'Medio':
        rango_min = UMBRALES_RIESGO['Bajo']['max_score']
        rango_max = UMBRALES_RIESGO['Medio']['max_score']
    else:  # Alto
        rango_min = UMBRALES_RIESGO['Medio']['max_score']
        rango_max = UMBRALES_RIESGO['Alto']['max_score']
    
    # Posición relativa en el rango (0 a 1)
    if rango_max - rango_min > 0:
        posicion_relativa = (puntaje - rango_min) / (rango_max - rango_min)
    else:
        posicion_relativa = 0
    
    # Ajuste adicional (hasta 0.02 o 2%)
    ajuste_adicional = posicion_relativa * 0.02
    
    return tasa_base + ajuste_adicional

def calcular_enganche_minimo(nivel_riesgo):
    """
    Determina el enganche mínimo requerido según el nivel de riesgo.
    
    Args:
        nivel_riesgo (str): Nivel de riesgo ('Bajo', 'Medio', 'Alto')
        
    Returns:
        float: Porcentaje de enganche mínimo (decimal)
    """
    return UMBRALES_RIESGO[nivel_riesgo]['enganche_minimo']

def calcular_prestamo_maximo(nivel_riesgo):
    """
    Determina el monto máximo de préstamo según el nivel de riesgo.
    
    Args:
        nivel_riesgo (str): Nivel de riesgo ('Bajo', 'Medio', 'Alto')
        
    Returns:
        float: Monto máximo de préstamo
    """
    return UMBRALES_RIESGO[nivel_riesgo]['prestamo_maximo']

def calcular_mensualidad(monto_prestamo, tasa_anual, plazo_anios, frecuencia_pago):
    """
    Calcula la mensualidad o cuota periódica.
    
    Args:
        monto_prestamo (float): Monto del préstamo
        tasa_anual (float): Tasa de interés anual (decimal)
        plazo_anios (int): Plazo en años
        frecuencia_pago (str): Frecuencia de pago ('Mensual', 'Bimestral', 'Anual')
        
    Returns:
        float: Monto de la cuota periódica
    """
    if frecuencia_pago == 'Mensual':
        tasa_periodica = tasa_anual / 12
        num_pagos = plazo_anios * 12
    elif frecuencia_pago == 'Bimestral':
        tasa_periodica = tasa_anual / 6
        num_pagos = plazo_anios * 6
    else:  # Anual
        tasa_periodica = tasa_anual
        num_pagos = plazo_anios
    
    if tasa_periodica > 0:
        mensualidad = monto_prestamo * (tasa_periodica * (1 + tasa_periodica) ** num_pagos) / ((1 + tasa_periodica) ** num_pagos - 1)
    else:
        mensualidad = monto_prestamo / num_pagos
    
    return mensualidad

def generar_tabla_amortizacion(monto_prestamo, tasa_anual, plazo_anios, frecuencia_pago):
    """
    Genera la tabla de amortización completa.
    
    Args:
        monto_prestamo (float): Monto del préstamo
        tasa_anual (float): Tasa de interés anual (decimal)
        plazo_anios (int): Plazo en años
        frecuencia_pago (str): Frecuencia de pago ('Mensual', 'Bimestral', 'Anual')
        
    Returns:
        pandas.DataFrame: Tabla de amortización
    """
    if frecuencia_pago == 'Mensual':
        tasa_periodica = tasa_anual / 12
        num_pagos = plazo_anios * 12
    elif frecuencia_pago == 'Bimestral':
        tasa_periodica = tasa_anual / 6
        num_pagos = plazo_anios * 6
    else:  # Anual
        tasa_periodica = tasa_anual
        num_pagos = plazo_anios
    
    mensualidad = calcular_mensualidad(monto_prestamo, tasa_anual, plazo_anios, frecuencia_pago)
    
    tabla = []
    saldo = monto_prestamo
    
    for i in range(1, int(num_pagos) + 1):
        interes = saldo * tasa_periodica
        capital = mensualidad - interes
        
        # Ajuste para el último pago
        if i == num_pagos:
            if abs(saldo - capital) > 0.01 and saldo > 0:
                capital = saldo
            if mensualidad < saldo and tasa_periodica > 0:
                capital = saldo
            mensualidad = capital + interes
        
        saldo = max(0, saldo - capital)
        
        tabla.append({
            'Cuota': i,
            'Pago': mensualidad,
            'Interés': interes,
            'Capital': capital,
            'Saldo': saldo
        })
    
    return pd.DataFrame(tabla)

def calcular_plusvalia(precio_inicial, plazo_anios, tasa_plusvalia=0.128):
    """
    Calcula el valor futuro de la propiedad considerando la plusvalía.
    
    Args:
        precio_inicial (float): Precio inicial de la propiedad
        plazo_anios (int): Plazo en años
        tasa_plusvalia (float): Tasa anual de plusvalía (default: 12.8%)
        
    Returns:
        float: Valor futuro de la propiedad
    """
    return precio_inicial * (1 + tasa_plusvalia) ** plazo_anios

def calcular_roi(ganancia, inversion):
    """
    Calcula el Retorno de Inversión (ROI).
    
    Args:
        ganancia (float): Ganancia estimada
        inversion (float): Inversión total
        
    Returns:
        float: ROI como decimal
    """
    if inversion > 0:
        return ganancia / inversion
    return 0

def simular_credito(datos):
    """
    Realiza una simulación completa de crédito y riesgo.
    
    Args:
        datos (dict): Diccionario con los datos del solicitante y del crédito
        
    Returns:
        dict: Resultados de la simulación
    """
    # Cálculo de riesgo
    puntaje_riesgo = calcular_puntaje_riesgo(datos)
    nivel_riesgo = determinar_nivel_riesgo(puntaje_riesgo)
    tasa_interes = calcular_tasa_interes(nivel_riesgo, puntaje_riesgo)
    enganche_minimo = calcular_enganche_minimo(nivel_riesgo)
    prestamo_maximo = calcular_prestamo_maximo(nivel_riesgo)
    
    # Cálculos financieros
    precio_final = datos['precioFinal']
    enganche_porcentaje = datos['enganchePorcentaje'] / 100
    valor_enganche = precio_final * enganche_porcentaje
    valor_prestamo = precio_final - valor_enganche
    
    # Validaciones y ajustes
    mensajes = []
    if enganche_porcentaje < enganche_minimo:
        mensajes.append(f"Enganche mínimo para riesgo {nivel_riesgo} es {enganche_minimo*100}%.")
    
    if valor_prestamo > prestamo_maximo:
        mensajes.append(f"Monto máximo de préstamo para riesgo {nivel_riesgo} es ${prestamo_maximo:,.2f}.")
    
    # Cálculo de mensualidad y tabla de amortización
    mensualidad = calcular_mensualidad(valor_prestamo, tasa_interes, datos['plazoAnios'], datos['frecuenciaPago'])
    tabla_amortizacion = generar_tabla_amortizacion(valor_prestamo, tasa_interes, datos['plazoAnios'], datos['frecuenciaPago'])
    
    # Cálculo de plusvalía y ROI
    valor_futuro = calcular_plusvalia(precio_final, datos['plazoAnios'])
    total_pagado = valor_enganche + tabla_amortizacion['Pago'].sum()
    ganancia_estimada = valor_futuro - precio_final
    roi = calcular_roi(ganancia_estimada, total_pagado)
    
    # Resultados
    return {
        'puntaje_riesgo': puntaje_riesgo,
        'nivel_riesgo': nivel_riesgo,
        'tasa_interes': tasa_interes,
        'enganche_minimo': enganche_minimo,
        'prestamo_maximo': prestamo_maximo,
        'valor_enganche': valor_enganche,
        'valor_prestamo': valor_prestamo,
        'mensualidad': mensualidad,
        'num_pagos': len(tabla_amortizacion),
        'tabla_amortizacion': tabla_amortizacion,
        'valor_futuro': valor_futuro,
        'total_pagado': total_pagado,
        'ganancia_estimada': ganancia_estimada,
        'roi': roi,
        'mensajes': mensajes
    }

def visualizar_ponderaciones():
    """
    Visualiza las ponderaciones de los factores de riesgo.
    """
    # Preparamos los datos para visualización
    factores = []
    valores = []
    categorias = []
    
    for factor, ponderaciones in PONDERACIONES.items():
        if factor != 'codigoPostal':  # Excluimos código postal por ser muy variable
            for categoria, valor in ponderaciones.items():
                factores.append(factor)
                valores.append(valor)
                categorias.append(str(categoria))
    
    # Creamos un DataFrame
    df = pd.DataFrame({
        'Factor': factores,
        'Categoría': categorias,
        'Puntaje': valores
    })
    
    # Pivotamos para mejor visualización
    pivot_df = df.pivot(index='Categoría', columns='Factor', values='Puntaje')
    
    # Visualizamos con heatmap
    plt.figure(figsize=(14, 10))
    ax = sns.heatmap(pivot_df, cmap=cmap_riesgo, annot=True, fmt='d', linewidths=.5)
    plt.title('Ponderaciones de Factores de Riesgo', fontsize=16)
    plt.ylabel('Categoría')
    plt.xlabel('Factor')
    plt.tight_layout()
    plt.show()
    
    # Mostramos también los umbrales de riesgo
    print("\nUmbrales de Riesgo y sus Efectos:")
    umbrales_df = pd.DataFrame({
        'Nivel': list(UMBRALES_RIESGO.keys()),
        'Puntaje Máximo': [UMBRALES_RIESGO[nivel]['max_score'] for nivel in UMBRALES_RIESGO],
        'Tasa Base': [f"{UMBRALES_RIESGO[nivel]['tasa_base']*100:.1f}%" for nivel in UMBRALES_RIESGO],
        'Enganche Mínimo': [f"{UMBRALES_RIESGO[nivel]['enganche_minimo']*100:.1f}%" for nivel in UMBRALES_RIESGO],
        'Préstamo Máximo': [f"${UMBRALES_RIESGO[nivel]['prestamo_maximo']:,.2f}" for nivel in UMBRALES_RIESGO]
    })
    display(umbrales_df)

def visualizar_impacto_factores(factor_x, factor_y, datos_base):
    """
    Visualiza el impacto de dos factores en el riesgo y la tasa de interés.
    
    Args:
        factor_x (str): Factor para el eje X
        factor_y (str): Factor para el eje Y
        datos_base (dict): Datos base para la simulación
    """
    # Obtenemos los valores posibles para cada factor
    valores_x = list(PONDERACIONES[factor_x].keys())
    valores_y = list(PONDERACIONES[factor_y].keys())
    
    # Matrices para almacenar resultados
    matriz_riesgo = np.zeros((len(valores_y), len(valores_x)))
    matriz_tasa = np.zeros((len(valores_y), len(valores_x)))
    
    # Calculamos el riesgo y la tasa para cada combinación
    for i, valor_y in enumerate(valores_y):
        for j, valor_x in enumerate(valores_x):
            datos_simulacion = datos_base.copy()
            datos_simulacion[factor_x] = valor_x
            datos_simulacion[factor_y] = valor_y
            
            puntaje = calcular_puntaje_riesgo(datos_simulacion)
            nivel = determinar_nivel_riesgo(puntaje)
            tasa = calcular_tasa_interes(nivel, puntaje)
            
            matriz_riesgo[i, j] = puntaje
            matriz_tasa[i, j] = tasa * 100  # Convertimos a porcentaje
    
    # Creamos la visualización
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Heatmap de puntaje de riesgo
    sns.heatmap(matriz_riesgo, annot=True, fmt='.1f', cmap=cmap_riesgo, 
                xticklabels=valores_x, yticklabels=valores_y, ax=ax1)
    ax1.set_title(f'Puntaje de Riesgo: {factor_y} vs {factor_x}', fontsize=14)
    ax1.set_xlabel(factor_x)
    ax1.set_ylabel(factor_y)
    
    # Heatmap de tasa de interés
    sns.heatmap(matriz_tasa, annot=True, fmt='.2f', cmap='YlOrRd', 
                xticklabels=valores_x, yticklabels=valores_y, ax=ax2)
    ax2.set_title(f'Tasa de Interés (%): {factor_y} vs {factor_x}', fontsize=14)
    ax2.set_xlabel(factor_x)
    ax2.set_ylabel(factor_y)
    
    plt.tight_layout()
    plt.show()

def visualizar_amortizacion(resultados):
    """
    Visualiza la tabla de amortización y distribución de pagos.
    
    Args:
        resultados (dict): Resultados de la simulación
    """
    tabla = resultados['tabla_amortizacion']
    
    # Gráfico de evolución del saldo
    plt.figure(figsize=(12, 6))
    plt.plot(tabla['Cuota'], tabla['Saldo'], 'b-', linewidth=2)
    plt.title('Evolución del Saldo del Préstamo', fontsize=14)
    plt.xlabel('Número de Cuota')
    plt.ylabel('Saldo ($)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Gráfico de distribución de pagos (interés vs capital)
    plt.figure(figsize=(12, 6))
    
    # Calculamos el acumulado de interés y capital
    interes_acumulado = tabla['Interés'].cumsum()
    capital_acumulado = tabla['Capital'].cumsum()
    
    plt.stackplot(tabla['Cuota'], [interes_acumulado, capital_acumulado], 
                 labels=['Interés', 'Capital'], alpha=0.7,
                 colors=['#ff9999', '#66b3ff'])
    
    plt.title('Distribución Acumulada de Pagos', fontsize=14)
    plt.xlabel('Número de Cuota')
    plt.ylabel('Monto Acumulado ($)')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Mostramos un resumen de la amortización
    interes_total = tabla['Interés'].sum()
    capital_total = tabla['Capital'].sum()
    
    print(f"Resumen de Amortización:")
    print(f"- Monto del préstamo: ${resultados['valor_prestamo']:,.2f}")
    print(f"- Total pagado: ${resultados['total_pagado']:,.2f}")
    print(f"- Total intereses: ${interes_total:,.2f}")
    print(f"- Porcentaje de intereses sobre el préstamo: {(interes_total/resultados['valor_prestamo'])*100:.2f}%")

def visualizar_plusvalia_roi(resultados):
    """
    Visualiza la plusvalía y el ROI.
    
    Args:
        resultados (dict): Resultados de la simulación
    """
    # Datos para el gráfico
    categorias = ['Precio Inicial', 'Total Pagado', 'Valor Futuro']
    valores = [resultados['valor_prestamo'] + resultados['valor_enganche'], 
               resultados['total_pagado'], 
               resultados['valor_futuro']]
    
    # Gráfico de barras
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categorias, valores, color=['#66b3ff', '#ff9999', '#99ff99'])
    
    # Añadimos etiquetas con los valores
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'${height:,.2f}', ha='center', va='bottom')
    
    plt.title('Comparativa de Inversión y Valor Futuro', fontsize=14)
    plt.ylabel('Monto ($)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
    
    # Mostramos un resumen
    print(f"Resumen de Plusvalía y ROI:")
    print(f"- Precio inicial: ${resultados['valor_prestamo'] + resultados['valor_enganche']:,.2f}")
    print(f"- Total pagado: ${resultados['total_pagado']:,.2f}")
    print(f"- Valor futuro estimado: ${resultados['valor_futuro']:,.2f}")
    print(f"- Ganancia estimada: ${resultados['ganancia_estimada']:,.2f}")
    print(f"- ROI: {resultados['roi']*100:.2f}%")

def interfaz_interactiva():
    """
    Crea una interfaz interactiva para explorar el modelo de riesgo.
    """
    # Widgets para los datos de entrada
    w_precio = widgets.FloatText(value=1000000, description='Precio ($):', min=100000, max=10000000)
    w_enganche = widgets.FloatSlider(value=15, description='Enganche (%):', min=10, max=50, step=5)
    w_plazo = widgets.IntSlider(value=15, description='Plazo (años):', min=1, max=30)
    w_frecuencia = widgets.Dropdown(options=['Mensual', 'Bimestral', 'Anual'], value='Mensual', description='Frecuencia:')
    
    w_edad = widgets.Dropdown(options=list(PONDERACIONES['edad'].keys()), value='30-34', description='Edad:')
    w_ingresos = widgets.Dropdown(options=list(PONDERACIONES['rangoIngresos'].keys()), value='25-30K', description='Ingresos:')
    w_tipo_ingreso = widgets.Dropdown(options=list(PONDERACIONES['tipoIngreso'].keys()), value='Comprobable 100%', description='Tipo Ingreso:')
    
    w_zona = widgets.Dropdown(options=list(PONDERACIONES['zonaLote'].keys()), value='Estándar', description='Zona:')
    w_credito = widgets.Dropdown(options=list(PONDERACIONES['tipoCredito'].keys()), value='Hipotecario', description='Tipo Crédito:')
    w_cp = widgets.Text(value='', description='Código Postal:')
    
    # Botones para acciones
    btn_simular = widgets.Button(description='Simular Crédito')
    btn_ponderaciones = widgets.Button(description='Ver Ponderaciones')
    btn_impacto = widgets.Button(description='Analizar Impacto')
    
    # Widgets para análisis de impacto
    w_factor_x = widgets.Dropdown(options=list(PONDERACIONES.keys()), value='enganchePorcentaje', description='Factor X:')
    w_factor_y = widgets.Dropdown(options=list(PONDERACIONES.keys()), value='plazoAnios', description='Factor Y:')
    
    # Área de salida
    output = widgets.Output()
    
    # Funciones de callback
    def on_simular_clicked(b):
        with output:
            clear_output()
            
            # Recopilamos los datos
            datos = {
                'precioFinal': w_precio.value,
                'enganchePorcentaje': w_enganche.value,
                'plazoAnios': w_plazo.value,
                'frecuenciaPago': w_frecuencia.value,
                'edad': w_edad.value,
                'rangoIngresos': w_ingresos.value,
                'tipoIngreso': w_tipo_ingreso.value,
                'zonaLote': w_zona.value,
                'tipoCredito': w_credito.value,
                'codigoPostal': w_cp.value
            }
            
            # Realizamos la simulación
            resultados = simular_credito(datos)
            
            # Mostramos resultados
            print(f"=== RESULTADOS DE LA SIMULACIÓN ===\n")
            
            # Mensajes de riesgo
            if resultados['mensajes']:
                print("AVISOS DEL MODELO DE RIESGO:")
                for msg in resultados['mensajes']:
                    print(f"- {msg}")
                print()
            
            # Resumen financiero
            print(f"RESUMEN FINANCIERO:")
            print(f"- Precio Final: ${datos['precioFinal']:,.2f}")
            print(f"- Enganche ({datos['enganchePorcentaje']}%): ${resultados['valor_enganche']:,.2f}")
            print(f"- Valor del Préstamo: ${resultados['valor_prestamo']:,.2f}")
            print(f"- {w_frecuencia.value}idad: ${resultados['mensualidad']:,.2f}")
            print(f"- Número de Cuotas: {resultados['num_pagos']}")
            print(f"- Total Pagado: ${resultados['total_pagado']:,.2f}")
            print(f"- Valor Futuro (Plusvalía): ${resultados['valor_futuro']:,.2f}")
            print(f"- Ganancia Estimada: ${resultados['ganancia_estimada']:,.2f}")
            print(f"- ROI: {resultados['roi']*100:.2f}%\n")
            
            # Información de riesgo
            print(f"INFORMACIÓN DE RIESGO:")
            print(f"- Puntaje de Riesgo: {resultados['puntaje_riesgo']}")
            print(f"- Nivel de Riesgo: {resultados['nivel_riesgo']}")
            print(f"- Tasa de Interés Anual: {resultados['tasa_interes']*100:.2f}%")
            print(f"- Enganche Mínimo Sugerido: {resultados['enganche_minimo']*100:.1f}%")
            print(f"- Préstamo Máximo Sugerido: ${resultados['prestamo_maximo']:,.2f}\n")
            
            # Visualizaciones
            visualizar_amortizacion(resultados)
            visualizar_plusvalia_roi(resultados)
    
    def on_ponderaciones_clicked(b):
        with output:
            clear_output()
            visualizar_ponderaciones()
    
    def on_impacto_clicked(b):
        with output:
            clear_output()
            
            # Recopilamos los datos base
            datos_base = {
                'precioFinal': w_precio.value,
                'enganchePorcentaje': w_enganche.value,
                'plazoAnios': w_plazo.value,
                'frecuenciaPago': w_frecuencia.value,
                'edad': w_edad.value,
                'rangoIngresos': w_ingresos.value,
                'tipoIngreso': w_tipo_ingreso.value,
                'zonaLote': w_zona.value,
                'tipoCredito': w_credito.value,
                'codigoPostal': w_cp.value
            }
            
            # Visualizamos el impacto
            visualizar_impacto_factores(w_factor_x.value, w_factor_y.value, datos_base)
    
    # Asignamos los callbacks
    btn_simular.on_click(on_simular_clicked)
    btn_ponderaciones.on_click(on_ponderaciones_clicked)
    btn_impacto.on_click(on_impacto_clicked)
    
    # Organizamos la interfaz
    datos_credito = widgets.VBox([
        widgets.HTML("<h3>Datos del Crédito</h3>"),
        w_precio, w_enganche, w_plazo, w_frecuencia
    ])
    
    datos_solicitante = widgets.VBox([
        widgets.HTML("<h3>Perfil del Solicitante</h3>"),
        w_edad, w_ingresos, w_tipo_ingreso
    ])
    
    datos_terreno = widgets.VBox([
        widgets.HTML("<h3>Datos del Terreno</h3>"),
        w_zona, w_credito, w_cp
    ])
    
    analisis_impacto = widgets.VBox([
        widgets.HTML("<h3>Análisis de Impacto</h3>"),
        w_factor_x, w_factor_y
    ])
    
    botones = widgets.HBox([btn_simular, btn_ponderaciones, btn_impacto])
    
    # Layout final
    izquierda = widgets.VBox([datos_credito, datos_solicitante])
    derecha = widgets.VBox([datos_terreno, analisis_impacto])
    arriba = widgets.HBox([izquierda, derecha])
    
    display(widgets.VBox([
        widgets.HTML("<h2>Simulador de Crédito y Modelo de Riesgo</h2>"),
        arriba,
        botones,
        output
    ]))

# Ejemplo de uso básico
if __name__ == "__main__":
    # Datos de ejemplo
    datos_ejemplo = {
        'precioFinal': 1000000,
        'enganchePorcentaje': 15,
        'plazoAnios': 15,
        'frecuenciaPago': 'Mensual',
        'edad': '30-34',
        'rangoIngresos': '25-30K',
        'tipoIngreso': 'Comprobable 100%',
        'zonaLote': 'Estándar',
        'tipoCredito': 'Hipotecario',
        'codigoPostal': ''
    }
    
    # Simulación
    resultados = simular_credito(datos_ejemplo)
    
    # Mostramos resultados básicos
    print(f"Puntaje de Riesgo: {resultados['puntaje_riesgo']}")
    print(f"Nivel de Riesgo: {resultados['nivel_riesgo']}")
    print(f"Tasa de Interés: {resultados['tasa_interes']*100:.2f}%")
    print(f"Mensualidad: ${resultados['mensualidad']:,.2f}")
    print(f"Total Pagado: ${resultados['total_pagado']:,.2f}")
    print(f"Valor Futuro: ${resultados['valor_futuro']:,.2f}")
    print(f"ROI: {resultados['roi']*100:.2f}%")
    
    # Para usar la interfaz interactiva en un notebook, descomentar:
    # interfaz_interactiva()
