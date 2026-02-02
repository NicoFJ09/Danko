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

# Control de corrección por paredes
UMBRAL_ZONA_MUERTA = 2.0  # cm - No corregir si error < umbral
GANANCIA_PARED = 0.015    # Corrección cuando error >= umbral

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
    """Calibra el drift del giroscopio"""
    print("Calibrando giroscopio...")
    suma = 0
    muestras = 0
    t0 = time.monotonic()
    
    while time.monotonic() - t0 < segundos:
        data = sensor.gyro[2]
        if abs(data) < 0.008:
            suma += sensor.gyro[2]
            muestras += 1
        time.sleep(0.005)
    
    if muestras == 0:
        print("⚠️  No se pudo calibrar - usando drift = 0")
        return 0.0
    
    drift = suma / muestras
    print(f"Drift: {drift:.4f} rad/s")
    return drift

def leer_sensores():
    """Lee los tres sensores ultrasónicos"""
    global last_frente, last_izq, last_der
    
    try:
        f = sonar_front.dist_cm()
        if f != -1 and f > 0:
            last_frente = f
    except:
        pass
    
    try:
        i = sonar_left.dist_cm()
        if i != -1 and i > 0:
            last_izq = i
    except:
        pass
    
    try:
        d = sonar_right.dist_cm()
        if d != -1 and d > 0:
            last_der = d
    except:
        pass
    
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

def girar_grados(sensor, grados, velocidad=0.25):
    """Gira usando el giroscopio - usa drift global"""
    global drift
    
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
    global heading
    
    grados_actual = LETRA_A_GRADOS[heading]
    grados_objetivo = LETRA_A_GRADOS[direccion_objetivo]
    
    diff = grados_objetivo - grados_actual
    if diff > 180:
        diff -= 360
    if diff < -180:
        diff += 360
    
    print(f"\n🧭 Girando {heading} → {direccion_objetivo} ({diff:+.0f}°)")
    girar_grados(sensor, diff)  # ✅ Sin pasar drift
    heading = direccion_objetivo

