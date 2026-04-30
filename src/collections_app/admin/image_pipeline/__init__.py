"""Pipeline de generación automática de imágenes para cards.

Tres etapas en cascada:
1. `PhotoFinder` busca/descarga foto del jugador (DDG → Wikipedia → placeholder).
2. `SketchGenerator` convierte la foto a sketch B&W con face detection.
3. `CardComposer` compone la card final con fondo, número, nombre y badge.

`ImagePipeline` orquesta las tres etapas en batches. Importar las clases
desde sus módulos directos para no acoplarlas todas (cv2/PIL pesan al
importar).
"""
