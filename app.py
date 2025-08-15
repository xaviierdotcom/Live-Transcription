import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sounddevice as sd
from RealtimeSTT import AudioToTextRecorder
import threading
import queue
import time
from pynput.keyboard import Controller

class LiveCaptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognition")
        self.root.geometry("900x700")
        self.root.configure(bg="#F7F7F7")
        
        self._setup_styles()
        self._create_ui()
        
        self.recorder = None
        self.th = None
        self.run = False
        self.q = queue.Queue()
        self.txt = ""
        self.keyboard = Controller()
        
        self.populate_devices()
        self.proc_q()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        
        styles = {
            'Title.TLabel': {'font': ('Segoe UI', 16, 'bold'), 'background': "#F7F7F7", 'foreground': "#1F2937"},
            'Heading.TLabel': {'font': ('Segoe UI', 11, 'bold'), 'background': "#FFFFFF", 'foreground': "#111827"},
            'Info.TLabel': {'font': ('Segoe UI', 9), 'background': "#FFFFFF", 'foreground': "#6B7280"},
            'Status.TLabel': {'font': ('Segoe UI', 10, 'bold'), 'background': "#F7F7F7", 'foreground': "#111827"},
            'Modern.TFrame': {'background': "#F7F7F7"},
            'Card.TFrame': {'background': "#FFFFFF", 'relief': "solid", 'borderwidth': 1},
            'Modern.TButton': {'font': ('Segoe UI', 10), 'padding': (12, 8), 'foreground': "#111827"},
            'Primary.TButton': {'font': ('Segoe UI', 10, 'bold'), 'padding': (15, 10), 'foreground': "#FFFFFF"},
            'Modern.TCombobox': {'font': ('Segoe UI', 10), 'fieldbackground': "#FFFFFF", 'foreground': "#111827"},
            'Modern.TCheckbutton': {'font': ('Segoe UI', 10), 'background': "#FFFFFF", 'foreground': "#111827"},
            'Danger.TButton': {'font': ('Segoe UI', 10, 'bold'), 'padding': (15, 10), 'foreground': "#FFFFFF"}
        }
        
        for style_name, config in styles.items():
            s.configure(style_name, **config)
        
        s.map('Modern.TButton',
              background=[('active', '#E5E7EB'), ('!active', '#F3F4F6'), ('disabled', '#F3F4F6')],
              foreground=[('disabled', '#9CA3AF')])
        s.map('Primary.TButton',
              background=[('active', '#1D4ED8'), ('!active', '#2563EB'), ('disabled', '#93C5FD')],
              foreground=[('disabled', '#E5E7EB')])
        s.map('Danger.TButton',
              background=[('active', '#B91C1C'), ('!active', '#DC2626'), ('disabled', '#FCA5A5')],
              foreground=[('disabled', '#FFFFFF')])
    
    def _create_ui(self):
        main = tk.Frame(self.root, bg="#F7F7F7", padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        main.grid_rowconfigure(2, weight=1)
        
        tf = tk.Frame(main, bg="#F7F7F7")
        tf.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(tf, text="Speech Recognition", style='Title.TLabel').pack(side=tk.LEFT)
        self.lbl = ttk.Label(tf, text="Ready", style='Status.TLabel', foreground="#10B981")
        self.lbl.pack(side=tk.RIGHT)
        
        cc = ttk.Frame(main, style='Card.TFrame', padding="20")
        cc.pack(fill=tk.X, pady=(0, 15))
        
        mf = tk.Frame(cc, bg="#FFFFFF")
        mf.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(mf, text="Microphone", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 8))
        self.cb = ttk.Combobox(mf, state="readonly", style='Modern.TCombobox', width=70)
        self.cb.pack(fill=tk.X)
        
        tf2 = tk.Frame(cc, bg="#FFFFFF")
        tf2.pack(fill=tk.X)
        th = tk.Frame(tf2, bg="#FFFFFF")
        th.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(th, text="Auto-Type", style='Heading.TLabel').pack(side=tk.LEFT)
        self.av = tk.BooleanVar()
        self.ac = ttk.Checkbutton(th, text="Enable Auto-Typing", variable=self.av, style='Modern.TCheckbutton')
        self.ac.pack(side=tk.RIGHT)
        ttk.Label(tf2, text="When enabled, transcribed text is typed into the active window", style='Info.TLabel').pack(anchor=tk.W)
        
        cf = tk.Frame(main, bg="#F7F7F7")
        cf.pack(fill=tk.X, pady=(0, 15))
        bf = tk.Frame(cf, bg="#F7F7F7")
        bf.pack(side=tk.LEFT)
        
        self.sb = ttk.Button(bf, text="Start", command=self.start_transcription, style='Primary.TButton')
        self.sb.pack(side=tk.LEFT, padx=(0, 10))
        self.stb = ttk.Button(bf, text="Stop", command=self.stop_transcription, state=tk.DISABLED, style='Modern.TButton')
        self.stb.pack(side=tk.LEFT, padx=(0, 10))
        self.clb = ttk.Button(bf, text="Clear", command=self.clear_text, style='Modern.TButton')
        self.clb.pack(side=tk.LEFT)
        
        sf = tk.Frame(cf, bg="#F7F7F7")
        sf.pack(side=tk.RIGHT)
        self.sl = ttk.Label(sf, text="Ready", style='Status.TLabel', foreground="#10B981")
        self.sl.pack()
        self.tl = ttk.Label(sf, text="Auto-Type: OFF", style='Status.TLabel', foreground="#757575")
        self.tl.pack()
        
        dc = ttk.Frame(main, style='Card.TFrame', padding="20")
        dc.pack(fill=tk.BOTH, expand=True)
        ch = tk.Frame(dc, bg="#FFFFFF")
        ch.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(ch, text="Speech Recognition", style='Heading.TLabel').pack(side=tk.LEFT)
        txf = tk.Frame(dc, bg="#FFFFFF")
        txf.pack(fill=tk.BOTH, expand=True)
        
        self.ta = scrolledtext.ScrolledText(txf, wrap=tk.WORD, font=("Consolas", 11), bg="#FFFFFF", fg="#1F2937", 
                                                  insertbackground="#1F2937", selectbackground="#E5E7EB", selectforeground="#111827", 
                                                  relief=tk.FLAT, borderwidth=0, padx=15, pady=15)
        self.ta.pack(fill=tk.BOTH, expand=True)
        self.add_welcome_message()
        self.av.trace('w', self.update_typing_status)
    
    def add_welcome_message(self):
        msg = "Click Start to begin.\n\n" + "=" * 60 + "\n\n"
        self.ta.insert(tk.END, msg)
    
    def update_typing_status(self, *args):
        on = self.av.get()
        self.tl.config(text=f"Auto-Type: {'ON' if on else 'OFF'}", 
                                 foreground="#10B981" if on else "#757575")
    
    def populate_devices(self):
        try:
            devs = sd.query_devices()
            inp = [f"{i}: {d['name']}" for i, d in enumerate(devs) if d['max_input_channels'] > 0]
            self.cb['values'] = inp
            
            if inp:
                try:
                    dd = sd.query_devices(kind='input')
                    dn = f"{sd.default.device[0]}: {dd['name']}"
                    self.cb.set(dn if dn in inp else inp[0])
                except:
                    self.cb.current(0)
            else:
                messagebox.showerror("Error", "No input devices found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enumerate audio devices: {str(e)}")
    
    def get_device_index(self):
        sel = self.cb.get()
        if not sel:
            return None
        try:
            return int(sel.split(':')[0])
        except:
            return None
    
    def start_transcription(self):
        idx = self.get_device_index()
        if idx is None:
            messagebox.showerror("Error", "Please select a microphone.")
            return
        
        try:
            self.sb.config(state=tk.DISABLED)
            self.stb.config(state=tk.NORMAL, style='Danger.TButton')
            self.sb.config(style='Modern.TButton')
            self.stb.focus_set()
            self.sl.config(text="Starting...", foreground="#F59E0B")
            self.ta.delete(1.0, tk.END)
            self.run = True
            
            if idx is not None:
                try:
                    cur = sd.default.device
                    out = cur[1] if isinstance(cur, (list, tuple)) and len(cur) > 1 else None
                except:
                    out = None
                sd.default.device = (idx, out)
            
            self.recorder = AudioToTextRecorder()
            try:
                if hasattr(self.recorder, "start") and callable(getattr(self.recorder, "start")):
                    self.recorder.start()
            except:
                pass
            
            self.txt = ""
            self.th = threading.Thread(target=self.transcribe_audio, daemon=True)
            self.th.start()
            self.sl.config(text="Recording...", foreground="#EF4444")
        except Exception as e:
            self.stop_transcription()
            messagebox.showerror("Error", f"Failed to start transcription: {str(e)}")
    
    def transcribe_audio(self):
        try:
            while self.run:
                if self.recorder:
                    txt = self.recorder.text()
                    if txt is not None:
                        cl = txt.strip()
                        if cl and cl != self.txt:
                            self.txt = cl
                            ts = time.strftime("%H:%M:%S")
                            fmt = f"[{ts}] {cl}\n"
                            self.q.put(('display', fmt))
                            if self.av.get():
                                self.q.put(('type', cl))
                time.sleep(0.1)
        except Exception as e:
            if self.run:
                self.q.put(('display', f"ERROR: {str(e)}\n"))
    
    def proc_q(self):
        try:
            while True:
                itm = self.q.get_nowait()
                if isinstance(itm, tuple):
                    act, con = itm
                    if act == 'display':
                        self.ta.insert(tk.END, con)
                        self.ta.see(tk.END)
                        self.ta.update_idletasks()
                    elif act == 'type':
                        self.auto_type_text(con)
                else:
                    self.ta.insert(tk.END, itm)
                    self.ta.see(tk.END)
                    self.ta.update_idletasks()
        except queue.Empty:
            pass
        self.root.after(100, self.proc_q)
    
    def auto_type_text(self, txt):
        try:
            time.sleep(0.1)
            self.keyboard.type(f"{txt} ")
        except Exception as e:
            self.q.put(('display', f"Auto-type error: {str(e)}\n"))
    
    def stop_transcription(self):
        self.run = False
        if self.recorder:
            try:
                self.recorder.stop()
            except:
                pass
            self.recorder = None
        if self.th and self.th.is_alive():
            self.th.join(timeout=2.0)
        
        self.sb.config(state=tk.NORMAL, style='Primary.TButton')
        self.stb.config(state=tk.DISABLED, style='Modern.TButton')
        self.sb.focus_set()
        self.sl.config(text="Ready", foreground="#10B981")
    
    def clear_text(self):
        self.ta.delete(1.0, tk.END)
        self.add_welcome_message()
    
    def on_close(self):
        self.stop_transcription()
        self.root.quit()
        self.root.destroy()

def main():
    deps = ['faster_whisper', 'RealtimeSTT', 'sounddevice', 'torch']
    try:
        for dep in deps:
            __import__(dep)
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install faster-whisper RealtimeSTT sounddevice torch")
        return
    
    root = tk.Tk()
    root.minsize(600, 500)
    app = LiveCaptionApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_close()

if __name__ == "__main__":
    main()
