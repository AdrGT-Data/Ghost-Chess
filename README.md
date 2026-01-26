# ♟️ Ghost Chess: Data-Driven Hardware Project

Proyecto autodidacta que integra ingeniería de hardware, inteligencia artificial y análisis de datos.

## Objetivos y descripción del proyecto:

La **idea principal** del proyecto es crear un tablero físico que mueva las piezas mediante un electroimán situado en la parte inferior movilizado con un sistema CoreXY (como el de las impresoras 3D). Este tablero analizará los movimientos del jugador contra la inteligencia artificial **StockFish**, una IA entrenada y especializada en ajedrez, y asesorará al jugador para mejorar.

## Stack Tecnológico
- **SO:** Linux (Ubuntu/Zorin)
- **Lenguaje:** Python 3.12
- **IA:** Stockfish Engine
- **Hardware:** Arduino / ESP32 (CoreXY System)
- **Data:** PostgreSQL / Docker / Streamlit

## Estructura de Directorios
- `src/`: Lógica principal(python), hardware e IA.
- `notebooks/`: Prototipado y experimentación.
- `data_raw/`: Logs de partidas y telemetría.
- `test/`: Archivos de prueba y experimentación.

## Estado del proyecto
- [x] Configuración de entorno Linux y venv.
- [x] Estructura de directorios.
- [x] Fase 0: Familiarización con librería `chess y lógica de IA (StockFish).
- [x] Fase 1: Simulación de partidas y tranformación de movimientos a coordenadas del tablero. 
- [x] Fase 2: Integración Hardware.

## FASE 1:


## FASE 2: INTEGRACIÓN HARDWARE

Una vez tenemos el código que nos da las coordenadas del tablero y los pasos para llegar a ellas, necesitamos una conexión que permita integrar la lógica de python con el hardware de Arduino.

Para lograr este hito he usado la comunicación bidireccional entre el sistema operativo Linux y el hardware de control mediante Python. En resumen, Arduino se queda continuamente esperando una señal concreta que python solo manda cuando el usuario se lo dice.

### El Camino del Aprendizaje:

1.  **Test del LED (Señalización):**
    * Objetivo: Validar el protocolo de comunicación Serial y los permisos de puerto en Linux.
    * Resultado: Control de un diodo LED mediante envío de bytes (`1`/`0`) desde la terminal.
2.  **Control de Potencia (Tracción):** * Implementación de un puente en H **L298N** para gestionar la carga de motores DC.
    * Sincronización de tierras (GND) entre la fuente de potencia (pilas 18650) y la lógica de control (Arduino).
    * Resultado: Control direccional de motores desde Python.

### Stack Tecnológico:
* **Lenguaje:** Python (Comandante) & C++ (Arduino IDE).
* **Comunicación:** Protocolo Serial a 9600 Baudios vía `pyserial`.
* **Hardware:** Arduino R3, Driver L298N, Motores DC, diodo LED, portapilas(18650).
