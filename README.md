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
- [ ] Fase 3: Control de Precisión (Motores paso a paso).
- [ ] Fase 4: Montaje Mecánico CoreXY.
- [ ] Fase 5: Integración del ElectroImán.
- [ ] Fase 6: Capa de Datos y Telemetría.

## FASE 1: Lógica de IA y Planificación de Movimientos

En esta etapa se desarrolló el "cerebro" del sistema, permitiendo que la lógica del juego se traduzca en coordenadas físicas precisas para el futuro sistema mecánico.

### Hitos Técnicos:
* **Integración de Motor de IA:** Implementación de **Stockfish 16** mediante la librería `python-chess` para el análisis de posiciones y toma de decisiones en tiempo real.
* **Sistema de Coordenadas Físicas:** Desarrollo de un traductor de notación algebraica (ej. `e2e4`) a milímetros reales. El sistema está optimizado para un tablero de **400x400 mm** con casillas de **50 mm**.
* **Algoritmo de Evasión de Colisiones (Pathfinding):** Implementación de una lógica de rutas que evita el choque entre piezas físicas. El imán se desplaza por los "pasillos" divisorios de las casillas, garantizando la integridad del juego.
* **Optimización de Seguridad:** Se ha definido un margen de seguridad basado en el diámetro de las piezas (**24 mm**) frente al tamaño de la casilla (**50 mm**), minimizando errores por fricción o interferencia magnética.

### Resultados:
Se ha logrado simular partidas completas en el terminal donde el sistema no solo decide la mejor jugada, sino que genera una lista de puntos $(x, y)$ que el hardware deberá recorrer.
## FASE 2: Integración Hardware

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
* **Hardware:** Arduino R3, Driver L298N, Motores DC, diodo LED, portapilas(18650)

Durante la implementación del sistema de agarre, se realizaron pruebas de estrés con el electroimán de 24V, obteniendo las siguientes conclusiones técnicas:

1. **Iteración del Control de Potencia**: Inicialmente se planteó el uso de un módulo **Relé** (Normalmente Abierto). Sin embargo, la carga inductiva del imán generaba caídas de tensión que provocaban el reinicio del microcontrolador Arduino por protección.
 
2. **Transición al Driver L298N**: Se optó por sustituir el relé por un módulo **L298N**. Esta configuración permite que los diodos de protección internos del driver absorban los picos de tensión al conmutar la carga, garantizando la estabilidad del sistema lógico y permitiendo el control mediante comandos seriales (`1` / `0`).
   
3. **Análisis de Eficiencia Energética**: Se detectó una deficiencia en la fuerza de atracción al alimentar el sistema con un pack de celdas Li-ion en serie (~14.8V - 16.8V).
   - **Fundamento Físico**: Considerando que la potencia disipada es proporcional al cuadrado del voltaje ($P = V^2 / R$), el funcionamiento a ~15V implica que el dispositivo opera apenas al **36-40% de su capacidad**.
   - **Resultado**: La densidad del campo magnético resultante es insuficiente para atravesar el tablero y desplazar las piezas con fiabilidad.

**Solución Prevista**: Implementación de una fuente de alimentación dedicada de 24V y optimización de la base de las piezas para maximizar el flujo magnético.

(Imagenes del circuito en la carpeta `docs`)

## FASE 2.5: Arquitectura CNC y Gestión Profesional (uv)

En esta etapa se ha realizado un "refactor" completo del sistema para pasar de un script de simulación a un software de control de maquinaria industrial (CNC).

### Hitos Técnicos:
* **Gestión con `uv`:** Migración del entorno a **uv**, garantizando una gestión de dependencias 100x más rápida y un entorno determinista mediante `pyproject.toml` y `uv.lock`.
* **Arquitectura Modular:** Separación de responsabilidades en tres núcleos:
    * `chess_engine.py`: Motor lógico y cálculo de trayectorias.
    * `communication.py`: Protocolo de comunicación Serial y sincronización de estados (Handshake OK).
    * `main.py`: Orquestador de la aplicación.
* **Protocolo G-Code:** Implementación del estándar industrial para el control de movimiento. El sistema ahora genera instrucciones `G0` (tránsito rápido) y `G1` (movimiento de carga) que cualquier controlador CNC podría interpretar.
* **Lógica de Captura Inteligente:** Desarrollo de una coreografía de movimiento para capturas. El sistema detecta si la casilla destino está ocupada y genera automáticamente una fase de "desahucio", retirando la pieza capturada al cementerio antes de realizar el movimiento principal.

### Estado del Software:
- [x] Migración a entorno `uv`.
- [x] Generador de G-Code para movimientos rectos y por costuras.
- [x] Protocolo de comunicación Serial con espera de confirmación.

------------------------------------------------------------
¿Qué vamos a hacer en la próxima sesión?
La próxima sesión será el "Día de la Integración Eléctrica". El objetivo será montar el "sistema nervioso" del tablero:

Pincharemos el Arduino Nano en la CNC Shield (si es compatible) o haremos el cableado.

Conectaremos los NEMA17 a los drivers (espero que vinieran con la shield).

Cargaremos un código de prueba para ver, por fin, los ejes girar.

Empezaremos a presentar las varillas de 8mm y los rodamientos LM8UU para entender cómo será el movimiento físico del CoreXY.
