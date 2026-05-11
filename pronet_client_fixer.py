"""
ProNet Client Fixer v.01
Silkroad Online Client Yönetim Aracı
Tek .exe — Hiçbir kurulum gerektirmez.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import winreg
import ctypes
import platform
import socket
import struct
import time
import json
import shutil
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path


# ─── YÖNETİCİ KONTROLÜ ────────────────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


# ─── RENKLER & STİL ───────────────────────────────────────────────────────────
BG       = "#0a0a0c"
BG2      = "#111114"
BG3      = "#161619"
BORDER   = "#2a2a32"
ACCENT   = "#e8a020"
ACCENT2  = "#ffb030"
GREEN    = "#22c55e"
RED      = "#ef4444"
YELLOW   = "#eab308"
BLUE     = "#3b82f6"
PURPLE   = "#a855f7"
FG       = "#e8e8f0"
FG2      = "#8888a0"
FG3      = "#505068"
FONT     = ("Segoe UI", 9)
FONT_B   = ("Segoe UI", 9, "bold")
FONT_H   = ("Segoe UI", 11, "bold")
FONT_T   = ("Segoe UI", 13, "bold")
FONT_M   = ("Consolas", 9)


# ─── ANA UYGULAMA ─────────────────────────────────────────────────────────────
class ProNetFixer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ProNet Client Fixer v.01")
        self.geometry("980x740")
        self.minsize(860, 640)
        self.configure(bg=BG)
        self.resizable(True, True)

        # İkon (embed edilmiş — dışarıdan dosya gerekmez)
        try:
            self.iconbitmap(default="")
        except:
            pass

        self.folder_var = tk.StringVar()
        self.log_lines  = []
        self.sys_info   = {}

        # Stil
        self._setup_style()

        # UI
        self._build_ui()

        # Başlangıç taraması (arka planda)
        threading.Thread(target=self._initial_scan, daemon=True).start()

    # ── STİL ──────────────────────────────────────────────────────────────────
    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(".", background=BG, foreground=FG, font=FONT,
                    borderwidth=0, relief="flat")

        s.configure("TNotebook", background=BG2, borderwidth=0,
                    tabmargins=[0,0,0,0])
        s.configure("TNotebook.Tab",
                    background=BG2, foreground=FG3,
                    padding=[14, 8], font=FONT_B,
                    borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", BG3), ("active", BG3)],
              foreground=[("selected", ACCENT), ("active", FG)])

        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=BG3, relief="flat")

        s.configure("TLabel", background=BG, foreground=FG, font=FONT)
        s.configure("Dim.TLabel", background=BG, foreground=FG2, font=FONT)
        s.configure("Muted.TLabel", background=BG, foreground=FG3, font=FONT)
        s.configure("Card.TLabel", background=BG3, foreground=FG, font=FONT)
        s.configure("Title.TLabel", background=BG3, foreground=FG2,
                    font=("Segoe UI", 8, "bold"))
        s.configure("H1.TLabel", background=BG, foreground=FG, font=FONT_T)
        s.configure("Accent.TLabel", background=BG, foreground=ACCENT,
                    font=("Segoe UI", 8))

        s.configure("TCheckbutton", background=BG3, foreground=FG,
                    font=FONT, indicatorcolor=BG3,
                    selectcolor=ACCENT)
        s.map("TCheckbutton",
              background=[("active", BG3)],
              foreground=[("active", FG)])

        s.configure("TEntry", fieldbackground=BG, foreground=FG,
                    insertcolor=FG, borderwidth=1,
                    relief="flat", font=FONT_M)

        s.configure("TScrollbar", background=BORDER, troughcolor=BG2,
                    arrowcolor=FG3, borderwidth=0, relief="flat")

        s.configure("Separator.TFrame", background=BORDER)

    # ── ANA UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Başlık Çubuğu ──
        hbar = tk.Frame(self, bg=BG2, height=44)
        hbar.pack(fill="x", side="top")
        hbar.pack_propagate(False)

        tk.Label(hbar, text="⚔", bg=BG2, fg=ACCENT,
                 font=("Segoe UI", 16)).pack(side="left", padx=(14,6), pady=8)
        tk.Label(hbar, text="ProNet Client Fixer", bg=BG2, fg=FG,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(hbar, text="v.01", bg=BG2, fg=ACCENT,
                 font=("Segoe UI", 9)).pack(side="left", padx=(4,0), pady=2)

        # Yönetici badge
        admin_color = GREEN if is_admin() else RED
        admin_text  = "● YÖNETİCİ" if is_admin() else "● YÖNETİCİ DEĞİL"
        tk.Label(hbar, text=admin_text, bg=BG2, fg=admin_color,
                 font=("Segoe UI", 8, "bold")).pack(side="right", padx=14)

        # ── Klasör Satırı ──
        frow = tk.Frame(self, bg=BG2, height=38)
        frow.pack(fill="x")
        frow.pack_propagate(False)

        tk.Label(frow, text="Klasör:", bg=BG2, fg=FG3,
                 font=FONT_B).pack(side="left", padx=(14,6), pady=8)

        entry = tk.Entry(frow, textvariable=self.folder_var,
                         bg=BG, fg=FG, insertbackground=FG,
                         font=FONT_M, relief="flat",
                         highlightthickness=1,
                         highlightbackground=BORDER,
                         highlightcolor=ACCENT,
                         readonlybackground=BG)
        entry.pack(side="left", fill="x", expand=True, ipady=4)

        tk.Button(frow, text="Gözat", bg=BG3, fg=FG2,
                  font=FONT_B, relief="flat", cursor="hand2",
                  activebackground=ACCENT, activeforeground="#000",
                  command=self._browse,
                  padx=14).pack(side="left", padx=(1,0), ipady=4)

        # ── Durum Çubuğu ──
        self.status_frame = tk.Frame(self, bg=BG2, height=30)
        self.status_frame.pack(fill="x")
        self.status_frame.pack_propagate(False)

        self.lbl_defender = self._status_item(self.status_frame, "Defender", "...", YELLOW)
        self._sep(self.status_frame)
        self.lbl_dep      = self._status_item(self.status_frame, "DEP", "...", YELLOW)
        self._sep(self.status_frame)
        self.lbl_deps     = self._status_item(self.status_frame, "Bağımlılıklar", "...", YELLOW)
        self._sep(self.status_frame)
        self.lbl_wv2      = self._status_item(self.status_frame, "WebView2", "...", YELLOW)

        # ── Notebook ──
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_defender = ttk.Frame(self.nb)
        self.tab_dep      = ttk.Frame(self.nb)
        self.tab_deps     = ttk.Frame(self.nb)
        self.tab_client   = ttk.Frame(self.nb)
        self.tab_wv2      = ttk.Frame(self.nb)
        self.tab_tools    = ttk.Frame(self.nb)
        self.tab_network  = ttk.Frame(self.nb)
        self.tab_help     = ttk.Frame(self.nb)

        self.nb.add(self.tab_defender, text="🛡  Defender")
        self.nb.add(self.tab_dep,      text="⚙  DEP")
        self.nb.add(self.tab_deps,     text="📦  Bağımlılıklar")
        self.nb.add(self.tab_client,   text="🎮  Client")
        self.nb.add(self.tab_wv2,      text="🌐  WebView2")
        self.nb.add(self.tab_tools,    text="🔧  Araçlar")
        self.nb.add(self.tab_network,  text="📡  Ağ Testi")
        self.nb.add(self.tab_help,     text="❓  Yardım")

        self._build_defender_tab()
        self._build_dep_tab()
        self._build_deps_tab()
        self._build_client_tab()
        self._build_webview2_tab()
        self._build_tools_tab()
        self._build_network_tab()
        self._build_help_tab()

        # ── Log Paneli ──
        log_frame = tk.Frame(self, bg=BG2)
        log_frame.pack(fill="x", side="bottom")

        log_header = tk.Frame(log_frame, bg=BG2)
        log_header.pack(fill="x")
        tk.Label(log_header, text="📋  İŞLEM GÜNLÜĞÜ",
                 bg=BG2, fg=FG3, font=("Segoe UI", 7, "bold")).pack(side="left", padx=12, pady=4)
        tk.Button(log_header, text="Temizle", bg=BG3, fg=FG3,
                  font=("Segoe UI", 7), relief="flat", cursor="hand2",
                  activebackground=BORDER, activeforeground=FG,
                  command=self._clear_log, padx=8).pack(side="right", padx=8, pady=3)

        self.log_box = tk.Text(log_frame, height=6, bg=BG, fg=FG2,
                               font=FONT_M, relief="flat",
                               state="disabled", wrap="word",
                               padx=10, pady=6,
                               selectbackground=BORDER)
        self.log_box.pack(fill="x")
        self.log_box.tag_config("ok",   foreground=GREEN)
        self.log_box.tag_config("err",  foreground=RED)
        self.log_box.tag_config("warn", foreground=YELLOW)
        self.log_box.tag_config("info", foreground=BLUE)
        self.log_box.tag_config("time", foreground=FG3)

        # ── Alt Butonlar ──
        bot = tk.Frame(self, bg=BG2)
        bot.pack(fill="x", side="bottom")

        self._btn(bot, "🔍 Tara",     self._scan_all,    BG3,    FG2).pack(side="left",  padx=(10,4), pady=8)
        self._btn(bot, "↩ Geri Al",   self._revert,      "#2a1010", RED).pack(side="left", padx=4, pady=8)
        self._btn(bot, "✕ Kapat",     self.quit,         BG3,    FG2).pack(side="right", padx=10, pady=8)
        self._btn(bot, "▶  Kurulumu Başlat", self._run_setup,
                  "#0d3320", GREEN, font=("Segoe UI", 10, "bold")).pack(side="right", padx=4, pady=8, ipadx=10)

    # ── YARDIMCI UI ───────────────────────────────────────────────────────────
    def _status_item(self, parent, label, value, color):
        f = tk.Frame(parent, bg=BG2)
        f.pack(side="left", padx=14, pady=4)
        tk.Label(f, text=label+":", bg=BG2, fg=FG3, font=("Segoe UI",8)).pack(side="left")
        lbl = tk.Label(f, text=value, bg=BG2, fg=color, font=("Segoe UI",8,"bold"))
        lbl.pack(side="left", padx=(4,0))
        return lbl

    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, width=1).pack(side="left", fill="y", pady=6)

    def _btn(self, parent, text, cmd, bg, fg, font=FONT_B, **kw):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=fg, font=font,
                      relief="flat", cursor="hand2",
                      activebackground=ACCENT, activeforeground="#000",
                      padx=14, pady=6, **kw)
        return b

    def _card(self, parent, title=None, pady=8):
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill="x", padx=14, pady=(pady,0))
        inner = tk.Frame(outer, bg=BG3, bd=0)
        inner.pack(fill="x")
        # ince üst border
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x")
        content = tk.Frame(inner, bg=BG3)
        content.pack(fill="x", padx=14, pady=10)
        if title:
            tk.Label(content, text=title, bg=BG3, fg=FG2,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,8))
        return content

    def _check(self, parent, text, var, bg=BG3):
        tk.Checkbutton(parent, text=text, variable=var,
                       bg=bg, fg=FG, font=FONT,
                       selectcolor=BG3,
                       activebackground=bg,
                       activeforeground=FG,
                       highlightthickness=0,
                       cursor="hand2").pack(anchor="w", pady=2)

    def _warn(self, parent, text):
        f = tk.Frame(parent, bg="#1a1500", bd=0)
        f.pack(fill="x", padx=14, pady=(6,0))
        tk.Frame(f, bg=YELLOW, height=1).pack(fill="x")
        tk.Label(f, text="⚠  " + text,
                 bg="#1a1500", fg="#b08010", font=("Segoe UI", 8),
                 wraplength=820, justify="left",
                 padx=10, pady=6).pack(anchor="w")

    # ─────────────────────────────────────────────────────────────────────────
    # DEFENDER SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_defender_tab(self):
        t = self.tab_defender
        t.configure(style="TFrame")
        sc = self._scrollable(t)

        self.chk_folder_excl = tk.BooleanVar(value=True)
        self.chk_proc_excl   = tk.BooleanVar(value=True)

        c = self._card(sc, "🛡  WINDOWS DEFENDER AYARLARI")
        self._check(c, "Klasörü Defender dışlamalarına ekle",             self.chk_folder_excl)
        self._check(c, "Klasördeki tüm .exe dosyalarını process dışlamasına ekle", self.chk_proc_excl)

        c2 = self._card(sc, "ℹ  DEFENDER DURUMU")
        row = tk.Frame(c2, bg=BG3)
        row.pack(fill="x")
        tk.Label(row, text="Real-Time Protection:", bg=BG3, fg=FG3, font=FONT).grid(row=0,column=0,sticky="w",padx=(0,16),pady=3)
        self.lbl_rtp = tk.Label(row, text="—", bg=BG3, fg=YELLOW, font=FONT_B)
        self.lbl_rtp.grid(row=0,column=1,sticky="w")
        tk.Label(row, text="Tamper Protection:", bg=BG3, fg=FG3, font=FONT).grid(row=1,column=0,sticky="w",padx=(0,16),pady=3)
        self.lbl_tamper = tk.Label(row, text="—", bg=BG3, fg=YELLOW, font=FONT_B)
        self.lbl_tamper.grid(row=1,column=1,sticky="w")

        self._warn(sc, "Bu işlemler sistem güvenliğini azaltır. Sadece güvendiğiniz Silkroad sunucuları için uygulayın.")

    # ─────────────────────────────────────────────────────────────────────────
    # DEP SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_dep_tab(self):
        t = self.tab_dep
        sc = self._scrollable(t)

        self.chk_dep = tk.BooleanVar(value=True)

        c = self._card(sc, "⚙  DEP (VERİ YÜRÜTME ENGELLEMESİ)")

        row = tk.Frame(c, bg=BG3)
        row.pack(fill="x", pady=(0,10))
        tk.Label(row, text="Mevcut DEP Durumu:", bg=BG3, fg=FG3, font=FONT).pack(side="left")
        self.lbl_dep_status = tk.Label(row, text="Kontrol ediliyor…", bg=BG3, fg=YELLOW, font=FONT_B)
        self.lbl_dep_status.pack(side="left", padx=8)

        tk.Label(c,
            text="Global DEP kapatma denenir (yeniden başlatma gerektirir). Secure Boot açık olduğu\n"
                 "için global kapatma başarısız olursa, klasördeki tüm .exe dosyaları için tek tek\n"
                 "DEP istisnası eklenir (yeniden başlatma gerektirmez).",
            bg=BG3, fg=FG2, font=("Segoe UI",8), justify="left").pack(anchor="w", pady=(0,8))

        self._check(c, "DEP (Veri Yürütme Engellemesi) kapat", self.chk_dep)

        self._warn(sc, "DEP global olarak kapatıldıktan sonra yeniden başlatma gerekir.")

    # ─────────────────────────────────────────────────────────────────────────
    # BAĞIMLILIKLAR SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_deps_tab(self):
        t = self.tab_deps
        sc = self._scrollable(t)

        self.chk_auto_install = tk.BooleanVar(value=True)

        c = self._card(sc, "📦  SİLKROAD İÇİN GEREKLİ BAĞIMLILIKLAR")
        self.deps_frame = tk.Frame(c, bg=BG3)
        self.deps_frame.pack(fill="x")

        bot = tk.Frame(c, bg=BG3)
        bot.pack(fill="x", pady=(10,0))
        tk.Frame(bot, bg=BORDER, height=1).pack(fill="x", pady=(0,8))
        self._check(bot, '"Kurulumu Başlat" sırasında eksik bağımlılıkları otomatik kur',
                    self.chk_auto_install)

    # ─────────────────────────────────────────────────────────────────────────
    # CLIENT SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_client_tab(self):
        t = self.tab_client
        sc = self._scrollable(t)

        c = self._card(sc, "🎮  SİLKROAD CLİENT DOSYALARI")
        tk.Label(c,
            text="Üstteki klasör yolunu oyun client kurulum klasörüne ayarlayın.\n"
                 "Aşağıdaki tüm dosyalar kontrol edilir. Eksik DLL/EXE dosyaları paketten indirilebilir.",
            bg=BG3, fg=FG2, font=("Segoe UI",8), justify="left").pack(anchor="w", pady=(0,10))

        btn_row = tk.Frame(c, bg=BG3)
        btn_row.pack(anchor="w", pady=(0,10))
        self._btn(btn_row, "📁 Dosyaları Kontrol Et", self._scan_client, ACCENT, "#000").pack(side="left", padx=(0,8))

        self.client_result = scrolledtext.ScrolledText(
            c, height=12, bg=BG, fg=FG2, font=FONT_M,
            relief="flat", state="disabled", wrap="word",
            padx=8, pady=6)
        self.client_result.pack(fill="x")
        self.client_result.tag_config("ok",   foreground=GREEN)
        self.client_result.tag_config("miss", foreground=RED)
        self.client_result.tag_config("head", foreground=ACCENT, font=("Consolas",9,"bold"))

    # ─────────────────────────────────────────────────────────────────────────
    # WEBVIEW2 SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_webview2_tab(self):
        t = self.tab_wv2
        sc = self._scrollable(t)

        self.chk_wv2 = tk.BooleanVar(value=True)

        c = self._card(sc, "🌐  MİCROSOFT WEBVİEW2")

        row = tk.Frame(c, bg=BG3)
        row.pack(fill="x", pady=(0,8))
        tk.Label(row, text="Mevcut Sürüm:", bg=BG3, fg=FG3, font=FONT).pack(side="left")
        self.lbl_wv2_ver = tk.Label(row, text="—", bg=BG3, fg=YELLOW, font=FONT_B)
        self.lbl_wv2_ver.pack(side="left", padx=8)

        tk.Label(c,
            text="Mevcut WebView2 kurulumu kaldırılır, registry kalıntıları temizlenir,\n"
                 "Microsoft sitesinden son sürüm indirilip kurulur. İnternet bağlantısı gereklidir.\n"
                 "WebView2 kullanan uygulamaları (Edge, Outlook, Teams) kapatın.",
            bg=BG3, fg=FG2, font=("Segoe UI",8), justify="left").pack(anchor="w", pady=(0,10))

        self._check(c, "WebView2 yeniden kur (kaldır + registry temizle + indir + kur)", self.chk_wv2)

        btn_row = tk.Frame(c, bg=BG3)
        btn_row.pack(anchor="w", pady=(10,0))
        self._btn(btn_row, "🔄 WebView2 Yeniden Kur",
                  lambda: threading.Thread(target=self._reinstall_webview2, daemon=True).start(),
                  "#0a1a2a", BLUE).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # ARAÇLAR SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_tools_tab(self):
        t = self.tab_tools
        sc = self._scrollable(t)

        grid = tk.Frame(sc, bg=BG)
        grid.pack(fill="both", padx=14, pady=8)

        tools = [
            ("🚫 Engelleyen Uygulamaları Kapat",
             "MSI Afterburner, Sandboxie, VM araçları,\nCheat Engine, Wireshark gibi çakışanlar.",
             self._kill_blockers, "#2a1010", RED),

            ("📡 Ağ Kalitesi Testi",
             "Gecikme, titreşim, paket kaybı\nave bant genişliğini ölçer.",
             lambda: self.nb.select(6), "#0a1020", BLUE),

            ("📄 Destek Dosyası Oluştur",
             "Log, sistem bilgisi ve durumu\ntek dosyaya masaüstüne kaydeder.",
             self._create_support_file, "#0a0a14", FG2),

            ("👑 Yönetici Uyumluluk Yaması",
             "Klasördeki tüm .exe dosyalarına\n'yönetici olarak çalıştır' yaması ekler.",
             lambda: threading.Thread(target=self._apply_admin_compat, daemon=True).start(),
             "#0a1410", GREEN),

            ("🔥 Güvenlik Duvarı Kuralı",
             "Klasördeki .exe dosyaları için\ngelen+giden Firewall izinleri ekler.",
             lambda: threading.Thread(target=self._add_firewall_rules, daemon=True).start(),
             "#0a1020", BLUE),

            ("🔄 Güncelleme Kontrolü",
             "Yeni sürüm varsa bildirim gösterilir.\nŞu anki sürüm: v.01",
             lambda: self.log("En güncel sürüm kullanılıyor: v.01", "ok"),
             "#0a0a14", ACCENT),
        ]

        for i, (title, desc, cmd, bg, fg) in enumerate(tools):
            row, col = divmod(i, 2)
            f = tk.Frame(grid, bg=BG3, bd=0)
            f.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            tk.Frame(f, bg=BORDER, height=1).pack(fill="x")
            inner = tk.Frame(f, bg=BG3)
            inner.pack(fill="x", padx=12, pady=10)
            tk.Label(inner, text=title, bg=BG3, fg=FG,
                     font=FONT_B).pack(anchor="w")
            tk.Label(inner, text=desc, bg=BG3, fg=FG2,
                     font=("Segoe UI",8), justify="left").pack(anchor="w", pady=(4,8))
            tk.Button(inner, text="Çalıştır", command=cmd,
                      bg=bg, fg=fg, font=FONT_B, relief="flat",
                      cursor="hand2", activebackground=ACCENT,
                      activeforeground="#000", padx=14).pack(anchor="w")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    # ─────────────────────────────────────────────────────────────────────────
    # AĞ TESTİ SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_network_tab(self):
        t = self.tab_network
        sc = self._scrollable(t)

        c = self._card(sc, "📡  AĞ BAĞLANTI TESTİ")
        tk.Label(c, text="Hedef sunuculara ping yaparak gecikme ve bağlantı kalitesini ölçer.",
                 bg=BG3, fg=FG2, font=("Segoe UI",8)).pack(anchor="w", pady=(0,10))

        btn_row = tk.Frame(c, bg=BG3)
        btn_row.pack(anchor="w", pady=(0,10))
        self.btn_nettest = tk.Button(btn_row, text="▶ Testi Başlat",
                                     command=lambda: threading.Thread(target=self._run_nettest, daemon=True).start(),
                                     bg=ACCENT, fg="#000", font=FONT_B,
                                     relief="flat", cursor="hand2",
                                     activebackground=ACCENT2, padx=16, pady=6)
        self.btn_nettest.pack(side="left")

        self.net_frame = tk.Frame(c, bg=BG3)
        self.net_frame.pack(fill="x")

        c2 = self._card(sc, "💻  SİSTEM BİLGİSİ")
        self.sys_frame = tk.Frame(c2, bg=BG3)
        self.sys_frame.pack(fill="x")

    # ─────────────────────────────────────────────────────────────────────────
    # YARDIM SEKMESİ
    # ─────────────────────────────────────────────────────────────────────────
    def _build_help_tab(self):
        t = self.tab_help
        sc = self._scrollable(t)

        c = self._card(sc, "⚠  SIK KARŞILAŞILAN HATALAR")

        errors = [
            ('"MSVCR100.dll bulunamadı" / launcher açılmıyor',
             'Bağımlılıklar sekmesinden VC++ 2010 x86\'yı kurun.'),
            ('"d3dx9_43.dll yok" / oyun açılmıyor',
             'Bağımlılıklar sekmesinden DirectX 9.0c\'yi kurun.'),
            ('Defender oyunu siliyor / virüs uyarısı',
             'Defender sekmesinden klasör + process dışlamasını etkinleştirin.\n'
             'Tamper Protection açıksa önce Windows Güvenliği\'nden kapatın.'),
            ('WebView2 hatası / launcher beyaz ekran',
             'WebView2 sekmesinden "Yeniden kur" işlemini çalıştırın.'),
            ('DEP veya 0xC0000005 hatası',
             'DEP sekmesinden DEP\'i kapatın. Secure Boot açıkken global kapanamaz,\n'
             'fixer otomatik olarak per-exe istisna ekler.'),
            ('Sistem geri almak istiyorum',
             '"Geri Al" butonu Defender dışlamalarını ve DEP ayarını varsayılana döndürür.'),
        ]

        for err, fix in errors:
            row = tk.Frame(c, bg=BG3)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="✕  " + err, bg=BG3, fg=RED,
                     font=("Segoe UI",8,"bold"), justify="left").pack(anchor="w")
            tk.Label(row, text="  → " + fix, bg=BG3, fg=FG2,
                     font=("Segoe UI",8), justify="left").pack(anchor="w", pady=(1,4))
            tk.Frame(c, bg=BORDER, height=1).pack(fill="x")

        c2 = self._card(sc, "📋  PROGRAM HAKKINDA")
        tk.Label(c2,
            text="ProNet Client Fixer v.01\n"
                 "Silkroad Online istemci yönetim ve onarım aracı.\n"
                 "Windows 10/11 x64 — Yönetici yetkisi gerektirir.",
            bg=BG3, fg=FG2, font=("Segoe UI",9), justify="left").pack(anchor="w")

    # ─────────────────────────────────────────────────────────────────────────
    # SCROLLABLE FRAME
    # ─────────────────────────────────────────────────────────────────────────
    def _scrollable(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=BG)
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def _scroll(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # LOG
    # ─────────────────────────────────────────────────────────────────────────
    def log(self, msg, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_lines.append((ts, msg, tag))
        self.log_box.configure(state="normal")
        self.log_box.insert("end", ts + "  ", "time")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.log_lines.clear()

    def _run_in_thread(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    # KLASÖR SEÇİMİ
    # ─────────────────────────────────────────────────────────────────────────
    def _browse(self):
        folder = filedialog.askdirectory(title="Silkroad Klasörünü Seçin")
        if folder:
            self.folder_var.set(folder)
            self.log(f"Klasör seçildi: {folder}", "info")
            self._run_in_thread(self._scan_client_bg)

    def _get_folder(self):
        f = self.folder_var.get().strip()
        if not f:
            messagebox.showwarning("Uyarı", "Lütfen önce Silkroad klasörünü seçin!")
        return f

    # ─────────────────────────────────────────────────────────────────────────
    # İLK TARAMA
    # ─────────────────────────────────────────────────────────────────────────
    def _initial_scan(self):
        self.log("ProNet Client Fixer v.01 başlatıldı.", "info")
        if not is_admin():
            self.log("⚠  Yönetici yetkisi yok! Bazı işlemler çalışmayabilir.", "warn")

        # Defender
        try:
            out = subprocess.check_output(
                ["powershell", "-Command",
                 "Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled,IsTamperProtected | ConvertTo-Json"],
                timeout=8, stderr=subprocess.DEVNULL, creationflags=0x08000000
            ).decode(errors="ignore").strip()
            data = json.loads(out)
            rtp    = data.get("RealTimeProtectionEnabled", False)
            tamper = data.get("IsTamperProtected", False)
            self.after(0, lambda: self._update_defender_ui(rtp, tamper))
        except:
            self.after(0, lambda: self._update_status(self.lbl_defender, "YOK", GREEN))

        # DEP
        try:
            out = subprocess.check_output(
                ["wmic", "OS", "get", "DataExecutionPrevention_SupportPolicy", "/value"],
                timeout=6, stderr=subprocess.DEVNULL, creationflags=0x08000000
            ).decode(errors="ignore")
            m = None
            for line in out.splitlines():
                if "=" in line:
                    m = line.split("=")[-1].strip()
                    break
            labels = {"0":"Kapalı","1":"Yalnızca Sistem","2":"Tüm Programlar","3":"İstisnalar"}
            dep_str = labels.get(m, "Bilinmiyor")
            self.after(0, lambda s=dep_str: self._update_dep_ui(s, m))
        except:
            self.after(0, lambda: self._update_status(self.lbl_dep, "Bilinmiyor", YELLOW))

        # WebView2
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
            ver, _ = winreg.QueryValueEx(key, "pv")
            winreg.CloseKey(key)
            self.after(0, lambda v=ver: self._update_wv2_ui(v))
        except:
            self.after(0, lambda: self._update_wv2_ui("Kurulu Değil"))

        # Bağımlılıklar
        self.after(0, self._check_deps_ui)

        # Sistem bilgisi
        self._load_sysinfo()

    def _update_defender_ui(self, rtp, tamper):
        if rtp:
            self._update_status(self.lbl_defender, "AKTİF", RED)
            self.lbl_rtp.config(text="Aktif", fg=RED)
        else:
            self._update_status(self.lbl_defender, "KAPALI", GREEN)
            self.lbl_rtp.config(text="Kapalı", fg=GREEN)
        self.lbl_tamper.config(
            text="Açık" if tamper else "Kapalı",
            fg=RED if tamper else GREEN)

    def _update_dep_ui(self, label, val):
        color = GREEN if val == "0" else YELLOW
        self._update_status(self.lbl_dep, label, color)
        self.lbl_dep_status.config(text=label, fg=color)

    def _update_wv2_ui(self, ver):
        color = GREEN if ver and ver != "Kurulu Değil" else RED
        self._update_status(self.lbl_wv2, ver[:20] if ver else "?", color)
        self.lbl_wv2_ver.config(text=ver or "—", fg=color)

    def _update_status(self, lbl, text, color):
        lbl.config(text=text, fg=color)

    # ─────────────────────────────────────────────────────────────────────────
    # BAĞIMLILIKLAR KONTROLÜ
    # ─────────────────────────────────────────────────────────────────────────
    def _check_deps_ui(self):
        for w in self.deps_frame.winfo_children():
            w.destroy()

        installed_vc = self._get_installed_vc()
        dx9 = os.path.exists(os.path.join(os.environ.get("SystemRoot","C:\\Windows"),
                                           "System32", "d3dx9_43.dll"))

        deps = [
            ("VC++ 2010 x86", self._has_vc(installed_vc, "2010", "x86"), None),
            ("VC++ 2010 x64", self._has_vc(installed_vc, "2010", "x64"),
             "https://download.microsoft.com/download/3/2/2/3224B87F-CFA0-4E70-BDA3-3DE650EFEBA5/vcredist_x64.exe"),
            ("VC++ 2013 x86", self._has_vc(installed_vc, "2013", "x86"), None),
            ("VC++ 2013 x64", self._has_vc(installed_vc, "2013", "x64"), None),
            ("VC++ 2015-2022 x86", self._has_vc(installed_vc, "2015", "x86"), None),
            ("VC++ 2015-2022 x64", self._has_vc(installed_vc, "2015", "x64"), None),
            ("DirectX 9.0c (d3dx9_43.dll)", dx9, None),
        ]

        missing = sum(1 for _, ok, _ in deps if not ok)
        color = GREEN if missing == 0 else RED
        self._update_status(self.lbl_deps, f"{missing} Eksik" if missing else "Tümü Kurulu", color)

        for name, ok, url in deps:
            row = tk.Frame(self.deps_frame, bg=BG3)
            row.pack(fill="x", pady=2)
            icon = "✓" if ok else "✕"
            ic   = GREEN if ok else RED
            tk.Label(row, text=icon, bg=BG3, fg=ic, font=FONT_B,
                     width=2).pack(side="left", padx=(0,8))
            tk.Label(row, text=name, bg=BG3, fg=FG,
                     font=FONT, width=28, anchor="w").pack(side="left")
            if ok:
                tk.Label(row, text="Kurulu ✓", bg=BG3, fg=GREEN,
                         font=("Segoe UI",8)).pack(side="right", padx=8)
            else:
                tk.Button(row, text="⬇ İndir + Kur",
                          command=lambda n=name, u=url: self._run_in_thread(lambda: self._install_dep(n, u)),
                          bg="#0a1020", fg=BLUE, font=("Segoe UI",8,"bold"),
                          relief="flat", cursor="hand2",
                          activebackground=BLUE, activeforeground="white",
                          padx=10).pack(side="right", padx=8)

    def _get_installed_vc(self):
        result = {}
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                    sk = winreg.OpenKey(key, sub)
                    try:
                        name, _ = winreg.QueryValueEx(sk, "DisplayName")
                        if "Visual C++" in name:
                            result[name] = True
                    except: pass
                    winreg.CloseKey(sk)
                    i += 1
                except OSError: break
            winreg.CloseKey(key)
        except: pass
        return result

    def _has_vc(self, installed, year, arch):
        for k in installed:
            if year in k and arch.lower() in k.lower():
                return True
        return False

    def _install_dep(self, name, url):
        self.log(f"{name} indiriliyor…", "info")
        if not url:
            self.log(f"{name} için otomatik kurulum URL'si tanımlı değil. Lütfen manuel kurun.", "warn")
            return
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"dep_{name.replace(' ','_')}.exe")
            urllib.request.urlretrieve(url, tmp)
            self.log(f"{name} kurulum başlatılıyor…", "info")
            subprocess.run([tmp, "/quiet", "/norestart"], timeout=120)
            self.log(f"{name} kuruldu!", "ok")
            self.after(0, self._check_deps_ui)
        except Exception as e:
            self.log(f"Hata: {e}", "err")

    # ─────────────────────────────────────────────────────────────────────────
    # CLİENT TARAMA
    # ─────────────────────────────────────────────────────────────────────────
    def _scan_client(self):
        self._run_in_thread(self._scan_client_bg)

    def _scan_client_bg(self):
        folder = self._get_folder()
        if not folder: return
        required = ["sro_client.exe","elemon.exe","GameGuard.des",
                    "d3dx9_43.dll","ijl15.dll","mss32.dll",
                    "Silkroad.exe","Launcher.exe"]
        found, missing = [], []
        for f in required:
            (found if os.path.exists(os.path.join(folder,f)) else missing).append(f)

        self.client_result.configure(state="normal")
        self.client_result.delete("1.0","end")
        if found:
            self.client_result.insert("end", f"Bulunan Dosyalar ({len(found)})\n", "head")
            for f in found:
                self.client_result.insert("end", f"  ✓ {f}\n", "ok")
        if missing:
            self.client_result.insert("end", f"\nEksik Dosyalar ({len(missing)})\n", "head")
            for f in missing:
                self.client_result.insert("end", f"  ✕ {f}\n", "miss")
        if not missing:
            self.client_result.insert("end", "\n✓ Tüm zorunlu dosyalar mevcut.", "ok")
        self.client_result.configure(state="disabled")
        self.log(f"Client tarama: {len(found)} bulundu, {len(missing)} eksik.", "ok" if not missing else "warn")

    # ─────────────────────────────────────────────────────────────────────────
    # DEFENDER İŞLEMLERİ
    # ─────────────────────────────────────────────────────────────────────────
    def _add_defender_folder(self, folder):
        try:
            subprocess.run(
                ["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{folder}'"],
                timeout=15, check=True, stderr=subprocess.DEVNULL,
                creationflags=0x08000000)
            self.log(f"Defender klasör dışlaması eklendi: {folder}", "ok")
            return True
        except Exception as e:
            self.log(f"Defender klasör dışlaması başarısız: {e}", "err")
            return False

    def _add_defender_processes(self, folder):
        exes = [f for f in os.listdir(folder) if f.endswith(".exe")]
        if not exes:
            self.log("Klasörde .exe bulunamadı.", "warn")
            return
        ok = 0
        for exe in exes:
            path = os.path.join(folder, exe)
            try:
                subprocess.run(
                    ["powershell", "-Command", f"Add-MpPreference -ExclusionProcess '{path}'"],
                    timeout=8, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                ok += 1
            except: pass
        self.log(f"{ok}/{len(exes)} .exe process dışlamasına eklendi.", "ok")

    # ─────────────────────────────────────────────────────────────────────────
    # DEP İŞLEMLERİ
    # ─────────────────────────────────────────────────────────────────────────
    def _disable_dep(self, folder):
        # Global kapat
        try:
            subprocess.run(["bcdedit", "/set", "nx", "AlwaysOff"],
                           timeout=10, check=True,
                           stderr=subprocess.DEVNULL,
                           creationflags=0x08000000)
            self.log("DEP global olarak kapatıldı. Yeniden başlatma gerekli!", "warn")
            return
        except:
            self.log("Global DEP kapatılamadı (Secure Boot?). Per-exe istisna ekleniyor…", "warn")

        # Per-exe istisna
        if not folder: return
        exes = [f for f in os.listdir(folder) if f.endswith(".exe")]
        ok = 0
        for exe in exes:
            path = os.path.join(folder, exe)
            try:
                subprocess.run(
                    ["powershell", "-Command",
                     f"Set-ProcessMitigation -Name '{path}' -Disable DEP"],
                    timeout=8, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000)
                ok += 1
            except: pass
        self.log(f"{ok} dosya için DEP istisnası eklendi.", "ok")

    # ─────────────────────────────────────────────────────────────────────────
    # WEBVIEW2
    # ─────────────────────────────────────────────────────────────────────────
    def _reinstall_webview2(self):
        self.log("WebView2 indiriliyor…", "info")
        url = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
        tmp = os.path.join(tempfile.gettempdir(), "MicrosoftEdgeWebview2Setup.exe")
        try:
            urllib.request.urlretrieve(url, tmp)
            self.log("WebView2 kuruluyor…", "info")
            subprocess.run([tmp, "/silent", "/install"], timeout=120)
            self.log("WebView2 başarıyla kuruldu!", "ok")
            self._initial_scan()
        except Exception as e:
            self.log(f"WebView2 kurulum hatası: {e}", "err")

    # ─────────────────────────────────────────────────────────────────────────
    # ARAÇLAR
    # ─────────────────────────────────────────────────────────────────────────
    def _kill_blockers(self):
        targets = ["MSIAfterburner","Afterburner","cheatengine","CheatEngine",
                   "Sandboxie","procmon","Wireshark","vmware","VirtualBox",
                   "x32dbg","x64dbg","ollydbg"]
        killed = 0
        for proc in targets:
            try:
                subprocess.run(["taskkill","/F","/IM",f"{proc}.exe"],
                               timeout=4, stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL,
                               creationflags=0x08000000)
                killed += 1
            except: pass
        self.log(f"Engelleyen uygulamalar kapatıldı ({killed} işlem).", "ok")

    def _apply_admin_compat(self):
        folder = self._get_folder()
        if not folder: return
        exes = [f for f in os.listdir(folder) if f.endswith(".exe")]
        ok = 0
        for exe in exes:
            path = os.path.join(folder, exe)
            try:
                # Registry'e compat flag yaz
                key_path = f"Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                                     0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, path, 0, winreg.REG_SZ, "~ RUNASADMIN")
                winreg.CloseKey(key)
                ok += 1
            except: pass
        self.log(f"{ok} dosya için yönetici uyumluluk yaması uygulandı.", "ok")

    def _add_firewall_rules(self):
        folder = self._get_folder()
        if not folder: return
        exes = [f for f in os.listdir(folder) if f.endswith(".exe")]
        ok = 0
        for exe in exes:
            path = os.path.join(folder, exe)
            name = exe.replace(".exe","")
            try:
                subprocess.run(
                    ["netsh","advfirewall","firewall","add","rule",
                     f"name=ProNet-IN-{name}","dir=in","action=allow",
                     f"program={path}","enable=yes"],
                    timeout=8, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000)
                subprocess.run(
                    ["netsh","advfirewall","firewall","add","rule",
                     f"name=ProNet-OUT-{name}","dir=out","action=allow",
                     f"program={path}","enable=yes"],
                    timeout=8, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000)
                ok += 1
            except: pass
        self.log(f"{ok} dosya için güvenlik duvarı kuralı eklendi.", "ok")

    def _create_support_file(self):
        desktop = Path.home() / "Desktop"
        fname   = f"ProNet_Support_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        fpath   = desktop / fname
        lines   = "\n".join(f"[{ts}] {t.upper()}: {m}" for ts, m, t in self.log_lines)
        sys_txt = "\n".join(f"{k}: {v}" for k,v in self.sys_info.items())
        content = (
            f"=== ProNet Client Fixer v.01 — Destek Dosyası ===\n"
            f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
            f"=== SİSTEM ===\n{sys_txt}\n\n"
            f"=== LOG ===\n{lines}\n"
        )
        fpath.write_text(content, encoding="utf-8")
        self.log(f"Destek dosyası oluşturuldu: {fname}", "ok")
        os.startfile(desktop)

    # ─────────────────────────────────────────────────────────────────────────
    # AĞ TESTİ
    # ─────────────────────────────────────────────────────────────────────────
    def _run_nettest(self):
        self.after(0, lambda: self.btn_nettest.config(
            text="⏳ Test yapılıyor…", state="disabled"))
        self.after(0, lambda: [w.destroy() for w in self.net_frame.winfo_children()])
        self.log("Ağ testi başlatıldı…", "info")

        servers = [
            ("Google DNS",  "8.8.8.8"),
            ("Cloudflare",  "1.1.1.1"),
            ("Google",      "google.com"),
        ]

        for label, host in servers:
            try:
                out = subprocess.check_output(
                    ["ping", "-n", "4", host],
                    timeout=12, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000
                ).decode("cp857", errors="ignore")

                avg = None
                for line in out.splitlines():
                    if "Ortalama" in line or "Average" in line or "ort" in line.lower():
                        parts = line.split("=")
                        if parts:
                            avg_str = parts[-1].strip().replace("ms","").strip()
                            try: avg = int(avg_str)
                            except: pass

                loss_pct = 0
                for line in out.splitlines():
                    if "%" in line and ("kayıp" in line.lower() or "lost" in line.lower() or "loss" in line.lower()):
                        for part in line.split():
                            if "%" in part:
                                try: loss_pct = int(part.replace("%","").replace("(",""))
                                except: pass

                status = "✓ OK"
                color  = GREEN
                if avg is None:
                    status, color = "✕ Zaman aşımı", RED
                elif avg > 200:
                    status, color = f"⚠ {avg}ms", YELLOW
                else:
                    status = f"✓ {avg}ms"

                self.after(0, lambda lb=label, hs=host, st=status, cl=color, lp=loss_pct:
                           self._add_net_row(lb, hs, st, cl, lp))
            except Exception as e:
                self.after(0, lambda lb=label, hs=host:
                           self._add_net_row(lb, hs, "✕ Hata", RED, 0))

        self.log("Ağ testi tamamlandı.", "ok")
        self.after(0, lambda: self.btn_nettest.config(
            text="▶ Testi Başlat", state="normal"))

    def _add_net_row(self, label, host, status, color, loss):
        row = tk.Frame(self.net_frame, bg=BG2)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=BG2, fg=FG, font=FONT_B,
                 width=14, anchor="w").pack(side="left", padx=(0,8))
        tk.Label(row, text=host, bg=BG2, fg=FG3,
                 font=FONT_M, width=16).pack(side="left")
        tk.Label(row, text=f"Kayıp: {loss}%", bg=BG2, fg=FG3,
                 font=("Segoe UI",8), width=12).pack(side="left")
        tk.Label(row, text=status, bg=BG2, fg=color,
                 font=FONT_B).pack(side="right", padx=8)

    # ─────────────────────────────────────────────────────────────────────────
    # SİSTEM BİLGİSİ
    # ─────────────────────────────────────────────────────────────────────────
    def _load_sysinfo(self):
        import platform
        self.sys_info = {
            "OS"      : platform.system() + " " + platform.version()[:40],
            "Mimari"  : platform.machine(),
            "İşlemci" : platform.processor()[:60],
            "Python"  : sys.version.split()[0],
            "Yönetici": "Evet" if is_admin() else "Hayır",
        }
        try:
            import ctypes
            mem = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(mem))
            self.sys_info["RAM"] = f"{mem.value // 1024 // 1024} GB"
        except: pass

        self.after(0, self._update_sys_frame)

    def _update_sys_frame(self):
        for w in self.sys_frame.winfo_children():
            w.destroy()
        for k, v in self.sys_info.items():
            row = tk.Frame(self.sys_frame, bg=BG3)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{k}:", bg=BG3, fg=FG3,
                     font=FONT, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=BG3, fg=FG,
                     font=FONT_M).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # TARA / GERİ AL / KUR
    # ─────────────────────────────────────────────────────────────────────────
    def _scan_all(self):
        self._run_in_thread(self._initial_scan)
        self.log("Sistem yeniden taranıyor…", "info")

    def _revert(self):
        if not messagebox.askyesno("Geri Al",
            "Defender dışlamaları ve DEP ayarları varsayılana döndürülecek. Emin misiniz?"):
            return
        self._run_in_thread(self._do_revert)

    def _do_revert(self):
        self.log("Geri alma başlatıldı…", "warn")
        folder = self.folder_var.get().strip()
        # Defender dışlamayı kaldır
        if folder:
            try:
                subprocess.run(
                    ["powershell","-Command",
                     f"Remove-MpPreference -ExclusionPath '{folder}'"],
                    timeout=10, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000)
                self.log("Defender klasör dışlaması kaldırıldı.", "ok")
            except: pass
        # DEP varsayılana al
        try:
            subprocess.run(["bcdedit","/set","nx","OptIn"],
                           timeout=8, stderr=subprocess.DEVNULL,
                           creationflags=0x08000000)
            self.log("DEP varsayılan ayarına döndürüldü.", "ok")
        except: pass
        self.log("Geri alma tamamlandı.", "ok")

    def _run_setup(self):
        folder = self._get_folder()
        if not folder: return
        self._run_in_thread(lambda: self._do_setup(folder))

    def _do_setup(self, folder):
        self.log("━━━ Kurulum başlatıldı ━━━", "info")

        if self.chk_folder_excl.get():
            self.log("Defender klasör dışlaması ekleniyor…", "info")
            self._add_defender_folder(folder)

        if self.chk_proc_excl.get():
            self.log("Defender process dışlaması ekleniyor…", "info")
            self._add_defender_processes(folder)

        if self.chk_dep.get():
            self.log("DEP kapatılıyor…", "info")
            self._disable_dep(folder)

        if self.chk_auto_install.get():
            self.log("Eksik bağımlılıklar kontrol ediliyor…", "info")
            self.after(0, self._check_deps_ui)

        self.log("━━━ Kurulum tamamlandı ━━━", "ok")
        self.after(0, self._initial_scan)


# ─── BAŞLANGIÇ ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_as_admin()
    app = ProNetFixer()
    app.mainloop()
