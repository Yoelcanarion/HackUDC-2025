import tkinter as tk
from tkinter import ttk, messagebox
import threading
from main import *

class FacialRecognitionGUI:
    """GUI implementation for facial recognition system with ringtone capabilities"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bell ID")
        self.root.configure(bg='black')
        self.recognition_active = False
        self.setup_gui()

    def setup_gui(self):
        """Initialize and configure all GUI elements"""
        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        # Main action buttons
        ttk.Button(frame, text="Registrar Usuario", command=self.register_user).pack(fill='x', pady=5)
        ttk.Button(frame, text="Reconocimiento Facial", command=self.recognize_wrapper).pack(fill='x', pady=5)
        ttk.Button(frame, text="Resetear Base de Datos", command=self.reset_database).pack(fill='x', pady=5)

        # Global ringtone selector
        ringtone_frame = ttk.Frame(frame)
        ringtone_frame.pack(fill='x', pady=10)

        ttk.Label(ringtone_frame, text="Timbre Global:").pack(side='left')
        self.ringtone_var = tk.StringVar(value=Persona.default_ringtone)
        self.ringtone_combo = ttk.Combobox(ringtone_frame, 
                                         textvariable=self.ringtone_var,
                                         values=list(Ringtone.names_dictionary.keys()),
                                         state='readonly')
        self.ringtone_combo.pack(side='left', padx=5)
        
        ttk.Button(ringtone_frame, text="Probar Sonido", 
                  command=self.test_sound).pack(side='left', padx=5)
        
        self.ringtone_combo.bind('<<ComboboxSelected>>', self.change_global_ringtone)

    def reset_database(self):
        """Handle database reset with confirmation dialog"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de BORRAR COMPLETAMENTE la base de datos?"):
            try:
                if os.path.exists(DATABASE_FILE):
                    os.remove(DATABASE_FILE)
                    Persona.personas.clear()
                    Persona.names_personas.clear()
                    messagebox.showinfo("Éxito", "Base de datos eliminada exitosamente")
                else:
                    messagebox.showwarning("Aviso", "No existe base de datos para eliminar")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar la base de datos: {str(e)}")

    def test_sound(self):
        """Play selected ringtone in a separate thread"""
        sd.stop()
        selected = self.ringtone_var.get()
        threading.Thread(target=lambda: Ringtone.pplay(selected), daemon=True).start()

    def change_global_ringtone(self, event=None):
        """Update system's default ringtone"""
        Persona.set_default_ringtone(self.ringtone_var.get())

    def register_user(self):
        """Open registration window and handle user registration process"""
        def start_registration():
            nombre = nombre_entry.get().strip()
            timbre = timbre_var.get()
            if not nombre:
                messagebox.showerror("Error", "Ingrese un nombre")
                return
            
            registro_window.destroy()
            
            # Check for existing user
            base_datos = cargar_base_datos()
            if nombre in base_datos:
                if not messagebox.askyesno("Usuario Existente", 
                                         "El usuario ya existe. ¿Desea agregar más muestras?"):
                    return

            # Initialize video capture and sample collection
            cap = cv2.VideoCapture(0)
            muestras = []
            contador = 0
            
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

            # Process collected samples
            if len(muestras) >= NUM_MUESTRAS:
                if nombre in base_datos:
                    base_datos[nombre]['muestras'].extend(muestras)
                else:
                    base_datos[nombre] = {
                        'muestras': muestras,
                        'timbre': timbre
                    }
                
                guardar_base_datos(base_datos)
                
                if timbre in Ringtone.names_dictionary:
                    Persona.add_persona(nombre, Ringtone.names_dictionary[timbre])
                else:
                    Persona.add_persona(nombre, Ringtone.names_dictionary[Persona.default_ringtone])
                    
                messagebox.showinfo("Éxito", 
                                  f"Usuario '{nombre}' registrado exitosamente con {len(muestras)} muestras")
            else:
                messagebox.showwarning("Advertencia", 
                                     "Registro cancelado o no se detectaron suficientes rostros")

        # Setup registration window
        registro_window = tk.Toplevel(self.root)
        registro_window.title("Registro de Usuario")
        registro_window.configure(bg='black')
        
        frame = ttk.Frame(registro_window)
        frame.pack(padx=20, pady=20)
        
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, pady=5)
        nombre_entry = ttk.Entry(frame)
        nombre_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Timbre:").grid(row=1, column=0, pady=5)
        timbre_var = tk.StringVar(value=Persona.default_ringtone)
        timbre_combo = ttk.Combobox(frame, textvariable=timbre_var,
                                  values=list(Ringtone.names_dictionary.keys()),
                                  state='readonly')
        timbre_combo.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Iniciar Registro", 
                  command=start_registration).grid(row=2, column=0, columnspan=2, pady=10)

    def recognize_wrapper(self):
        """Manage facial recognition thread state"""
        if self.recognition_active:
            self.recognition_active = False
            return
        self.recognition_active = True
        threading.Thread(target=reconocer_usuario, daemon=True).start()

def main():
    """Initialize main application window and load user data"""
    root = tk.Tk()
    root.configure(bg='black')

    icon = tk.PhotoImage(file="icon.png")
    root.iconphoto(True, icon)
    
    # Load existing users and their ringtones
    base_datos = cargar_base_datos()
    for nombre, datos in base_datos.items():
        try:
            timbre = datos['timbre']
            Persona.add_persona(nombre, Ringtone.names_dictionary.get(timbre, 
                              Ringtone.names_dictionary[Persona.default_ringtone]))
        except KeyError:
            Persona.add_persona(nombre, Ringtone.names_dictionary[Persona.default_ringtone])
    
    app = FacialRecognitionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()