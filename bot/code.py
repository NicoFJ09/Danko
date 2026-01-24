# MazeRunner Bot - Test de Avance con Telemetría
# Avanza 2 segundos enviando datos del sensor frontal real

import board
import time
import math
import wifi
import socketpool
from ideaboard import IdeaBoard
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
from hcsr04 import HCSR04
from adafruit_httpserver import Server, Request, Response

# ============ CONFIGURACIÓN ============
WIFI_SSID = "Coworking"      # ← CAMBIAR
WIFI_PASSWORD = "12345678"     # ← CAMBIAR

# Sensores hardcodeados (no existen físicamente todavía)
SENSOR_LEFT = 4   # cm - pared cercana
SENSOR_RIGHT = 4  # cm - pared cercana
# ======================================

# Inicialización
ib = IdeaBoard()
i2c = board.I2C()
gyro_sensor = LSM6DS3TRC(i2c, 0x6b)

# Sensor ultrasónico frontal (REAL)
# TRIG conectado al pin IO10, y ECHO al Pin IO19
sonar_front = HCSR04(board.IO18, board.IO19)

# Estado del bot
heading = "N"  # Dirección actual (Norte por defecto)
last_front_reading = 0
is_moving = False

# Constantes
RAD_A_GRADOS = 180 / math.pi

# ============ WIFI ============
print(f"📡 Conectando a: {WIFI_SSID}")
try:
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"✅ Conectado!")
    print(f"🌐 IP del bot: {wifi.radio.ipv4_address}")
except Exception as e:
    print(f"❌ Error WiFi: {e}")
    raise

# ============ HTTP SERVER ============
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, debug=False)

@server.route("/data")
def get_data(request: Request):
    """Devuelve telemetría actual: <heading> <front> <left> <right>"""
    global heading, last_front_reading
    
    # Formato: "N 15.5 4 4"
    message = f"{heading} {last_front_reading:.1f} {SENSOR_LEFT} {SENSOR_RIGHT}"
    
    print(f"📤 Enviando: {message}")
    return Response(request, message, content_type="text/plain")

# Iniciar servidor
server.start(str(wifi.radio.ipv4_address), port=80)
print(f"🔄 Servidor HTTP activo\n")

# ============ FUNCIONES DE MOVIMIENTO ============

def calibrar_drift(sensor, segundos=2):
    """Calibrar el drift del giroscopio"""
    print("🔄 Calibrando giroscopio...")
    suma = 0
    muestras = 0
    t0 = time.monotonic()
    
    while time.monotonic() - t0 < segundos:
        data = sensor.gyro[2]
        if abs(data) < 0.008:
            suma += sensor.gyro[2]
            muestras += 1
        time.sleep(0.005)
    
    drift = suma / muestras if muestras > 0 else 0
    print(f"✅ Drift: {drift:.4f} rad/s")
    return drift

def leer_sensor_frontal():
    """Lee el sensor ultrasónico frontal"""
    global last_front_reading
    try:
        dist = sonar_front.dist_cm()
        last_front_reading = dist
        return dist
    except Exception as e:
        print(f"⚠️ Error leyendo sensor: {e}")
        return last_front_reading

def straight_move_con_telemetria(velocidad, duracion, drift, Kp=0.15, Ki=0.8, Kd=0.05):
    """
    Avanza recto enviando telemetría constantemente
    """
    global is_moving
    is_moving = True
    
    t0 = time.monotonic()
    velocidad_base = abs(velocidad)
    direccion = 1 if velocidad > 0 else -1

    error_anterior = 0
    error_integral = 0
    max_correccion = 0.3

    t_anterior = time.monotonic()
    t_ultimo_sensor = time.monotonic()

    print(f"🚀 Avanzando {duracion}s...")

    while time.monotonic() - t0 < duracion:
        t_actual = time.monotonic()
        dt = 1
        t_anterior = t_actual

        if dt == 0:
            continue

        # Leer sensor frontal cada 0.2s
        if time.monotonic() - t_ultimo_sensor >= 0.2:
            leer_sensor_frontal()
            t_ultimo_sensor = time.monotonic()

        # Control PID para movimiento recto
        error = gyro_sensor.gyro[2] - drift
        error_integral += error * dt
        error_derivativo = (error - error_anterior) / dt
        correccion = Kp * error + Ki * error_integral + Kd * error_derivativo
        correccion = max(-max_correccion, min(max_correccion, correccion))

        v1 = velocidad_base * direccion + correccion
        v2 = velocidad_base * direccion - correccion
        v1 = max(-1, min(1, v1))
        v2 = max(-1, min(1, v2))

        ib.motor_1.throttle = v1
        ib.motor_2.throttle = v2

        error_anterior = error
        
        # Procesar requests del servidor mientras se mueve
        server.poll()
        
        time.sleep(0.01)

    # Detener
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    is_moving = False
    print(f"🛑 Detenido")

# ============ PROGRAMA PRINCIPAL ============

print("🤖 MazeRunner - Test de Avance")
print("="*40)

# Calibrar giroscopio (LED rojo)
ib.pixel = (255, 0, 0)
drift = calibrar_drift(gyro_sensor, 3)
ib.pixel = (0, 0, 0)

print("\n⏳ Iniciando en 2 segundos...")
time.sleep(2)

# LED verde durante movimiento
ib.pixel = (0, 255, 0)

try:
    # Leer sensor inicial
    leer_sensor_frontal()
    print(f"📏 Sensor frontal inicial: {last_front_reading:.1f}cm")
    
    # Avanzar 2 segundos
    straight_move_con_telemetria(velocidad=0.5, duracion=2, drift=drift)
    
    # LED azul al terminar
    ib.pixel = (0, 0, 255)
    print("\n✅ Movimiento completado!")
    print(f"📏 Sensor frontal final: {last_front_reading:.1f}cm")
    
    # Seguir respondiendo requests aunque esté detenido
    print("\n🔄 Bot detenido, servidor activo...")
    while True:
        server.poll()
        time.sleep(0.1)
    
except KeyboardInterrupt:
    print("\n⚠️ Interrumpido")
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    ib.pixel = (255, 0, 0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    ib.pixel = (255, 0, 0)

ib.pixel = (0, 0, 0)