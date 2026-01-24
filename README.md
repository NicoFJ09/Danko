# MazeRunner - Danko 🤖

Sistema de exploración autónoma de laberintos basado en grafos.

## 🏗️ Arquitectura

### Sistema Basado en Checkpoints y Grafos

El sistema utiliza un **grafo de checkpoints** donde cada nodo representa un **punto de detección de cambio** en el laberinto.

#### Conceptos Clave

**Checkpoint (Nodo)**:
- Se crea cuando el bot detecta un **cambio significativo** en sensores laterales (±15cm)
- Representa una esquina, apertura o intersección detectada
- **NO implica que el bot gire ahí** - solo marca dónde detectó el cambio
- El bot puede seguir recto después de detectar el checkpoint
- Cada checkpoint tiene 4 direcciones cardinales: **N, S, E, W**
- Cada dirección puede estar en uno de 3 estados:
  - `UNEXPLORED` 🟡 - No explorada aún
  - `EXPLORED` 🟢 - Ya explorada con conexión
  - `BLOCKED` 🔴 - Pared detectada

**Conexiones**:
- Los checkpoints se conectan entre sí cuando el bot se mueve
- Las conexiones son bidireccionales
- Forman el grafo del laberinto explorado

### 📦 Componentes

```
server/
├── config.py              # Configuración visual
├── graph_state.py         # Sistema de grafo (checkpoints + conexiones)
├── simple_camera.py       # Cámara con pan/zoom
├── graph_renderer.py      # Renderizado anti-aliased
├── main.py                # Loop principal + input manual
├── requirements.txt       # Dependencias (pygame)
└── old_system/            # Sistema anterior (archivado)
```

## 🎮 Uso

### Instalar e iniciar:
```bash
cd server
pip3 install -r requirements.txt
python3 main.py
```

### Comandos por Consola

**Crear checkpoint** (desde el actual):
```
<HEADING> <FRONT> <LEFT> <RIGHT>

Ejemplo:
N BLOCKED UNEXPLORED UNEXPLORED
```
- `HEADING`: Dirección actual del bot (N/S/E/W) - **CRÍTICO**
- `FRONT/LEFT/RIGHT`: Estados de sensores
- Estados: `UNEXPLORED` (U), `BLOCKED` (B), `EXPLORED` (E)

**¿Por qué HEADING es importante?**
El bot envía su **orientación absoluta** (basada en giroscopio) para que el servidor convierta las lecturas relativas (frente/izquierda/derecha) a direcciones absolutas (N/S/E/W).

**Otros**:
- `move <id>` - Saltar a checkpoint
- `update <id> <dir> <estado>` - Actualizar dirección
- `deadend` - Marcar como dead-end
- `stats` - Ver estadísticas
- `reset` - Reiniciar
- `quit` - Salir

### Controles de Cámara

- **Drag**: Pan
- **Scroll**: Zoom
- **Espacio**: Centrar en checkpoint actual
- **ESC**: Salir

## 🎨 Visualización

- **Círculos grandes**: Checkpoints
  - 🔵 Azul = Normal
  - 🟢 Verde = Actual (donde está el bot)
  - 🔴 Rojo = Dead-end
- **Círculos pequeños**: Estados de direcciones (N/S/E/W)
  - 🟡 UNEXPLORED
  - 🟢 EXPLORED
  - 🔴 BLOCKED
- **Líneas grises**: Conexiones entre checkpoints

## 🧠 Algoritmo (Bot)

**Detección de Checkpoint**:
- Mientras avanza, monitorea sensores laterales continuamente
- Cuando detecta cambio ±15cm → CHECKPOINT detectado
- Marca la posición y lee todos los sensores
- El bot NO necesariamente gira ahí - puede seguir recto

**Flujo de exploración**:
1. **En checkpoint**: Leer sensores → determinar estados de 4 direcciones
2. **Elegir dirección**: Prioridad recto si UNEXPLORED, sino N-E-W-S
3. **Avanzar**: Monitorear laterales hasta nuevo cambio ±15cm
   - Mientras avanza, las **reglas del checkpoint actual se mantienen**
   - Los sensores pueden leer lo que sea, pero las decisiones ya están tomadas
   - Ejemplo: Si S=EXPLORED en el checkpoint, el bot NO considerará ir al sur aunque los sensores lean 180cm en esa dirección
4. **Crear checkpoint**: Solo cuando detecta cambio ±15cm → nuevo nodo + nueva evaluación de estados
5. **Backtracking**: Si no hay UNEXPLORED, volver a parent

### Umbrales
```
FRENTE_BLOCKED = 5cm
LATERAL_BLOCKED = 20cm
CAMBIO_SIGNIFICATIVO = 15cm
```

## 📚 Documentación

- [EJEMPLO_LABERINTO.md](server/EJEMPLO_LABERINTO.md) - Recorrido completo paso a paso con laberinto de 4 habitaciones
- [DETECCION_CICLOS_MOVIMIENTO.md](server/DETECCION_CICLOS_MOVIMIENTO.md) - Prevenir loops infinitos (lógica del bot, no afecta checkpoints)

## 📝 Ejemplo

```bash
> N UNEXPLORED BLOCKED BLOCKED
✅ Checkpoint #1 creado
🤖 Ahora en Checkpoint #1

> E BLOCKED UNEXPLORED UNEXPLORED
✅ Checkpoint #2 creado

> stats
📊 Total: 3 | Dead-ends: 0 | Sin explorar: 7
```

## 🔮 Próximos Pasos

**Bot**:
- [ ] Implementar detección de checkpoints
- [ ] Sistema de memoria de checkpoints
- [ ] **Detección de ciclos de movimiento** (pattern matching)
- [ ] Algoritmo DFS + backtracking
- [ ] Envío HTTP al server

**Server**:
- [ ] Modo recepción HTTP
- [ ] Actualización en tiempo real

---

**Estado**: ✅ Visualizador funcionando | 🔄 Bot en desarrollo

**Tech**: CircuitPython (bot) | Python + PyGame (server)
