#!/usr/bin/env python3
"""
Test script para verificar la lógica del grafo sin GUI
"""

from graph_state import MazeGraph, DirectionState, Cardinal

def test_basic_graph():
    """Prueba básica del sistema de grafo"""
    print("=" * 60)
    print("🧪 TEST: Sistema de Grafo de Checkpoints")
    print("=" * 60)
    
    # Crear grafo
    graph = MazeGraph()
    print(f"\n✅ Grafo creado con checkpoint inicial #0")
    print(f"   Posición: ({graph.checkpoints[0].render_x}, {graph.checkpoints[0].render_y})")
    
    # Crear primer checkpoint (avanzar al norte)
    print("\n📍 Creando checkpoint #1 al NORTE con:")
    print("   - Frente: UNEXPLORED")
    print("   - Izquierda: BLOCKED")
    print("   - Derecha: BLOCKED")
    
    cp1 = graph.create_checkpoint(
        parent_id=0,
        arrival_direction=Cardinal.NORTH,
        front_state=DirectionState.UNEXPLORED,
        left_state=DirectionState.BLOCKED,
        right_state=DirectionState.BLOCKED,
        current_heading=Cardinal.NORTH
    )
    
    print(f"   ✅ Checkpoint #{cp1.id} creado")
    print(f"   Posición: ({cp1.render_x}, {cp1.render_y})")
    print(f"   Direcciones: {[(d.value, s.value) for d, s in cp1.directions.items()]}")
    print(f"   Conexiones: {[(d.value, cid) for d, cid in cp1.connections.items()]}")
    
    # Verificar conexión bidireccional
    print("\n🔗 Verificando conexión bidireccional:")
    print(f"   Checkpoint #0 → Norte → #{graph.checkpoints[0].connections.get(Cardinal.NORTH, 'None')}")
    print(f"   Checkpoint #1 → Sur → #{cp1.connections.get(Cardinal.SOUTH, 'None')}")
    
    # Mover a checkpoint 1
    graph.set_current_checkpoint(cp1.id)
    print(f"\n🤖 Movido a checkpoint #{graph.current_checkpoint_id}")
    
    # Crear segundo checkpoint (girar al este)
    print("\n📍 Creando checkpoint #2 al ESTE desde #1")
    cp2 = graph.create_checkpoint(
        parent_id=cp1.id,
        arrival_direction=Cardinal.EAST,
        front_state=DirectionState.BLOCKED,
        left_state=DirectionState.UNEXPLORED,
        right_state=DirectionState.UNEXPLORED,
        current_heading=Cardinal.EAST
    )
    
    print(f"   ✅ Checkpoint #{cp2.id} creado")
    print(f"   Posición: ({cp2.render_x}, {cp2.render_y})")
    
    # Estadísticas
    print("\n📊 Estadísticas finales:")
    stats = graph.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Verificar unexplored
    print("\n🔍 Direcciones UNEXPLORED por checkpoint:")
    for cp in graph.get_all_checkpoints():
        unexplored = cp.get_unexplored_directions()
        print(f"   Checkpoint #{cp.id}: {[d.value for d in unexplored]}")
    
    # Test de búsqueda
    print("\n🎯 Buscar siguiente checkpoint con UNEXPLORED:")
    next_cp = graph.find_next_unexplored_checkpoint()
    if next_cp:
        print(f"   ✅ Encontrado: Checkpoint #{next_cp.id}")
    else:
        print(f"   ❌ No hay más checkpoints con UNEXPLORED")
    
    # Conexiones para renderizado
    print("\n🎨 Conexiones para renderizado:")
    connections = graph.get_connection_endpoints()
    for i, (x1, y1, x2, y2) in enumerate(connections):
        print(f"   Conexión {i+1}: ({x1}, {y1}) → ({x2}, {y2})")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    test_basic_graph()
