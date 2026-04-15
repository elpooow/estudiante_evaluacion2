# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import sys
import platform
import datetime
import threading
import time
import re
import math
import urllib.request
import urllib.parse
import webbrowser
import tempfile
import pyttsx3
import random

try:
    from pydub import AudioSegment
    PYDUB_OK = True
except ImportError:
    PYDUB_OK = False

OS = platform.system()   # 'Windows', 'Darwin', 'Linux'


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
        self.hablando = False

        # ── TOP ──
        top_frame = tk.Frame(self.root, bg="#0a1128")
        top_frame.pack(fill="x", pady=(10, 0))

        self.canvas = tk.Canvas(top_frame, width=120, height=120,
                                bg="#0a1128", highlightthickness=0)
        self.canvas.pack()
        self.draw_orb()

        tk.Label(top_frame, text="J.A.R.V.I.S",
                 font=("Courier", 14, "bold"),
                 bg="#0a1128", fg="#00e5ff").pack(pady=(2, 6))

        # ── INPUT ──
        input_frame = tk.Frame(self.root, bg="#0a1128", pady=8)
        input_frame.pack(side="bottom", fill="x", padx=16)

        self.entry = tk.Entry(
            input_frame, font=("Arial", 12), bg="#0d2044", fg="#ffffff",
            insertbackground="#00e5ff", relief="flat",
            highlightthickness=2, highlightcolor="#00e5ff",
            highlightbackground="#1a3a6a"
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

        #Chatting
        self.chat = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Consolas", 11),
            bg="#060e1f", fg="#cce8ff", state="disabled",
            padx=14, pady=10, relief="flat",
            selectbackground="#003580"
        )
        self.chat.pack(padx=16, pady=(0, 4), fill="both", expand=True)

        self.chat.tag_config("jarvis", foreground="#00e5ff")
        self.chat.tag_config("user",   foreground="#7ec8ff")
        self.chat.tag_config("info",   foreground="#b0ffb0")
        self.chat.tag_config("sep",    foreground="#1a3a6a")

        self.init_voice_engine()
        threading.Thread(target=self.presentarse, daemon=True).start()
        self.root.mainloop()

    #Voz- Función de habla
    def init_voice_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 165)
            self.engine.setProperty("volume", 1.0)
            voices = self.engine.getProperty("voices")
            # Prioridad: voz en español, luego inglés UK, luego cualquiera
            for lang in ["spanish", "es_", "español"]:
                for v in voices:
                    if lang in v.name.lower() or lang in v.id.lower():
                        self.engine.setProperty("voice", v.id)
                        return
            for lang in ["uk", "british", "english"]:
                for v in voices:
                    if lang in v.name.lower() or lang in v.id.lower():
                        self.engine.setProperty("voice", v.id)
                        return
        except Exception as e:
            print(f"Motor de voz no disponible: {e}")
            self.engine = None

    def apply_jarvis_effect(self, audio_segment):
        """Baja el tono ligeramente para efecto robótico."""
        lowered = audio_segment._spawn(
            audio_segment.raw_data,
            overrides={"frame_rate": int(audio_segment.frame_rate * 0.87)}
        ).set_frame_rate(audio_segment.frame_rate)
        return lowered.reverse().apply_gain(-8).reverse()
    
    #Sistema de audio
    def speak(self, text):
        self.hablando = True
        """Reproduce voz en hilo separado usando ffplay (estable)."""
        if not self.engine:
            return

        def _run():
            temp_wav = None
            try:
                # Generar WAV con pyttsx3
                fd, temp_wav = tempfile.mkstemp(suffix='.wav', prefix='jarvis_')
                os.close(fd)
                self.engine.save_to_file(text, temp_wav)
                self.engine.runAndWait()

                if PYDUB_OK and os.path.exists(temp_wav):
                    sound = AudioSegment.from_wav(temp_wav)
                    jarvis_sound = self.apply_jarvis_effect(sound)
                    # Exportar a otro temporal para ffplay
                    fd2, temp_effect = tempfile.mkstemp(suffix='.wav', prefix='jarvis_eff_')
                    os.close(fd2)
                    jarvis_sound.export(temp_effect, format='wav')
                    # Reproducir con ffplay (silencioso, auto-salir)
                    subprocess.run(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', temp_effect],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.unlink(temp_effect)
                else:
                    # Fallback sin pydub: usar pyttsx3 directo
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                print(f"speak error: {e}")
                # Último intento
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except:
                    pass
            finally:
                self.hablando = False
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.unlink(temp_wav)
                    except:
                        pass

        threading.Thread(target=_run, daemon=True).start()

    # ═══════════════════════════════════════════════
    #  ORB ANIMADO
    # ═══════════════════════════════════════════════
    def draw_orb(self):
        self.canvas.delete("all")
        cx, cy, r = 60, 60, 46
        p = self.orb_pulse
        a = self.orb_angle

        self.canvas.create_oval(cx-r+6, cy-r+10, cx+r+6, cy+r+10,
                                fill="#000820", outline="")
        for i in range(r, 0, -1):
            ratio = i / r
            green = int(80  + 120 * (1 - ratio))
            blue  = int(160 + 95  * (1 - ratio))
            color = f"#00{green:02x}{blue:02x}"
            self.canvas.create_oval(cx-i, cy-i, cx+i, cy+i,
                                    fill=color, outline="")

        self.canvas.create_oval(cx-28, cy-32, cx+4, cy+2,
                                fill="#55eeff", outline="", stipple="gray25")
        self.canvas.create_oval(cx-22, cy-26, cx-2, cy-10,
                                fill="#aaffff", outline="", stipple="gray50")

        ring_y = cy + int(12 * math.sin(math.radians(a)))
        ring_r = int(r * abs(math.cos(math.radians(a))) * 0.85)
        glow = max(80, 255 - int(p * 100))
        if ring_r > 2:
            self.canvas.create_oval(cx-ring_r, ring_y-5, cx+ring_r, ring_y+5,
                                    outline=f"#00{glow:02x}ff", width=2)

        gw = 2 + int(2 * math.sin(math.radians(p * 180)))
        self.canvas.create_oval(cx-r-4, cy-r-4, cx+r+4, cy+r+4,
                                outline=f"#00{min(255,180+gw*20):02x}ff", width=gw)

        scan_y = cy - r + int((2 * r) * ((a % 360) / 360))
        half   = int(math.sqrt(max(0, r**2 - (scan_y - cy)**2)))
        if half > 4:
            self.canvas.create_line(cx-half, scan_y, cx+half, scan_y,
                                    fill="#00ffff", width=1, stipple="gray50")

        self.orb_angle = (a + 2) % 360
        self.orb_pulse = (p + 0.03) % 1
        #Lineas tipo grabadora
        self.audio_offset = getattr(self, "audio_offset", 0)
        if self.hablando:
            base_y = cy
            amplitud = 20

            puntos =[]
            for x in range(cx - 40, cx + 40, 4):
                y = base_y + random.randint(-amplitud, amplitud)
                puntos.append(x)
                puntos.append(y)

            self.canvas.create_line(
                puntos,
                fill = "#1e6402",
                width=2,
                smooth=True
            )

        self.root.after(40, self.draw_orb)

    # ═══════════════════════════════════════════════
    #CLEAR
    
    def limpiar_chat(self):
        """Borra todo el contenido del chat de forma segura."""
        def _clear():
            self.chat.config(state='normal')
            self.chat.delete(1.0, tk.END)
            self.chat.config(state='disabled')
        self.root.after(0, _clear)
    # ═══════════════════════════════════════════════
    #  MENSAJES UI
    # ═══════════════════════════════════════════════
    def msg(self, who, text, tag="jarvis"):
        def _insert():
            self.chat.config(state="normal")
            self.chat.insert(tk.END, f"{who}: ", "user" if who == "Usted" else tag)
            self.chat.insert(tk.END, f"{text}\n\n")
            self.chat.see(tk.END)
            self.chat.config(state="disabled")
        self.root.after(0, _insert)

    def sep(self):
        def _insert():
            self.chat.config(state="normal")
            self.chat.insert(tk.END, "─" * 60 + "\n\n", "sep")
            self.chat.config(state="disabled")
        self.root.after(0, _insert)

    # ═══════════════════════════════════════════════
    #  RED – fetch genérico
    # ═══════════════════════════════════════════════
    def fetch_url(self, url, timeout=12):
        req = urllib.request.Request(url, headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "es-PY,es;q=0.9,es-419;q=0.8"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")

    def limpiar_html(self, html):
        for tag in ["script","style","nav","footer","header","aside","form","button"]:
            html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', ' ', html,
                          flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<li[^>]*>', '\n• ', html, flags=re.IGNORECASE)
        html = re.sub(r'<p[^>]*>',  '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<h[1-6][^>]*>', '\n\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<[^>]+>', ' ', html)
        for e, r in [('&amp;','&'),('&quot;','"'),('&#x27;',"'"),('&lt;','<'),
                     ('&gt;','>'),('&nbsp;',' '),('&apos;',"'"),('&#39;',"'")]:
            html = html.replace(e, r)
        lines = [l.strip() for l in html.splitlines() if len(l.strip()) > 40]
        return "\n".join(lines[:60])

    # ═══════════════════════════════════════════════
    #  CLIMA – wttr.in (no necesita curl, usa urllib)
    # ═══════════════════════════════════════════════
    def obtener_clima(self):
        try:
            url = "https://wttr.in/Encarnacion,Paraguay?format=%C+%t+Humedad:%h+Viento:%w&lang=es"
            req = urllib.request.Request(url, headers={
                "User-Agent": "curl/7.68.0",
                "Accept-Language": "es"
            })
            with urllib.request.urlopen(req, timeout=8) as r:
                return r.read().decode("utf-8", errors="ignore").strip()
        except Exception:
            return "no disponible"

    # ═══════════════════════════════════════════════
    #  COTIZACIONES – Cambios Alberdi (py)
    # ═══════════════════════════════════════════════
    def obtener_cotizaciones(self):
        urls = [
            "https://www.cambiosalberdi.com/",
            "https://www.cambiosalberdi.com/cotizaciones",
            "https://cambio.com.py/cotizaciones",
        ]
        patrones = [
            (r'(?:USD|D[oó]lar)[^\d]{0,30}?([\d][,\.\d]+)',   'USD'),
            (r'(?:EUR|Euro)[^\d]{0,30}?([\d][,\.\d]+)',        'EUR'),
            (r'(?:ARS|Peso\s+Arg)[^\d]{0,30}?([\d][,\.\d]+)', 'ARS'),
            (r'(?:MXN|Peso\s+Mex)[^\d]{0,30}?([\d][,\.\d]+)', 'MXN'),
            (r'(?:PEN|Sol)[^\d]{0,30}?([\d][,\.\d]+)',         'PEN'),
            (r'(?:VES|Bol[ií]var)[^\d]{0,30}?([\d][,\.\d]+)', 'VES'),
            (r'(?:JPY|Yen)[^\d]{0,30}?([\d][,\.\d]+)',         'JPY'),
            (r'(?:BRL|Real)[^\d]{0,30}?([\d][,\.\d]+)',        'BRL'),
        ]
        for url in urls:
            try:
                html = self.fetch_url(url, timeout=10)
                resultado = {}
                for patron, moneda in patrones:
                    m = re.search(patron, html, re.IGNORECASE)
                    if m:
                        val_str = m.group(1).replace(".", "").replace(",", ".")
                        try:
                            resultado[moneda] = float(val_str)
                        except ValueError:
                            pass
                if resultado:
                    return resultado
            except Exception:
                continue
        return None

    def formatear_cotizaciones(self, cantidad_pyg, cotizaciones):
        lineas = [f"{cantidad_pyg:,.0f} PYG equivale aproximadamente a:\n"]
        nombres = {
            "USD": "Dólar (USD)",
            "EUR": "Euro (EUR)",
            "ARS": "Peso Argentino (ARS)",
            "MXN": "Peso Mexicano (MXN)",
            "PEN": "Sol Peruano (PEN)",
            "VES": "Bolívar (VES)",
            "JPY": "Yen Japonés (JPY)",
            "BRL": "Real Brasileño (BRL)",
        }
        for cod, nombre in nombres.items():
            if cod in cotizaciones and cotizaciones[cod] > 0:
                valor = cantidad_pyg / cotizaciones[cod]
                lineas.append(f"  {nombre}: {valor:,.4f}")
        if len(lineas) == 1:
            tasas = {"USD":7350,"EUR":7950,"ARS":8.5,"MXN":430,"PEN":1980,"VES":0.20,"JPY":49,"BRL":1470}
            lineas.append("  (Tasas de referencia – no se pudo conectar con Cambios Alberdi)")
            for cod, nombre in nombres.items():
                if cod in tasas:
                    valor = cantidad_pyg / tasas[cod]
                    lineas.append(f"  {nombre}: {valor:,.4f}")
        return "\n".join(lineas)

    # ═══════════════════════════════════════════════
    #  BÚSQUEDA WEB (DuckDuckGo → páginas reales)
    # ═══════════════════════════════════════════════
    def buscar_web(self, query):
        try:
            query_es = query + " en español"
            url_busq = ("https://html.duckduckgo.com/html/?q="
                        + urllib.parse.quote(query_es)
                        + "&kl=es-es")
            html_busq = self.fetch_url(url_busq)

            urls = re.findall(
                r'<a[^>]+class="result__url"[^>]*href="([^"]+)"', html_busq)
            if not urls:
                urls = re.findall(r'href="(https?://[^"&]+)"', html_busq)

            urls_limpias = []
            for u in urls:
                if "duckduckgo" in u:
                    continue
                if u.startswith("//"):
                    u = "https:" + u
                if u.startswith("http") and not any(
                        x in u for x in ["doubleclick","googlesyndication","amazon-adsystem"]):
                    urls_limpias.append(u)
                if len(urls_limpias) >= 3:
                    break

            if not urls_limpias:
                snippets = re.findall(
                    r'class="result__snippet"[^>]*>(.*?)</a', html_busq, re.DOTALL)
                def cl(s):
                    s = re.sub(r'<[^>]+>', '', s)
                    return re.sub(r'\s+', ' ', s).strip()
                snippets = [cl(s) for s in snippets if len(cl(s)) > 30][:5]
                return (f"Resultados para: {query}\n\n"
                        + "\n\n".join(snippets)) if snippets else "Sin resultados."

            resultados = []
            for u in urls_limpias:
                try:
                    html_pag = self.fetch_url(u)
                    texto    = self.limpiar_html(html_pag)
                    if len(texto) > 200:
                        resultados.append(f"[Fuente: {u[:70]}]\n{texto[:1500]}")
                except Exception:
                    continue

            if resultados:
                return (f"Informacion sobre: {query}\n{'='*50}\n\n"
                        + ("\n\n" + "─"*50 + "\n\n").join(resultados))
            return f"No se pudo obtener contenido para '{query}'."
        except Exception as e:
            return f"Error al buscar: {e}"

    # ═══════════════════════════════════════════════
    #  PRESENTACIÓN INICIAL
    # ═══════════════════════════════════════════════
    def presentarse(self):
        now   = datetime.datetime.now()
        hora  = now.hour
        saludo = ("Buenos dias" if hora < 12
                  else "Buenas tardes" if hora < 19
                  else "Buenas noches")
        fecha_str = now.strftime("%A %d de %B de %Y, hora: %H:%M")
        clima = self.obtener_clima()

        texto = (f"{saludo} senor.\n"
                 f"Soy J.A.R.V.I.S., su asistente personal.\n\n"
                 f"Hoy es {fecha_str}.\n\n"
                 f"Clima en Encarnacion, Paraguay:\n{clima}\n\n"
                 f"Todos los sistemas operativos. Listo para asistirle.\n\n"
                 f"Escriba 'ayuda' para ver los comandos disponibles.")
        self.msg("JARVIS", texto)
        self.speak(
            f"{saludo} senor. Soy JARVIS, su asistente personal. "
            f"Hoy es {fecha_str}. "
            f"El clima en Encarnacion es {clima}. "
            f"Listo para asistirle. "
            f"Escriba ayuda para ver los comandos disponibles."
        )

    # ═══════════════════════════════════════════════
    #  CONVERSIÓN DE MONEDAS
    # ═══════════════════════════════════════════════
    def convertir(self, lower):
        numeros = re.findall(r'[\d]+(?:[.,]\d+)?', lower)
        if not numeros:
            return "No encontre un numero. Ejemplo: convierte 150000 guaranies a dolares"
        cantidad = float(numeros[0].replace(",", "."))

        if any(x in lower for x in ["guarani", "guaranies", "pyg"]):
            self.msg("JARVIS", "Consultando cotizaciones del dia en Cambios Alberdi...")
            cot = self.obtener_cotizaciones()
            return self.formatear_cotizaciones(cantidad, cot or {})

        if any(x in lower for x in ["celsius a fahrenheit", "c a f", "centigrado"]):
            return f"{cantidad}°C = {cantidad * 9/5 + 32:.2f}°F"
        if any(x in lower for x in ["fahrenheit a celsius", "f a c"]):
            return f"{cantidad}°F = {(cantidad - 32) * 5/9:.2f}°C"

        if "km a metro" in lower:
            return f"{cantidad} km = {cantidad * 1000:,.0f} metros"
        if "metro a km" in lower:
            return f"{cantidad} metros = {cantidad / 1000:.4f} km"
        if "milla" in lower and "km" in lower:
            return f"{cantidad} millas = {cantidad * 1.60934:.3f} km"
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

        return ("No reconoci la conversion. Ejemplos:\n"
                "  convierte 100000 guaranies a dolares\n"
                "  convierte 25 C a F\n"
                "  convierte 5 km a metros\n"
                "  convierte 70 kg a lb")

    # ═══════════════════════════════════════════════
    #  ABRIR APLICACIONES (cross-platform)
    # ═══════════════════════════════════════════════
    def abrir_app(self, app):
        try:
            if app == "vscode":
                cmds = {
                    "Windows": ["code"],
                    "Darwin":  ["code"],
                    "Linux":   ["code"],
                }
                subprocess.Popen(cmds.get(OS, ["code"]))
            elif app == "notepad":
                if OS == "Windows":
                    subprocess.Popen(["notepad"])
                elif OS == "Darwin":
                    subprocess.Popen(["open", "-a", "TextEdit"])
                else:
                    for ed in ["gedit","kate","mousepad","xed","nano"]:
                        try:
                            subprocess.Popen([ed]); return
                        except FileNotFoundError:
                            continue
            return True
        except FileNotFoundError:
            return False

    # ═══════════════════════════════════════════════
    #  PROCESADOR DE COMANDOS
    # ═══════════════════════════════════════════════
    def procesar(self, comando):
        lower = comando.lower().strip()

        if any(x in lower for x in ["comandos", "ayuda", "help"]):
            r = ("Comandos disponibles:\n\n"
                 "• limpiar chat / clear\n\n"
                 "• clima\n"
                 "• fecha\n\n"
                 "Conversiones:\n"
                 "• convierte [N] guaranies  → muestra cotizaciones reales del dia\n"
                 "• convierte [N] C a F / F a C\n"
                 "• convierte [N] km a metros / millas a km\n"
                 "• convierte [N] kg a lb / lb a kg\n\n"
                 "Temporizador:\n"
                 "• temporizador [N] minutos / segundos / horas\n"
                 "• alarma [N] minutos\n\n"
                 "Codigos C:\n"
                 "• crea hola mundo / bucle for / bucle while\n"
                 "• crea factorial / fibonacci / tabla / primo / if else\n\n"
                 "Busqueda:\n"
                 "• busca [tema]  → abre Google en el navegador\n"
                 "• noticias / receta de X / dato curioso de X\n"
                 "• informacion sobre X / que es X / quien es X\n\n"
                 "Aplicaciones:\n"
                 "• abre navegador\n"
                 "• abre vscode\n"
                 "• abre bloc de notas\n\n"
                 "• crea carpeta [nombre]\n"
                 "• cerrar ventana")
            self.msg("JARVIS", r)
            self.speak("Aqui estan los comandos disponibles")
            return
        #===========================================================
        # CLEAR 
        #===========================================================
        if any(x in lower for x in ["clear", "limpiar", "borrar pantalla", "cls"]):
            self.limpiar_chat()
            self.msg("JARVIS", "Pantalla limpiada.")
            self.speak("Pantalla limpiada")
            return
        #============================================================
        #CONVERTIDOR
        #============================================================
        if any(x in lower for x in ["convierte", "convertir", "conversion"]):
            self.msg("JARVIS", self.convertir(lower))
            self.speak("Conversion realizada")
            return

        if any(x in lower for x in ["cotizacion", "dolar hoy", "tipo de cambio",
                                      "cambio alberdi", "precio dolar"]):
            self.msg("JARVIS", "Consultando Cambios Alberdi...")
            self.speak("Consultando cotizaciones")
            cot = self.obtener_cotizaciones()
            if cot:
                lineas = ["Cotizaciones del dia (Cambios Alberdi):\n"]
                nombres = {
                    "USD":"Dólar (USD)","EUR":"Euro (EUR)",
                    "ARS":"Peso Argentino (ARS)","MXN":"Peso Mexicano (MXN)",
                    "PEN":"Sol Peruano (PEN)","VES":"Bolívar (VES)",
                    "JPY":"Yen Japonés (JPY)","BRL":"Real Brasileño (BRL)",
                }
                for cod, nombre in nombres.items():
                    if cod in cot:
                        lineas.append(f"  1 {nombre} = {cot[cod]:,.2f} PYG")
                self.msg("JARVIS", "\n".join(lineas), "info")
            else:
                self.msg("JARVIS", "No se pudo conectar con Cambios Alberdi en este momento.")
            self.speak("Listo")
            return

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
                    fname = key.replace(" ", "_") + ".c"
                    if "en la carpeta" in lower:
                        try:
                            folder = lower.split("carpeta")[-1].strip().split()[0]
                            os.makedirs(folder, exist_ok=True)
                            fname  = os.path.join(folder, fname)
                        except Exception:
                            pass
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(codigo)
                    try:
                        subprocess.Popen(["code", fname])
                    except FileNotFoundError:
                        pass
                    self.msg("JARVIS", f"Codigo '{key}' creado: {fname}")
                    self.speak("Codigo creado")
                    return
            self.msg("JARVIS", "Codigo no reconocido. Pruebe: crea hola mundo, crea factorial, etc.")
            return

        if lower.startswith("busca"):
            query = re.sub(r'^busca[r]?\s+', '', lower).strip()
            if query:
                url = "https://www.google.com/search?q=" + urllib.parse.quote(query) + "&hl=es"
                webbrowser.open(url)
                self.msg("JARVIS", f"Abriendo Google: {query}")
                self.speak(f"Buscando {query} en Google")
            else:
                self.msg("JARVIS", "¿Que desea buscar?")
            return

        if "crea carpeta" in lower:
            partes = lower.split("carpeta")[-1].strip().split()
            nombre = partes[0] if partes else "nueva_carpeta"
            os.makedirs(nombre, exist_ok=True)
            self.msg("JARVIS", f"Carpeta '{nombre}' creada.")
            self.speak("Carpeta creada")
            return

        if "clima" in lower or "temperatura" in lower or "tiempo" in lower:
            clima = self.obtener_clima()
            self.msg("JARVIS", f"Clima en Encarnacion: {clima}")
            self.speak(f"Clima en Encarnacion: {clima}")
            return

        if any(x in lower for x in ["fecha", "dia", "hoy", "hora"]):
            now = datetime.datetime.now()
            r   = f"Hoy es {now.strftime('%A %d de %B de %Y')}, hora: {now.strftime('%H:%M')}"
            self.msg("JARVIS", r)
            self.speak(r)
            return

        if any(x in lower for x in ["temporizador", "alarma", "cronometro"]):
            try:
                nums = re.findall(r'\d+', lower)
                n    = int(nums[0]) if nums else 5
                if "hora" in lower:
                    segundos, etiqueta = n * 3600, f"{n} hora(s)"
                elif "segundo" in lower:
                    segundos, etiqueta = n, f"{n} segundo(s)"
                else:
                    segundos, etiqueta = n * 60, f"{n} minuto(s)"
                self.msg("JARVIS", f"Temporizador iniciado: {etiqueta}.")
                self.speak(f"Temporizador de {etiqueta} iniciado")
                def timer():
                    time.sleep(segundos)
                    self.msg("JARVIS", f"TIEMPO TERMINADO ({etiqueta})")
                    self.speak("Tiempo terminado senor")
                threading.Thread(target=timer, daemon=True).start()
            except Exception:
                self.msg("JARVIS", "Ejemplo: temporizador 30 minutos / 2 horas / 45 segundos")
            return

        if any(x in lower for x in ["noticia","receta","dato curioso","curiosidad",
                                      "informacion sobre","que es","quien es",
                                      "como se","evento","conmemora"]):
            self.msg("JARVIS", f"Buscando informacion sobre: {lower}...")
            self.speak("Buscando informacion")
            r = self.buscar_web(lower)
            self.sep()
            self.msg("JARVIS", r, "info")
            self.sep()
            self.speak("Listo")
            return

        if any(x in lower for x in ["abre navegador", "abre brave", "abre chrome",
                                      "abre firefox", "abre edge"]):
            webbrowser.open("https://www.google.com")
            self.msg("JARVIS", "Abriendo navegador predeterminado...")
            self.speak("Abriendo navegador")
            return

        if any(x in lower for x in ["vscode", "vs code", "abre code", "visual studio"]):
            ok = self.abrir_app("vscode")
            if ok:
                self.msg("JARVIS", "Abriendo Visual Studio Code.")
                self.speak("Abriendo Visual Studio Code")
            else:
                
                self.msg("JARVIS", "Visual Studio Code no encontrado. Verifique que este instalado.")
            return

        if any(x in lower for x in ["bloc de notas", "notepad", "abre editor"]):
            self.abrir_app("notepad")
            self.msg("JARVIS", "Abriendo editor de texto.")
            self.speak("Abriendo editor de texto")
            return

        if "cerrar ventana" in lower:
            if OS == "Linux":
                try:
                    subprocess.run(["xdotool", "key", "Alt+F4"])
                    self.msg("JARVIS", "Ventana cerrada.")
                except FileNotFoundError:
                    self.msg("JARVIS", "Instale xdotool para esta funcion en Linux.")
            elif OS == "Windows":
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
                self.msg("JARVIS", "Ventana cerrada.")
            elif OS == "Darwin":
                subprocess.run(["osascript", "-e",
                                'tell application "System Events" to keystroke "w" using command down'])
                self.msg("JARVIS", "Ventana cerrada.")
            return

        # DEFAULT → búsqueda informativa en español
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


if __name__ == "__main__":
    Jarvis()