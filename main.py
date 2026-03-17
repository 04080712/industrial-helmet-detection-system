import cv2
import numpy as np
import time
import logging
from datetime import datetime
from ultralytics import YOLO
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText # Widget de log com scroll
from PIL import Image, ImageTk

# ---------------------------------
# CONFIGURAÇÕES E LOGGING EXTERNO
# ---------------------------------
MODEL_PATH = "best.pt"
CONF_LEVEL = 0.45 

# Configura o log para salvar em arquivo .log
logging.basicConfig(
    filename='sistema_seguranca.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class DetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SENTRY VISION v3.2 - Monitoramento com Log de Eventos")
        self.root.geometry("1350x900")
        self.root.minsize(1200, 800)
        
        self.style = ttk.Style("darkly")
        
        # Estado lógico
        self.running = False
        self.last_status = "STANDBY" # Controle para evitar logs repetidos
        
        try:
            self.model = YOLO(MODEL_PATH)
            logging.info("Modelo YOLO carregado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao carregar o modelo: {e}")

        self.prev_time = 0
        self.fps = 0
        self.kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) 

        self.create_layout()
        self.add_log("Sistema iniciado e pronto para operação.", INFO)

    def add_log(self, message, level=INFO):
        """Adiciona uma mensagem ao widget de Log na UI e ao arquivo log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        # Insere na UI com cor baseada no nível
        bootstyle = SECONDARY
        if level == DANGER: bootstyle = DANGER
        if level == SUCCESS: bootstyle = SUCCESS
        if level == INFO: bootstyle = INFO
        
        self.log_widget.insert(END, formatted_msg, bootstyle)
        self.log_widget.see(END) # Faz o scroll automático
        
        # Salva no arquivo físico
        if level == DANGER: logging.warning(message)
        else: logging.info(message)

    def setup_camera(self):
        """Configura a câmera e loga as propriedades"""
        self.camera = cv2.VideoCapture(1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if self.camera.isOpened():
            self.add_log("Câmera conectada em Alta Definição (1080p).", SUCCESS)
        else:
            self.add_log("Falha ao conectar com a câmera!", DANGER)

    def create_layout(self):
        """Layout Estático com painel de Log inferior"""
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=True)

        # --- SIDEBAR DIREITA ---
        self.sidebar = ttk.Frame(self.main_frame, width=350)
        self.sidebar.pack(side=RIGHT, fill=Y, padx=(10, 0))
        self.sidebar.pack_propagate(False)

        # Status Badge
        status_top = ttk.Frame(self.sidebar)
        status_top.pack(fill=X, pady=5)
        self.cam_led = ttk.Label(status_top, text="●", font=("Helvetica", 22), foreground="red")
        self.cam_led.pack(side=LEFT)
        self.cam_text = ttk.Label(status_top, text=" SISTEMA OFFLINE", font=("Helvetica", 10, "bold"))
        self.cam_text.pack(side=LEFT, padx=5)

        self.alert_box = ttk.Label(
            self.sidebar, text="STANDBY", font=("Helvetica", 22, "bold"),
            anchor=CENTER, padding=25, bootstyle="secondary-inverse"
        )
        self.alert_box.pack(fill=X, pady=10)

        # Dashboard Métricas
        metrics_group = ttk.Labelframe(self.sidebar, text=" TELEMETRIA ", padding=15)
        metrics_group.pack(fill=X, pady=10)

        def add_metric(label, bootstyle):
            f = ttk.Frame(metrics_group)
            f.pack(fill=X, pady=5)
            ttk.Label(f, text=label, font=("Helvetica", 10)).pack(side=LEFT)
            val = ttk.Label(f, text="0", font=("Consolas", 14, "bold"), bootstyle=bootstyle)
            val.pack(side=RIGHT)
            return val

        self.ui_danger = add_metric("RISCOS DETECTADOS:", DANGER)
        self.ui_safe = add_metric("SEGUROS (OK):", SUCCESS)
        self.ui_fps = add_metric("FPS:", SECONDARY)

        # --- NOVO: LOG DE ATIVIDADES ---
        log_group = ttk.Labelframe(self.sidebar, text=" LOG DE EVENTOS ", padding=5)
        log_group.pack(fill=BOTH, expand=True, pady=10)
        
        self.log_widget = ScrolledText(log_group, height=10, font=("Consolas", 9), autohide=True)
        self.log_widget.pack(fill=BOTH, expand=True)

        # Botões
        self.btn_stop = ttk.Button(self.sidebar, text="⏹ PARAR MONITORAMENTO", bootstyle=DANGER, 
                                  command=self.stop, state=DISABLED, padding=10)
        self.btn_stop.pack(side=BOTTOM, fill=X, pady=5)
        
        self.btn_start = ttk.Button(self.sidebar, text="▶ INICIAR SISTEMA", bootstyle=SUCCESS, 
                                   command=self.start, padding=10)
        self.btn_start.pack(side=BOTTOM, fill=X, pady=5)

        # --- ÁREA DO VÍDEO ---
        self.video_container = ttk.Labelframe(self.main_frame, text=" MONITORAMENTO HD ", bootstyle=INFO)
        self.video_container.pack(side=LEFT, fill=BOTH, expand=True)
        self.video_container.pack_propagate(False)

        self.video_label = ttk.Label(self.video_container, background="#000")
        self.video_label.pack(fill=BOTH, expand=True, padx=2, pady=2)

    def start(self):
        if not self.running:
            self.setup_camera()
            self.running = True
            self.btn_start.config(state=DISABLED)
            self.btn_stop.config(state=NORMAL)
            self.cam_led.config(foreground="#00FF00")
            self.cam_text.config(text=" SISTEMA ONLINE")
            self.add_log("Monitoramento iniciado pelo usuário.", SUCCESS)
            self.update_frame()

    def stop(self):
        if self.running:
            self.running = False
            if hasattr(self, 'camera'): self.camera.release()
            self.btn_start.config(state=NORMAL)
            self.btn_stop.config(state=DISABLED)
            self.cam_led.config(foreground="red")
            self.cam_text.config(text=" SISTEMA OFFLINE")
            self.alert_box.config(text="OFFLINE", bootstyle="secondary-inverse")
            self.video_label.config(image="")
            self.add_log("Monitoramento interrompido pelo usuário.", WARNING)

    def process_frame(self, frame):
        frame = cv2.filter2D(frame, -1, self.kernel)
        results = self.model(frame, conf=CONF_LEVEL, verbose=False)

        count_safe, count_danger = 0, 0
        danger_in_frame = False

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = self.model.names[int(box.cls[0])].lower()
            
            if "no" in label or "head" in label:
                danger_in_frame, count_danger = True, count_danger + 1
                color, tag = (0, 0, 255), "RISCO: SEM CAPACETE"
            elif "helmet" in label:
                count_safe += 1
                color, tag = (0, 255, 0), "OK: CAPACETE"
            else:
                color, tag = (255, 255, 0), "PESSOA"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            cv2.putText(frame, tag, (x1, y1 - 10), 2, 0.5, color, 1)

        is_safe = not danger_in_frame
        
        # LOGICA DE LOG DE EVENTO (Apenas quando o status muda)
        new_status = "SAFE" if is_safe else "DANGER"
        if new_status != self.last_status:
            if not is_safe:
                self.add_log(f"VIOLAÇÃO DETECTADA: {count_danger} pessoa(s) sem EPI!", DANGER)
            elif is_safe and count_safe > 0:
                self.add_log("Ambiente normalizado. Todos com EPI.", SUCCESS)
            self.last_status = new_status

        # Borda de aviso
        if not is_safe:
            cv2.rectangle(frame, (0,0), (frame.shape[1], frame.shape[0]), (0,0,255), 15)
        
        return frame, is_safe, count_danger, count_safe

    def update_frame(self):
        if not self.running: return
        ret, frame = self.camera.read()
        if not ret: return

        processed, is_safe, c_danger, c_safe = self.process_frame(frame)

        # FPS
        curr_time = time.time()
        self.fps = 1 / (curr_time - self.prev_time) if (curr_time - self.prev_time) > 0 else 0
        self.prev_time = curr_time

        # Redimensionamento Estável
        tw, th = self.video_label.winfo_width(), self.video_label.winfo_height()
        if tw > 100:
            h, w = processed.shape[:2]
            scale = min(tw/w, th/h)
            processed = cv2.resize(processed, (int(w*scale), int(h*scale)))

        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)))
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

        # UI Update
        if not is_safe: self.alert_box.config(text="❌ INSEGURO", bootstyle="danger-inverse")
        elif c_safe > 0: self.alert_box.config(text="✅ SEGURO", bootstyle="success-inverse")
        else: self.alert_box.config(text="AGUARDANDO", bootstyle="secondary-inverse")

        self.ui_danger.config(text=str(c_danger))
        self.ui_safe.config(text=str(c_safe))
        self.ui_fps.config(text=f"{self.fps:.1f}")

        self.root.after(10, self.update_frame)

    def on_close(self):
        self.add_log("Finalizando aplicação...", INFO)
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    app_root = ttk.Window(themename="darkly")
    app = DetectionApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_close)
    app_root.mainloop()