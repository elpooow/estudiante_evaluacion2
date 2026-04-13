import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import datetime
import threading
import time
import re
import math
import urllib.request
import urllib.parse
import webbrowser
#Nuevas Librerias
import pyttsx3
import io
from pydub import AudioSegment
from pydub.playback import play
class Jarvis:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.geometry("900x650")
        self.root.configure(bg="#0a1128")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.orb_angle = 0
        self.orb_pulse = 0

        
        top_frame = tk.Frame(self.root, bg="#0a1128")
        top_frame.pack(fill="x", pady=(10, 0))

        self.canvas = tk.Canvas(top_frame, width=120, height=120, bg="#0a1128", highlightthickness=0)
        self.canvas.pack()
        self.draw_orb()

        tk.Label(top_frame, text="J.A.R.V.I.S", font=("Courier", 14, "bold"),
                 bg="#0a1128", fg="#00e5ff").pack(pady=(2, 6))


        input_frame = tk.Frame(self.root, bg="#0a1128", pady=8)
        input_frame.pack(side="bottom", fill="x", padx=16)

        self.entry = tk.Entry(
            input_frame, font=("Arial", 12), bg="#0d2044", fg="#ffffff",
            insertbackground="#00e5ff", relief="flat",
            highlightthickness=2, highlightcolor="#00e5ff", highlightbackground="#1a3a6a"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.enviar())
        self.entry.focus()

        tk.Button(
            input_frame, text="▶  ENVIAR", font=("Courier", 10, "bold"),
            bg="#003580", fg="#00e5ff", activebackground="#0055cc",
            activeforeground="#ffffff", relief="flat", padx=16, cursor="hand2",
            command=self.enviar
        ).pack(side="right")

        
        self.chat = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Consolas", 11),
            bg="#060e1f", fg="#cce8ff", state='disabled',
            padx=14, pady=10, relief="flat",
            selectbackground="#003580"
        )
        self.chat.pack(padx=16, pady=(0, 4), fill="both", expand=True)

        
        self.chat.tag_config("jarvis", foreground="#00e5ff")
        self.chat.tag_config("user",   foreground="#7ec8ff")
        self.chat.tag_config("info",   foreground="#b0ffb0")
        self.chat.tag_config("sep",    foreground="#1a3a6a")

        threading.Thread(target=self.presentarse, daemon=True).start()
        self.init_voice_engine()
        self.root.mainloop()
    #voz nueva
    def init_voice_engine(self):
        """Inicializa el motor de voz con la mejor voz disponible."""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 175)
        self.engine.setProperty('volume', 1.0)

        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'english' in voice.name.lower():
                if 'uk' in voice.id.lower() or 'british' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"Usando voz: {voice.name}")
                    break
        else:
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"Usando voz (fallback): {voice.name}")
                    break

