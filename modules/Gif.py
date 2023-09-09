from PIL import Image, ImageDraw, ImageFont
import imageio
import json
import os
import io

def cargar_pasos(ruta_json="orden.json"):
    with open(ruta_json, 'r') as file:
        data = json.load(file)
    return data['Orden']

def ajustar_imagen(imagen, max_ancho, max_alto):
    """Ajusta la imagen a las dimensiones máximas proporcionadas, manteniendo la relación de aspecto."""
    ancho, alto = imagen.size
    ratio = min(max_ancho / ancho, max_alto / alto)
    nuevo_ancho = int(ancho * ratio)
    nuevo_alto = int(alto * ratio)
    return imagen.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)

def centrar_en_canvas(imagen, ancho, alto, texto="AFN DE THOMPSON"):
    # Ajusta la imagen si es más grande que el canvas
    if imagen.width > ancho or imagen.height > alto:
        imagen = ajustar_imagen(imagen, ancho, alto)
        
    canvas = Image.new('RGBA', (ancho, alto), (255, 255, 255))
    x = (ancho - imagen.width) // 2
    y = (alto - imagen.height) // 2
    
    # Si la imagen tiene un canal alfa (transparencia), lo usamos como máscara
    if imagen.mode == 'RGBA':
        mask = imagen.split()[3]
        canvas.paste(imagen, (x, y), mask)
    else:
        canvas.paste(imagen, (x, y))
    
    # Agregar texto
    draw = ImageDraw.Draw(canvas)
    
    # Puedes ajustar el tamaño de fuente según tus necesidades.
    try:
        font = ImageFont.truetype("Arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((10, 10), texto, fill=(0, 0, 0), font=font)

    return canvas


def obtener_numero_imagen(ruta_imagen):
    # Extrae el nombre del archivo de la ruta
    nombre_imagen = os.path.basename(ruta_imagen)
    # Extrae el número de "thompson_x.png"
    return int(nombre_imagen.split('_')[1].split('.')[0])

def crear_gif_desde_imagenes(directorio_imagenes, archivo_salida, duracion_frame=0.5, repeticiones=1, pasos=None):
    # Obtener una lista de las imágenes en el directorio
    imagenes = [os.path.join(directorio_imagenes, f) for f in os.listdir(directorio_imagenes) if f.startswith('thompson_') and f.endswith('.png')]
    imagenes_ordenadas = sorted(imagenes, key=obtener_numero_imagen)

    # Leer cada imagen, centrarla en un canvas de 1500x1000, y añadirla a la lista
    print("Creando frames con un total de", len(imagenes_ordenadas), "imágenes...")
    frames = []
    for i, imagen in enumerate(imagenes_ordenadas):
        texto = pasos[i] if pasos and i < len(pasos) else "AFN DE THOMPSON"
        frame = centrar_en_canvas(Image.open(imagen), 1280, 720, texto)
        frames.append(frame)
    
    print("Convirtiendo imágenes PIL a imágenes imageio...")
    # Convertir imágenes PIL a imágenes imageio y guardar en GIF
    frames_io = []
    for frame in frames:
        with io.BytesIO() as output:
            frame.save(output, format="PNG")
            for _ in range(repeticiones):
                frames_io.append(imageio.imread(output.getvalue(), format="png"))

    print(f"Guardando {len(frames_io)} frames en {archivo_salida}...")
    imageio.mimsave(archivo_salida, frames_io, duration=250.0)
    # imageio.mimsave(archivo_salida, frames_io, duration=100.0, loop=0)


# Uso de la función
def crear_gif_thompson():
    directorio = "AFN_Imagenes"
    archivo_salida = "static/RESULTADO.gif"
    pasos = cargar_pasos()
    crear_gif_desde_imagenes(directorio, archivo_salida, duracion_frame=0.5, repeticiones=10, pasos=pasos)

