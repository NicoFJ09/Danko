import board
import time
import math
from ideaboard import IdeaBoard
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
from hcsr04 import HCSR04

# ===== HARDWARE =====
ib = IdeaBoard()
sonar_left  = HCSR04(board.IO4,  board.IO5)
sonar_front = HCSR04(board.IO18, board.IO19)
sonar_right = HCSR04(board.IO25, board.IO26)
i2c = board.I2C()
sensor = LSM6DS3TRC(i2c, 0x6b)

# ===== CONSTANTES =====
RAD_A_GRADOS = 180 / math.pi
UMBRAL_FRONTAL_BLOQUEADO = 6 # 6 cm antes de considerar frente como pared
UMBRAL_LATERAL_BLOQUEADO = 30 # cualquier numero mayor a 30 es libre

# ===== VARIABLES GLOBALES =====
drift = 0.0
heading = "N"
checkpoint_actual = 0
last_frente = 100.0
last_izq    = 100.0
last_der    = 100.0

# ===== MAPAS =====
NORTE = 0
ESTE  = 90
SUR   = 180
OESTE = 270
LETRA_A_GRADOS = {'N': NORTE, 'E': ESTE, 'S': SUR, 'W': OESTE}

RUTA = [
    (0, 'N', 1),
    (1, 'N', 2),
    (2, 'N', 3),
    (3, 'N', 4),
    (4, 'E', 5),
    (5, 'E', 6),
]

ESTADOS = {
    0: {'N': 'EX', 'S': 'BL', 'E': 'BL', 'W': 'BL'},
    1: {'N': 'EX', 'S': 'EX', 'E': 'EX', 'W': 'BL'},
    2: {'N': 'EX', 'S': 'EX', 'E': 'BL', 'W': 'BL'},
    3: {'N': 'EX', 'S': 'EX', 'E': 'EX', 'W': 'BL'},
    4: {'N': 'BL', 'S': 'EX', 'E': 'EX', 'W': 'BL'},
    5: {'N': 'BL', 'S': 'BL', 'E': 'EX', 'W': 'EX'},
    6: {'N': 'BL', 'S': 'EX', 'E': 'EX', 'W': 'EX'},
}

# ===== FUNCIONES =====
def calibrar_drift(sensor, segundos=2):
    """Calibra el drift del giroscopio - código de Tomás"""
    print("Calibrando giroscopio...")
    suma = 0
    muestras = 0
    t0 = time.monotonic()
    
    while time.monotonic() - t0 < segundos: # mientras que tiempo actualizado menos tiempo inicial sea menor a segundos
        data = sensor.gyro[2] # leyendo eje z del giroscopio
        # evita promediar saltos que son error
        if abs(data) < 0.008: #mientras sea menor al umbral acumula la desviacion
            suma += sensor.gyro[2]
            muestras += 1
        time.sleep(0.005)
    
    drift = suma / muestras # promedio de todas las desviaciones
    print(f"Drift promedio: {drift:.4f} rad/s")
    return drift

def leer_sensores():
    """Lee los tres sensores ultrasónicos"""
    global last_frente, last_izq, last_der
    
    f = sonar_front.dist_cm()
    if f != -1 and f > 0:
        last_frente = f
    
    i = sonar_left.dist_cm()
    if i != -1 and i > 0:
        last_izq = i
    
    d = sonar_right.dist_cm()
    if d != -1 and d > 0:
        last_der = d
    
    time.sleep(0.005) 
    return {'frente': last_frente, 'izq': last_izq, 'der': last_der}

def sensores_a_direcciones_globales(sensores_locales, heading):
    """Convierte lecturas locales a direcciones globales"""
    rot_izq = {'N': 'W', 'E': 'N', 'S': 'E', 'W': 'S'}
    rot_der = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
    
    return {
        heading: sensores_locales['frente'],
        rot_izq[heading]: sensores_locales['izq'],
        rot_der[heading]: sensores_locales['der']
    }

def verificar_estado(sensores_globales, patron_esperado, heading):
    """Verifica si llegamos al checkpoint"""
    for direccion in ['N', 'E', 'S', 'W']:
        if direccion not in sensores_globales:
            continue
            
        distancia = sensores_globales[direccion]
        esperado = patron_esperado[direccion]
        umbral = UMBRAL_FRONTAL_BLOQUEADO if direccion == heading else UMBRAL_LATERAL_BLOQUEADO
        
        if esperado == 'BL' and distancia >= umbral:
            return False
        if esperado == 'EX' and distancia < umbral:
            return False
    
    return True

