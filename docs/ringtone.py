from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf


class Ringtone:

    directory = r"ringtones"
    ringtones = []
    names_dictionary = {}

    def __init__(self, name, wav_data, samplerate):
        self.name = name
        self.wav_data = wav_data
        self.samplerate = samplerate

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise ValueError("Name must be a string.")
        
    @property
    def wav_data(self):
        return self._wav_data
    
    @wav_data.setter
    def wav_data(self, value):
        if isinstance(value, np.ndarray):
            self._wav_data = value
        else:
            raise ValueError("wav_data must be a numpy array.")
        
    def play(self):
        sd.play(self._wav_data, self.samplerate)
        sd.wait()  # Ensures the sound plays completely

    @classmethod
    def pplay(cls, ringtone_name="Ringtone_1"):
        if ringtone_name in cls.names_dictionary:
            cls.names_dictionary[ringtone_name].play()
        else:
            raise ValueError(f"Ringtone {ringtone_name} not found.")

    @classmethod
    def get_ringtones(cls):
        if not cls.ringtones:
            cls.ringtones.clear()
            for idx, wav_path in enumerate(Path(cls.directory).glob("*.wav")):
                data, rate = sf.read(wav_path)
                cls.ringtones.append(Ringtone(f"Ringtone_{idx+1}", data, rate))
            cls.init_dictionary()

    @classmethod
    def add_ringtone(cls, wav_path, name="Custom"):
        data, rate = sf.read(wav_path)
        new_ring = Ringtone(name, data, rate)
        cls.ringtones.append(new_ring)
        cls.init_dictionary()

    @classmethod
    def init_dictionary(cls):
        cls.names_dictionary = {rt.name: rt for rt in cls.ringtones}

Ringtone.get_ringtones()
print(Ringtone.names_dictionary)