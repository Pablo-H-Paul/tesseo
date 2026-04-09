

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from google import genai
import pyperclip

# --- CONFIGURACIÓN ---
# Reemplaza con tu API KEY
# usada con el mail apellido nombre
API_KEY = "AIzaSyCBc_G44ZMXG_UJEmOb-bVRAzfOq0N9H5g"

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Error inicializando cliente: {e}")

# try 
class LinkedInApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tesseo Analytics - LinkedIn Post AI")
        self.root.geometry("600x800")

        self.incluir_iconos = tk.BooleanVar(value=True)
        self.incluir_hashtags = tk.BooleanVar(value=True)
        self.objetivo = tk.StringVar(value="Generar Engagement")
        self.modelo_seleccionado = tk.StringVar()

        self.setup_ui()
        self.cargar_modelos_seguro()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Selector de Modelo
        ttk.Label(main_frame, text="1. Seleccionar Modelo de Gemini:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.combo_modelos = ttk.Combobox(
            main_frame, textvariable=self.modelo_seleccionado, state="readonly")
        self.combo_modelos.pack(fill=tk.X, pady=(5, 15))

        # 2. Prompt Base
        ttk.Label(main_frame, text="2. Contexto del negocio / Tema:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.prompt_input = scrolledtext.ScrolledText(
            main_frame, height=5, wrap=tk.WORD)
        self.prompt_input.insert(
            tk.INSERT, """Somos dos socios, uno experto en Data Science y IA, otro socio experto en Logística y Compras (Supply Chain) tenemos una consultora con base en esas dos temáticas. Queremos ofrecer capacitaciones y servicios de asesoramiento en IA, logística, compras y Supply Chain. Nuestro perfil en Linkedin es https://www.linkedin.com/company/tesseo-analytics/ . Queremos que te comportes como un especialista en posicionamiento de empresas y marketing y nos diseñes un posteo para LinkedIn con temáticas actuales. Tener en cuenta previos posteos para no repetir temática.""")
        self.prompt_input.pack(fill=tk.X, pady=(5, 15))

        # 3. Opciones y Estrategia
        opts_frame = ttk.LabelFrame(
            main_frame, text="Configuración y Estrategia", padding="10")
        opts_frame.pack(fill=tk.X, pady=10)

        tk.Checkbutton(opts_frame, text="Emojis 🚀",
                       variable=self.incluir_iconos).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(opts_frame, text="Hashtags #",
                       variable=self.incluir_hashtags).pack(side=tk.LEFT, padx=10)

        ttk.Label(main_frame, text="Objetivo del Post:", font=(
            'Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        combo_obj = ttk.Combobox(
            main_frame, textvariable=self.objetivo, state="readonly")
        combo_obj['values'] = ("Generar Engagement",
                               "Viralizar",
                               "Aumentar Audiencia")
        combo_obj.pack(fill=tk.X, pady=(5, 15))

        # 4. Botón Generar
        self.btn_generar = ttk.Button(
            main_frame, text="GENERAR POSTEO ✨", command=self.generar_posteo)
        self.btn_generar.pack(fill=tk.X, pady=10)

        # 5. Resultado
        self.result_text = scrolledtext.ScrolledText(
            main_frame, height=12, wrap=tk.WORD, background="#f8f9fa")
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 6. Botón Copiar
        btn_copy = ttk.Button(
            main_frame, text="COPIAR TEXTO 📋", command=self.copiar_texto)
        btn_copy.pack(fill=tk.X, pady=10)

    def cargar_modelos_seguro(self):
        """Lista modelos de forma simplificada para evitar errores de atributos según versión."""
        try:
            modelos_disponibles = []
            # Listamos TODOS los modelos disponibles en la cuenta
            for m in client.models.list():
                # Extraemos el nombre ignorando los atributos de métodos para evitar el error
                nombre = m.name.split('/')[-1] if '/' in m.name else m.name

                # Filtro manual para no llenar la lista con modelos que no son de texto (como embeddings o bge)
                if "gemini" in nombre.lower():
                    modelos_disponibles.append(nombre)

            # Ordenamos para que los más nuevos (1.5) aparezcan arriba
            modelos_disponibles.sort(reverse=True)
            self.combo_modelos['values'] = modelos_disponibles

            # Prioridad de selección inicial
            preferidos = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            for p in preferidos:
                if p in modelos_disponibles:
                    self.combo_modelos.set(p)
                    break
            else:
                if modelos_disponibles:
                    self.combo_modelos.current(0)

        except Exception as e:
            messagebox.showerror("Error de Modelos",
                                 f"No se pudo conectar con la API: {str(e)}")

    def generar_posteo(self):
        if not self.modelo_seleccionado.get():
            messagebox.showwarning(
                "Aviso", "Por favor selecciona un modelo de la lista.")
            return

        try:
            self.btn_generar.config(state="disabled", text="Generando...")
            self.root.update_idletasks()

            prompt_final = f"""
            Genera un post de LinkedIn profesional para Tesseo Analytics.
            Tema/Contexto: {self.prompt_input.get("1.0", tk.END)}
            Objetivo: {self.objetivo.get()}
            Incluir Emojis: {self.incluir_iconos.get()}
            Incluir Hashtags: {self.incluir_hashtags.get()}
            ---
            Instrucciones de formato: Párrafos cortos, gancho inicial potente, tono experto pero accesible.
            Formato original, no como el típico posteo de LinkedIn. 
            Darle un toque más personal, que parezca más humano. 
            Devuelve únicamente el texto para publicar.
            """

            response = client.models.generate_content(
                model=self.modelo_seleccionado.get(),
                contents=prompt_final
            )

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.INSERT, response.text)

        except Exception as e:
            messagebox.showerror("Error", f"Detalle: {str(e)}")
        finally:
            self.btn_generar.config(state="normal", text="GENERAR POSTEO ✨")

    def copiar_texto(self):
        contenido = self.result_text.get("1.0", tk.END).strip()
        if contenido:
            pyperclip.copy(contenido)
            messagebox.showinfo("Tesseo AI", "¡Listo! Texto copiado.")


if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedInApp(root)
    root.mainloop()
