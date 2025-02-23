import cv2
import mediapipe as mp
import numpy as np
import json
import os
from collections import defaultdict
import sounddevice as sd
from persona import *
from ringtone import *

# Configuración de MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False, 
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# Archivo de base de datos
DATABASE_FILE = "database.json"
NUM_MUESTRAS = 150  # Número de muestras por registro
TOLERANCIA = 1  # Umbral de reconocimiento

# Cargar base de datos
def cargar_base_datos():
    base_datos = defaultdict(dict)
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            try:
                data = json.load(f)
                for nombre, datos_usuario in data.items():
                    if isinstance(datos_usuario, list):
                        muestras = [np.array(m) for m in datos_usuario]
                        base_datos[nombre] = {
                            'muestras': muestras,
                            'timbre': Persona.default_ringtone
                        }
                    else:
                        muestras = [np.array(m) for m in datos_usuario.get('muestras', [])]
                        timbre = datos_usuario.get('timbre', Persona.default_ringtone)
                        base_datos[nombre] = {
                            'muestras': muestras,
                            'timbre': timbre
                        }
            except Exception as e:
                print(f"Error al cargar la base de datos: {e}")
    return base_datos

# Guardar base de datos
def guardar_base_datos(base_datos):
    datos_serializables = {}
    for nombre, datos_usuario in base_datos.items():
        muestras = datos_usuario.get('muestras', [])
        datos_serializables[nombre] = {
            'muestras': [m.tolist() for m in muestras] if muestras else [],
            'timbre': datos_usuario.get('timbre', Persona.default_ringtone)
        }
    with open(DATABASE_FILE, "w") as f:
        json.dump(datos_serializables, f, indent=4)

# Normalización de landmarks
def normalizar_landmarks(landmarks):
    landmarks = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
    nariz = landmarks[4]
    ojo_izquierdo = landmarks[468]
    ojo_derecho = landmarks[473]
    
    landmarks_normalizados = landmarks - nariz
    distancia_ojos = np.linalg.norm(ojo_derecho - ojo_izquierdo)
    if distancia_ojos > 0:
        landmarks_normalizados /= distancia_ojos
        
    return landmarks_normalizados

def cambiar_ringtone_global():

    print(f"Timbre global actual: {Persona.default_ringtone}")
    timbre = input(f"\nSeleccione uno de los timbres {list(Ringtone.names_dictionary.keys())}: ")
    if timbre in Ringtone.names_dictionary.keys():
        Persona.set_default_ringtone(timbre)
    else:
        print("Timbre no reconocido. Escriba una opción de las que se indique.")