def apply_jarvis_effect(self, audio_segment):
    """Aplica efectos para sonar como J.A.R.V.I.S."""
    lowered = audio_segment._spawn(audio_segment.raw_data, overrides={
        "frame_rate": int(audio_segment.frame_rate * 0.87)
    }).set_frame_rate(audio_segment.frame_rate)

    reverb = lowered.reverse().apply_gain(-8).reverse()
    return reverb
        
        

    def presentarse(self):
        now = datetime.datetime.now()
        hora = now.hour
        if hora < 12:
            saludo = "Buenos dias"
        elif hora < 19:
            saludo = "Buenas tardes"
        else:
            saludo = "Buenas noches"
        fecha_str = now.strftime('%A %d de %B de %Y, hora: %H:%M')
        try:
            clima = subprocess.check_output(
                ["curl", "-s", "wttr.in/Encarnacion?format=%C+%t+Humedad:%h+Viento:%w"],
                universal_newlines=True, timeout=8
            ).strip()
        except:
            clima = "no disponible"
        texto = (f"{saludo} senor.\n"
                 f"Soy J.A.R.V.I.S., su asistente personal.\n\n"
                 f"Hoy es {fecha_str}.\n\n"
                 f"Clima en Encarnacion, Paraguay:\n{clima}\n\n"
                 f"Todos los sistemas operativos. Listo para asistirle.\n\n"
                 f"Escriba `ayuda´ para ver los comandos")
        self.msg("JARVIS", texto)
        self.speak(
            f"{saludo} senor. Soy JARVIS su asistente personal. "
            f"Hoy es {fecha_str}. "
            f"El clima en Encarnacion es {clima}. "
            f"Listo para asistirle."
            f"Escriba ayuda para ver los comandos"
        )

    
    def draw_orb(self):
        self.canvas.delete("all")
        cx, cy, r = 60, 60, 46
        p = self.orb_pulse
        a = self.orb_angle

        
        self.canvas.create_oval(cx-r+6, cy-r+10, cx+r+6, cy+r+10,
                                fill="#000820", outline="")
        
        for i in range(r, 0, -1):
            ratio = i / r
            red   = int(0   + (0)   * ratio)
            green = int(80  + (120) * (1 - ratio))
            blue  = int(160 + (95)  * (1 - ratio))
            color = f"#{red:02x}{green:02x}{blue:02x}"
            self.canvas.create_oval(cx-i, cy-i, cx+i, cy+i, fill=color, outline="")

        
        self.canvas.create_oval(cx-28, cy-32, cx+4, cy+2,
                                fill="#55eeff", outline="", stipple="gray25")
        self.canvas.create_oval(cx-22, cy-26, cx-2, cy-10,
                                fill="#aaffff", outline="", stipple="gray50")

        
        ring_y = cy + int(12 * math.sin(math.radians(a)))
        ring_r = int(r * abs(math.cos(math.radians(a))) * 0.85)
        glow = max(80, 255 - int(p * 100))
        ring_color = f"#00{glow:02x}ff"
        if ring_r > 2:
            self.canvas.create_oval(cx - ring_r, ring_y - 5,
                                    cx + ring_r, ring_y + 5,
                                    outline=ring_color, width=2)

        
        gw = 2 + int(2 * math.sin(math.radians(p * 180)))
        self.canvas.create_oval(cx-r-4, cy-r-4, cx+r+4, cy+r+4,
                                outline=f"#00{min(255,180+gw*20):02x}ff",
                                width=gw)

        
        scan_y = cy - r + int((2 * r) * ((a % 360) / 360))
        half = int(math.sqrt(max(0, r**2 - (scan_y - cy)**2)))
        if half > 4:
            self.canvas.create_line(cx - half, scan_y, cx + half, scan_y,
                                    fill="#00ffff", width=1, stipple="gray50")

        self.orb_angle = (a + 2) % 360
        self.orb_pulse = (p + 0.03) % 1
        self.root.after(40, self.draw_orb)


    def msg(self, who, text, tag="jarvis"):
        self.chat.config(state='normal')
        if who == "Usted":
            tag = "user"
        self.chat.insert(tk.END, f"{who}: ", tag)
        self.chat.insert(tk.END, f"{text}\n\n")
        self.chat.see(tk.END)
        self.chat.config(state='disabled')

    def sep(self):
        self.chat.config(state='normal')
        self.chat.insert(tk.END, "─" * 60 + "\n\n", "sep")
        self.chat.config(state='disabled')

    def speak(self, text):
        """Genera y reproduce la voz con efectos de J.A.R.V.I.S."""
    def t():
        temp_file = "temp_jarvis.wav"
        try:
            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()

            sound = AudioSegment.from_wav(temp_file)
            jarvis_sound = self.apply_jarvis_effect(sound)
            play(jarvis_sound)

        except Exception as e:
            print(f"Error con efectos de voz: {e}")
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    threading.Thread(target=t, daemon=True).start()

    
    def fetch_url(self, url):
        """Descarga HTML de una URL."""
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120",
            "Accept-Language": "es-ES,es;q=0.9"
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read().decode("utf-8", errors="ignore")

    def limpiar_html(self, html):
        """Extrae texto legible de HTML."""
    
        for tag in ["script", "style", "nav", "footer", "header", "aside", "form", "button"]:
            html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
        
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<li[^>]*>', '\n• ', html, flags=re.IGNORECASE)
        html = re.sub(r'<p[^>]*>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<h[1-6][^>]*>', '\n\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<[^>]+>', ' ', html)
        
        for e, r in [('&amp;','&'),('&quot;','"'),('&#x27;',"'"),('&lt;','<'),
                     ('&gt;','>'),('&nbsp;',' '),('&apos;',"'"),('&#39;',"'")]:
            html = html.replace(e, r)
        
        lines = [l.strip() for l in html.splitlines() if len(l.strip()) > 40]
        return "\n".join(lines[:60])

    def buscar_web(self, query):
        """Busca en DuckDuckGo, entra a los primeros resultados y extrae contenido real."""
        try:
            
            url_busq = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
            html_busq = self.fetch_url(url_busq)

            
            urls = re.findall(r'<a[^>]+class="result__url"[^>]*href="([^"]+)"', html_busq)
            if not urls:
                urls = re.findall(r'href="(https?://[^"&]+)"', html_busq)

            
            urls_limpias = []
            for u in urls:
                if "duckduckgo" in u:
                    continue
                if u.startswith("//"):
                    u = "https:" + u
                if u.startswith("http") and not any(x in u for x in ["ad.doubleclick","googlesyndication","amazon-adsystem"]):
                    urls_limpias.append(u)
                if len(urls_limpias) >= 3:
                    break

            if not urls_limpias:
        
                snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a', html_busq, re.DOTALL)
                def cl(s):
                    s = re.sub(r'<[^>]+>','',s)
                    return re.sub(r'\s+',' ',s).strip()
                snippets = [cl(s) for s in snippets if len(cl(s)) > 30][:5]
                return f"Resultados para: {query}\n\n" + "\n\n".join(snippets) if snippets else "Sin resultados."

            
            resultados = []
            for u in urls_limpias:
                try:
                    html_pag = self.fetch_url(u)
                    texto = self.limpiar_html(html_pag)
                    if len(texto) > 200:
                    
                        resultados.append(f"[Fuente: {u[:60]}]\n{texto[:1500]}")
                except:
                    continue

            if resultados:
                return f"Informacion sobre: {query}\n{'='*50}\n\n" + "\n\n" + ("─"*50+"\n\n").join(resultados)
            else:
                return f"No se pudo obtener contenido para '{query}'."

        except Exception as e:
            return f"Error al buscar: {e}"

    
    def convertir(self, lower):
        
        numeros = re.findall(r'[\d]+(?:[.,]\d+)?', lower)
        if not numeros:
            return "No encontre un numero. Ejemplo: convierte 150000 guaranies a dolares"
        cantidad = float(numeros[0].replace(",", "."))

        
        if any(x in lower for x in ["guarani", "guaranies", "pyg"]):
            return (f"{cantidad:,.0f} PYG equivale a:\n"
                    f"  {cantidad * 0.000135:.4f} USD (dolar)\n"
                    f"  {cantidad * 0.000124:.4f} EUR (euro)\n"
                    f"  {cantidad * 0.135:.2f}   ARS (peso arg)\n"
                    f"  {cantidad * 0.000490:.4f} BRL (real)\n"
                    f"  {cantidad * 0.00135:.4f}  BOB (boliviano)\n"
                    f"  {cantidad * 0.000900:.4f} USD black (aprox)")

        
        if "dolar" in lower or "usd" in lower:
            if "guarani" in lower or "pyg" in lower:
                return f"{cantidad} USD = {cantidad / 0.000135:,.0f} PYG"
            return f"{cantidad} USD = {cantidad / 0.000135:,.0f} PYG"

        
        if any(x in lower for x in [" c a f", "celsius a fahrenheit", "centigrado"]):
            return f"{cantidad}°C = {cantidad * 9/5 + 32:.2f}°F"
        if any(x in lower for x in [" f a c", "fahrenheit a celsius"]):
            return f"{cantidad}°F = {(cantidad - 32) * 5/9:.2f}°C"

        
        if "km a metro" in lower or "kilometro" in lower:
            return f"{cantidad} km = {cantidad * 1000:,.0f} metros"
        if "metro a km" in lower:
            return f"{cantidad} metros = {cantidad / 1000:.4f} km"
        if "milla" in lower and "km" in lower:
            return f"{cantidad} millas = {cantidad * 1.60934:.3f} km"
        if "km" in lower and "milla" in lower:
            return f"{cantidad} km = {cantidad / 1.60934:.3f} millas"
        if "pie" in lower or "feet" in lower or "foot" in lower:
            return f"{cantidad} pies = {cantidad * 0.3048:.3f} metros"
        if "pulgada" in lower or "inch" in lower:
            return f"{cantidad} pulgadas = {cantidad * 2.54:.3f} cm"

        
        if "kg a lb" in lower or "kilo a libra" in lower:
            return f"{cantidad} kg = {cantidad * 2.20462:.3f} libras"
        if "lb a kg" in lower or "libra a kilo" in lower:
            return f"{cantidad} lb = {cantidad * 0.453592:.3f} kg"
        if "gramo a oz" in lower:
            return f"{cantidad} g = {cantidad * 0.035274:.4f} oz"

        return (f"No reconoci la conversion. Ejemplos:\n"
                f"  convierte 100000 guaranies a dolares\n"
                f"  convierte 25 C a F\n"
                f"  convierte 5 km a metros\n"
                f"  convierte 70 kg a lb")

    
    def procesar(self, comando):
        lower = comando.lower().strip()

        
        if any(x in lower for x in ["comandos", "ayuda", "help"]):
            r = ("Comandos:\n\n"
                 "• clima\n• fecha\n\n"
                 "• convierte [cantidad] guaranies a dolares/euros/etc\n"
                 "• convierte [cantidad] C a F\n"
                 "• convierte [cantidad] km a metros\n"
                 "• convierte [cantidad] kg a lb\n\n"
                 "• temporizador [N] minutos/segundos/horas\n"
                 "• alarma [N] minutos\n\n"
                 "Codigos C:\n"
                 "• crea hola mundo / bucle for / bucle while\n"
                 "• crea factorial / fibonacci / tabla / primo / if else\n\n"
                 "Busqueda (info real dentro de esta ventana):\n"
                 "• busca [cualquier cosa]\n"
                 "• noticias / receta de X / dato curioso de X\n\n"
                 "• abre brave / abre vscode\n"
                 "• crea carpeta [nombre]\n"
                 "• cerrar ventanas")
            self.msg("JARVIS", r)
            self.speak("Aqui estan los comandos disponibles")
            return

        
        if "convierte" in lower or "convertir" in lower or "conversion" in lower:
            self.msg("JARVIS", self.convertir(lower))
            self.speak("Conversion realizada")
            return
        
        #creador de codigos C:
        if any(x in lower for x in ["crea", "genera"]) and "carpeta" not in lower:
            templates = {
                "hola mundo":  '#include <stdio.h>\n\nint main() {\n    printf("Hola Mundo.\\n");\n    return 0;\n}\n',
                "bucle for":   '#include <stdio.h>\n\nint main() {\n    for(int i=1;i<=10;i++)\n        printf("i=%d\\n",i);\n    return 0;\n}\n',
                "bucle while": '#include <stdio.h>\n\nint main() {\n    int i=1;\n    while(i<=10){printf("i=%d\\n",i);i++;}\n    return 0;\n}\n',
                "factorial":   '#include <stdio.h>\n\nint main() {\n    int n=5,f=1;\n    for(int i=1;i<=n;i++) f*=i;\n    printf("Factorial de %d = %d\\n",n,f);\n    return 0;\n}\n',
                "fibonacci":   '#include <stdio.h>\n\nint main() {\n    int a=0,b=1,t;\n    printf("Fibonacci: ");\n    for(int i=0;i<10;i++){printf("%d ",a);t=a+b;a=b;b=t;}\n    printf("\\n");\n    return 0;\n}\n',
                "tabla":       '#include <stdio.h>\n\nint main() {\n    int n=7;\n    for(int i=1;i<=10;i++) printf("%d x %d = %d\\n",n,i,n*i);\n    return 0;\n}\n',
                "primo":       '#include <stdio.h>\n\nint main() {\n    int n=17,p=1;\n    for(int i=2;i<=n/2;i++) if(n%i==0){p=0;break;}\n    printf("%d %s primo.\\n",n,p?"es":"no es");\n    return 0;\n}\n',
                "if else":     '#include <stdio.h>\n\nint main() {\n    int n=10;\n    if(n>0) printf("Positivo.\\n");\n    else printf("Negativo o cero.\\n");\n    return 0;\n}\n',
            }
            for key, codigo in templates.items():
                if key in lower:
                    fname = key.replace(' ','_') + ".c"
                    if "en la carpeta" in lower:
                        try:
                            folder = lower.split("carpeta")[-1].strip().split()[0]
                            os.makedirs(folder, exist_ok=True)
                            fname = os.path.join(folder, fname)
                        except: pass
                    with open(fname, "w") as f:
                        f.write(codigo)
                    try: subprocess.Popen(["code", fname])
                    except: pass
                    self.msg("JARVIS", f"Codigo '{key}' creado: {fname}")
                    self.speak("Codigo creado y abierto en VS Code")
                    return
            self.msg("JARVIS", "Codigo no reconocido. Pruebe: crea hola mundo, crea factorial, etc.")
            return

        
        # Comando de búsqueda en navegador reemplazado
        if lower.startswith("busca"):
            query = re.sub(r'^busca[r]?\s+', '', lower).strip()
            if query:
                url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
                webbrowser.open(url)
                self.msg("JARVIS", f"Abriendo navegador con búsqueda: {query}")
                self.speak(f"Buscando {query} en internet")
            else:
                self.msg("JARVIS", "¿Qué deseas buscar?")
            return

        if "crea carpeta" in lower:
            nombre = lower.split("carpeta")[-1].strip().split()[0] if lower.split("carpeta")[-1].strip() else "nueva_carpeta"
            os.makedirs(nombre, exist_ok=True)
            self.msg("JARVIS", f"Carpeta '{nombre}' creada.")
            self.speak("Carpeta creada")
            return

        
        if "clima" in lower:
            try:
                out = subprocess.check_output(["curl","-s","wttr.in/Encarnacion?format=%C+%t"],
                                              universal_newlines=True, timeout=8).strip()
                self.msg("JARVIS", f"Clima en Encarnacion: {out}")
                self.speak(f"Clima en Encarnacion: {out}")
            except:
                self.msg("JARVIS", "No se pudo obtener el clima.")
            return

        # FECHA
        if "fecha" in lower or "dia" in lower or "hoy" in lower:
            now = datetime.datetime.now()
            r = f"Hoy es {now.strftime('%A %d de %B de %Y')}, hora: {now.strftime('%H:%M')}"
            self.msg("JARVIS", r)
            self.speak(r)
            return

        
        if "temporizador" in lower or "alarma" in lower or "cronometro" in lower:
            try:
                nums = re.findall(r'\d+', lower)
                n = int(nums[0]) if nums else 5
                if "hora" in lower:
                    segundos = n * 3600
                    etiqueta = f"{n} hora(s)"
                elif "segundo" in lower:
                    segundos = n
                    etiqueta = f"{n} segundo(s)"
                else:
                    segundos = n * 60
                    etiqueta = f"{n} minuto(s)"
                self.msg("JARVIS", f"Temporizador iniciado: {etiqueta}.")
                self.speak(f"Temporizador de {etiqueta} iniciado")
                def timer():
                    time.sleep(segundos)
                    self.msg("JARVIS", f"TIEMPO TERMINADO ({etiqueta})")
                    self.speak("Tiempo terminado senor")
                threading.Thread(target=timer, daemon=True).start()
            except:
                self.msg("JARVIS", "Ejemplo: temporizador 30 minutos / temporizador 2 horas / temporizador 45 segundos")
            return

        
        if any(x in lower for x in ["noticia","receta","dato curioso","curiosidad","informacion sobre","que es","quien es","como se","evento","conmemora"]):
            self.msg("JARVIS", f"Buscando informacion real sobre: {lower}...")
            self.speak("Buscando informacion")
            r = self.buscar_web(lower)
            self.sep()
            self.msg("JARVIS", r, "info")
            self.sep()
            self.speak("Listo")
            return

        
        if "abre brave" in lower or "abre navegador" in lower:
            webbrowser.open("https://www.google.com")
            self.msg("JARVIS", "Abriendo navegador...")
            self.speak("Abriendo navegador")
            return

        
        if any(x in lower for x in ["vscode","vs code","abre code"]):
            subprocess.Popen(["code"])
            self.msg("JARVIS", "Abriendo Visual Studio Code.")
            self.speak("Abriendo Visual Studio Code")
            return

        
        if "cerrar ventana" in lower:
            try:
                subprocess.run(["xdotool","key","Alt+F4"])
                self.msg("JARVIS", "Ventana cerrada.")
            except:
                self.msg("JARVIS", "Instale xdotool para esta funcion.")
            return

        
        self.msg("JARVIS", f"Buscando informacion sobre: {comando}...")
        self.speak("Buscando")
        r = self.buscar_web(comando)
        self.sep()
        self.msg("JARVIS", r, "info")
        self.sep()
        self.speak("Listo")

    def enviar(self):
        comando = self.entry.get().strip()
        if not comando:
            return
        self.msg("Usted", comando)
        self.entry.delete(0, tk.END)
        threading.Thread(target=self.procesar, args=(comando,), daemon=True).start()

    def on_closing(self):
        if messagebox.askokcancel("Cerrar JARVIS", "¿Desea cerrar JARVIS?"):
            self.root.destroy()

    def on_closing(self):
        if messagebox.askokcancel("Cerrar JARVIS", "Desea cerrar JARVIS?"):
            self.root.destroy()

if __name__ == "__main__":
    Jarvis()