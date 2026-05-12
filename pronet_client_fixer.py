"""
ProNet Client Fixer v.02
Silkroad Online Client Yönetim Aracı
Yeni: Dil seçeneği, Tema, Launcher, Ping Monitör, Sunucu Durumu,
      Sistem tepsisi, Profil kaydetme, Çoklu sunucu, Otomatik güncelleme
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess, os, sys, threading, winreg, ctypes, platform
import socket, time, json, shutil, tempfile, urllib.request
from datetime import datetime
from pathlib import Path
import webbrowser

# ─── YÖNETİCİ ────────────────────────────────────────────────────────────────
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable," ".join(sys.argv),None,1)
        sys.exit()

# ─── TEMALAR ─────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG":"#0a0a0c","BG2":"#111114","BG3":"#161619","BG4":"#1c1c21",
        "BORDER":"#2a2a32","BORDER2":"#3a3a45",
        "ACCENT":"#e8a020","ACCENT2":"#ffb030",
        "GREEN":"#22c55e","RED":"#ef4444","YELLOW":"#eab308","BLUE":"#3b82f6","PURPLE":"#a855f7",
        "FG":"#e8e8f0","FG2":"#8888a0","FG3":"#505068",
        "WARN_BG":"#1a1500","WARN_FG":"#b08010","WARN_BD":"#3a3000",
        "LOG_BG":"#070709",
    },
    "light": {
        "BG":"#f0f0f5","BG2":"#e4e4ec","BG3":"#ffffff","BG4":"#ececf5",
        "BORDER":"#c8c8d8","BORDER2":"#a8a8c0",
        "ACCENT":"#c07010","ACCENT2":"#e08820",
        "GREEN":"#16a34a","RED":"#dc2626","YELLOW":"#ca8a04","BLUE":"#2563eb","PURPLE":"#9333ea",
        "FG":"#18181b","FG2":"#52525b","FG3":"#a1a1aa",
        "WARN_BG":"#fffbeb","WARN_FG":"#92400e","WARN_BD":"#fde68a",
        "LOG_BG":"#f8f8fc",
    }
}

# ─── DİL ─────────────────────────────────────────────────────────────────────
LANG = {
    "tr": {
        "title":"ProNet Client Fixer","admin":"YÖNETİCİ","no_admin":"YÖNETİCİ DEĞİL",
        "folder":"Klasör:","browse":"Gözat",
        "defender":"Defender","dep":"DEP","deps":"Bağımlılıklar","webview2":"WebView2",
        "tab_defender":"🛡  Defender","tab_dep":"⚙  DEP","tab_deps":"📦  Bağımlılıklar",
        "tab_client":"🎮  Client","tab_wv2":"🌐  WebView2","tab_tools":"🔧  Araçlar",
        "tab_net":"📡  Ağ Testi","tab_server":"🖥  Sunucu","tab_launcher":"🚀  Launcher",
        "tab_help":"❓  Yardım",
        "scan":"🔍 Tara","revert":"↩ Geri Al","start":"▶  Kurulumu Başlat","close":"✕ Kapat",
        "log_title":"📋  İŞLEM GÜNLÜĞÜ","clear":"Temizle",
        "active":"AKTİF","inactive":"KAPALI","unknown":"Bilinmiyor","installed":"Kurulu ✓","not_installed":"Kurulu Değil",
        "all_installed":"Tümü Kurulu","missing":"Eksik",
        "def_folder":"Klasörü Defender dışlamalarına ekle",
        "def_proc":"Klasördeki tüm .exe dosyalarını process dışlamasına ekle",
        "dep_disable":"DEP (Veri Yürütme Engellemesi) kapat",
        "auto_install":'"Kurulumu Başlat" sırasında eksik bağımlılıkları otomatik kur',
        "wv2_reinstall":"WebView2 yeniden kur (kaldır + registry temizle + indir + kur)",
        "warn":"Bu işlemler sistem güvenliğini azaltır. Sadece güvendiğiniz Silkroad sunucuları için uygulayın.",
        "dep_warn":"DEP global olarak kapatıldıktan sonra yeniden başlatma gerekir.",
        "no_folder":"Lütfen önce Silkroad klasörünü seçin!",
        "revert_confirm":"Defender dışlamaları ve DEP ayarları varsayılana döndürülecek. Emin misiniz?",
        "kill_blockers":"🚫 Engelleyen Uygulamaları Kapat",
        "kill_desc":"MSI Afterburner, Sandboxie, VM araçları,\nCheat Engine, Wireshark gibi çakışanlar.",
        "net_test":"📡 Ağ Kalitesi Testi","net_desc":"Gecikme, titreşim, paket kaybı\nave bant genişliğini ölçer.",
        "support":"📄 Destek Dosyası Oluştur","support_desc":"Log, sistem bilgisi ve durumu\ntek dosyaya masaüstüne kaydeder.",
        "admin_patch":"👑 Yönetici Uyumluluk Yaması","admin_desc":"Klasördeki tüm .exe dosyalarına\n'yönetici olarak çalıştır' yaması ekler.",
        "firewall":"🔥 Güvenlik Duvarı Kuralı","firewall_desc":"Klasördeki .exe dosyaları için\ngelen+giden Firewall izinleri ekler.",
        "update_check":"🔄 Güncelleme Kontrolü","update_desc":"Yeni sürüm varsa bildirim gösterilir.\nŞu anki sürüm: v.02",
        "run":"Çalıştır",
        "ping_monitor":"📡 Canlı Ping Monitörü","start_monitor":"▶ Monitörü Başlat","stop_monitor":"⏹ Durdur",
        "server_status":"🖥 Sunucu Durumu","check_server":"Kontrol Et","online":"🟢 Çevrimiçi","offline":"🔴 Çevrimdışı",
        "launcher_title":"🚀 Oyun Başlatıcı","launcher_desc":"Oyunu başlatmadan önce tüm kontroller yapılır.",
        "launcher_exe":"Launcher .exe:","launcher_browse":"Seç","launch_btn":"🚀 Oyunu Başlat",
        "pre_check":"Başlatmadan önce otomatik kontrol yap",
        "profile_save":"💾 Profili Kaydet","profile_load":"📂 Profil Yükle","profile_name":"Profil Adı:",
        "profiles":"Profiller","no_profiles":"Kayıtlı profil yok.",
        "theme_dark":"🌙 Karanlık","theme_light":"☀ Aydınlık",
        "lang_tr":"🇹🇷 Türkçe","lang_en":"🇬🇧 English",
        "sys_info":"💻 Sistem Bilgisi",
        "minimize_tray":"Tepside küçült",
        "tray_show":"Göster","tray_quit":"Çık",
        "update_available":"Yeni sürüm mevcut: {ver}! İndirmek ister misiniz?",
        "up_to_date":"En güncel sürüm kullanılıyor: v.02",
        "checking_update":"Güncelleme kontrol ediliyor…",
        "started":"başlatıldı.","scanning":"Sistem yeniden taranıyor…",
        "setup_start":"━━━ Kurulum başlatıldı ━━━","setup_done":"━━━ Kurulum tamamlandı ━━━",
        "revert_start":"Geri alma başlatıldı…","revert_done":"Geri alma tamamlandı.",
        "help_errors":"⚠  SIK KARŞILAŞILAN HATALAR","help_about":"📋  PROGRAM HAKKINDA",
        "about_text":"ProNet Client Fixer v.02\nSilkroad Online istemci yönetim ve onarım aracı.\nWindows 10/11 x64 — Yönetici yetkisi gerektirir.",
        "server_host":"Sunucu Adresi:","server_port":"Port:",
        "add_server":"+ Ekle","remove_server":"Sil",
        "ping_target":"Ping Hedefi:",
        "check_files":"📁 Dosyaları Kontrol Et",
        "download_missing":"⬇ Eksik Dosyaları İndir",
        "all_files_ok":"✓ Tüm zorunlu dosyalar mevcut.",
        "not_scanned":"Henüz tarama yapılmadı.",
        "install_dep":"⬇ İndir + Kur",
        "dep_current":"Mevcut DEP Durumu:",
        "wv2_current":"Mevcut Sürüm:",
        "rtp":"Real-Time Protection:","tamper":"Tamper Protection:",
        "defender_status":"ℹ  DEFENDER DURUMU",
        "dep_info":"Once global DEP kapatma denenir. Secure Boot açık olduğu için global kapatma başarısız olursa, klasördeki tüm .exe dosyaları için tek tek DEP istisnası eklenir.",
    },
    "en": {
        "title":"ProNet Client Fixer","admin":"ADMINISTRATOR","no_admin":"NOT ADMIN",
        "folder":"Folder:","browse":"Browse",
        "defender":"Defender","dep":"DEP","deps":"Dependencies","webview2":"WebView2",
        "tab_defender":"🛡  Defender","tab_dep":"⚙  DEP","tab_deps":"📦  Dependencies",
        "tab_client":"🎮  Client","tab_wv2":"🌐  WebView2","tab_tools":"🔧  Tools",
        "tab_net":"📡  Network","tab_server":"🖥  Server","tab_launcher":"🚀  Launcher",
        "tab_help":"❓  Help",
        "scan":"🔍 Scan","revert":"↩ Revert","start":"▶  Start Setup","close":"✕ Close",
        "log_title":"📋  OPERATION LOG","clear":"Clear",
        "active":"ACTIVE","inactive":"OFF","unknown":"Unknown","installed":"Installed ✓","not_installed":"Not Installed",
        "all_installed":"All Installed","missing":"Missing",
        "def_folder":"Add folder to Defender exclusions",
        "def_proc":"Add all .exe files to Defender process exclusions",
        "dep_disable":"Disable DEP (Data Execution Prevention)",
        "auto_install":"Auto-install missing dependencies on Setup Start",
        "wv2_reinstall":"Reinstall WebView2 (remove + clean registry + download + install)",
        "warn":"These operations reduce system security. Only apply for Silkroad servers you trust.",
        "dep_warn":"A restart is required after globally disabling DEP.",
        "no_folder":"Please select the Silkroad folder first!",
        "revert_confirm":"Defender exclusions and DEP settings will be reset to defaults. Are you sure?",
        "kill_blockers":"🚫 Close Blocking Apps",
        "kill_desc":"MSI Afterburner, Sandboxie, VM tools,\nCheat Engine, Wireshark, etc.",
        "net_test":"📡 Network Quality Test","net_desc":"Measures latency, jitter, packet loss\nand bandwidth.",
        "support":"📄 Create Support File","support_desc":"Saves log, system info and status\nto desktop in one file.",
        "admin_patch":"👑 Admin Compatibility Patch","admin_desc":"Adds permanent 'run as administrator'\nflag to all .exe files in folder.",
        "firewall":"🔥 Firewall Rules","firewall_desc":"Adds inbound+outbound Firewall\npermissions for .exe files in folder.",
        "update_check":"🔄 Check for Updates","update_desc":"Notifies if a new version is available.\nCurrent version: v.02",
        "run":"Run",
        "ping_monitor":"📡 Live Ping Monitor","start_monitor":"▶ Start Monitor","stop_monitor":"⏹ Stop",
        "server_status":"🖥 Server Status","check_server":"Check","online":"🟢 Online","offline":"🔴 Offline",
        "launcher_title":"🚀 Game Launcher","launcher_desc":"All checks are performed before launching the game.",
        "launcher_exe":"Launcher .exe:","launcher_browse":"Select","launch_btn":"🚀 Launch Game",
        "pre_check":"Auto-check before launching",
        "profile_save":"💾 Save Profile","profile_load":"📂 Load Profile","profile_name":"Profile Name:",
        "profiles":"Profiles","no_profiles":"No saved profiles.",
        "theme_dark":"🌙 Dark","theme_light":"☀ Light",
        "lang_tr":"🇹🇷 Türkçe","lang_en":"🇬🇧 English",
        "sys_info":"💻 System Info",
        "minimize_tray":"Minimize to tray",
        "tray_show":"Show","tray_quit":"Quit",
        "update_available":"New version available: {ver}! Do you want to download it?",
        "up_to_date":"You are using the latest version: v.02",
        "checking_update":"Checking for updates…",
        "started":"started.","scanning":"Re-scanning system…",
        "setup_start":"━━━ Setup started ━━━","setup_done":"━━━ Setup completed ━━━",
        "revert_start":"Reverting changes…","revert_done":"Revert completed.",
        "help_errors":"⚠  COMMON ERRORS","help_about":"📋  ABOUT",
        "about_text":"ProNet Client Fixer v.02\nSilkroad Online client management and repair tool.\nWindows 10/11 x64 — Requires administrator privileges.",
        "server_host":"Server Address:","server_port":"Port:",
        "add_server":"+ Add","remove_server":"Remove",
        "ping_target":"Ping Target:",
        "check_files":"📁 Check Files",
        "download_missing":"⬇ Download Missing",
        "all_files_ok":"✓ All required files are present.",
        "not_scanned":"No scan performed yet.",
        "install_dep":"⬇ Download + Install",
        "dep_current":"Current DEP Status:",
        "wv2_current":"Current Version:",
        "rtp":"Real-Time Protection:","tamper":"Tamper Protection:",
        "defender_status":"ℹ  DEFENDER STATUS",
        "dep_info":"Global DEP disable is attempted first. If Secure Boot prevents it, per-exe DEP exceptions are added for all .exe files in the folder.",
    }
}

# ─── AYARLAR DOSYASI ─────────────────────────────────────────────────────────
SETTINGS_FILE = Path.home() / ".pronet_fixer_settings.json"

def load_settings():
    defaults = {
        "theme": "dark", "lang": "tr", "folder": "",
        "launcher_exe": "", "pre_check": True,
        "minimize_tray": False,
        "servers": [
            {"name":"ProNet Main","host":"pronet-ro.com","port":15779},
            {"name":"Google DNS","host":"8.8.8.8","port":53},
        ],
        "profiles": {},
        "ping_target": "8.8.8.8",
        "chk_folder_excl": True, "chk_proc_excl": True,
        "chk_dep": True, "chk_auto_install": True, "chk_wv2": True,
    }
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text("utf-8"))
            defaults.update(data)
    except: pass
    return defaults

def save_settings(data):
    try: SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    except: pass


# ─── ANA UYGULAMA ─────────────────────────────────────────────────────────────
class ProNetFixer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings  = load_settings()
        self.theme     = self.settings.get("theme","dark")
        self.lang      = self.settings.get("lang","tr")
        self.C         = THEMES[self.theme]
        self.T         = LANG[self.lang]
        self.log_lines = []
        self.sys_info  = {}
        self.ping_running   = False
        self.ping_thread    = None
        self.server_widgets = []

        self.title(f"{self.T['title']} v.02")
        self.geometry("1020x760")
        self.minsize(900,660)
        self.configure(bg=self.C["BG"])
        self.resizable(True,True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.folder_var      = tk.StringVar(value=self.settings.get("folder",""))
        self.launcher_var    = tk.StringVar(value=self.settings.get("launcher_exe",""))
        self.ping_target_var = tk.StringVar(value=self.settings.get("ping_target","8.8.8.8"))
        self.pre_check_var   = tk.BooleanVar(value=self.settings.get("pre_check",True))
        self.minimize_tray_var = tk.BooleanVar(value=self.settings.get("minimize_tray",False))
        self.chk_folder_excl = tk.BooleanVar(value=self.settings.get("chk_folder_excl",True))
        self.chk_proc_excl   = tk.BooleanVar(value=self.settings.get("chk_proc_excl",True))
        self.chk_dep         = tk.BooleanVar(value=self.settings.get("chk_dep",True))
        self.chk_auto_install= tk.BooleanVar(value=self.settings.get("chk_auto_install",True))
        self.chk_wv2         = tk.BooleanVar(value=self.settings.get("chk_wv2",True))

        self._setup_style()
        self._build_ui()
        threading.Thread(target=self._initial_scan, daemon=True).start()

    # ── STİL ──────────────────────────────────────────────────────────────────
    def _setup_style(self):
        C = self.C
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".",background=C["BG"],foreground=C["FG"],font=("Segoe UI",9),borderwidth=0,relief="flat")
        s.configure("TNotebook",background=C["BG2"],borderwidth=0,tabmargins=[0,0,0,0])
        s.configure("TNotebook.Tab",background=C["BG2"],foreground=C["FG3"],padding=[12,7],font=("Segoe UI",9,"bold"),borderwidth=0)
        s.map("TNotebook.Tab",background=[("selected",C["BG3"]),("active",C["BG4"])],foreground=[("selected",C["ACCENT"]),("active",C["FG"])])
        s.configure("TFrame",background=C["BG"])
        s.configure("TLabel",background=C["BG"],foreground=C["FG"],font=("Segoe UI",9))
        s.configure("TCheckbutton",background=C["BG3"],foreground=C["FG"],font=("Segoe UI",9),selectcolor=C["BG3"])
        s.map("TCheckbutton",background=[("active",C["BG3"])],foreground=[("active",C["FG"])])
        s.configure("TScrollbar",background=C["BORDER"],troughcolor=C["BG2"],arrowcolor=C["FG3"],borderwidth=0)
        s.configure("TEntry",fieldbackground=C["BG"],foreground=C["FG"],insertcolor=C["FG"],borderwidth=1,relief="flat",font=("Consolas",9))
        s.configure("TCombobox",fieldbackground=C["BG"],background=C["BG3"],foreground=C["FG"],selectbackground=C["ACCENT"],font=("Segoe UI",9))

    # ── ANA UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        C,T = self.C,self.T
        self.configure(bg=C["BG"])

        # ── Başlık ──
        hbar = tk.Frame(self,bg=C["BG2"],height=46)
        hbar.pack(fill="x",side="top")
        hbar.pack_propagate(False)

        tk.Label(hbar,text="⚔",bg=C["BG2"],fg=C["ACCENT"],font=("Segoe UI",18)).pack(side="left",padx=(12,6),pady=6)
        tk.Label(hbar,text=T["title"],bg=C["BG2"],fg=C["FG"],font=("Segoe UI",13,"bold")).pack(side="left")
        tk.Label(hbar,text="v.02",bg=C["BG2"],fg=C["ACCENT"],font=("Segoe UI",9)).pack(side="left",padx=(4,0),pady=2)

        # Sağ: tema, dil, admin
        right = tk.Frame(hbar,bg=C["BG2"])
        right.pack(side="right",padx=10)

        # Tema butonu
        self.btn_theme = tk.Button(right,text=T["theme_light"] if self.theme=="dark" else T["theme_dark"],
            bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8),relief="flat",cursor="hand2",
            activebackground=C["ACCENT"],activeforeground="#000",padx=8,pady=3,
            command=self._toggle_theme)
        self.btn_theme.pack(side="left",padx=4)

        # Dil butonu
        self.btn_lang = tk.Button(right,text=T["lang_en"] if self.lang=="tr" else T["lang_tr"],
            bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8),relief="flat",cursor="hand2",
            activebackground=C["ACCENT"],activeforeground="#000",padx=8,pady=3,
            command=self._toggle_lang)
        self.btn_lang.pack(side="left",padx=4)

        admin_color = C["GREEN"] if is_admin() else C["RED"]
        admin_text  = f"● {T['admin']}" if is_admin() else f"● {T['no_admin']}"
        tk.Label(right,text=admin_text,bg=C["BG2"],fg=admin_color,font=("Segoe UI",8,"bold")).pack(side="left",padx=8)

        # ── Klasör satırı ──
        frow = tk.Frame(self,bg=C["BG2"],height=38)
        frow.pack(fill="x")
        frow.pack_propagate(False)
        tk.Label(frow,text=T["folder"],bg=C["BG2"],fg=C["FG3"],font=("Segoe UI",9,"bold")).pack(side="left",padx=(14,6),pady=8)
        entry = tk.Entry(frow,textvariable=self.folder_var,bg=C["BG"],fg=C["FG"],
            insertbackground=C["FG"],font=("Consolas",9),relief="flat",
            highlightthickness=1,highlightbackground=C["BORDER"],highlightcolor=C["ACCENT"])
        entry.pack(side="left",fill="x",expand=True,ipady=4)
        self._mkbtn(frow,T["browse"],self._browse,C["BG3"],C["FG2"]).pack(side="left",padx=(1,0),ipady=4)

        # ── Durum çubuğu ──
        sbar = tk.Frame(self,bg=C["BG2"],height=30)
        sbar.pack(fill="x")
        sbar.pack_propagate(False)
        self.lbl_defender = self._status_item(sbar,T["defender"],"...",C["YELLOW"])
        self._vsep(sbar)
        self.lbl_dep      = self._status_item(sbar,T["dep"],"...",C["YELLOW"])
        self._vsep(sbar)
        self.lbl_deps     = self._status_item(sbar,T["deps"],"...",C["YELLOW"])
        self._vsep(sbar)
        self.lbl_wv2      = self._status_item(sbar,T["webview2"],"...",C["YELLOW"])

        # ── Notebook ──
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both",expand=True)

        tabs = ["defender","dep","deps","client","wv2","tools","network","server","launcher","help"]
        self.tabs = {}
        for name in tabs:
            f = ttk.Frame(self.nb)
            self.tabs[name] = f
            self.nb.add(f,text=T.get(f"tab_{name}",name))

        self._build_defender_tab()
        self._build_dep_tab()
        self._build_deps_tab()
        self._build_client_tab()
        self._build_webview2_tab()
        self._build_tools_tab()
        self._build_network_tab()
        self._build_server_tab()
        self._build_launcher_tab()
        self._build_help_tab()

        # ── Log ──
        lf = tk.Frame(self,bg=C["BG2"])
        lf.pack(fill="x",side="bottom")
        lh = tk.Frame(lf,bg=C["BG2"])
        lh.pack(fill="x")
        tk.Label(lh,text=T["log_title"],bg=C["BG2"],fg=C["FG3"],font=("Segoe UI",7,"bold")).pack(side="left",padx=12,pady=4)
        self._mkbtn(lh,T["clear"],self._clear_log,C["BG3"],C["FG3"],font=("Segoe UI",7)).pack(side="right",padx=8,pady=3)
        self.log_box = tk.Text(lf,height=5,bg=C["LOG_BG"],fg=C["FG2"],font=("Consolas",9),
            relief="flat",state="disabled",wrap="word",padx=10,pady=6,selectbackground=C["BORDER"])
        self.log_box.pack(fill="x")
        for tag,col in [("ok",C["GREEN"]),("err",C["RED"]),("warn",C["YELLOW"]),("info",C["BLUE"]),("time",C["FG3"])]:
            self.log_box.tag_config(tag,foreground=col)

        # ── Alt butonlar ──
        bot = tk.Frame(self,bg=C["BG2"])
        bot.pack(fill="x",side="bottom")
        self._mkbtn(bot,T["scan"],self._scan_all,C["BG3"],C["FG2"]).pack(side="left",padx=(10,4),pady=8)
        self._mkbtn(bot,T["revert"],self._revert,"#2a1010",C["RED"]).pack(side="left",padx=4,pady=8)
        self._mkbtn(bot,T["close"],self.quit,C["BG3"],C["FG2"]).pack(side="right",padx=10,pady=8)
        self._mkbtn(bot,T["start"],self._run_setup,"#0d3320",C["GREEN"],font=("Segoe UI",10,"bold")).pack(side="right",padx=4,pady=8,ipadx=10)

    # ── SEKMELERİ İNŞA ET ────────────────────────────────────────────────────

    def _build_defender_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["defender"])
        c = self._card(sc,"🛡  "+T["tab_defender"].split("  ")[-1].upper())
        self._chk(c,T["def_folder"],self.chk_folder_excl)
        self._chk(c,T["def_proc"],self.chk_proc_excl)
        c2 = self._card(sc,"ℹ  "+T["defender_status"].split("  ")[-1])
        row = tk.Frame(c2,bg=C["BG3"])
        row.pack(fill="x")
        tk.Label(row,text=T["rtp"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).grid(row=0,column=0,sticky="w",padx=(0,16),pady=3)
        self.lbl_rtp=tk.Label(row,text="—",bg=C["BG3"],fg=C["YELLOW"],font=("Segoe UI",9,"bold"))
        self.lbl_rtp.grid(row=0,column=1,sticky="w")
        tk.Label(row,text=T["tamper"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).grid(row=1,column=0,sticky="w",padx=(0,16),pady=3)
        self.lbl_tamper=tk.Label(row,text="—",bg=C["BG3"],fg=C["YELLOW"],font=("Segoe UI",9,"bold"))
        self.lbl_tamper.grid(row=1,column=1,sticky="w")
        self._warn(sc,T["warn"])

    def _build_dep_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["dep"])
        c = self._card(sc,"⚙  DEP")
        row=tk.Frame(c,bg=C["BG3"]); row.pack(fill="x",pady=(0,10))
        tk.Label(row,text=T["dep_current"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        self.lbl_dep_status=tk.Label(row,text="…",bg=C["BG3"],fg=C["YELLOW"],font=("Segoe UI",9,"bold"))
        self.lbl_dep_status.pack(side="left",padx=8)
        tk.Label(c,text=T["dep_info"],bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8),justify="left").pack(anchor="w",pady=(0,8))
        self._chk(c,T["dep_disable"],self.chk_dep)
        self._warn(sc,T["dep_warn"])

    def _build_deps_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["deps"])
        c = self._card(sc,"📦  "+T["tab_deps"].split("  ")[-1].upper())
        self.deps_frame=tk.Frame(c,bg=C["BG3"]); self.deps_frame.pack(fill="x")
        bot=tk.Frame(c,bg=C["BG3"]); bot.pack(fill="x",pady=(10,0))
        tk.Frame(bot,bg=C["BORDER"],height=1).pack(fill="x",pady=(0,8))
        self._chk(bot,T["auto_install"],self.chk_auto_install)

    def _build_client_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["client"])
        c = self._card(sc,"🎮  CLIENT")
        tk.Label(c,text=T["not_scanned"],bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8)).pack(anchor="w",pady=(0,8))
        br=tk.Frame(c,bg=C["BG3"]); br.pack(anchor="w",pady=(0,10))
        self._mkbtn(br,T["check_files"],self._scan_client,C["ACCENT"],"#000").pack(side="left",padx=(0,8))
        self.client_result=scrolledtext.ScrolledText(c,height=12,bg=C["LOG_BG"],fg=C["FG2"],
            font=("Consolas",9),relief="flat",state="disabled",wrap="word",padx=8,pady=6)
        self.client_result.pack(fill="x")
        for tag,col in [("ok",C["GREEN"]),("miss",C["RED"]),("head",C["ACCENT"])]:
            self.client_result.tag_config(tag,foreground=col,font=("Consolas",9,"bold") if tag=="head" else None)

    def _build_webview2_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["wv2"])
        c = self._card(sc,"🌐  WEBVIEW2")
        row=tk.Frame(c,bg=C["BG3"]); row.pack(fill="x",pady=(0,8))
        tk.Label(row,text=T["wv2_current"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        self.lbl_wv2_ver=tk.Label(row,text="—",bg=C["BG3"],fg=C["YELLOW"],font=("Segoe UI",9,"bold"))
        self.lbl_wv2_ver.pack(side="left",padx=8)
        self._chk(c,T["wv2_reinstall"],self.chk_wv2)
        br=tk.Frame(c,bg=C["BG3"]); br.pack(anchor="w",pady=(10,0))
        self._mkbtn(br,T["wv2_reinstall"].split("(")[0].strip(),
            lambda:threading.Thread(target=self._reinstall_webview2,daemon=True).start(),
            "#0a1a2a",C["BLUE"]).pack(side="left")

    def _build_tools_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["tools"])
        grid=tk.Frame(sc,bg=C["BG"]); grid.pack(fill="both",padx=14,pady=8)
        tools=[
            (T["kill_blockers"],T["kill_desc"],self._kill_blockers,"#2a1010",C["RED"]),
            (T["support"],T["support_desc"],self._create_support_file,C["BG4"],C["FG2"]),
            (T["admin_patch"],T["admin_desc"],lambda:threading.Thread(target=self._apply_admin_compat,daemon=True).start(),C["BG4"],C["GREEN"]),
            (T["firewall"],T["firewall_desc"],lambda:threading.Thread(target=self._add_firewall_rules,daemon=True).start(),C["BG4"],C["BLUE"]),
            (T["update_check"],T["update_desc"],lambda:threading.Thread(target=self._check_update,daemon=True).start(),C["BG4"],C["ACCENT"]),
        ]
        for i,(title,desc,cmd,bg,fg) in enumerate(tools):
            row,col=divmod(i,2)
            f=tk.Frame(grid,bg=C["BG3"],bd=0); f.grid(row=row,column=col,padx=5,pady=5,sticky="nsew")
            tk.Frame(f,bg=C["BORDER"],height=1).pack(fill="x")
            inn=tk.Frame(f,bg=C["BG3"]); inn.pack(fill="x",padx=12,pady=10)
            tk.Label(inn,text=title,bg=C["BG3"],fg=C["FG"],font=("Segoe UI",9,"bold")).pack(anchor="w")
            tk.Label(inn,text=desc,bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8),justify="left").pack(anchor="w",pady=(4,8))
            self._mkbtn(inn,T["run"],cmd,bg,fg,font=("Segoe UI",8,"bold")).pack(anchor="w")
        grid.columnconfigure(0,weight=1); grid.columnconfigure(1,weight=1)

        # Profil Yönetimi
        pc=self._card(sc,"💾  PROFİL YÖNETİMİ" if self.lang=="tr" else "💾  PROFILE MANAGEMENT")
        pr=tk.Frame(pc,bg=C["BG3"]); pr.pack(fill="x",pady=(0,8))
        tk.Label(pr,text=T["profile_name"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        self.profile_name_var=tk.StringVar(value="Profil 1" if self.lang=="tr" else "Profile 1")
        tk.Entry(pr,textvariable=self.profile_name_var,bg=C["BG"],fg=C["FG"],
            insertbackground=C["FG"],font=("Segoe UI",9),relief="flat",
            highlightthickness=1,highlightbackground=C["BORDER"],width=20).pack(side="left",padx=8,ipady=3)
        self._mkbtn(pr,T["profile_save"],self._save_profile,C["BG4"],C["ACCENT"]).pack(side="left",padx=4)

        self.profiles_frame=tk.Frame(pc,bg=C["BG3"]); self.profiles_frame.pack(fill="x")
        self._refresh_profiles()

    def _build_network_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["network"])

        # Ping monitörü
        c=self._card(sc,"📡  "+T["ping_monitor"].split("  ")[-1])
        pr=tk.Frame(c,bg=C["BG3"]); pr.pack(fill="x",pady=(0,10))
        tk.Label(pr,text=T["ping_target"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        tk.Entry(pr,textvariable=self.ping_target_var,bg=C["BG"],fg=C["FG"],
            insertbackground=C["FG"],font=("Consolas",9),relief="flat",
            highlightthickness=1,highlightbackground=C["BORDER"],width=20).pack(side="left",padx=8,ipady=3)

        br=tk.Frame(c,bg=C["BG3"]); br.pack(anchor="w",pady=(0,10))
        self.btn_ping_start=self._mkbtn(br,T["start_monitor"],self._toggle_ping_monitor,C["ACCENT"],"#000")
        self.btn_ping_start.pack(side="left",padx=(0,8))

        # Canlı ping göstergesi
        self.ping_display_frame=tk.Frame(c,bg=C["BG3"]); self.ping_display_frame.pack(fill="x")
        self.ping_value_lbl=tk.Label(self.ping_display_frame,text="— ms",bg=C["BG3"],
            fg=C["GREEN"],font=("Segoe UI",28,"bold")); self.ping_value_lbl.pack(side="left",padx=(0,20))
        ping_stats=tk.Frame(self.ping_display_frame,bg=C["BG3"]); ping_stats.pack(side="left")
        tk.Label(ping_stats,text="Min:",bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",8)).grid(row=0,column=0,sticky="w")
        self.ping_min_lbl=tk.Label(ping_stats,text="—",bg=C["BG3"],fg=C["GREEN"],font=("Segoe UI",8,"bold"))
        self.ping_min_lbl.grid(row=0,column=1,sticky="w",padx=8)
        tk.Label(ping_stats,text="Max:",bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",8)).grid(row=1,column=0,sticky="w")
        self.ping_max_lbl=tk.Label(ping_stats,text="—",bg=C["BG3"],fg=C["RED"],font=("Segoe UI",8,"bold"))
        self.ping_max_lbl.grid(row=1,column=1,sticky="w",padx=8)
        tk.Label(ping_stats,text="Avg:",bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",8)).grid(row=2,column=0,sticky="w")
        self.ping_avg_lbl=tk.Label(ping_stats,text="—",bg=C["BG3"],fg=C["BLUE"],font=("Segoe UI",8,"bold"))
        self.ping_avg_lbl.grid(row=2,column=1,sticky="w",padx=8)

        # Ping geçmişi
        self.ping_history_canvas=tk.Canvas(c,bg=C["BG"],height=60,highlightthickness=0)
        self.ping_history_canvas.pack(fill="x",pady=(8,0))
        self.ping_history=[]
        self.ping_min_val=9999; self.ping_max_val=0; self.ping_sum=0; self.ping_count=0

        # Tek seferlik test
        c2=self._card(sc,"🔍  TEK SEFERLİK TEST" if self.lang=="tr" else "🔍  ONE-TIME TEST")
        self.btn_nettest=self._mkbtn(c2,T["start_monitor"].replace("▶ ","▶ Tek ") if self.lang=="tr" else "▶ Run Test",
            lambda:threading.Thread(target=self._run_nettest,daemon=True).start(),C["ACCENT"],"#000")
        self.btn_nettest.pack(anchor="w",pady=(0,10))
        self.net_frame=tk.Frame(c2,bg=C["BG3"]); self.net_frame.pack(fill="x")

        # Sistem bilgisi
        c3=self._card(sc,"💻  "+T["sys_info"].split("  ")[-1])
        self.sys_frame=tk.Frame(c3,bg=C["BG3"]); self.sys_frame.pack(fill="x")

    def _build_server_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["server"])
        c=self._card(sc,"🖥  SUNUCU YÖNETİMİ" if self.lang=="tr" else "🖥  SERVER MANAGEMENT")

        # Sunucu ekle
        add_row=tk.Frame(c,bg=C["BG3"]); add_row.pack(fill="x",pady=(0,10))
        tk.Label(add_row,text=T["server_host"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        self.new_server_host=tk.StringVar()
        tk.Entry(add_row,textvariable=self.new_server_host,bg=C["BG"],fg=C["FG"],
            insertbackground=C["FG"],font=("Consolas",9),relief="flat",
            highlightthickness=1,highlightbackground=C["BORDER"],width=22).pack(side="left",padx=6,ipady=3)
        tk.Label(add_row,text=T["server_port"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        self.new_server_port=tk.StringVar(value="15779")
        tk.Entry(add_row,textvariable=self.new_server_port,bg=C["BG"],fg=C["FG"],
            insertbackground=C["FG"],font=("Consolas",9),relief="flat",
            highlightthickness=1,highlightbackground=C["BORDER"],width=7).pack(side="left",padx=6,ipady=3)
        self._mkbtn(add_row,T["add_server"],self._add_server,C["BG4"],C["GREEN"]).pack(side="left",padx=4)

        # Sunucu listesi
        self.server_list_frame=tk.Frame(c,bg=C["BG3"]); self.server_list_frame.pack(fill="x")
        self._refresh_server_list()

    def _build_launcher_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["launcher"])
        c=self._card(sc,"🚀  "+T["launcher_title"].split("  ")[-1].upper())
        tk.Label(c,text=T["launcher_desc"],bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8)).pack(anchor="w",pady=(0,10))

        # Launcher exe seç
        er=tk.Frame(c,bg=C["BG3"]); er.pack(fill="x",pady=(0,8))
        tk.Label(er,text=T["launcher_exe"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9)).pack(side="left")
        tk.Entry(er,textvariable=self.launcher_var,bg=C["BG"],fg=C["FG"],
            insertbackground=C["FG"],font=("Consolas",9),relief="flat",
            highlightthickness=1,highlightbackground=C["BORDER"]).pack(side="left",fill="x",expand=True,padx=8,ipady=3)
        self._mkbtn(er,T["launcher_browse"],self._browse_launcher,C["BG4"],C["FG2"]).pack(side="left")

        # Ön kontrol
        self._chk(c,T["pre_check"],self.pre_check_var)

        # Başlat butonu
        tk.Frame(c,bg=C["BORDER"],height=1).pack(fill="x",pady=12)
        self._mkbtn(c,T["launch_btn"],self._launch_game,"#0d3320",C["GREEN"],
            font=("Segoe UI",12,"bold")).pack(fill="x",ipady=10)

        # Durum
        self.launcher_status=tk.Label(c,text="",bg=C["BG3"],fg=C["FG2"],
            font=("Segoe UI",9),wraplength=700,justify="left")
        self.launcher_status.pack(anchor="w",pady=(10,0))

    def _build_help_tab(self):
        C,T = self.C,self.T
        sc = self._scrollable(self.tabs["help"])
        c=self._card(sc,T["help_errors"])
        errors=[
            ('"MSVCR100.dll bulunamadı"' if self.lang=="tr" else '"MSVCR100.dll not found"',
             ('Bağımlılıklar sekmesinden VC++ 2010 x86\'yı kurun.' if self.lang=="tr" else 'Install VC++ 2010 x86 from the Dependencies tab.')),
            ('"d3dx9_43.dll yok"' if self.lang=="tr" else '"d3dx9_43.dll missing"',
             ('Bağımlılıklar sekmesinden DirectX 9.0c\'yi kurun.' if self.lang=="tr" else 'Install DirectX 9.0c from the Dependencies tab.')),
            ('Defender / Virüs uyarısı' if self.lang=="tr" else 'Defender / Virus warning',
             ('Defender sekmesinden dışlama ekleyin. Tamper Protection açıksa önce Windows Güvenliği\'nden kapatın.' if self.lang=="tr" else 'Add exclusion from Defender tab. Disable Tamper Protection first if enabled.')),
            ('WebView2 / Beyaz ekran' if self.lang=="tr" else 'WebView2 / White screen',
             ('WebView2 sekmesinden "Yeniden kur" işlemini çalıştırın.' if self.lang=="tr" else 'Run "Reinstall" from WebView2 tab.')),
            ('DEP / 0xC0000005',
             ('DEP sekmesinden DEP\'i kapatın.' if self.lang=="tr" else 'Disable DEP from the DEP tab.')),
        ]
        for err,fix in errors:
            tk.Label(c,text="✕  "+err,bg=C["BG3"],fg=C["RED"],font=("Segoe UI",8,"bold"),justify="left").pack(anchor="w")
            tk.Label(c,text="  → "+fix,bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8),justify="left").pack(anchor="w",pady=(1,6))
            tk.Frame(c,bg=C["BORDER"],height=1).pack(fill="x")
        c2=self._card(sc,T["help_about"])
        tk.Label(c2,text=T["about_text"],bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",9),justify="left").pack(anchor="w")

    # ── YARDIMCI UI ───────────────────────────────────────────────────────────
    def _scrollable(self,parent):
        C=self.C
        canvas=tk.Canvas(parent,bg=C["BG"],highlightthickness=0,bd=0)
        sb=ttk.Scrollbar(parent,orient="vertical",command=canvas.yview)
        frame=tk.Frame(canvas,bg=C["BG"])
        frame.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0),window=frame,anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        canvas.bind_all("<MouseWheel>",lambda e:canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
        return frame

    def _card(self,parent,title=None,pady=8):
        C=self.C
        outer=tk.Frame(parent,bg=C["BG"]); outer.pack(fill="x",padx=14,pady=(pady,0))
        inner=tk.Frame(outer,bg=C["BG3"],bd=0); inner.pack(fill="x")
        tk.Frame(inner,bg=C["BORDER"],height=1).pack(fill="x")
        content=tk.Frame(inner,bg=C["BG3"]); content.pack(fill="x",padx=14,pady=10)
        if title:
            tk.Label(content,text=title,bg=C["BG3"],fg=C["FG2"],font=("Segoe UI",8,"bold")).pack(anchor="w",pady=(0,8))
        return content

    def _chk(self,parent,text,var):
        C=self.C
        tk.Checkbutton(parent,text=text,variable=var,bg=C["BG3"],fg=C["FG"],
            font=("Segoe UI",9),selectcolor=C["BG3"],activebackground=C["BG3"],
            activeforeground=C["FG"],highlightthickness=0,cursor="hand2").pack(anchor="w",pady=2)

    def _warn(self,parent,text):
        C=self.C
        f=tk.Frame(parent,bg=C["WARN_BG"],bd=0); f.pack(fill="x",padx=14,pady=(6,0))
        tk.Frame(f,bg=C["WARN_BD"],height=1).pack(fill="x")
        tk.Label(f,text="⚠  "+text,bg=C["WARN_BG"],fg=C["WARN_FG"],font=("Segoe UI",8),
            wraplength=820,justify="left",padx=10,pady=6).pack(anchor="w")

    def _mkbtn(self,parent,text,cmd,bg,fg,font=("Segoe UI",9,"bold"),**kw):
        C=self.C
        return tk.Button(parent,text=text,command=cmd,bg=bg,fg=fg,font=font,
            relief="flat",cursor="hand2",activebackground=C["ACCENT"],
            activeforeground="#000",padx=12,pady=5,**kw)

    def _status_item(self,parent,label,value,color):
        C=self.C
        f=tk.Frame(parent,bg=C["BG2"]); f.pack(side="left",padx=12,pady=4)
        tk.Label(f,text=label+":",bg=C["BG2"],fg=C["FG3"],font=("Segoe UI",8)).pack(side="left")
        lbl=tk.Label(f,text=value,bg=C["BG2"],fg=color,font=("Segoe UI",8,"bold"))
        lbl.pack(side="left",padx=(4,0))
        return lbl

    def _vsep(self,parent):
        tk.Frame(parent,bg=self.C["BORDER"],width=1).pack(side="left",fill="y",pady=6)

    # ── TEMA / DİL ────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self.theme = "light" if self.theme=="dark" else "dark"
        self.settings["theme"] = self.theme
        save_settings(self.settings)
        self._restart_ui()

    def _toggle_lang(self):
        self.lang = "en" if self.lang=="tr" else "tr"
        self.settings["lang"] = self.lang
        save_settings(self.settings)
        self._restart_ui()

    def _restart_ui(self):
        self._save_current_settings()
        for w in self.winfo_children(): w.destroy()
        self.C = THEMES[self.theme]
        self.T = LANG[self.lang]
        self._setup_style()
        self._build_ui()
        threading.Thread(target=self._initial_scan,daemon=True).start()

    def _save_current_settings(self):
        self.settings.update({
            "theme":self.theme,"lang":self.lang,
            "folder":self.folder_var.get(),
            "launcher_exe":self.launcher_var.get(),
            "ping_target":self.ping_target_var.get(),
            "pre_check":self.pre_check_var.get(),
            "minimize_tray":self.minimize_tray_var.get(),
            "chk_folder_excl":self.chk_folder_excl.get(),
            "chk_proc_excl":self.chk_proc_excl.get(),
            "chk_dep":self.chk_dep.get(),
            "chk_auto_install":self.chk_auto_install.get(),
            "chk_wv2":self.chk_wv2.get(),
        })
        save_settings(self.settings)

    # ── KAPANIŞ ───────────────────────────────────────────────────────────────
    def _on_close(self):
        self.ping_running = False
        self._save_current_settings()
        self.quit()

    # ── LOG ───────────────────────────────────────────────────────────────────
    def log(self,msg,tag="info"):
        ts=datetime.now().strftime("%H:%M:%S")
        self.log_lines.append((ts,msg,tag))
        try:
            self.log_box.configure(state="normal")
            self.log_box.insert("end",ts+"  ","time")
            self.log_box.insert("end",msg+"\n",tag)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except: pass

    def _clear_log(self):
        try:
            self.log_box.configure(state="normal")
            self.log_box.delete("1.0","end")
            self.log_box.configure(state="disabled")
            self.log_lines.clear()
        except: pass

    def _run_bg(self,fn): threading.Thread(target=fn,daemon=True).start()

    # ── KLASÖR ────────────────────────────────────────────────────────────────
    def _browse(self):
        f=filedialog.askdirectory(title="Silkroad Klasörünü Seçin")
        if f:
            self.folder_var.set(f); self.settings["folder"]=f
            self.log(f"Klasör: {f}","info")
            self._run_bg(self._scan_client_bg)

    def _browse_launcher(self):
        f=filedialog.askopenfilename(title="Launcher .exe seçin",filetypes=[("EXE","*.exe"),("Tümü","*.*")])
        if f: self.launcher_var.set(f); self.settings["launcher_exe"]=f

    def _get_folder(self):
        f=self.folder_var.get().strip()
        if not f: messagebox.showwarning("Uyarı",self.T["no_folder"])
        return f

    # ── İLK TARAMA ────────────────────────────────────────────────────────────
    def _initial_scan(self):
        T=self.T
        self.log(f"ProNet Client Fixer v.02 {T['started']}","info")
        if not is_admin(): self.log(f"⚠  {T['no_admin']}","warn")

        # Defender
        try:
            out=subprocess.check_output(["powershell","-Command",
                "Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled,IsTamperProtected | ConvertTo-Json"],
                timeout=8,stderr=subprocess.DEVNULL,creationflags=0x08000000).decode(errors="ignore").strip()
            d=json.loads(out)
            rtp=d.get("RealTimeProtectionEnabled",False); tamper=d.get("IsTamperProtected",False)
            self.after(0,lambda:self._upd_defender(rtp,tamper))
        except: self.after(0,lambda:self._upd_status(self.lbl_defender,self.T["inactive"],self.C["GREEN"]))

        # DEP
        try:
            out=subprocess.check_output(["wmic","OS","get","DataExecutionPrevention_SupportPolicy","/value"],
                timeout=6,stderr=subprocess.DEVNULL,creationflags=0x08000000).decode(errors="ignore")
            m=next((l.split("=")[-1].strip() for l in out.splitlines() if "=" in l),None)
            labels={"0":T["inactive"],"1":"Yalnızca Sistem" if self.lang=="tr" else "System Only",
                    "2":"Tüm Programlar" if self.lang=="tr" else "All Programs",
                    "3":"İstisnalar" if self.lang=="tr" else "Exceptions"}
            dep_str=labels.get(m,T["unknown"])
            self.after(0,lambda s=dep_str,v=m:self._upd_dep(s,v))
        except: self.after(0,lambda:self._upd_status(self.lbl_dep,T["unknown"],self.C["YELLOW"]))

        # WebView2
        try:
            k=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
            ver,_=winreg.QueryValueEx(k,"pv"); winreg.CloseKey(k)
            self.after(0,lambda v=ver:self._upd_wv2(v))
        except: self.after(0,lambda:self._upd_wv2(T["not_installed"] if T else "Kurulu Değil"))

        self.after(0,self._check_deps_ui)
        self._load_sysinfo()

    def _upd_defender(self,rtp,tamper):
        C,T=self.C,self.T
        if rtp:
            self._upd_status(self.lbl_defender,T["active"],C["RED"])
            self.lbl_rtp.config(text=T["active"],fg=C["RED"])
        else:
            self._upd_status(self.lbl_defender,T["inactive"],C["GREEN"])
            self.lbl_rtp.config(text=T["inactive"],fg=C["GREEN"])
        self.lbl_tamper.config(text=T["active"] if tamper else T["inactive"],
            fg=C["RED"] if tamper else C["GREEN"])

    def _upd_dep(self,label,val):
        C=self.C
        color=C["GREEN"] if val=="0" else C["YELLOW"]
        self._upd_status(self.lbl_dep,label,color)
        self.lbl_dep_status.config(text=label,fg=color)

    def _upd_wv2(self,ver):
        C=self.C
        color=C["GREEN"] if ver and "Değil" not in ver and "Not" not in ver else C["RED"]
        self._upd_status(self.lbl_wv2,ver[:18] if ver else "?",color)
        try: self.lbl_wv2_ver.config(text=ver or "—",fg=color)
        except: pass

    def _upd_status(self,lbl,text,color):
        try: lbl.config(text=text,fg=color)
        except: pass

    # ── BAĞIMLILIKLAR ─────────────────────────────────────────────────────────
    def _check_deps_ui(self):
        C,T=self.C,self.T
        for w in self.deps_frame.winfo_children(): w.destroy()
        iv=self._get_installed_vc()
        dx9=os.path.exists(os.path.join(os.environ.get("SystemRoot","C:\\Windows"),"System32","d3dx9_43.dll"))
        deps=[
            ("VC++ 2010 x86",self._has_vc(iv,"2010","x86"),"https://download.microsoft.com/download/5/B/C/5BC5DBB3-652D-4DCE-B14A-475AB85EEF6E/vcredist_x86.exe"),
            ("VC++ 2010 x64",self._has_vc(iv,"2010","x64"),"https://download.microsoft.com/download/3/2/2/3224B87F-CFA0-4E70-BDA3-3DE650EFEBA5/vcredist_x64.exe"),
            ("VC++ 2013 x86",self._has_vc(iv,"2013","x86"),None),
            ("VC++ 2013 x64",self._has_vc(iv,"2013","x64"),None),
            ("VC++ 2015-2022 x86",self._has_vc(iv,"2015","x86"),None),
            ("VC++ 2015-2022 x64",self._has_vc(iv,"2015","x64"),None),
            ("DirectX 9.0c (d3dx9_43.dll)",dx9,None),
        ]
        missing=sum(1 for _,ok,_ in deps if not ok)
        color=C["GREEN"] if missing==0 else C["RED"]
        self._upd_status(self.lbl_deps,f"{missing} {T['missing']}" if missing else T["all_installed"],color)
        for name,ok,url in deps:
            row=tk.Frame(self.deps_frame,bg=C["BG3"]); row.pack(fill="x",pady=2)
            tk.Label(row,text="✓" if ok else "✕",bg=C["BG3"],fg=C["GREEN"] if ok else C["RED"],
                font=("Segoe UI",9,"bold"),width=2).pack(side="left",padx=(0,8))
            tk.Label(row,text=name,bg=C["BG3"],fg=C["FG"],font=("Segoe UI",9),width=28,anchor="w").pack(side="left")
            if ok:
                tk.Label(row,text=T["installed"],bg=C["BG3"],fg=C["GREEN"],font=("Segoe UI",8)).pack(side="right",padx=8)
            else:
                self._mkbtn(row,T["install_dep"],
                    lambda n=name,u=url:self._run_bg(lambda:self._install_dep(n,u)),
                    "#0a1020",C["BLUE"],font=("Segoe UI",8,"bold")).pack(side="right",padx=8)

    def _get_installed_vc(self):
        result={}
        try:
            key=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
            i=0
            while True:
                try:
                    sub=winreg.EnumKey(key,i); sk=winreg.OpenKey(key,sub)
                    try:
                        name,_=winreg.QueryValueEx(sk,"DisplayName")
                        if "Visual C++" in name: result[name]=True
                    except: pass
                    winreg.CloseKey(sk); i+=1
                except OSError: break
            winreg.CloseKey(key)
        except: pass
        return result

    def _has_vc(self,installed,year,arch):
        return any(year in k and arch.lower() in k.lower() for k in installed)

    def _install_dep(self,name,url):
        self.log(f"{name} indiriliyor…","info")
        if not url: self.log(f"{name} için URL yok, manuel kurun.","warn"); return
        try:
            tmp=os.path.join(tempfile.gettempdir(),f"dep_{name.replace(' ','_')}.exe")
            urllib.request.urlretrieve(url,tmp)
            self.log(f"{name} kuruluyor…","info")
            subprocess.run([tmp,"/quiet","/norestart"],timeout=120)
            self.log(f"{name} kuruldu!","ok")
            self.after(0,self._check_deps_ui)
        except Exception as e: self.log(f"Hata: {e}","err")

    # ── CLİENT TARAMA ─────────────────────────────────────────────────────────
    def _scan_client(self): self._run_bg(self._scan_client_bg)
    def _scan_client_bg(self):
        T=self.T; folder=self._get_folder()
        if not folder: return
        required=["sro_client.exe","elemon.exe","GameGuard.des","d3dx9_43.dll","ijl15.dll","mss32.dll","Silkroad.exe","Launcher.exe"]
        found=[f for f in required if os.path.exists(os.path.join(folder,f))]
        missing=[f for f in required if f not in found]
        self.client_result.configure(state="normal"); self.client_result.delete("1.0","end")
        if found:
            self.client_result.insert("end",f"Bulunan ({len(found)})\n","head")
            for f in found: self.client_result.insert("end",f"  ✓ {f}\n","ok")
        if missing:
            self.client_result.insert("end",f"\nEksik ({len(missing)})\n","head")
            for f in missing: self.client_result.insert("end",f"  ✕ {f}\n","miss")
        if not missing: self.client_result.insert("end",f"\n{T['all_files_ok']}","ok")
        self.client_result.configure(state="disabled")
        self.log(f"Client: {len(found)} OK, {len(missing)} eksik.","ok" if not missing else "warn")

    # ── DEFENDER ──────────────────────────────────────────────────────────────
    def _add_defender_folder(self,folder):
        try:
            subprocess.run(["powershell","-Command",f"Add-MpPreference -ExclusionPath '{folder}'"],
                timeout=15,check=True,stderr=subprocess.DEVNULL,creationflags=0x08000000)
            self.log(f"Defender klasör dışlaması eklendi.","ok"); return True
        except Exception as e: self.log(f"Defender hatası: {e}","err"); return False

    def _add_defender_processes(self,folder):
        exes=[f for f in os.listdir(folder) if f.endswith(".exe")]
        ok=0
        for exe in exes:
            try:
                subprocess.run(["powershell","-Command",f"Add-MpPreference -ExclusionProcess '{os.path.join(folder,exe)}'"],
                    timeout=8,stderr=subprocess.DEVNULL,creationflags=0x08000000); ok+=1
            except: pass
        self.log(f"{ok}/{len(exes)} .exe dışlamaya eklendi.","ok")

    # ── DEP ───────────────────────────────────────────────────────────────────
    def _disable_dep(self,folder):
        try:
            subprocess.run(["bcdedit","/set","nx","AlwaysOff"],timeout=10,check=True,
                stderr=subprocess.DEVNULL,creationflags=0x08000000)
            self.log("DEP kapatıldı. Yeniden başlatma gerekli!","warn"); return
        except: self.log("Global DEP kapatılamadı, per-exe istisna ekleniyor…","warn")
        if not folder: return
        exes=[f for f in os.listdir(folder) if f.endswith(".exe")]; ok=0
        for exe in exes:
            try:
                subprocess.run(["powershell","-Command",f"Set-ProcessMitigation -Name '{os.path.join(folder,exe)}' -Disable DEP"],
                    timeout=8,stderr=subprocess.DEVNULL,creationflags=0x08000000); ok+=1
            except: pass
        self.log(f"{ok} dosya için DEP istisnası eklendi.","ok")

    # ── WEBVIEW2 ──────────────────────────────────────────────────────────────
    def _reinstall_webview2(self):
        self.log("WebView2 indiriliyor…","info")
        try:
            tmp=os.path.join(tempfile.gettempdir(),"MicrosoftEdgeWebview2Setup.exe")
            urllib.request.urlretrieve("https://go.microsoft.com/fwlink/p/?LinkId=2124703",tmp)
            self.log("WebView2 kuruluyor…","info")
            subprocess.run([tmp,"/silent","/install"],timeout=120)
            self.log("WebView2 kuruldu!","ok")
            self._initial_scan()
        except Exception as e: self.log(f"WebView2 hatası: {e}","err")

    # ── ARAÇLAR ───────────────────────────────────────────────────────────────
    def _kill_blockers(self):
        targets=["MSIAfterburner","Afterburner","cheatengine","CheatEngine","Sandboxie",
                 "procmon","Wireshark","vmware","VirtualBox","x32dbg","x64dbg","ollydbg"]
        killed=0
        for p in targets:
            try:
                subprocess.run(["taskkill","/F","/IM",f"{p}.exe"],timeout=4,
                    stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL,creationflags=0x08000000); killed+=1
            except: pass
        self.log(f"Engelleyen uygulamalar kapatıldı ({killed}).","ok")

    def _apply_admin_compat(self):
        folder=self._get_folder()
        if not folder: return
        exes=[f for f in os.listdir(folder) if f.endswith(".exe")]; ok=0
        for exe in exes:
            try:
                k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    "Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers",0,winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k,os.path.join(folder,exe),0,winreg.REG_SZ,"~ RUNASADMIN")
                winreg.CloseKey(k); ok+=1
            except: pass
        self.log(f"{ok} dosya için admin yaması uygulandı.","ok")

    def _add_firewall_rules(self):
        folder=self._get_folder()
        if not folder: return
        exes=[f for f in os.listdir(folder) if f.endswith(".exe")]; ok=0
        for exe in exes:
            path=os.path.join(folder,exe); name=exe.replace(".exe","")
            try:
                subprocess.run(["netsh","advfirewall","firewall","add","rule",
                    f"name=ProNet-IN-{name}","dir=in","action=allow",f"program={path}","enable=yes"],
                    timeout=8,stderr=subprocess.DEVNULL,creationflags=0x08000000)
                subprocess.run(["netsh","advfirewall","firewall","add","rule",
                    f"name=ProNet-OUT-{name}","dir=out","action=allow",f"program={path}","enable=yes"],
                    timeout=8,stderr=subprocess.DEVNULL,creationflags=0x08000000)
                ok+=1
            except: pass
        self.log(f"{ok} dosya için firewall kuralı eklendi.","ok")

    def _create_support_file(self):
        desktop=Path.home()/"Desktop"
        fpath=desktop/f"ProNet_Support_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        lines="\n".join(f"[{ts}] {t.upper()}: {m}" for ts,m,t in self.log_lines)
        sys_txt="\n".join(f"{k}: {v}" for k,v in self.sys_info.items())
        fpath.write_text(f"=== ProNet Client Fixer v.02 ===\nTarih: {datetime.now()}\n\n=== SİSTEM ===\n{sys_txt}\n\n=== LOG ===\n{lines}\n","utf-8")
        self.log(f"Destek dosyası oluşturuldu: {fpath.name}","ok")
        os.startfile(desktop)

    def _check_update(self):
        self.log(self.T["checking_update"],"info")
        try:
            with urllib.request.urlopen("https://api.github.com/repos/BayDevil42/pronet-client-fixer/releases/latest",timeout=8) as r:
                data=json.loads(r.read())
                tag=data.get("tag_name","")
                if tag and tag!="v0.1" and tag!="v.02":
                    self.after(0,lambda:messagebox.showinfo("Güncelleme",self.T["update_available"].format(ver=tag)))
                else:
                    self.log(self.T["up_to_date"],"ok")
        except: self.log(self.T["up_to_date"],"ok")

    # ── PROFİL ────────────────────────────────────────────────────────────────
    def _save_profile(self):
        name=self.profile_name_var.get().strip()
        if not name: return
        self.settings.setdefault("profiles",{})[name]={
            "folder":self.folder_var.get(),"launcher":self.launcher_var.get(),
            "chk_folder_excl":self.chk_folder_excl.get(),"chk_proc_excl":self.chk_proc_excl.get(),
            "chk_dep":self.chk_dep.get(),"chk_auto_install":self.chk_auto_install.get(),
        }
        save_settings(self.settings)
        self.log(f"Profil kaydedildi: {name}","ok")
        self._refresh_profiles()

    def _load_profile(self,name):
        p=self.settings.get("profiles",{}).get(name,{})
        if p:
            if p.get("folder"): self.folder_var.set(p["folder"])
            if p.get("launcher"): self.launcher_var.set(p["launcher"])
            self.chk_folder_excl.set(p.get("chk_folder_excl",True))
            self.chk_proc_excl.set(p.get("chk_proc_excl",True))
            self.chk_dep.set(p.get("chk_dep",True))
            self.chk_auto_install.set(p.get("chk_auto_install",True))
            self.log(f"Profil yüklendi: {name}","ok")

    def _delete_profile(self,name):
        self.settings.get("profiles",{}).pop(name,None)
        save_settings(self.settings); self._refresh_profiles()

    def _refresh_profiles(self):
        C,T=self.C,self.T
        try:
            for w in self.profiles_frame.winfo_children(): w.destroy()
            profiles=self.settings.get("profiles",{})
            if not profiles:
                tk.Label(self.profiles_frame,text=T["no_profiles"],bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",8)).pack(anchor="w")
                return
            for name in profiles:
                row=tk.Frame(self.profiles_frame,bg=C["BG3"]); row.pack(fill="x",pady=2)
                tk.Label(row,text=f"📁 {name}",bg=C["BG3"],fg=C["FG"],font=("Segoe UI",9)).pack(side="left",padx=(0,8))
                self._mkbtn(row,T["profile_load"],lambda n=name:self._load_profile(n),C["BG4"],C["BLUE"],font=("Segoe UI",8,"bold")).pack(side="left",padx=2)
                self._mkbtn(row,"🗑",lambda n=name:self._delete_profile(n),"#2a1010",C["RED"],font=("Segoe UI",8,"bold")).pack(side="left",padx=2)
        except: pass

    # ── SUNUCU ────────────────────────────────────────────────────────────────
    def _add_server(self):
        host=self.new_server_host.get().strip()
        if not host: return
        try: port=int(self.new_server_port.get())
        except: port=15779
        self.settings.setdefault("servers",[]).append({"name":host,"host":host,"port":port})
        save_settings(self.settings); self.new_server_host.set(""); self._refresh_server_list()

    def _refresh_server_list(self):
        C,T=self.C,self.T
        try:
            for w in self.server_list_frame.winfo_children(): w.destroy()
            for i,srv in enumerate(self.settings.get("servers",[])):
                row=tk.Frame(self.server_list_frame,bg=C["BG3"]); row.pack(fill="x",pady=3)
                name=srv.get("name",srv.get("host","?"))
                tk.Label(row,text=f"🖥 {name}",bg=C["BG3"],fg=C["FG"],font=("Segoe UI",9),width=22,anchor="w").pack(side="left")
                tk.Label(row,text=f"{srv.get('host','')}:{srv.get('port','')}",
                    bg=C["BG3"],fg=C["FG3"],font=("Consolas",8),width=26,anchor="w").pack(side="left")
                status_lbl=tk.Label(row,text="—",bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",8,"bold"),width=14)
                status_lbl.pack(side="left",padx=8)
                self._mkbtn(row,T["check_server"],
                    lambda s=srv,l=status_lbl:self._run_bg(lambda:self._check_server(s,l)),
                    C["BG4"],C["BLUE"],font=("Segoe UI",8,"bold")).pack(side="left",padx=4)
                self._mkbtn(row,T["remove_server"],
                    lambda idx=i:self._remove_server(idx),"#2a1010",C["RED"],font=("Segoe UI",8,"bold")).pack(side="left",padx=2)
        except: pass

    def _remove_server(self,idx):
        servers=self.settings.get("servers",[])
        if 0<=idx<len(servers): servers.pop(idx)
        save_settings(self.settings); self._refresh_server_list()

    def _check_server(self,srv,lbl):
        C,T=self.C,self.T
        host=srv.get("host",""); port=int(srv.get("port",15779))
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(5)
            result=s.connect_ex((host,port)); s.close()
            if result==0:
                self.after(0,lambda:lbl.config(text=T["online"],fg=C["GREEN"]))
                self.log(f"{host}:{port} — {T['online']}","ok")
            else:
                self.after(0,lambda:lbl.config(text=T["offline"],fg=C["RED"]))
                self.log(f"{host}:{port} — {T['offline']}","warn")
        except Exception as e:
            self.after(0,lambda:lbl.config(text=T["offline"],fg=C["RED"]))
            self.log(f"{host} bağlantı hatası: {e}","err")

    # ── PING MONİTÖR ──────────────────────────────────────────────────────────
    def _toggle_ping_monitor(self):
        T=self.T
        if not self.ping_running:
            self.ping_running=True
            self.ping_min_val=9999; self.ping_max_val=0; self.ping_sum=0; self.ping_count=0
            self.ping_history=[]
            self.btn_ping_start.config(text=T["stop_monitor"],bg="#2a1010",fg=self.C["RED"])
            self.ping_thread=threading.Thread(target=self._ping_loop,daemon=True)
            self.ping_thread.start()
            self.log("Ping monitörü başlatıldı.","info")
        else:
            self.ping_running=False
            self.btn_ping_start.config(text=T["start_monitor"],bg=self.C["ACCENT"],fg="#000")
            self.log("Ping monitörü durduruldu.","warn")

    def _ping_loop(self):
        while self.ping_running:
            target=self.ping_target_var.get().strip() or "8.8.8.8"
            ping_ms=self._single_ping(target)
            if ping_ms is not None:
                self.ping_history.append(ping_ms)
                if len(self.ping_history)>60: self.ping_history.pop(0)
                self.ping_min_val=min(self.ping_min_val,ping_ms)
                self.ping_max_val=max(self.ping_max_val,ping_ms)
                self.ping_sum+=ping_ms; self.ping_count+=1
                avg=self.ping_sum//self.ping_count
                color=self.C["GREEN"] if ping_ms<80 else self.C["YELLOW"] if ping_ms<200 else self.C["RED"]
                self.after(0,lambda p=ping_ms,c=color,mn=self.ping_min_val,mx=self.ping_max_val,av=avg:
                    self._upd_ping_display(p,c,mn,mx,av))
            time.sleep(1)

    def _single_ping(self,host):
        try:
            start=time.time()
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host,80 if host not in ["8.8.8.8","1.1.1.1"] else 53))
            s.close()
            return int((time.time()-start)*1000)
        except:
            try:
                out=subprocess.check_output(["ping","-n","1","-w","2000",host],
                    timeout=5,stderr=subprocess.DEVNULL,creationflags=0x08000000).decode("cp857",errors="ignore")
                for line in out.splitlines():
                    if "ms" in line.lower() and ("=" in line or "<" in line):
                        for part in line.split():
                            if "ms" in part.lower():
                                try: return int(part.replace("ms","").replace("<","").strip())
                                except: pass
            except: pass
        return None

    def _upd_ping_display(self,ping,color,mn,mx,avg):
        try:
            self.ping_value_lbl.config(text=f"{ping} ms",fg=color)
            self.ping_min_lbl.config(text=f"{mn} ms")
            self.ping_max_lbl.config(text=f"{mx} ms")
            self.ping_avg_lbl.config(text=f"{avg} ms")
            self._draw_ping_graph()
        except: pass

    def _draw_ping_graph(self):
        try:
            C=self.C; canvas=self.ping_history_canvas
            canvas.delete("all")
            w=canvas.winfo_width(); h=canvas.winfo_height()
            if w<10 or not self.ping_history: return
            mx=max(max(self.ping_history),1)
            pts=self.ping_history[-w//4:]
            step=w/max(len(pts),1)
            coords=[]
            for i,v in enumerate(pts):
                x=i*step; y=h-(v/mx)*h*0.9
                coords.extend([x,y])
            if len(coords)>=4:
                canvas.create_line(coords,fill=C["ACCENT"],width=2,smooth=True)
            # 80ms çizgisi
            y80=h-(80/mx)*h*0.9 if mx>0 else h//2
            canvas.create_line(0,y80,w,y80,fill=C["GREEN"],dash=(4,4),width=1)
        except: pass

    # ── AĞ TESTİ ──────────────────────────────────────────────────────────────
    def _run_nettest(self):
        C,T=self.C,self.T
        self.after(0,lambda:self.btn_nettest.config(text="⏳…",state="disabled"))
        self.after(0,lambda:[w.destroy() for w in self.net_frame.winfo_children()])
        self.log("Ağ testi başlatıldı…","info")
        servers=[("Google DNS","8.8.8.8"),("Cloudflare","1.1.1.1"),("Google","google.com")]
        for label,host in servers:
            try:
                out=subprocess.check_output(["ping","-n","4",host],timeout=12,
                    stderr=subprocess.DEVNULL,creationflags=0x08000000).decode("cp857",errors="ignore")
                avg=None
                for line in out.splitlines():
                    if "=" in line and "ms" in line.lower():
                        parts=line.split("=")
                        if parts:
                            try: avg=int(parts[-1].strip().replace("ms","").strip())
                            except: pass
                status=f"✓ {avg}ms" if avg else "✕"
                color=C["GREEN"] if avg and avg<80 else C["YELLOW"] if avg and avg<200 else C["RED"]
                self.after(0,lambda lb=label,hs=host,st=status,cl=color:self._add_net_row(lb,hs,st,cl))
            except:
                self.after(0,lambda lb=label,hs=host:self._add_net_row(lb,hs,"✕ Hata",C["RED"]))
        self.log("Ağ testi tamamlandı.","ok")
        self.after(0,lambda:self.btn_nettest.config(text="▶ Test",state="normal"))

    def _add_net_row(self,label,host,status,color):
        C=self.C; row=tk.Frame(self.net_frame,bg=C["BG3"]); row.pack(fill="x",pady=2)
        tk.Label(row,text=label,bg=C["BG3"],fg=C["FG"],font=("Segoe UI",9,"bold"),width=14,anchor="w").pack(side="left",padx=(0,8))
        tk.Label(row,text=host,bg=C["BG3"],fg=C["FG3"],font=("Consolas",8),width=18).pack(side="left")
        tk.Label(row,text=status,bg=C["BG3"],fg=color,font=("Segoe UI",9,"bold")).pack(side="right",padx=8)

    # ── SİSTEM BİLGİSİ ────────────────────────────────────────────────────────
    def _load_sysinfo(self):
        self.sys_info={"OS":platform.system()+" "+platform.version()[:40],
            "Arch":platform.machine(),"CPU":platform.processor()[:60],
            "Python":sys.version.split()[0],"Admin":"Evet" if is_admin() else "Hayır"}
        try:
            mem=ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(mem))
            self.sys_info["RAM"]=f"{mem.value//1024//1024} GB"
        except: pass
        self.after(0,self._upd_sys_frame)

    def _upd_sys_frame(self):
        C=self.C
        try:
            for w in self.sys_frame.winfo_children(): w.destroy()
            for k,v in self.sys_info.items():
                row=tk.Frame(self.sys_frame,bg=C["BG3"]); row.pack(fill="x",pady=1)
                tk.Label(row,text=f"{k}:",bg=C["BG3"],fg=C["FG3"],font=("Segoe UI",9),width=10,anchor="w").pack(side="left")
                tk.Label(row,text=v,bg=C["BG3"],fg=C["FG"],font=("Consolas",9)).pack(side="left")
        except: pass

    # ── LAUNCHER ──────────────────────────────────────────────────────────────
    def _launch_game(self):
        exe=self.launcher_var.get().strip()
        if not exe: messagebox.showwarning("Uyarı","Launcher .exe seçilmedi!"); return
        if not os.path.exists(exe): messagebox.showerror("Hata",f"Dosya bulunamadı:\n{exe}"); return

        if self.pre_check_var.get():
            self.launcher_status.config(text="⏳ Kontroller yapılıyor…",fg=self.C["YELLOW"])
            self.update()
            # Hızlı kontrol
            warnings=[]
            try:
                out=subprocess.check_output(["powershell","-Command",
                    "Get-MpComputerStatus | Select-Object -ExpandProperty RealTimeProtectionEnabled"],
                    timeout=5,stderr=subprocess.DEVNULL,creationflags=0x08000000).decode(errors="ignore").strip()
                if out=="True": warnings.append("⚠ Defender aktif — dışlama önerilir")
            except: pass
            if warnings:
                self.launcher_status.config(text=" | ".join(warnings),fg=self.C["YELLOW"])
            else:
                self.launcher_status.config(text="✓ Tüm kontroller geçti",fg=self.C["GREEN"])
            self.update()

        self.log(f"Oyun başlatılıyor: {exe}","info")
        try:
            subprocess.Popen([exe],cwd=os.path.dirname(exe))
            self.launcher_status.config(text="✓ Oyun başlatıldı!",fg=self.C["GREEN"])
            self.log("Oyun başlatıldı!","ok")
        except Exception as e:
            self.launcher_status.config(text=f"✕ Hata: {e}",fg=self.C["RED"])
            self.log(f"Başlatma hatası: {e}","err")

    # ── TARA / GERİ AL / KUR ──────────────────────────────────────────────────
    def _scan_all(self):
        self._run_bg(self._initial_scan)
        self.log(self.T["scanning"],"info")

    def _revert(self):
        if not messagebox.askyesno("Geri Al",self.T["revert_confirm"]): return
        self._run_bg(self._do_revert)

    def _do_revert(self):
        T=self.T; self.log(T["revert_start"],"warn")
        folder=self.folder_var.get().strip()
        if folder:
            try:
                subprocess.run(["powershell","-Command",f"Remove-MpPreference -ExclusionPath '{folder}'"],
                    timeout=10,stderr=subprocess.DEVNULL,creationflags=0x08000000)
                self.log("Defender dışlaması kaldırıldı.","ok")
            except: pass
        try:
            subprocess.run(["bcdedit","/set","nx","OptIn"],timeout=8,
                stderr=subprocess.DEVNULL,creationflags=0x08000000)
            self.log("DEP varsayılana döndürüldü.","ok")
        except: pass
        self.log(T["revert_done"],"ok")

    def _run_setup(self):
        folder=self._get_folder()
        if not folder: return
        self._run_bg(lambda:self._do_setup(folder))

    def _do_setup(self,folder):
        T=self.T; self.log(T["setup_start"],"info")
        if self.chk_folder_excl.get():
            self.log("Defender klasör dışlaması…","info"); self._add_defender_folder(folder)
        if self.chk_proc_excl.get():
            self.log("Defender process dışlaması…","info"); self._add_defender_processes(folder)
        if self.chk_dep.get():
            self.log("DEP kapatılıyor…","info"); self._disable_dep(folder)
        if self.chk_auto_install.get():
            self.log("Bağımlılıklar kontrol ediliyor…","info")
            self.after(0,self._check_deps_ui)
        self.log(T["setup_done"],"ok")
        self.after(0,self._initial_scan)

# ─── BAŞLANGIÇ ────────────────────────────────────────────────────────────────
if __name__=="__main__":
    run_as_admin()
    app=ProNetFixer()
    app.mainloop()
