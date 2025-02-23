import numpy
import threading
import time
from pathlib import Path
import soundfile as sf
import sounddevice as sd
from ringtone import *

        
class Persona:

    personas = []
    names_personas = dict()
    default_ringtone = "Ringtone_3"

    def __init__(self, name, ringtone):

        self.name = name
        self.ringtone = ringtone

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise ValueError("Name must be a string type variable.")
        
    @property
    def ringtone(self):
        return self._ringtone
    
    @ringtone.setter
    def ringtone(self, value):
        if value in Ringtone.ringtones:
            self._ringtone = value
        else:
            raise ValueError("'ringtone' must be an instance of Ringtone class.")
        
    @classmethod
    def set_default_ringtone(cls, value: str):
        cls.default_ringtone = value

    def play_ringtone(self):
        self.ringtone.play()

    @classmethod
    def play_ringtone_safe(cls, nombre):
        """Reproduce el timbre en un hilo separado con control de estado"""
        if nombre in cls.names_personas:
            # Detener cualquier reproducción previa
            sd.stop()
            
            # Crear un hilo para la reproducción
            def play_thread():
                try:
                    cls.names_personas[nombre].ringtone.play()
                except Exception as e:
                    print(f"Error al reproducir: {str(e)}")
            
            threading.Thread(target=play_thread, daemon=True).start()
        else:
            print(f"⚠️ Timbre no configurado para {nombre}")

    @classmethod
    def update_dic(cls):
        names = [person.name for person in cls.personas]
        cls.names_personas = dict(zip(names, cls.personas))

    @classmethod
    def add_persona(cls, NAME, RINGTONE):
        cls.personas.append(Persona(NAME, RINGTONE))
        cls.update_dic()