def girar_grados(sensor, grados, drift, velocidad=0.25):
    """Gira usando el giroscopio"""
    if abs(grados) < 2:
        print("  ⏭️  Giro pequeño, omitiendo")
        return
    
    print(f"  🔄 Girando {grados:+.0f}°...")
    
    sentido = 1 if grados > 0 else -1
    grados_objetivo = abs(grados) - 2
    acumulado = 0
    t_anterior = time.monotonic()
    
    ib.motor_1.throttle = velocidad * sentido
    ib.motor_2.throttle = -velocidad * sentido
    
    while acumulado < grados_objetivo:
        t_actual = time.monotonic()
        dt = t_actual - t_anterior
        t_anterior = t_actual
        
        vel_angular = sensor.gyro[2] - drift
        delta_grados = vel_angular * dt * RAD_A_GRADOS
        acumulado += abs(delta_grados)
        
        if grados_objetivo - acumulado <= grados_objetivo / 2:
            ib.motor_1.throttle = 0.15 * sentido
            ib.motor_2.throttle = -0.15 * sentido
        
        time.sleep(0.005)
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    print(f"  ✅ Completado")
    time.sleep(0.5)

def girar_a_direccion(direccion_objetivo):
    """Gira a una dirección cardinal"""
    global heading, drift
    
    grados_actual = LETRA_A_GRADOS[heading]
    grados_objetivo = LETRA_A_GRADOS[direccion_objetivo]
    
    diff = grados_objetivo - grados_actual
    if diff > 180:
        diff -= 360
    if diff < -180:
        diff += 360
    
    print(f"\n🧭 Girando {heading} → {direccion_objetivo} ({diff:+.0f}°)")
    girar_grados(sensor, diff, drift)
    heading = direccion_objetivo

def avanzar_hasta_checkpoints(checkpoints_destino, velocidad=0.45, Kp=0.20, Ki=0.05, Kd=0.10):

    """
    Control PID mejorado con mejor corrección de deriva
    """
    global checkpoint_actual, drift, heading
    
    # ===== PARÁMETROS PID MEJORADOS =====
    velocidad_base = abs(velocidad)
    direccion = 1 if velocidad > 0 else -1
    
    angulo_acumulado = 0.0
    error_anterior = 0.0
    error_integral = 0.0
    max_correccion = 0.15  # ✅ Aumentado ligeramente
    
    # ✅ CAMBIOS CLAVE:
    zona_muerta = 0.5        # ✅ Reducido de 3.0° a 1.0°
    limite_integral = 30     # ✅ Aumentado de 10 a 30
    
    print(f"\n🚀 Avanzando hacia: {checkpoints_destino}")
    print(f"⚙️  PID MEJORADO: Kp={Kp}, Ki={Ki}, Kd={Kd}")
    print(f"   Zona muerta: ±{zona_muerta}° | Integral: ±{limite_integral}\n")
    
    t_anterior = time.monotonic()
    t0 = time.monotonic()
    checkpoint_idx = 0
    
    while checkpoint_idx < len(checkpoints_destino):
        t_actual = time.monotonic()
        dt = t_actual - t_anterior
        t_anterior = t_actual
        
        if dt == 0:
            continue
        
        # ===== LEER SENSORES =====
        sensores_locales = leer_sensores()
        sensores_globales = sensores_a_direcciones_globales(sensores_locales, heading)
        
        checkpoint_objetivo = checkpoints_destino[checkpoint_idx]
        patron_esperado = ESTADOS[checkpoint_objetivo]
        
        # Verificar checkpoint
        if verificar_estado(sensores_globales, patron_esperado, heading):
            checkpoint_actual = checkpoint_objetivo
            tiempo = time.monotonic() - t0
            
            print(f"\n✅ CHECKPOINT {checkpoint_objetivo} detectado ({tiempo:.1f}s)")
            print(f"   Sensores: F={sensores_locales['frente']:.1f} I={sensores_locales['izq']:.1f} D={sensores_locales['der']:.1f}")
            
            checkpoint_idx += 1
            
            if checkpoint_idx >= len(checkpoints_destino):
                ib.motor_1.throttle = 0
                ib.motor_2.throttle = 0
                print(f"🛑 Fin del segmento\n")
                return
            
            print(f"➡️  Continúa hacia CP{checkpoints_destino[checkpoint_idx]}...\n")
            time.sleep(0.2)
        
        # ===== CONTROL PID MEJORADO =====
        
        # Leer velocidad angular
        vel_angular = sensor.gyro[2] - drift
        
        # Acumular ángulo
        angulo_acumulado += vel_angular * dt * RAD_A_GRADOS
        
        # ERROR = desviación del rumbo deseado (cero)
        error = angulo_acumulado
        
        # ✅ Zona muerta REDUCIDA - solo ignora vibraciones menores
        if abs(error) < zona_muerta:
            error_para_correccion = 0
        else:
            error_para_correccion = error
        
        # ✅ Integral SIEMPRE acumula (incluso en zona muerta)
        # Esto asegura que el error pequeño persistente se corrija
        error_integral += error * dt
        
        # Limitar integral con rango MÁS AMPLIO
        error_integral = max(-limite_integral, min(limite_integral, error_integral))
        
        # Término derivativo
        error_derivativo = (error - error_anterior) / dt if dt > 0 else 0
        
        # ✅ Control PID usa error_para_correccion (con zona muerta)
        # pero la integral usa el error REAL
        correccion = Kp * error_para_correccion + Ki * error_integral + Kd * error_derivativo
        
        # Límite de corrección
        correccion = max(-max_correccion, min(max_correccion, correccion))
        
        # ===== AJUSTE DE VELOCIDADES =====
        v1 = velocidad_base * direccion + correccion
        v2 = velocidad_base * direccion - correccion
        
        # Saturación
        v1 = max(-1, min(1, v1))
        v2 = max(-1, min(1, v2))
        
        ib.motor_1.throttle = v1
        ib.motor_2.throttle = v2
        
        error_anterior = error
        
        # ===== DISPLAY =====
        f_ok = "✅" if 1 < sensores_locales['frente'] < 350 else "❌"
        i_ok = "✅" if 1 < sensores_locales['izq'] < 350 else "❌"
        d_ok = "✅" if 1 < sensores_locales['der'] < 350 else "❌"
        
        if abs(angulo_acumulado) < zona_muerta:
            estado = "⬆️ RECTO"
        elif abs(error_integral) > 5:
            estado = "🔧 INTEG"  # Integral está corrigiendo
        elif abs(error) > 3:
            estado = "🔄 CORR"
        else:
            estado = "↗️ LEVE"
        
        print(f"\r{estado} →CP{checkpoint_objetivo} | {f_ok}F:{sensores_locales['frente']:5.1f} {i_ok}I:{sensores_locales['izq']:5.1f} {d_ok}D:{sensores_locales['der']:5.1f} | Δθ:{angulo_acumulado:6.2f}° | I:{error_integral:6.2f} | M1:{v1:.2f} M2:{v2:.2f}", end="")
        
        time.sleep(0.01)