# Proceso de registro
def registrar_usuario():
    nombre = input("\nIngrese el nombre del nuevo usuario: ")
    timbre = input(f"\nSeleccione uno de los timbres {list(Ringtone.names_dictionary.keys())}: ")
    base_datos = cargar_base_datos()
    
    if nombre in base_datos:
        print(f"⚠️  El nombre '{nombre}' ya existe. ¿Desea agregar más muestras? (s/n)")
        if input().lower() != 's':
            return

    cap = cv2.VideoCapture(0)
    muestras = []
    contador = 0
    
    print(f"\nCapturando {NUM_MUESTRAS} muestras...")
    print("Mueva su cabeza y manténgase con cara seria durante la captura")

    while contador < NUM_MUESTRAS:
        ret, frame = cap.read()
        if not ret:
            continue
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = face_mesh.process(rgb_frame)
        
        if resultados.multi_face_landmarks:
            for landmarks in resultados.multi_face_landmarks:
                landmarks_normalizados = normalizar_landmarks(landmarks.landmark)
                muestras.append(landmarks_normalizados)
                contador += 1
                
                cv2.putText(frame, f"Muestras: {contador}/{NUM_MUESTRAS}", 
                           (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
        cv2.imshow('Registro - Presione Q para cancelar', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    if len(muestras) >= NUM_MUESTRAS:
        if nombre in base_datos:
            base_datos[nombre]['muestras'].extend(muestras)
        else:
            base_datos[nombre] = {
                'muestras': muestras,
                'timbre': timbre
            }
        
        guardar_base_datos(base_datos)
        print(f"\n✅ Usuario '{nombre}' registrado exitosamente con {len(muestras)} muestras")
        
        if timbre in Ringtone.names_dictionary:
            Persona.add_persona(nombre, Ringtone.names_dictionary[timbre])
        else:
            print(f"⚠️  Timbre '{timbre}' no válido. Usando por defecto.")
            Persona.add_persona(nombre, Ringtone.names_dictionary[Persona.default_ringtone])
    else:
        print("\n❌ Registro cancelado o no se detectaron suficientes rostros")

# Proceso de reconocimiento (modificado con espera para desconocido)
def reconocer_usuario():
    base_datos = cargar_base_datos()
    if not base_datos:
        print("\n⚠️ Base de datos vacía. Registre usuarios primero.")
        return

    cap = cv2.VideoCapture(0)
    print("\nBuscando rostros... (Presione Q para salir)")
    
    reconocimiento_activo = True
    unknown_frames = 0
    unknown_threshold = 100  # Número de frames que se esperan antes de concluir desconocido

    while reconocimiento_activo:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = face_mesh.process(rgb_frame)

        if resultados.multi_face_landmarks:
            # Procesar solo la primera cara detectada
            landmarks = resultados.multi_face_landmarks[0]
            landmarks_actuales = normalizar_landmarks(landmarks.landmark)
            
            mejor_coincidencia = None
            menor_distancia = float('inf')
            
            for nombre, datos in base_datos.items():
                for muestra in datos['muestras'][::5]:
                    distancia = np.linalg.norm(muestra - landmarks_actuales)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        mejor_coincidencia = nombre

            # Si la cara es reconocida, reproducir la melodía elegida y salir
            if mejor_coincidencia and menor_distancia < TOLERANCIA:
                texto = f"{mejor_coincidencia} ({menor_distancia:.3f})"
                cv2.putText(frame, texto, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                try:
                    sd.stop()
                    # Se reproduce la melodía elegida para el usuario correspondiente
                    Persona.names_personas[mejor_coincidencia].play_ringtone()
                except Exception as e:
                    print(f"Error al reproducir: {str(e)}")
                reconocimiento_activo = False
            else:
                # Incrementar el contador de frames en los que la cara se detecta como desconocida
                unknown_frames += 1
                texto = "Desconocido"
                cv2.putText(frame, texto, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # Si se ha esperado suficientes frames, se reproduce la melodía por defecto
                if unknown_frames >= unknown_threshold:
                    try:
                        sd.stop()
                        if Persona.default_ringtone in Ringtone.names_dictionary:
                            Ringtone.names_dictionary[Persona.default_ringtone].play()
                        else:
                            print("Timbre por defecto no encontrado.")
                    except Exception as e:
                        print(f"Error al reproducir timbre por defecto: {str(e)}")
                    reconocimiento_activo = False
        else:
            # Si no se detecta ninguna cara, se reinicia el contador
            unknown_frames = 0

        cv2.imshow('Reconocimiento - Presione Q para salir', frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            reconocimiento_activo = False

    cap.release()
    cv2.destroyAllWindows()
    sd.stop()

def menu_principal():
    print("\n" + "="*30)
    print("Sistema de Reconocimiento Facial")
    print("1. Registrar nuevo usuario")
    print("2. Reconocimiento facial")
    print("3. Resetear toda la base de datos (borrar archivo JSON)")
    print("4. Cambiar timbre global")
    print("5. Salir")
    return input("Seleccione una opción: ")

def resetear_base_datos():
    confirmacion = input("\n¿Está seguro de BORRAR COMPLETAMENTE el archivo JSON con todos los datos? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            if os.path.exists(DATABASE_FILE):
                os.remove(DATABASE_FILE)
                Persona.personas.clear()
                Persona.names_personas.clear()
                print("\n✅ Archivo JSON eliminado exitosamente")
            else:
                print("\n⚠️  El archivo JSON no existía")
        except Exception as e:
            print(f"\n❌ Error al eliminar el archivo: {str(e)}")
    else:
        print("\n❌ Operación cancelada")

if __name__ == "__main__":
    base_datos = cargar_base_datos()
    for nombre, datos in base_datos.items():
        try:
            timbre = datos['timbre']
            if timbre in Ringtone.names_dictionary:
                Persona.add_persona(nombre, Ringtone.names_dictionary[timbre])
            else:
                Persona.add_persona(nombre, Ringtone.names_dictionary[Persona.default_ringtone])
        except KeyError:
            Persona.add_persona(nombre, Ringtone.names_dictionary[Persona.default_ringtone])

    while True:
        opcion = menu_principal()
        
        if opcion == '1':
            registrar_usuario()
        elif opcion == '2':
            reconocer_usuario()
        elif opcion == '3':
            resetear_base_datos()
        elif opcion == '4':
            cambiar_ringtone_global()
        elif opcion == '5':
            print("\n¡Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida. Intente nuevamente.")