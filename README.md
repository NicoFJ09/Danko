# MazeRunner - Danko 🤖

Sistema de exploración autónoma de laberintos basado en grafos.

## 🏗️ Arquitectura

### Sistema Basado en Checkpoints y Grafos

El sistema ahora utiliza un **grafo de checkpoints** en lugar de un grid continuo basado en distancias. Esto simplifica enormemente la lógica y se alinea con el algoritmo DFS (Depth-First Search) con backtracking.

#### Conceptos Clave

**Checkpoint (Nodo)**:
- Representa un punto de decisión en el laberinto (intersección, esquina, dead-end)
- Cada checkpoint tiene 4 direcciones cardinales: **N, S, E, W**
- Cada dirección puede estar en uno de 3 estados:
  - `UNEXPLORED` - No explorada aún (amarillo)
  - `EXPLORED` - Ya explorada con conexión a otro checkpoint (verde)
  - `BLOCKED` - Pared detectada (rojo)

**Conexiones**:
- Los checkpoints se conectan entre sí cuando el bot se mueve
- Las conexiones son bidireccionales
- Forman el grafo del laberinto explorado

### 📦 Componentes del Server

```
server/
├── config.py              # Configuración (colores, ventana, zoom)
├── graph_state.py         # Sistema de grafo (checkpoints + conexiones)
├── simple_camera.py       # Cámara con pan/zoom
├── graph_renderer.py      # Renderizado visual del grafo
├── main.py                # Loop principal + input manual
└── old_system/            # Sistema anterior (archivado)
    ├── map/
    └── network/
```

## 🎮 Uso del Visualizador

### Iniciar el servidor:
```bash
cd server
python main.py
```

### Comandos Disponibles

**Crear nuevo checkpoint** (desde checkpoint actual):
```
<DIRECCION> <FRONT> <LEFT> <RIGHT>

Ejemplo:
N BLOCKED UNEXPLORED UNEXPLORED
```
- `DIRECCION`: N, S, E, W (dirección hacia la que avanzó el bot)
- `FRONT/LEFT/RIGHT`: Estados de los sensores
  - `UNEXPLORED` (U): Camino sin explorar
  - `BLOCKED` (B): Pared detectada
  - `EXPLORED` (E): Ya explorado

**Otros comandos**:
- `move <id>` - Mover a checkpoint específico
- `update <id> <dir> <estado>` - Actualizar dirección de checkpoint
- `deadend` - Marcar checkpoint actual como dead-end
- `stats` - Ver estadísticas del grafo
- `reset` - Resetear grafo completo
- `quit` - Salir

### Controles de Cámara

- **Click + Drag**: Pan (mover vista)
- **Scroll**: Zoom in/out
- **Espacio**: Centrar en checkpoint actual
- **ESC**: Salir

## 🎨 Visualización

### Colores de Checkpoints
- 🟡 **Amarillo**: Checkpoint actual (donde está el bot)
- 🔵 **Azul**: Checkpoint normal
- 🔴 **Rojo**: Dead-end

### Indicadores de Direcciones
Alrededor de cada checkpoint hay 4 círculos pequeños (N, S, E, W):
- 🟡 **Amarillo**: UNEXPLORED
- 🟢 **Verde**: EXPLORED
- 🔴 **Rojo**: BLOCKED

### Conexiones
- Líneas grises conectan checkpoints explorados

## 🧠 Algoritmo de Exploración (Bot)

El bot sigue un algoritmo **DFS con backtracking**:

1. **En cada checkpoint**: Leer sensores → determinar estados de direcciones
2. **Elegir dirección**:
   - Prioridad: seguir recto si está UNEXPLORED
   - Si no: primera dirección UNEXPLORED en orden N-E-W-S
   - Si no hay UNEXPLORED: **backtracking** a checkpoint anterior con UNEXPLORED
3. **Avanzar**: Hasta detectar cambio significativo en sensores laterales (±15cm)
4. **Crear checkpoint**: Marcar nuevo nodo con estados de sensores
5. **Repetir** hasta que no queden direcciones UNEXPLORED

### Umbrales de Detección (Bot)
```python
FRENTE_BLOCKED = 5cm        # Pared muy cerca al frente
LATERAL_BLOCKED = 20cm      # Considera pared en lateral
CAMBIO_SIGNIFICATIVO = 15cm # Cambio que indica nuevo checkpoint
```

## 🔮 Próximos Pasos

### Bot (CircuitPython):
- [ ] Implementar sensores laterales (hardware)
- [ ] Implementar algoritmo DFS completo
- [ ] Sistema de checkpoints en memoria
- [ ] Backtracking automático
- [ ] Enviar datos de checkpoints al server vía HTTP

### Server:
- [ ] Modo de recepción HTTP (además de manual)
- [ ] Visualización en tiempo real
- [ ] Exportar grafo a JSON
- [ ] Algoritmo de path-finding sobre grafo explorado

## 📝 Ejemplo de Sesión

```bash
> N BLOCKED UNEXPLORED UNEXPLORED
✅ Checkpoint #1 creado (parent: #0)
🧭 Heading actualizado: N
🤖 Ahora en Checkpoint #1

> E UNEXPLORED BLOCKED UNEXPLORED
✅ Checkpoint #2 creado (parent: #1)
🧭 Heading actualizado: E
🤖 Ahora en Checkpoint #2

> stats
📊 ESTADÍSTICAS:
   Total checkpoints: 3
   Dead-ends: 0
   Direcciones sin explorar: 8
   Exploración completa: ❌ NO
```

## 🛠️ Tecnologías

**Bot**: CircuitPython, IdeaBoard, LSM6DS3TRC (gyro), HCSR04 (ultrasónico)  
**Server**: Python, PyGame, Grafos

---

**Estado actual**: ✅ Sistema de grafos funcionando | 🔄 Algoritmo del bot en desarrollo