def avanzar_hasta_checkpoints(checkpoints_destino, velocidad=0.40):
    """
    Navegación basada en corrección por paredes con ganancia dual
    """
    global checkpoint_actual, heading
    
    velocidad_base = abs(velocidad)
    direccion = 1 if velocidad > 0 else -1
    
    # Pared seleccionada (se fija al inicio y se mantiene)
    pared_elegida = None  # 'izq' o 'der'
    distancia_referencia = None
    
    umbral_minimo_pared = 20.0  # Si ambas > 20cm, no corregir
    umbral_cambio_brusco = 10.0  # Cambio radical para re-seleccionar
    
    t0 = time.monotonic()
    checkpoint_idx = 0
    iteracion = 0
    t_ultima_iter = time.monotonic()  # Para medir latencia entre iteraciones
    
    while checkpoint_idx < len(checkpoints_destino):
        iteracion += 1
        t_iter_actual = time.monotonic()
        dt_iter = t_iter_actual - t_ultima_iter  # Tiempo desde última iteración
        t_ultima_iter = t_iter_actual
        
        # ===== LEER SENSORES =====
        sensores_locales = leer_sensores()
        sensores_globales = sensores_a_direcciones_globales(sensores_locales, heading)
        
        checkpoint_objetivo = checkpoints_destino[checkpoint_idx]
        patron_esperado = ESTADOS[checkpoint_objetivo]
        
        # ===== VERIFICAR CHECKPOINT =====
        if verificar_estado(sensores_globales, patron_esperado, heading):
            checkpoint_actual = checkpoint_objetivo
            print(f"\n✅ CP{checkpoint_objetivo}")
            
            checkpoint_idx += 1
            
            if checkpoint_idx >= len(checkpoints_destino):
                ib.motor_1.throttle = 0
                ib.motor_2.throttle = 0
                return
            
            # Resetear pared seleccionada para nuevo tramo
            pared_elegida = None
            distancia_referencia = None
            
            time.sleep(0.2)

        # ===== SELECCIONAR PARED (solo una vez al inicio o si se pierde) =====
        if pared_elegida is None:
            # Elegir la pared MÁS LEJANA si alguna está < 20cm
            if sensores_locales['izq'] < umbral_minimo_pared or sensores_locales['der'] < umbral_minimo_pared:
                if sensores_locales['izq'] < umbral_minimo_pared and sensores_locales['der'] < umbral_minimo_pared:
                    # Ambas disponibles → elegir la más lejana
                    if sensores_locales['izq'] > sensores_locales['der']:
                        pared_elegida = 'izq'
                        distancia_referencia = sensores_locales['izq']
                    else:
                        pared_elegida = 'der'
                        distancia_referencia = sensores_locales['der']
                    print(f"   📏 Pared seleccionada: {pared_elegida.upper()} (Ref: {distancia_referencia:.1f}cm)")
                elif sensores_locales['izq'] < umbral_minimo_pared:
                    pared_elegida = 'izq'
                    distancia_referencia = sensores_locales['izq']
                    print(f"   📏 Pared seleccionada: IZQ (Ref: {distancia_referencia:.1f}cm)")
                else:
                    pared_elegida = 'der'
                    distancia_referencia = sensores_locales['der']
                    print(f"   📏 Pared seleccionada: DER (Ref: {distancia_referencia:.1f}cm)")
        
        # ===== DETECTAR PÉRDIDA DE PARED (cambio radical) =====
        if pared_elegida is not None and distancia_referencia is not None:
            dist_actual_pared = sensores_locales[pared_elegida]
            
            # Si cambio brusco o pared muy lejos → re-seleccionar
            if abs(dist_actual_pared - distancia_referencia) > umbral_cambio_brusco or dist_actual_pared > umbral_minimo_pared:
                print(f"   🔄 Pared {pared_elegida.upper()} perdida: {distancia_referencia:.1f} → {dist_actual_pared:.1f}cm")
                pared_elegida = None
                distancia_referencia = None

        # ===== CALCULAR CORRECCIÓN =====
        correccion = 0.0
        error_pared = 0.0
        
        # Timestamp relativo desde inicio
        t_actual = time.monotonic() - t0
        
        if pared_elegida is not None and distancia_referencia is not None:
            dist_actual = sensores_locales[pared_elegida]
            error_pared = dist_actual - distancia_referencia  # Error ABSOLUTO respecto a referencia
            
            # ZONA MUERTA: sin corrección si error < umbral, con corrección si error >= umbral
            if abs(error_pared) >= UMBRAL_ZONA_MUERTA:
                # Corrección: mantener distancia constante
                if pared_elegida == 'izq':
                    # Si error > 0: más lejos → acercar (girar izq) → corr negativa
                    # Si error < 0: más cerca → alejar (girar der) → corr positiva
                    correccion = -error_pared * GANANCIA_PARED
                else:  # 'der'
                    # Si error > 0: más lejos → acercar (girar der) → corr positiva
                    # Si error < 0: más cerca → alejar (girar izq) → corr negativa
                    correccion = +error_pared * GANANCIA_PARED
                
                # Debug frecuente (cada 3 iteraciones)
                if iteracion % 3 == 0:
                    print(f"[{t_actual:6.2f}s | #{iteracion:03d} | Δt:{dt_iter*1000:4.0f}ms] 🧱{pared_elegida.upper()} Ref:{distancia_referencia:.1f} Act:{dist_actual:.1f} Err:{error_pared:+.2f}cm Corr:{correccion:+.3f}")
            else:
                # Zona muerta - sin corrección, motores iguales
                if iteracion % 3 == 0:
                    print(f"[{t_actual:6.2f}s | #{iteracion:03d} | Δt:{dt_iter*1000:4.0f}ms] ✅{pared_elegida.upper()} Ref:{distancia_referencia:.1f} Act:{dist_actual:.1f} Err:{error_pared:+.2f}cm ZONA_MUERTA")
        
        else:
            # SIN pared seleccionada - avanzar recto
            if iteracion % 3 == 0:
                print(f"[{t_actual:6.2f}s | #{iteracion:03d} | Δt:{dt_iter*1000:4.0f}ms] ⬆️ SIN_PARED (I:{sensores_locales['izq']:.1f} D:{sensores_locales['der']:.1f}) - Recto")
        
        # Limitar corrección máxima
        correccion_sin_limitar = correccion
        correccion = max(-0.20, min(0.20, correccion))
        
        if abs(correccion_sin_limitar) > 0.20:
            print(f"[{t_actual:6.2f}s] ⚠️ LÍMITE! {correccion_sin_limitar:+.3f} → {correccion:+.3f}")

        # ===== AJUSTE DE VELOCIDADES =====
        v1 = velocidad_base * direccion + correccion
        v2 = velocidad_base * direccion - correccion
        
        # Saturación
        v1_sin_saturar = v1
        v2_sin_saturar = v2
        v1 = max(-1, min(1, v1))
        v2 = max(-1, min(1, v2))
        
        # Avisar si hubo saturación
        if abs(v1_sin_saturar) > 1.0 or abs(v2_sin_saturar) > 1.0:
            print(f"[{t_actual:6.2f}s] ⚠️ SATURACIÓN! M1:{v1_sin_saturar:.2f}→{v1:.2f} M2:{v2_sin_saturar:.2f}→{v2:.2f}")
        
        # Mostrar velocidades cuando hay corrección significativa (cada 3 iter)
        if abs(correccion) > 0.05 and iteracion % 3 == 0:
            print(f"       → Motores: M1={v1:.2f} M2={v2:.2f}")
        
        ib.motor_1.throttle = v1
        ib.motor_2.throttle = v2
        
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
    """Sigue la ruta agrupada por dirección - SIN giroscopio"""
    global checkpoint_actual, heading
    
    checkpoint_actual = 0
    heading = 'N'
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    time.sleep(0.5)
    
    # Agrupar ruta
    ruta_agrupada = agrupar_ruta_por_direccion(RUTA)
    
    print(f"\n🗺️  Navegando {len(ruta_agrupada)} segmentos\n")
    
    for idx, (origen, direccion, checkpoints) in enumerate(ruta_agrupada, 1):
        print(f"📍 Segmento {idx}: {direccion}")
        girar_a_direccion(direccion)
        avanzar_hasta_checkpoints(checkpoints, velocidad=0.40)
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    ib.pixel = (0, 255, 0)
    print(f"\n🎉 Completado\n")

# ===== PROGRAMA PRINCIPAL =====
if __name__ == "__main__":
    print("\n🤖 Iniciando...")
    
    ib.motor_1.throttle = 0
    ib.motor_2.throttle = 0
    ib.pixel = (0, 0, 0)
    time.sleep(1)
    
    ib.pixel = (255, 0, 0)
    print("Calibrando (quieto)...")
    time.sleep(2)
    drift = calibrar_drift(sensor, 5)
    ib.pixel = (0, 0, 0)
    print("Listo\n")
    
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