def agrupar_ruta_por_direccion(ruta):
    """Agrupa checkpoints consecutivos por dirección"""
    if not ruta:
        return []
    
    grupos = []
    grupo_actual_origen = ruta[0][0]
    grupo_actual_dir = ruta[0][1]
    grupo_actual_checkpoints = []
    
    for origen, direccion, destino in ruta:
        if direccion == grupo_actual_dir:
            grupo_actual_checkpoints.append(destino)
        else:
            grupos.append((grupo_actual_origen, grupo_actual_dir, grupo_actual_checkpoints))
            grupo_actual_origen = origen
            grupo_actual_dir = direccion
            grupo_actual_checkpoints = [destino]
    
    grupos.append((grupo_actual_origen, grupo_actual_dir, grupo_actual_checkpoints))
    return grupos

def seguir_ruta():
    """Sigue la ruta agrupada por dirección"""
    global drift, checkpoint_actual, heading
    
    checkpoint_actual = 0
    heading = 'N'
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    time.sleep(0.5)
    
    # Calibrar (método de Tomás)
    ib.pixel = (255, 0, 0)
    print("\n⚠️  Robot completamente quieto para calibrar")
    time.sleep(2)
    drift = calibrar_drift(sensor, 5)
    ib.pixel = (0, 0, 0)
    
    # Agrupar ruta
    ruta_agrupada = agrupar_ruta_por_direccion(RUTA)
    
    print(f"\n{'='*60}")
    print(f"🗺️  NAVEGACIÓN ULTRA-SUAVE")
    print(f"{'='*60}")
    print(f"🎯 {len(ruta_agrupada)} segmentos\n")
    
    for idx, (origen, direccion, checkpoints) in enumerate(ruta_agrupada, 1):
        print(f"{'='*60}")
        print(f"📍 SEGMENTO {idx}/{len(ruta_agrupada)}")
        print(f"   De: CP{origen} → CP{checkpoints[-1]}")
        print(f"   Dirección: {direccion}")
        print(f"{'='*60}")
        
        girar_a_direccion(direccion)
        avanzar_hasta_checkpoints(checkpoints)
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    ib.pixel = (0, 255, 0)
    
    print(f"\n{'='*60}")
    print(f"🎉 RUTA COMPLETADA")
    print(f"{'='*60}\n")

# ===== PROGRAMA PRINCIPAL =====
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 NAVEGACIÓN PID ULTRA-SUAVE")
    print("="*60)
    print("Ganancias mínimas para eliminar wiggle completamente\n")
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    ib.pixel = (0, 0, 0)
    time.sleep(1)
    
    print("✅ Robot listo\n")
    
    try:
        seguir_ruta()
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        ib.motor_1.throttle = 0
        ib.motor_2.throttle = 0
        ib.pixel = (0, 0, 0)
    
    print("\n🏁 Programa terminado")