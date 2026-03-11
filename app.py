#!/usr/bin/env python3
"""
PyShield Antivirus - Professional Desktop App
Redesigned UI - Direct integration (no subprocess spawning)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import time
import json
import platform
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

OPT_LOADED = False
try:
    from optimizer import (
        kill_bloat_processes, get_running_processes, kill_process_by_name, get_process_count,
        set_high_performance_power, set_ultimate_performance_power,
        disable_xbox_game_bar, disable_fullscreen_optimizations,
        set_timer_resolution, get_temp_size, clear_temp_files,
        clear_dns_cache, clear_prefetch, optimize_network,
        disable_animations, enable_animations, disable_transparency,
        set_best_performance_visual, get_startup_items, disable_startup_item,
        get_ram_info, free_standby_ram, get_system_info,
        disable_auto_updates_temporarily, enable_auto_updates
    )
    OPT_LOADED = True
except ImportError:
    pass

VPN_LOADED = False
try:
    from vpn import (
        get_ip_info, check_dns_leak, get_dns_servers,
        find_tor, start_tor, stop_tor, is_tor_running,
        set_win_proxy, get_tor_port, FREE_VPN_SERVERS, find_openvpn,
        generate_ovpn_config, COUNTRY_FLAGS,
        set_dns_servers, reset_dns_to_automatic, disable_webrtc_leak,
        enable_webrtc, block_non_vpn_traffic, remove_leak_firewall_rules,
        get_leak_status, PRIVACY_DNS_OPTIONS,
        ping_all_servers, get_fastest_server, ping_server,
        enable_kill_switch, disable_kill_switch, is_kill_switch_active,
        vpn_session_start, vpn_session_elapsed, get_network_stats
    )
    VPN_LOADED = True
except ImportError:
    pass

AV_LOADED = False
AV_ERROR  = ""
try:
    from antivirus import (
        Scanner, Quarantine, SignatureDB,
        load_config, LOG_FILE, QUARANTINE_DIR,
        get_all_drives
    )
    AV_LOADED = True
except ImportError as e:
    AV_ERROR = str(e)

# ─────────────────────────────────────────────
#  VERSION  —  bump this whenever you update
# ─────────────────────────────────────────────
VERSION = "2.0"

# GitHub raw URLs — points to YOUR repo
GITHUB_USER    = "stars1xxxxx-cloud"
GITHUB_REPO    = "TurbotweaksV.10"
VERSION_URL    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.txt"
APP_URL        = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/app.py"

def _check_for_updates(root_window):
    """Runs in background thread. Prompts user if update available."""
    try:
        import urllib.request
        with urllib.request.urlopen(VERSION_URL, timeout=5) as r:
            latest = r.read().decode().strip()

        if latest != VERSION:
            def prompt():
                answer = messagebox.askyesno(
                    "PyShield Update Available",
                    f"A new version of PyShield is available!\n\n"
                    f"  Current:  v{VERSION}\n"
                    f"  Latest:   v{latest}\n\n"
                    f"Update now? (The app will restart automatically)",
                    icon="info"
                )
                if answer:
                    _do_update(root_window, latest)
            root_window.after(0, prompt)
    except Exception:
        pass  # silently fail if no internet or GitHub down

def _do_update(root_window, new_version):
    """Downloads new app.py and restarts."""
    import urllib.request, shutil, subprocess
    try:
        app_path  = Path(__file__).resolve()
        backup    = app_path.with_suffix(".py.bak")
        tmp_path  = app_path.with_suffix(".py.new")

        # Download new version
        def download():
            try:
                urllib.request.urlretrieve(APP_URL, str(tmp_path))
                # Replace current file
                shutil.copy2(str(app_path), str(backup))
                shutil.move(str(tmp_path), str(app_path))
                # Restart
                def restart():
                    messagebox.showinfo(
                        "Updated!",
                        f"PyShield updated to v{new_version}!\nRestarting now..."
                    )
                    subprocess.Popen([sys.executable, str(app_path)])
                    root_window.destroy()
                root_window.after(0, restart)
            except Exception as e:
                root_window.after(0, lambda: messagebox.showerror(
                    "Update Failed",
                    f"Could not download update:\n{e}\n\nTry re-downloading manually from GitHub."
                ))
        threading.Thread(target=download, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Update Error", str(e))

# ─────────────────────────────────────────────
#  DESIGN TOKENS  —  Obsidian Premium Theme
# ─────────────────────────────────────────────
BG      = "#05060a"   # near-black
PANEL   = "#090c14"   # sidebar/topbar — deep navy
CARD    = "#0e1220"   # content cards
CARD2   = "#131828"   # raised card
CARD3   = "#181e32"   # deepest card
BORDER  = "#1a2038"   # subtle dividers
BORDER2 = "#232d50"   # visible borders
ACCENT  = "#00e5ff"   # electric cyan — sharp & cyber
ACCENTD = "#00b4cc"   # deeper accent
GREEN   = "#00e676"   # neon green
GREEND  = "#00b85a"   # deep green
AMBER   = "#ffab00"   # electric amber
RED     = "#ff1744"   # vivid red — danger
REDD    = "#c4000e"   # deep red
PURPLE  = "#d500f9"   # electric purple
TEXT    = "#e8eeff"   # cool white
TEXT2   = "#7a8aaa"   # secondary text
MUTED   = "#2a3555"   # muted elements
DARK    = "#030408"   # deepest black
GLOW    = "#00e5ff15" # glow tint
BLUE    = ACCENTD          # backwards compat alias
CARD_ALT = CARD2           # alias

# Typography — premium fonts
FT  = ("Segoe UI", 20, "bold")
FH  = ("Segoe UI", 13, "bold")
FB  = ("Segoe UI", 10)
FBB = ("Segoe UI Semibold", 10, "bold") if True else ("Segoe UI", 10, "bold")
FS  = ("Segoe UI", 8)
FM  = ("Consolas", 9)
FG  = ("Segoe UI", 26, "bold")
FC  = ("Segoe UI", 10)
FCB = ("Segoe UI Semibold", 10, "bold") if True else ("Segoe UI", 10, "bold")
FLG = ("Consolas", 14, "bold")  # logo font
FNM = ("Consolas", 9)           # nav monospace

# ─────────────────────────────────────────────
#  WIDGETS
# ─────────────────────────────────────────────
class GlowBtn(tk.Button):
    """Premium button with cyber glow hover effect."""
    def __init__(self, parent, text, bg=ACCENT, command=None, fg=DARK, **kw):
        super().__init__(
            parent, text=text, font=("Consolas", 9, "bold"),
            bg=bg, fg=fg, bd=0, padx=20, pady=10, cursor="hand2",
            activebackground=TEXT, activeforeground=DARK,
            relief="flat", command=command, **kw
        )
        self._bg  = bg
        self._fg  = fg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.configure(bg=TEXT, fg=DARK)

    def _on_leave(self, e):
        self.configure(bg=self._bg, fg=self._fg)


class OutlineBtn(tk.Button):
    """Ghost/outline button variant."""
    def __init__(self, parent, text, color=ACCENT, command=None, **kw):
        super().__init__(
            parent, text=text, font=("Consolas", 9, "bold"),
            bg=CARD2, fg=color, bd=0, padx=14, pady=8,
            cursor="hand2", activebackground=BORDER2,
            activeforeground=color, relief="flat", command=command,
            highlightthickness=1, highlightbackground=BORDER2,
            highlightcolor=color, **kw
        )
        self._color = color
        self.bind("<Enter>", lambda e: self.configure(bg=CARD3, highlightbackground=color))
        self.bind("<Leave>", lambda e: self.configure(bg=CARD2, highlightbackground=BORDER2))


class OutBox(tk.Text):
    """Styled terminal-style output box."""
    def __init__(self, parent, **kw):
        super().__init__(
            parent, font=("Consolas", 9), bg="#060d1a", fg=TEXT2,
            insertbackground=ACCENT, bd=0, wrap="word",
            state="disabled", highlightthickness=1,
            highlightbackground=BORDER2, highlightcolor=ACCENT,
            selectbackground=BORDER2, spacing1=2, spacing3=2,
            padx=8, pady=6, **kw
        )
        self.tag_configure("danger",  foreground="#fb7185")
        self.tag_configure("warn",    foreground=AMBER)
        self.tag_configure("success", foreground=GREEN)
        self.tag_configure("accent",  foreground=ACCENT)
        self.tag_configure("muted",   foreground=MUTED)
        self.tag_configure("white",   foreground=TEXT)

    def append(self, text, tag=None):
        self.configure(state="normal")
        if tag:
            self.insert("end", text, tag)
        else:
            self.insert("end", text)
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class StatCard(tk.Frame):
    """Premium stat display card with accent top bar and glow."""
    def __init__(self, parent, label, value, color=ACCENT, **kw):
        super().__init__(parent, bg=CARD2, **kw)
        # Top color bar
        tk.Frame(self, bg=color, height=3).pack(fill="x")
        inner = tk.Frame(self, bg=CARD2, padx=20, pady=16)
        inner.pack(fill="both", expand=True)
        self.val_lbl = tk.Label(inner, text=value,
                                font=("Consolas", 26, "bold"),
                                bg=CARD2, fg=color)
        self.val_lbl.pack(anchor="w")
        tk.Label(inner, text=label, font=("Consolas", 8),
                 bg=CARD2, fg=TEXT2).pack(anchor="w", pady=(2,0))

    def set(self, value, color=None):
        self.val_lbl.configure(text=value)
        if color:
            self.val_lbl.configure(fg=color)


def header(parent, title, sub=""):
    """Section header with colored left bar."""
    f = tk.Frame(parent, bg=BG)
    row = tk.Frame(f, bg=BG)
    row.pack(fill="x", anchor="w")
    tk.Frame(row, bg=ACCENT, width=4).pack(side="left", fill="y")
    right = tk.Frame(row, bg=BG, padx=14)
    right.pack(side="left")
    tk.Label(right, text=title, font=("Consolas", 16, "bold"),
             bg=BG, fg=TEXT).pack(anchor="w")
    if sub:
        tk.Label(right, text=sub, font=("Segoe UI", 9),
                 bg=BG, fg=TEXT2).pack(anchor="w", pady=(2,0))
    return f

def section_label(parent, text):
    """Small uppercase section divider label."""
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=text, font=("Consolas", 8, "bold"),
             bg=BG, fg=MUTED).pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8,0), pady=5)
    return f

def chk(parent, var, label):
    tk.Checkbutton(
        parent, text=label, variable=var, font=("Segoe UI", 9),
        bg=BG, fg=TEXT2, selectcolor=CARD2,
        activebackground=BG, activeforeground=ACCENT,
        cursor="hand2"
    ).pack(side="left", padx=(0,18))

# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyShield — Security Suite")
        self.geometry("1120x740")
        self.minsize(900, 600)
        self.configure(bg=BG)

        # State
        self._scanning   = False
        self._mon_active = False
        self._mon_thread = None
        self._tor_active = False
        self._vpn_proc   = None
        self._pulse_tick = 0

        self._build()
        self._show("dashboard")
        self._tick_clock()
        self._pulse_status()
        # Check for updates silently in background
        threading.Thread(target=_check_for_updates,
                         args=(self,), daemon=True).start()

    # ── Layout ────────────────────────────────
    def _build(self):
        # ── Top bar ──────────────────────────
        bar = tk.Frame(self, bg=PANEL, height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Top accent line
        tk.Frame(self, bg=ACCENT, height=1).place(x=0, y=0, relwidth=1)

        # Logo — icon box + name
        logo_frame = tk.Frame(bar, bg=PANEL)
        logo_frame.pack(side="left", padx=(22,0))

        # Glowing icon box
        icon_box = tk.Frame(logo_frame, bg=ACCENT, padx=10, pady=10)
        icon_box.pack(side="left", pady=14)
        tk.Label(icon_box, text="⬡", font=("Consolas", 14, "bold"),
                 bg=ACCENT, fg=DARK).pack()

        name_frame = tk.Frame(logo_frame, bg=PANEL)
        name_frame.pack(side="left", padx=(12,0))
        tk.Label(name_frame, text="PYSHIELD",
                 font=("Consolas", 15, "bold"),
                 bg=PANEL, fg=TEXT).pack(anchor="w", pady=(16,0))
        tk.Label(name_frame, text="SECURITY SUITE",
                 font=("Consolas", 7),
                 bg=PANEL, fg=MUTED).pack(anchor="w")

        # Divider
        tk.Frame(bar, bg=BORDER2, width=1).pack(side="left", fill="y", padx=22, pady=14)

        # Status pill
        self._status_frame = tk.Frame(bar, bg="#001a0e", padx=14, pady=0)
        self._status_frame.pack(side="left")
        self._status_dot = tk.Label(self._status_frame, text="●",
                                    font=("Segoe UI", 12),
                                    bg="#001a0e", fg=GREEN)
        self._status_dot.pack(side="left", pady=10)
        self._status_lbl = tk.Label(self._status_frame, text="PROTECTED",
                                    font=("Consolas", 9, "bold"),
                                    bg="#001a0e", fg=GREEN)
        self._status_lbl.pack(side="left", padx=(6,0))

        # Right side
        right = tk.Frame(bar, bg=PANEL)
        right.pack(side="right", padx=24)
        self._clock = tk.Label(right, text="",
                               font=("Consolas", 9), bg=PANEL, fg=TEXT2)
        self._clock.pack(side="right")
        tk.Frame(right, bg=BORDER2, width=1).pack(
            side="right", fill="y", pady=18, padx=14)
        tk.Label(right, text="v2.0", font=("Consolas", 8, "bold"),
                 bg=PANEL, fg=MUTED).pack(side="right")

        # Bottom accent line
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        # ── Sidebar ──────────────────────────
        side = tk.Frame(body, bg=PANEL, width=220)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")

        tk.Frame(side, bg=PANEL, height=20).pack()
        tk.Label(side, text="  NAVIGATION",
                 font=("Consolas", 7),
                 bg=PANEL, fg=MUTED).pack(anchor="w", padx=18, pady=(0,10))

        self._nav      = {}
        self._nav_bars = {}

        # Nav items — each with its own accent color
        items = [
            ("dashboard",  "◈", "Overview",      ACCENT),
            ("─", "", "", ""),
            ("scan",       "⬡", "File Scan",      GREEN),
            ("fullscan",   "◎", "Full PC Scan",   RED),
            ("monitor",    "◐", "Real-Time",       AMBER),
            ("quarantine", "⊘", "Quarantine",      RED),
            ("signatures", "⊞", "Signatures",      PURPLE),
            ("logs",       "≡", "Logs",            TEXT2),
            ("─", "", "", ""),
            ("vpn",        "⊕", "VPN & Privacy",  ACCENT),
            ("optimizer",  "◆", "Optimizer",       AMBER),
            ("─", "", "", ""),
            ("developers", "★", "Developers",      PURPLE),
        ]

        for pid, icon, lbl, color in items:
            if pid == "─":
                tk.Frame(side, bg=BORDER, height=1).pack(
                    fill="x", padx=18, pady=5)
                continue

            outer = tk.Frame(side, bg=PANEL, height=46)
            outer.pack(fill="x")
            outer.pack_propagate(False)

            bar_indicator = tk.Frame(outer, bg=PANEL, width=3)
            bar_indicator.pack(side="left", fill="y")
            self._nav_bars[pid] = bar_indicator

            inner = tk.Frame(outer, bg=PANEL)
            inner.pack(side="left", fill="both", expand=True)

            icon_lbl = tk.Label(inner, text=icon, font=("Segoe UI", 12),
                                bg=PANEL, fg=MUTED, width=3)
            icon_lbl.pack(side="left", padx=(8,6), pady=13)

            text_lbl = tk.Label(inner, text=lbl, font=("Segoe UI", 10),
                                bg=PANEL, fg=TEXT2, anchor="w")
            text_lbl.pack(side="left", fill="x", expand=True)

            def make_cmd(p=pid, il=icon_lbl, tl=text_lbl,
                         o=outer, i=inner, c=color):
                for w in (outer, inner, il, tl):
                    w.bind("<Button-1>", lambda e, p=p: self._show(p))
                    w.configure(cursor="hand2")
                    w.bind("<Enter>", lambda e, il=il, tl=tl, o=o, i=i:
                           [w2.configure(bg=CARD3) for w2 in (il,tl,o,i)
                            if w2.cget("bg") != CARD])
                    w.bind("<Leave>", lambda e, il=il, tl=tl, o=o, i=i:
                           [w2.configure(bg=PANEL) for w2 in (il,tl,o,i)
                            if w2.cget("bg") != CARD])

            make_cmd()
            self._nav[pid] = (outer, inner, icon_lbl, text_lbl, color)

        # Sidebar footer
        tk.Frame(side, bg=BORDER, height=1).pack(fill="x", side="bottom")
        btm = tk.Frame(side, bg=PANEL)
        btm.pack(side="bottom", fill="x", padx=18, pady=12)
        tk.Label(btm, text="PyShield v2.0",
                 font=("Consolas", 8, "bold"),
                 bg=PANEL, fg=TEXT2).pack(anchor="w")
        tk.Label(btm, text="Personal Security Suite",
                 font=("Segoe UI", 7),
                 bg=PANEL, fg=MUTED).pack(anchor="w")

        # ── Content area ─────────────────────
        self._content = tk.Frame(body, bg=BG)
        self._content.pack(side="right", fill="both", expand=True)

        self._pages = {
            "dashboard":  self._pg_dash(),
            "scan":       self._pg_scan(),
            "fullscan":   self._pg_fullscan(),
            "monitor":    self._pg_monitor(),
            "quarantine": self._pg_quarantine(),
            "signatures": self._pg_signatures(),
            "logs":       self._pg_logs(),
            "vpn":        self._pg_vpn(),
            "optimizer":  self._pg_optimizer(),
            "developers": self._pg_developers(),
        }

    def _show(self, pid):
        for p in self._pages.values():
            p.pack_forget()
        self._pages[pid].pack(fill="both", expand=True)

        for k, (outer, inner, icon_lbl, text_lbl, color) in self._nav.items():
            if k == pid:
                for w in (outer, inner, icon_lbl, text_lbl):
                    w.configure(bg=CARD)
                icon_lbl.configure(fg=color, font=("Segoe UI", 12, "bold"))
                text_lbl.configure(fg=TEXT,  font=("Segoe UI", 10, "bold"))
                self._nav_bars[k].configure(bg=color)
            else:
                for w in (outer, inner, icon_lbl, text_lbl):
                    w.configure(bg=PANEL)
                icon_lbl.configure(fg=MUTED, font=("Segoe UI", 12))
                text_lbl.configure(fg=TEXT2, font=("Segoe UI", 10))
                self._nav_bars[k].configure(bg=PANEL)

    def _tick_clock(self):
        self._clock.configure(
            text=datetime.now().strftime("%a  %d %b  %H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _pulse_status(self):
        """Animate the status dot for a live feel."""
        self._pulse_tick += 1
        if self._scanning or self._mon_active:
            colors = [ACCENT, ACCENTD, ACCENT]
            self._status_dot.configure(
                fg=colors[self._pulse_tick % len(colors)])
        self.after(600, self._pulse_status)

    def _setstatus(self, text, color=GREEN):
        bg = "#001a0e" if color == GREEN else \
             "#1a0e00" if color == AMBER else \
             "#1a0005" if color == RED  else \
             "#00101a"
        def update():
            self._status_lbl.configure(text=text.lstrip("● "), fg=color)
            self._status_dot.configure(fg=color)
            self._status_frame.configure(bg=bg)
            self._status_lbl.configure(bg=bg)
            self._status_dot.configure(bg=bg)
        self.after(0, update)

    # ── Dashboard ─────────────────────────────
    def _pg_dash(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "SECURITY OVERVIEW",
               "System status and quick actions").pack(fill="x", padx=30, pady=(25,18))

        # Stat cards — premium StatCard widgets
        row = tk.Frame(f, bg=BG)
        row.pack(fill="x", padx=30, pady=(0,22))
        self._stat_cards = {}
        for label, val, color in [
            ("Threats Found",  "0",    RED),
            ("Files Scanned",  "0",    ACCENT),
            ("Quarantined",    "0",    AMBER),
            ("Status",         "SAFE", GREEN),
        ]:
            sc = StatCard(row, label.upper(), val, color)
            sc.pack(side="left", expand=True, fill="both", padx=(0,10), ipady=4)
            self._stat_cards[label.replace(" ","")] = sc
        self._stats = {
            "THREATSFOUND": (None, RED),
            "FILESSCANNED": (None, ACCENT),
            "QUARANTINED":  (None, AMBER),
            "STATUS":       (None, GREEN),
        }

        # Quick actions
        tk.Label(f, text="QUICK ACTIONS", font=("Consolas", 9, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(5,8))
        acts = tk.Frame(f, bg=BG)
        acts.pack(fill="x", padx=30, pady=(0,18))
        GlowBtn(acts, "⬡  SCAN DOWNLOADS", ACCENT,
                command=lambda: self._quick_scan(str(Path.home()/"Downloads"))).pack(side="left", padx=(0,10))
        GlowBtn(acts, "⬡  SCAN DESKTOP", BLUE,
                command=lambda: self._quick_scan(
                    str(Path.home()/"OneDrive"/"Desktop"))).pack(side="left", padx=(0,10))
        GlowBtn(acts, "◎  FULL PC SCAN", RED,
                command=lambda: self._show("fullscan")).pack(side="left", padx=(0,10))
        OutlineBtn(acts, "⊘  QUARANTINE",
                   command=lambda: self._show("quarantine")).pack(side="left")

        # ── IP Leak Warning Banner (hidden by default) ──
        self._leak_banner = tk.Frame(f, bg="#1a0508", padx=20, pady=14)
        # Don't pack yet — shown only if leak detected

        banner_left = tk.Frame(self._leak_banner, bg="#1a0508")
        banner_left.pack(side="left", fill="x", expand=True)

        banner_top = tk.Frame(banner_left, bg="#1a0508")
        banner_top.pack(anchor="w")
        tk.Label(banner_top, text="  ⚠", font=("Segoe UI", 13),
                 bg="#1a0508", fg=RED).pack(side="left")
        tk.Label(banner_top, text="  IP LEAK DETECTED",
                 font=("Segoe UI", 11, "bold"),
                 bg="#1a0508", fg=RED).pack(side="left")

        self._leak_banner_detail = tk.Label(
            banner_left,
            text="Your IP address may be exposed. Click to view and fix the leak.",
            font=("Segoe UI", 9), bg="#1a0508", fg="#f87171")
        self._leak_banner_detail.pack(anchor="w", pady=(4,0))

        GlowBtn(self._leak_banner, "FIX LEAKS NOW →", RED,
                command=self._goto_leak_fix).pack(side="right", padx=(10,0))

        tk.Label(f, text="SCAN OUTPUT", font=("Consolas", 9, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(0,4))
        self._dash_out = OutBox(f, height=10)
        self._dash_out.pack(fill="both", expand=True, padx=30, pady=(0,20))
        self._dash_out.append("  PyShield ready. Select a scan option above.\n", "muted")

        # Check for leaks in background on startup
        self.after(1500, self._dash_check_leaks)
        return f

    def _dash_check_leaks(self):
        """Silently check for IP leaks and show banner if found."""
        def run():
            try:
                from vpn import get_leak_status
                status = get_leak_status()
                leaking = not status.get("dns_safe", True) or                           not status.get("webrtc_blocked", True) or                           not status.get("firewall_active", True)
                issues = []
                if not status.get("dns_safe", True):
                    issues.append("DNS")
                if not status.get("webrtc_blocked", True):
                    issues.append("WebRTC")
                if not status.get("firewall_active", True):
                    issues.append("Firewall")

                def update():
                    if leaking:
                        detail = "Leaking via: {}  — Click to fix it now.".format(
                            ", ".join(issues))
                        self._leak_banner_detail.configure(text=detail)
                        self._leak_banner.pack(fill="x", padx=30, pady=(0,14),
                                               before=self._dash_out)
                    else:
                        self._leak_banner.pack_forget()
                self.after(0, update)
            except Exception:
                pass
        threading.Thread(target=run, daemon=True).start()

    def _goto_leak_fix(self):
        """Navigate to VPN > Leak Protection tab."""
        self._show("vpn")
        # Switch to leak tab (index 4) after a short delay
        self.after(100, lambda: [
            w for w in self._pages["vpn"].winfo_children()
            if isinstance(w, ttk.Notebook) and w.select(4)
        ])

    def _quick_scan(self, path):
        self._show("dashboard")
        self._dash_out.clear()
        self._dash_out.append("  Scanning: {}\n\n".format(path), "accent")
        self._run_scan(path, self._dash_out)

    def _update_stats(self, scanned=None, threats=None, quarantined=None):
        if scanned is not None and "FilesScanned" in self._stat_cards:
            self._stat_cards["FilesScanned"].set(str(scanned))
        if threats is not None and "ThreatsFound" in self._stat_cards:
            self._stat_cards["ThreatsFound"].set(
                str(threats), RED if threats > 0 else GREEN)
        if quarantined is not None and "Quarantined" in self._stat_cards:
            self._stat_cards["Quarantined"].set(str(quarantined))

    # ── Scan ──────────────────────────────────
    def _pg_scan(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "FILE SCAN", "Scan any file or folder for threats").pack(
            fill="x", padx=30, pady=(25,18))

        card = tk.Frame(f, bg=CARD, padx=20, pady=16)
        card.pack(fill="x", padx=30, pady=(0,14))
        tk.Label(card, text="TARGET PATH", font=("Consolas", 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        pr = tk.Frame(card, bg=CARD)
        pr.pack(fill="x", pady=(6,0))
        self._spath = tk.StringVar(value=str(Path.home()/"Downloads"))
        tk.Entry(pr, textvariable=self._spath, font=FM, bg=BG, fg=TEXT,
                 insertbackground=ACCENT, bd=0,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(
                     side="left", fill="x", expand=True, ipady=8, padx=(0,10))
        OutlineBtn(pr, "BROWSE", ACCENT,
                   command=lambda: self._spath.set(
                       filedialog.askdirectory() or self._spath.get())).pack(side="left")

        opts = tk.Frame(f, bg=BG)
        opts.pack(fill="x", padx=30, pady=(0,14))
        self._srec = tk.BooleanVar(value=True)
        self._squa = tk.BooleanVar(value=False)
        self._srem = tk.BooleanVar(value=False)
        chk(opts, self._srec, "Recursive")
        chk(opts, self._squa, "Auto-Quarantine confirmed threats")
        chk(opts, self._srem, "Remove confirmed threats")

        br = tk.Frame(f, bg=BG)
        br.pack(anchor="w", padx=30, pady=(0,14))
        self._sbtn = GlowBtn(br, "◉  START SCAN", ACCENT, command=self._do_scan)
        self._sbtn.pack(side="left", padx=(0,10))
        OutlineBtn(br, "CLEAR", command=lambda: self._sout.clear()).pack(side="left")

        tk.Label(f, text="SCAN OUTPUT", font=("Consolas", 9, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(0,4))
        self._sout = OutBox(f)
        self._sout.pack(fill="both", expand=True, padx=30, pady=(0,20))
        return f

    def _do_scan(self):
        if self._scanning:
            return
        path = self._spath.get().strip()
        if not path:
            return
        args = type("A",(),{"quarantine":self._squa.get(),
                             "remove":self._srem.get(),
                             "no_recursive":not self._srec.get()})()
        self._sout.clear()
        self._sbtn.configure(state="disabled", text="SCANNING...")
        self._run_scan(path, self._sout, args,
                       done=lambda: self.after(0, lambda: self._sbtn.configure(
                           state="normal", text="◉  START SCAN")))

    # ── Full PC Scan ───────────────────────────
    def _pg_fullscan(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "FULL PC SCAN",
               "Scan all drives — trusted system folders skipped automatically").pack(
               fill="x", padx=30, pady=(25,18))

        row = tk.Frame(f, bg=BG)
        row.pack(fill="x", padx=30, pady=(0,18))
        for title, body, color in [
            ("SKIPPED (SAFE)",   "Windows, System32, Program Files,\nbrowser caches, Temp", GREEN),
            ("CONFIRMED THREAT", "Score >= 8\nSafe to quarantine automatically", RED),
            ("SUSPICIOUS",       "Score 3-7\nReview manually before acting", AMBER),
        ]:
            c = tk.Frame(row, bg=CARD, padx=16, pady=14)
            c.pack(side="left", expand=True, fill="both", padx=(0,10))
            tk.Frame(c, bg=color, height=2).pack(fill="x")
            tk.Frame(c, bg=CARD, height=6).pack()
            tk.Label(c, text=title, font=("Consolas", 9, "bold"), bg=CARD, fg=color).pack(anchor="w")
            tk.Label(c, text=body, font=FS, bg=CARD, fg=MUTED,
                     wraplength=185, justify="left").pack(anchor="w", pady=(4,0))

        opts = tk.Frame(f, bg=BG)
        opts.pack(fill="x", padx=30, pady=(0,12))
        self._fqua = tk.BooleanVar(value=False)
        self._frem = tk.BooleanVar(value=False)
        chk(opts, self._fqua, "Auto-Quarantine confirmed threats")
        chk(opts, self._frem, "Remove confirmed threats")

        warn = tk.Frame(f, bg="#150b00", padx=16, pady=10)
        warn.pack(fill="x", padx=30, pady=(0,14))
        tk.Label(warn, text="  WARNING: Full scan may take 10-30 min depending on drive size.",
                 font=("Consolas", 9), bg="#150b00", fg=AMBER).pack(anchor="w")

        br = tk.Frame(f, bg=BG)
        br.pack(anchor="w", padx=30, pady=(0,14))
        self._fbtn = GlowBtn(br, "◎  START FULL PC SCAN", RED, command=self._do_fullscan)
        self._fbtn.pack(side="left", padx=(0,10))
        OutlineBtn(br, "CLEAR", command=lambda: self._fout.clear()).pack(side="left")

        tk.Label(f, text="SCAN OUTPUT", font=("Consolas", 9, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(0,4))
        self._fout = OutBox(f)
        self._fout.pack(fill="both", expand=True, padx=30, pady=(0,20))
        return f

    def _do_fullscan(self):
        if self._scanning:
            return
        self._fout.clear()
        self._fout.append("  Starting Full PC Scan...\n", "accent")
        self._fout.append("  Trusted system folders will be skipped.\n\n", "success")
        args = type("A",(),{"quarantine":self._fqua.get(),"remove":self._frem.get()})()
        self._fbtn.configure(state="disabled", text="SCANNING...")
        self._run_scan("__FULLSCAN__", self._fout, args,
                       done=lambda: self.after(0, lambda: self._fbtn.configure(
                           state="normal", text="◎  START FULL PC SCAN")))

    # ── Monitor ────────────────────────────────
    def _pg_monitor(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "REAL-TIME MONITOR",
               "Watch folders and intercept threats as they appear").pack(
               fill="x", padx=30, pady=(25,18))

        # Status card
        sc = tk.Frame(f, bg=CARD, padx=24, pady=20)
        sc.pack(fill="x", padx=30, pady=(0,18))
        self._mon_lbl = tk.Label(sc, text="●  MONITOR OFFLINE",
                                 font=("Consolas", 14, "bold"), bg=CARD, fg=MUTED)
        self._mon_lbl.pack(anchor="w")
        tk.Label(sc, text="Auto-quarantine only applies to CONFIRMED threats (score >= 8)",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(6,0))

        pr = tk.Frame(f, bg=BG)
        pr.pack(fill="x", padx=30, pady=(0,12))
        self._mpath = tk.StringVar(value=str(Path.home()/"Downloads"))
        tk.Entry(pr, textvariable=self._mpath, font=FM, bg=CARD, fg=TEXT,
                 insertbackground=ACCENT, bd=0,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(
                     side="left", fill="x", expand=True, ipady=8, padx=(0,10))
        OutlineBtn(pr, "BROWSE", ACCENT,
                   command=lambda: self._mpath.set(
                       filedialog.askdirectory() or self._mpath.get())).pack(side="left")

        self._mauto = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text="Auto-quarantine confirmed threats",
                       variable=self._mauto, font=FB,
                       bg=BG, fg=TEXT, selectcolor=CARD,
                       activebackground=BG).pack(anchor="w", padx=30, pady=(0,12))

        br = tk.Frame(f, bg=BG)
        br.pack(anchor="w", padx=30, pady=(0,14))
        self._mon_start = GlowBtn(br, "◐  ACTIVATE MONITOR", GREEN, command=self._start_mon)
        self._mon_start.pack(side="left", padx=(0,10))
        self._mon_stop = GlowBtn(br, "■  DEACTIVATE", RED, command=self._stop_mon)
        self._mon_stop.pack(side="left")
        self._mon_stop.configure(state="disabled")

        tk.Label(f, text="ACTIVITY LOG", font=("Consolas", 9, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", padx=30, pady=(0,4))
        self._mout = OutBox(f)
        self._mout.pack(fill="both", expand=True, padx=30, pady=(0,20))
        return f

    def _start_mon(self):
        if self._mon_active:
            return
        path = self._mpath.get().strip()
        if not path or not Path(path).exists():
            messagebox.showwarning("Invalid path", "Please enter a valid folder path.")
            return

        self._mon_active = True
        self._mout.clear()
        self._mon_start.configure(state="disabled")
        self._mon_stop.configure(state="normal")
        self._mon_lbl.configure(text="●  MONITOR ONLINE", fg=GREEN)
        self._setstatus("● MONITORING", GREEN)

        auto_q = self._mauto.get()

        def run():
            try:
                from watchdog.observers import Observer
                from watchdog.events import FileSystemEventHandler

                scanner    = Scanner()
                quarantine = Quarantine()
                lock       = threading.Lock()

                class H(FileSystemEventHandler):
                    def _handle(self2, p_str):
                        p = Path(p_str)
                        if not p.is_file() or not scanner.should_scan(p):
                            return
                        with lock:
                            r = scanner.scan_file(p)
                            if not r.clean:
                                level = "CONFIRMED" if r.confirmed else "SUSPICIOUS"
                                tag   = "danger" if r.confirmed else "warn"
                                self._out_append(self._mout,
                                    "  [{}] {}\n".format(level, p.name), tag)
                                if auto_q and r.confirmed:
                                    quarantine.quarantine_file(p, r.threat)
                                    self._out_append(self._mout,
                                        "  Quarantined: {}\n".format(p.name), "success")
                    def on_created(self2, e):
                        if not e.is_directory: self2._handle(e.src_path)
                    def on_modified(self2, e):
                        if not e.is_directory: self2._handle(e.src_path)

                obs = Observer()
                obs.schedule(H(), path, recursive=True)
                obs.start()
                self._out_append(self._mout, "  Monitoring: {}\n".format(path), "accent")
                self._out_append(self._mout, "  Watching for threats...\n", "muted")

                while self._mon_active:
                    time.sleep(0.5)

                obs.stop()
                obs.join()

            except ImportError:
                self._out_append(self._mout,
                    "  ERROR: watchdog not installed.\n  Run: py -m pip install watchdog\n", "danger")
            except Exception as e:
                self._out_append(self._mout, "  ERROR: {}\n".format(e), "danger")
            finally:
                self._mon_active = False
                self.after(0, self._mon_stopped_ui)

        self._mon_thread = threading.Thread(target=run, daemon=True)
        self._mon_thread.start()

    def _stop_mon(self):
        self._mon_active = False

    def _mon_stopped_ui(self):
        self._mon_start.configure(state="normal")
        self._mon_stop.configure(state="disabled")
        self._mon_lbl.configure(text="●  MONITOR OFFLINE", fg=MUTED)
        self._setstatus("● PROTECTED", GREEN)
        self._out_append(self._mout, "\n  Monitor deactivated.\n", "muted")

    # ── Quarantine ─────────────────────────────
    def _pg_quarantine(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "QUARANTINE VAULT",
               "Isolated threats — safely stored, fully manageable").pack(
               fill="x", padx=30, pady=(25,18))

        br = tk.Frame(f, bg=BG)
        br.pack(fill="x", padx=30, pady=(0,14))
        GlowBtn(br, "REFRESH",   ACCENT,  command=self._qrefresh).pack(side="left", padx=(0,8))
        GlowBtn(br, "RESTORE",   GREEN,   command=self._qrestore).pack(side="left", padx=(0,8))
        GlowBtn(br, "DELETE",    RED,     command=self._qdelete).pack(side="left", padx=(0,8))
        OutlineBtn(br, "PURGE ALL", MUTED, command=self._qpurge).pack(side="left")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("PS.Treeview",
                        background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=30,
                        font=FM, borderwidth=0)
        style.configure("PS.Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Consolas", 9, "bold"), relief="flat")
        style.map("PS.Treeview",
                  background=[("selected", BORDER)],
                  foreground=[("selected", ACCENT)])

        cols = ("File", "Threat", "Date")
        self._qtree = ttk.Treeview(f, columns=cols, show="headings",
                                   style="PS.Treeview", height=14)
        for c in cols:
            self._qtree.heading(c, text=c)
        self._qtree.column("File",   width=280)
        self._qtree.column("Threat", width=280)
        self._qtree.column("Date",   width=160)

        sc = ttk.Scrollbar(f, orient="vertical", command=self._qtree.yview)
        self._qtree.configure(yscrollcommand=sc.set)
        self._qtree.pack(fill="both", expand=True, padx=30, pady=(0,5))

        self._qlbl = tk.Label(f, text="", font=FS, bg=BG, fg=MUTED)
        self._qlbl.pack(anchor="w", padx=30, pady=(2,15))

        self._qrefresh()
        return f

    def _qrefresh(self):
        for r in self._qtree.get_children():
            self._qtree.delete(r)
        manifest = QUARANTINE_DIR / "manifest.json"
        if manifest.exists():
            try:
                with open(manifest) as f:
                    items = json.load(f)
                for qid, info in items.items():
                    self._qtree.insert("", "end", iid=qid, values=(
                        Path(info.get("original_path","")).name,
                        info.get("threat",""),
                        info.get("quarantined_at","")
                    ))
                self._qlbl.configure(text="{} item(s) in vault".format(len(items)))
            except Exception:
                pass

    def _qsel(self):
        s = self._qtree.selection()
        if not s:
            messagebox.showinfo("No selection", "Please select an item.")
            return None
        return s[0]

    def _qrestore(self):
        qid = self._qsel()
        if qid and messagebox.askyesno("Restore", "Restore file to original location?"):
            Quarantine().restore_file(qid)
            self.after(600, self._qrefresh)

    def _qdelete(self):
        qid = self._qsel()
        if qid and messagebox.askyesno("Delete", "Permanently delete this file?"):
            Quarantine().delete_from_quarantine(qid)
            self.after(600, self._qrefresh)

    def _qpurge(self):
        if messagebox.askyesno("Purge All", "Delete ALL quarantined files permanently?"):
            q = Quarantine()
            for item in q.list_quarantined():
                q.delete_from_quarantine(item["id"])
            self.after(600, self._qrefresh)

    # ── Signatures ─────────────────────────────
    def _pg_signatures(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "SIGNATURE DATABASE",
               "Manage known malware hash signatures").pack(
               fill="x", padx=30, pady=(25,18))

        card = tk.Frame(f, bg=CARD, padx=24, pady=18)
        card.pack(fill="x", padx=30, pady=(0,14))
        tk.Label(card, text="ADD FILE TO DATABASE",
                 font=("Consolas", 10, "bold"), bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(card, text="Hashes the file (SHA256 + MD5) and marks it as a known threat",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,10))

        r1 = tk.Frame(card, bg=CARD)
        r1.pack(fill="x")
        self._sigpath = tk.StringVar()
        tk.Entry(r1, textvariable=self._sigpath, font=FM, bg=BG, fg=TEXT,
                 insertbackground=ACCENT, bd=0, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT,
                 width=40).pack(side="left", ipady=7, padx=(0,10))
        OutlineBtn(r1, "BROWSE", ACCENT,
                   command=lambda: self._sigpath.set(
                       filedialog.askopenfilename() or self._sigpath.get())).pack(side="left")

        tk.Label(card, text="THREAT NAME (optional)",
                 font=("Consolas", 8), bg=CARD, fg=MUTED).pack(anchor="w", pady=(12,3))
        self._signame = tk.StringVar()
        tk.Entry(card, textvariable=self._signame, font=FM, bg=BG, fg=TEXT,
                 insertbackground=ACCENT, bd=0, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT,
                 width=35).pack(anchor="w", ipady=7)
        GlowBtn(card, "⊞  ADD TO DATABASE", ACCENT,
                command=self._sigadd).pack(anchor="w", pady=(12,0))

        ir = tk.Frame(f, bg=BG)
        ir.pack(fill="x", padx=30, pady=(0,10))
        self._siglbl = tk.Label(ir, text="", font=FM, bg=BG, fg=MUTED)
        self._siglbl.pack(side="left")
        OutlineBtn(ir, "REFRESH", ACCENT, command=self._sigrefresh).pack(side="right")

        self._sigout = OutBox(f, height=10)
        self._sigout.pack(fill="both", expand=True, padx=30, pady=(0,20))
        self._sigrefresh()
        return f

    def _sigadd(self):
        path = self._sigpath.get().strip()
        if not path:
            messagebox.showwarning("No file", "Select a file first.")
            return
        db   = SignatureDB()
        p    = Path(path)
        name = self._signame.get().strip()
        if p.is_file():
            sha256, md5 = db.hash_file(p)
            n = name or "Custom.{}".format(p.name)
            db.add(sha256, n)
            if md5:
                db.add(md5, n)
            self._sigout.clear()
            self._sigout.append("  [OK] Added: {}\n".format(p.name), "success")
            self._sigout.append("  SHA256: {}\n".format(sha256), "muted")
        else:
            n = name or "Custom.Unknown"
            db.add(path, n)
            self._sigout.clear()
            self._sigout.append("  [OK] Added hash -> {}\n".format(n), "success")
        self._sigrefresh()

    def _sigrefresh(self):
        db = SignatureDB()
        self._siglbl.configure(
            text="  {} signatures  |  {}".format(db.count(), QUARANTINE_DIR.parent / "signatures.json"))

    # ── Logs ───────────────────────────────────
    def _pg_logs(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "SYSTEM LOGS",
               "Audit trail of all detections and actions").pack(
               fill="x", padx=30, pady=(25,18))

        br = tk.Frame(f, bg=BG)
        br.pack(fill="x", padx=30, pady=(0,12))
        GlowBtn(br, "REFRESH", ACCENT, command=self._logload).pack(side="left", padx=(0,10))
        OutlineBtn(br, "CLEAR LOGS", RED, command=self._logclear).pack(side="left")

        self._logout = OutBox(f, height=30)
        self._logout.pack(fill="both", expand=True, padx=30, pady=(0,20))
        self._logload()
        return f

    def _logload(self):
        self._logout.clear()
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            for line in lines[-400:]:
                tag = ("danger"  if "THREAT" in line or "ERROR" in line else
                       "warn"    if "QUARANTINE" in line or "ALERT" in line else
                       "success" if "RESTORE" in line else
                       "accent"  if "SCAN" in line else "muted")
                self._logout.append(line, tag)
        else:
            self._logout.append("  No log file yet.\n", "muted")

    def _logclear(self):
        if messagebox.askyesno("Clear Logs", "Clear all log entries?"):
            LOG_FILE.write_text("")
            self._logload()

    # ── Core scan runner ───────────────────────
    def _out_append(self, box, text, tag=None):
        self.after(0, lambda: box.append(text, tag))

    def _run_scan(self, path, out, args=None, done=None):
        if self._scanning:
            return
        self._scanning = True
        self._setstatus("● SCANNING", AMBER)

        def run():
            try:
                scanner    = Scanner()
                quarantine = Quarantine()
                threats    = []

                # Full PC scan mode
                if path == "__FULLSCAN__":
                    drives = get_all_drives()
                    self._out_append(out, "  Drives: {}\n\n".format(
                        [str(d) for d in drives]), "muted")

                    for drive in drives:
                        self._out_append(out,
                            "\n  ── Drive: {} ──\n".format(drive), "accent")

                        def prog(r, cur, tot, d=drive):
                            if cur % 200 == 0:
                                pct = int(100 * cur / max(tot, 1))
                                self._out_append(out,
                                    "  {}%  ({}/{} files)\n".format(pct, cur, tot), "muted")
                            if not r.clean:
                                lv  = "CONFIRMED" if r.confirmed else "SUSPICIOUS"
                                tag = "danger" if r.confirmed else "warn"
                                self._out_append(out,
                                    "  [{}] {}\n".format(lv, r.path), tag)
                                threats.append(r)

                        try:
                            scanner.scan_directory(drive, recursive=True, callback=prog)
                        except (PermissionError, OSError):
                            pass
                else:
                    p = Path(path)
                    if not p.exists():
                        self._out_append(out,
                            "  Path not found: {}\n".format(path), "danger")
                        return

                    no_rec = getattr(args, "no_recursive", False) if args else False

                    def prog(r, cur, tot):
                        if cur % 25 == 0:
                            pct = int(100 * cur / max(tot, 1))
                            bar = "#" * int(20*pct/100) + "-" * (20-int(20*pct/100))
                            self._out_append(out,
                                "  [{}] {}%  ({}/{})\n".format(bar, pct, cur, tot), "muted")
                        if not r.clean:
                            lv  = "CONFIRMED" if r.confirmed else "SUSPICIOUS"
                            tag = "danger" if r.confirmed else "warn"
                            self._out_append(out,
                                "  [{}] {}\n  -> {}\n".format(lv, r.path.name, r.threat), tag)
                            threats.append(r)

                    if p.is_file():
                        r = scanner.scan_file(p)
                        if not r.clean:
                            threats.append(r)
                            lv  = "CONFIRMED" if r.confirmed else "SUSPICIOUS"
                            tag = "danger" if r.confirmed else "warn"
                            self._out_append(out,
                                "  [{}] {}\n".format(lv, r.path), tag)
                        else:
                            self._out_append(out,
                                "  [OK] Clean: {}\n".format(r.path), "success")
                    else:
                        scanner.scan_directory(p, recursive=not no_rec, callback=prog)

                # Summary
                confirmed  = [r for r in threats if r.confirmed]
                suspicious = [r for r in threats if not r.confirmed]
                s = scanner.stats

                self._out_append(out, "\n  " + "-"*48 + "\n", "muted")
                self._out_append(out,
                    "  Scanned: {}   Skipped (trusted): {}   Errors: {}\n".format(
                        s["scanned"], s.get("skipped",0), s["errors"]), "muted")
                self._out_append(out,
                    "  Confirmed threats: {}   Suspicious: {}\n".format(
                        len(confirmed), len(suspicious)),
                    "danger" if confirmed else "success")

                if not threats:
                    self._out_append(out, "\n  All clear — no threats found.\n", "success")

                do_q = getattr(args, "quarantine", False) if args else False
                do_r = getattr(args, "remove",    False) if args else False

                if do_q and confirmed:
                    self._out_append(out, "\n  Quarantining confirmed threats...\n", "warn")
                    for r in confirmed:
                        ok = quarantine.quarantine_file(r.path, r.threat)
                        self._out_append(out,
                            "  {} {}\n".format("[OK]" if ok else "[!!]", r.path.name),
                            "success" if ok else "danger")
                elif do_r and confirmed:
                    self._out_append(out, "\n  Removing confirmed threats...\n", "danger")
                    for r in confirmed:
                        ok = quarantine.remove_file(r.path)
                        self._out_append(out,
                            "  {} {}\n".format("[OK]" if ok else "[!!]", r.path.name),
                            "success" if ok else "danger")

                color = RED if confirmed else GREEN
                txt   = "● THREATS FOUND" if confirmed else "● PROTECTED"
                self._setstatus(txt, color)
                self.after(0, lambda: self._update_stats(
                    s["scanned"], len(confirmed),
                    len(quarantine.list_quarantined())))

            finally:
                self._scanning = False
                if done:
                    self.after(0, done)

        threading.Thread(target=run, daemon=True).start()


    # ── VPN Page ───────────────────────────────
    def _pg_vpn(self):
        f = tk.Frame(self._content, bg=BG)

        # ── Big NordVPN-style connect panel at top ──
        hero = tk.Frame(f, bg=PANEL, padx=30, pady=24)
        hero.pack(fill="x")

        hero_left = tk.Frame(hero, bg=PANEL)
        hero_left.pack(side="left", fill="x", expand=True)

        # Status row
        status_row = tk.Frame(hero_left, bg=PANEL)
        status_row.pack(anchor="w")
        self._vpn_dot = tk.Label(status_row, text="●", font=("Segoe UI", 14),
                                  bg=PANEL, fg=MUTED)
        self._vpn_dot.pack(side="left")
        self._vpn_status_big = tk.Label(status_row, text="NOT CONNECTED",
                                         font=("Segoe UI", 18, "bold"),
                                         bg=PANEL, fg=TEXT2)
        self._vpn_status_big.pack(side="left", padx=(8,0))

        self._vpn_location_lbl = tk.Label(hero_left,
                                           text="Select a server and connect",
                                           font=("Segoe UI", 10),
                                           bg=PANEL, fg=MUTED)
        self._vpn_location_lbl.pack(anchor="w", pady=(6,0))

        # Connection stats row
        stats_row = tk.Frame(hero_left, bg=PANEL)
        stats_row.pack(anchor="w", pady=(12,0))
        for attr, label, color in [
            ("_vpn_timer_lbl", "⏱ 00:00:00", ACCENT),
            ("_vpn_ip_lbl",    "⊕ ---.---.---.---", TEXT2),
            ("_vpn_rx_lbl",    "↓ 0 MB", GREEN),
            ("_vpn_tx_lbl",    "↑ 0 MB", AMBER),
        ]:
            lbl = tk.Label(stats_row, text=label,
                           font=("Consolas", 9), bg=PANEL, fg=color)
            lbl.pack(side="left", padx=(0,20))
            setattr(self, attr, lbl)

        # Right — big connect button
        hero_right = tk.Frame(hero, bg=PANEL)
        hero_right.pack(side="right")

        self._vpn_connect_btn = tk.Button(
            hero_right,
            text="CONNECT",
            font=("Segoe UI", 13, "bold"),
            bg=GREEN, fg="#050810",
            width=14, height=2,
            bd=0, cursor="hand2", relief="flat",
            command=self._vpn_quick_connect
        )
        self._vpn_connect_btn.pack(pady=(0,8))
        self._vpn_connect_btn.bind("<Enter>", lambda e: self._vpn_connect_btn.configure(bg="#6ee7b7"))
        self._vpn_connect_btn.bind("<Leave>", lambda e: self._vpn_connect_btn.configure(
            bg=RED if self._tor_active else GREEN))

        # Quick toggles row under button
        toggle_row = tk.Frame(hero_right, bg=PANEL)
        toggle_row.pack()
        self._ks_var = tk.BooleanVar(value=False)
        ks_chk = tk.Checkbutton(toggle_row, text="Kill Switch",
                                  variable=self._ks_var,
                                  font=("Segoe UI", 8),
                                  bg=PANEL, fg=TEXT2,
                                  selectcolor=CARD2,
                                  activebackground=PANEL,
                                  activeforeground=ACCENT,
                                  cursor="hand2",
                                  command=self._vpn_toggle_killswitch)
        ks_chk.pack(side="left", padx=(0,8))

        # Accent divider
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x")

        # ── Tabs ──
        style = ttk.Style()
        style.configure("VPN.TNotebook", background=BG, borderwidth=0)
        style.configure("VPN.TNotebook.Tab",
                        background=PANEL, foreground=TEXT2,
                        padding=[16,9], font=("Segoe UI", 9, "bold"))
        style.map("VPN.TNotebook.Tab",
                  background=[("selected", CARD2)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(f, style="VPN.TNotebook")
        nb.pack(fill="both", expand=True, padx=0, pady=0)
        self._vpn_nb = nb

        nb.add(self._vpn_tab_servers(nb), text="  SERVERS  ")
        nb.add(self._vpn_tab_ip(nb),      text="  MY IP  ")
        nb.add(self._vpn_tab_tor(nb),     text="  TOR  ")
        nb.add(self._vpn_tab_dns(nb),     text="  DNS LEAK  ")
        nb.add(self._vpn_tab_leak(nb),    text="  LEAK PROTECTION  ")

        # Start stats ticker
        self._vpn_stats_tick()
        return f

    def _vpn_set_connected(self, country, city, flag, ip=""):
        """Update hero panel to connected state."""
        self._tor_active = True
        self._vpn_connect_btn.configure(text="DISCONNECT", bg=RED)
        self._vpn_dot.configure(fg=GREEN)
        self._vpn_status_big.configure(text="CONNECTED", fg=GREEN)
        loc = "{} {}  {}{}".format(
            COUNTRY_FLAGS.get(flag,"🌐"), country,
            "— " if city else "", city)
        self._vpn_location_lbl.configure(text=loc, fg=ACCENT)
        if ip:
            self._vpn_ip_lbl.configure(text="⊕ {}".format(ip))
        vpn_session_start()

    def _vpn_set_disconnected(self):
        """Update hero panel to disconnected state."""
        self._tor_active = False
        self._vpn_connect_btn.configure(text="CONNECT", bg=GREEN)
        self._vpn_dot.configure(fg=MUTED)
        self._vpn_status_big.configure(text="NOT CONNECTED", fg=TEXT2)
        self._vpn_location_lbl.configure(text="Select a server and connect", fg=MUTED)
        self._vpn_ip_lbl.configure(text="⊕ ---.---.---.---")
        self._vpn_timer_lbl.configure(text="⏱ 00:00:00")

    def _vpn_quick_connect(self):
        """Connect button in hero — toggle or quick connect to best server."""
        if self._tor_active:
            self._tor_disconnect()
            self._vpn_set_disconnected()
        else:
            # Find fastest pinged server and connect via Tor
            self._vpn_connect_btn.configure(text="CONNECTING...", bg=AMBER, state="disabled")
            self._vpn_dot.configure(fg=AMBER)
            self._vpn_status_big.configure(text="CONNECTING...", fg=AMBER)
            self._vpn_location_lbl.configure(text="Finding fastest server...", fg=AMBER)
            self._tor_connect()

    def _vpn_toggle_killswitch(self):
        if self._ks_var.get():
            if messagebox.askyesno("Kill Switch",
                "Enable Kill Switch?\n\nThis will block ALL internet if VPN disconnects.\nMake sure VPN is connected first."):
                enable_kill_switch()
            else:
                self._ks_var.set(False)
        else:
            disable_kill_switch()

    def _vpn_stats_tick(self):
        """Update timer and stats every second."""
        if self._tor_active:
            elapsed = vpn_session_elapsed()
            self._vpn_timer_lbl.configure(text="⏱ {}".format(elapsed))
        self.after(1000, self._vpn_stats_tick)


    def _vpn_tab_ip(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=0, pady=0)

        top = tk.Frame(f, bg=CARD, padx=24, pady=20)
        top.pack(fill="x")

        tk.Label(top, text="YOUR PUBLIC IP INFO",
                 font=("Consolas",10,"bold"), bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(top, text="Click Refresh to fetch your current IP address and location",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,12))

        # Big IP display
        ip_card = tk.Frame(top, bg=BG, padx=20, pady=18)
        ip_card.pack(fill="x", pady=(0,12))
        self._ip_big = tk.Label(ip_card, text="---.---.---.---",
                                font=("Consolas",28,"bold"), bg=BG, fg=ACCENT)
        self._ip_big.pack(anchor="w")
        self._ip_sub = tk.Label(ip_card, text="Press Refresh to load",
                                font=FM, bg=BG, fg=MUTED)
        self._ip_sub.pack(anchor="w")

        # Info grid
        grid = tk.Frame(top, bg=CARD)
        grid.pack(fill="x", pady=(0,12))
        self._ip_fields = {}
        for i, (label, key) in enumerate([
            ("City",     "city"),
            ("Region",   "region"),
            ("Country",  "country"),
            ("Provider", "org"),
            ("Timezone", "timezone"),
        ]):
            col = i % 3
            row = i // 3
            cell = tk.Frame(grid, bg=BG, padx=12, pady=10)
            cell.grid(row=row, column=col, padx=(0,8), pady=(0,8), sticky="ew")
            grid.columnconfigure(col, weight=1)
            tk.Label(cell, text=label.upper(), font=("Consolas",7), bg=BG, fg=MUTED).pack(anchor="w")
            v = tk.Label(cell, text="—", font=("Consolas",11,"bold"), bg=BG, fg=TEXT)
            v.pack(anchor="w")
            self._ip_fields[key] = v

        btn_row = tk.Frame(top, bg=CARD)
        btn_row.pack(anchor="w")
        self._ip_refresh_btn = GlowBtn(btn_row, "REFRESH IP", ACCENT,
                                       command=self._refresh_ip)
        self._ip_refresh_btn.pack(side="left", padx=(0,10))
        self._ip_status = tk.Label(btn_row, text="", font=FM, bg=CARD, fg=MUTED)
        self._ip_status.pack(side="left")

        return f

    def _refresh_ip(self):
        self._ip_refresh_btn.configure(state="disabled", text="Loading...")
        self._ip_status.configure(text="Fetching...", fg=AMBER)
        def run():
            info = get_ip_info()
            def update():
                self._ip_big.configure(text=info.get("ip","Unknown"))
                self._ip_sub.configure(
                    text="{}, {}  //  {}".format(
                        info.get("city","?"),
                        info.get("country","?"),
                        info.get("org","?")
                    ))
                for key, lbl in self._ip_fields.items():
                    lbl.configure(text=info.get(key, "Unknown"))
                self._ip_refresh_btn.configure(state="normal", text="REFRESH IP")
                self._ip_status.configure(text="Updated", fg=GREEN)
            self.after(0, update)
        threading.Thread(target=run, daemon=True).start()

    def _vpn_tab_tor(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)

        tk.Label(f, text="TOR ANONYMOUS ROUTING",
                 font=("Consolas",10,"bold"), bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Route your traffic through the Tor network to hide your real IP",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        # Status card
        sc = tk.Frame(f, bg=BG, padx=20, pady=16)
        sc.pack(fill="x", pady=(0,15))
        self._tor_status_lbl = tk.Label(sc, text="●  TOR OFFLINE",
                                        font=("Consolas",14,"bold"), bg=BG, fg=MUTED)
        self._tor_status_lbl.pack(anchor="w")
        self._tor_ip_lbl = tk.Label(sc, text="Hidden IP: Not connected",
                                    font=FM, bg=BG, fg=MUTED)
        self._tor_ip_lbl.pack(anchor="w", pady=(6,0))

        # Info box
        info = tk.Frame(f, bg="#0a1500", padx=16, pady=12)
        info.pack(fill="x", pady=(0,15))
        tk.Label(info, text=(
"  Tor works by bouncing your connection through 3 relays worldwide.\n"
            "  Your real IP is hidden from websites and trackers.\n"
            "  Requires Tor Browser to be installed on this PC."
        ), font=FS, bg="#0a1500", fg=GREEN, justify="left").pack(anchor="w")

        btn_row = tk.Frame(f, bg=CARD)
        btn_row.pack(anchor="w", pady=(0,12))
        self._tor_start_btn = GlowBtn(btn_row, "CONNECT TOR", GREEN, command=self._tor_connect)
        self._tor_start_btn.pack(side="left", padx=(0,10))
        self._tor_stop_btn = GlowBtn(btn_row, "DISCONNECT", RED, command=self._tor_disconnect)
        self._tor_stop_btn.pack(side="left")
        self._tor_stop_btn.configure(state="disabled")

        tk.Label(f, text="TOR LOG", font=("Consolas",8,"bold"), bg=CARD, fg=MUTED).pack(anchor="w", pady=(8,4))
        self._tor_out = OutBox(f, height=10)
        self._tor_out.pack(fill="both", expand=True)

        return f

    def _tor_connect(self):
        if self._tor_active:
            return
        self._tor_active = True
        self._tor_start_btn.configure(state="disabled", text="Connecting...")
        self._tor_stop_btn.configure(state="normal")
        self._tor_status_lbl.configure(text="●  CONNECTING TO TOR...", fg=AMBER)
        self._tor_out.clear()

        def log_cb(line):
            self._out_append(self._tor_out, "  " + line + "\n", "muted")

        def run():
            ok, msg = start_tor(log_cb=log_cb)
            if ok:
                port = get_tor_port()
                set_win_proxy(port=port, enable=True)
                # Get hidden IP
                info = get_ip_info()
                def update():
                    self._tor_status_lbl.configure(text="●  TOR ONLINE", fg=GREEN)
                    self._tor_ip_lbl.configure(
                        text="Hidden IP: {}  ({}, {})".format(
                            info.get("ip","?"),
                            info.get("city","?"),
                            info.get("country","?")),
                        fg=GREEN)
                    self._tor_start_btn.configure(state="disabled")
                    self._tor_out.append("\n  Connected! Your traffic is now routed through Tor.\n", "success")
                    self._tor_out.append("  Hidden IP: {}\n".format(info.get("ip","?")), "accent")
                self.after(0, update)
            else:
                def fail():
                    self._tor_active = False
                    self._tor_status_lbl.configure(text="●  TOR OFFLINE", fg=MUTED)
                    self._tor_start_btn.configure(state="normal", text="CONNECT TOR")
                    self._tor_stop_btn.configure(state="disabled")
                    self._tor_out.append("\n  Failed: " + msg + "\n", "danger")
                self.after(0, fail)

        threading.Thread(target=run, daemon=True).start()

    def _tor_disconnect(self):
        stop_tor()
        set_win_proxy(enable=False)
        self._tor_active = False
        self._tor_status_lbl.configure(text="●  TOR OFFLINE", fg=MUTED)
        self._tor_ip_lbl.configure(text="Hidden IP: Not connected", fg=MUTED)
        self._tor_start_btn.configure(state="normal", text="CONNECT TOR")
        self._tor_stop_btn.configure(state="disabled")
        self._tor_out.append("\n  Disconnected from Tor.\n", "warn")

    def _vpn_tab_dns(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)

        tk.Label(f, text="DNS LEAK CHECK",
                 font=("Consolas",10,"bold"), bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Check if your DNS requests are leaking your real identity",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        # Rating card
        self._dns_rating_frame = tk.Frame(f, bg=BG, padx=20, pady=16)
        self._dns_rating_frame.pack(fill="x", pady=(0,15))
        self._dns_rating_lbl = tk.Label(self._dns_rating_frame,
                                        text="NOT CHECKED YET",
                                        font=("Consolas",18,"bold"), bg=BG, fg=MUTED)
        self._dns_rating_lbl.pack(anchor="w")
        self._dns_detail_lbl = tk.Label(self._dns_rating_frame,
                                        text="Click Run DNS Leak Test to check",
                                        font=FM, bg=BG, fg=MUTED)
        self._dns_detail_lbl.pack(anchor="w", pady=(6,0))

        # What it means
        info = tk.Frame(f, bg="#00080f", padx=16, pady=12)
        info.pack(fill="x", pady=(0,15))
        tk.Label(info, text=(
"  SAFE     = Your DNS uses a known private provider (Cloudflare, Google, etc.)\n"
            "  WARNING  = Mix of known and unknown DNS servers detected\n"
            "  LEAKING  = Unknown DNS server — your ISP may see your browsing"
        ), font=FS, bg="#00080f", fg=ACCENT, justify="left").pack(anchor="w")

        GlowBtn(f, "RUN DNS LEAK TEST", ACCENT, command=self._run_dns_check).pack(anchor="w", pady=(0,12))

        tk.Label(f, text="DNS SERVERS DETECTED", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(8,4))
        self._dns_out = OutBox(f, height=8)
        self._dns_out.pack(fill="both", expand=True)

        return f

    def _run_dns_check(self):
        self._dns_rating_lbl.configure(text="CHECKING...", fg=AMBER)
        self._dns_out.clear()

        def run():
            result = check_dns_leak()
            rating = result["rating"]
            color  = GREEN if rating == "Safe" else AMBER if rating == "Warning" else RED

            def update():
                self._dns_rating_lbl.configure(text=rating.upper(), fg=color)
                detail = {
                    "Safe":    "Your DNS looks good — no leaks detected",
                    "Warning": "Some unknown DNS servers found — review below",
                    "Leaking": "DNS is leaking! Unknown servers detected",
                }
                self._dns_detail_lbl.configure(text=detail[rating], fg=color)
                tag = "success" if rating == "Safe" else "warn" if rating == "Warning" else "danger"
                self._dns_out.append("  DNS Servers found on this system:\n\n", "muted")
                for label in result["labels"]:
                    self._dns_out.append("  {}\n".format(label), tag)
                if result["leaking"]:
                    self._dns_out.append("\n  RECOMMENDATION: Switch to Cloudflare (1.1.1.1)\n"
                                         "  or Google (8.8.8.8) for better privacy.\n", "warn")
                else:
                    self._dns_out.append("\n  All clear! Your DNS provider is known and trusted.\n", "success")
            self.after(0, update)

        threading.Thread(target=run, daemon=True).start()

    def _vpn_tab_servers(self, parent):
        f = tk.Frame(parent, bg=BG)

        # Top bar — search + filters + ping all button
        bar = tk.Frame(f, bg=PANEL, padx=20, pady=12)
        bar.pack(fill="x")

        tk.Label(bar, text="🔍", font=("Segoe UI",11),
                 bg=PANEL, fg=MUTED).pack(side="left")
        self._vpn_search_var = tk.StringVar()
        self._vpn_search_var.trace("w", lambda *a: self._vpn_filter_servers())
        search = tk.Entry(bar, textvariable=self._vpn_search_var,
                          font=("Segoe UI",10), bg=CARD2, fg=TEXT,
                          insertbackground=ACCENT, bd=0,
                          highlightthickness=1,
                          highlightbackground=BORDER2,
                          highlightcolor=ACCENT,
                          width=22)
        search.pack(side="left", padx=(6,14), ipady=5)
        search.insert(0, "Search country or city...")
        search.bind("<FocusIn>",  lambda e: search.delete(0,"end") if search.get().startswith("Search") else None)
        search.bind("<FocusOut>", lambda e: search.insert(0,"Search country or city...") if not search.get() else None)

        # Protocol filter
        self._vpn_proto_var = tk.StringVar(value="ALL")
        for proto in ("ALL","UDP","TCP"):
            rb = tk.Radiobutton(bar, text=proto,
                                variable=self._vpn_proto_var, value=proto,
                                font=("Segoe UI",9), bg=PANEL, fg=TEXT2,
                                selectcolor=CARD2, activebackground=PANEL,
                                activeforeground=ACCENT, cursor="hand2",
                                command=self._vpn_filter_servers)
            rb.pack(side="left", padx=4)

        GlowBtn(bar, "⚡ PING ALL", ACCENTD,
                command=self._vpn_ping_all).pack(side="left", padx=(12,8))
        GlowBtn(bar, "⚡ FASTEST", GREEN,
                command=self._vpn_connect_fastest).pack(side="left")

        self._vpn_server_count = tk.Label(bar, text="42 servers",
                                           font=("Consolas",9),
                                           bg=PANEL, fg=MUTED)
        self._vpn_server_count.pack(side="right")

        # Column headers
        cols_f = tk.Frame(f, bg=CARD2, padx=20, pady=6)
        cols_f.pack(fill="x")
        for text, w in [("  FLAG + COUNTRY / CITY", 280), ("PING", 80),
                        ("PROTOCOL", 90), ("PORT", 70), ("", 100)]:
            tk.Label(cols_f, text=text, font=("Segoe UI",8,"bold"),
                     bg=CARD2, fg=MUTED, width=w//8, anchor="w").pack(side="left")

        # Scrollable server list
        canvas = tk.Canvas(f, bg=BG, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(f, orient="vertical", command=canvas.yview)
        self._vpn_server_frame = tk.Frame(canvas, bg=BG)
        self._vpn_server_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self._vpn_server_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        # Bottom action bar
        action_bar = tk.Frame(f, bg=PANEL, padx=20, pady=10)
        action_bar.pack(fill="x", side="bottom")
        self._vpn_selected_lbl = tk.Label(action_bar,
                                           text="No server selected",
                                           font=("Segoe UI",9),
                                           bg=PANEL, fg=MUTED)
        self._vpn_selected_lbl.pack(side="left")
        GlowBtn(action_bar, "💾 SAVE CONFIG", ACCENTD,
                command=self._vpn_save_config).pack(side="right", padx=(8,0))
        GlowBtn(action_bar, "▶ CONNECT", GREEN,
                command=self._vpn_connect).pack(side="right")

        self._vpn_selected_server = None
        self._vpn_server_rows = []
        self._vpn_fill_servers(FREE_VPN_SERVERS)
        return f

    def _vpn_fill_servers(self, servers):
        """Render server rows into the scrollable list."""
        for w in self._vpn_server_frame.winfo_children():
            w.destroy()
        self._vpn_server_rows = []

        for i, srv in enumerate(servers):
            flag  = COUNTRY_FLAGS.get(srv["flag"], "🌐")
            ping  = srv.get("_ping_ms")
            if ping is None:
                ping_txt   = "— ms"
                ping_color = MUTED
            elif ping < 50:
                ping_txt   = "{}ms".format(ping)
                ping_color = GREEN
            elif ping < 120:
                ping_txt   = "{}ms".format(ping)
                ping_color = AMBER
            else:
                ping_txt   = "{}ms".format(ping)
                ping_color = RED

            row_bg = CARD2 if i % 2 == 0 else BG
            row = tk.Frame(self._vpn_server_frame, bg=row_bg,
                           padx=20, pady=0, cursor="hand2")
            row.pack(fill="x")

            # Left indicator bar (hidden by default)
            indicator = tk.Frame(row, bg=row_bg, width=3)
            indicator.pack(side="left", fill="y")

            # Content
            inner = tk.Frame(row, bg=row_bg, pady=10)
            inner.pack(side="left", fill="x", expand=True)

            # Flag + country + city
            loc_frame = tk.Frame(inner, bg=row_bg)
            loc_frame.pack(side="left")
            tk.Label(loc_frame, text=flag, font=("Segoe UI",14),
                     bg=row_bg, fg=TEXT).pack(side="left")
            name_frame = tk.Frame(loc_frame, bg=row_bg)
            name_frame.pack(side="left", padx=(8,0))
            tk.Label(name_frame, text=srv["country"],
                     font=("Segoe UI",10,"bold"),
                     bg=row_bg, fg=TEXT, anchor="w").pack(anchor="w")
            tk.Label(name_frame, text=srv.get("city",""),
                     font=("Segoe UI",8),
                     bg=row_bg, fg=TEXT2, anchor="w").pack(anchor="w")

            # Ping badge
            ping_lbl = tk.Label(inner, text=ping_txt,
                                 font=("Consolas",9,"bold"),
                                 bg=row_bg, fg=ping_color, width=8)
            ping_lbl.pack(side="left", padx=(20,0))

            # Protocol + port
            tk.Label(inner, text=srv["protocol"],
                     font=("Consolas",9),
                     bg=row_bg, fg=ACCENT, width=6).pack(side="left")
            tk.Label(inner, text=str(srv["port"]),
                     font=("Consolas",9),
                     bg=row_bg, fg=TEXT2, width=6).pack(side="left")

            # Connect button (appears on hover)
            conn_btn = GlowBtn(inner, "CONNECT", GREEN,
                               command=lambda s=srv: self._vpn_connect_server(s))
            # Don't pack yet — shown on hover

            self._vpn_server_rows.append((row, inner, indicator, ping_lbl, conn_btn, srv))

            # Hover effects
            def make_hover(r, i, ind, btn, bg):
                def enter(e):
                    for w in r.winfo_children(): w.configure(bg=CARD)
                    for w in i.winfo_children(): w.configure(bg=CARD)
                    r.configure(bg=CARD)
                    i.configure(bg=CARD)
                    ind.configure(bg=ACCENT)
                    btn.pack(side="right")
                def leave(e):
                    if self._vpn_selected_server != r:
                        for w in r.winfo_children(): 
                            try: w.configure(bg=bg)
                            except: pass
                        r.configure(bg=bg)
                        i.configure(bg=bg)
                        ind.configure(bg=bg)
                    btn.pack_forget()
                r.bind("<Enter>", enter)
                r.bind("<Leave>", leave)
                i.bind("<Enter>", enter)
                i.bind("<Leave>", leave)
                r.bind("<Button-1>", lambda e, s=srv: self._vpn_select_server(s))
                i.bind("<Button-1>", lambda e, s=srv: self._vpn_select_server(s))
            make_hover(row, inner, indicator, conn_btn, row_bg)

        self._vpn_server_count.configure(text="{} servers".format(len(servers)))

    def _vpn_select_server(self, srv):
        self._vpn_selected_server = srv
        city = srv.get("city","")
        flag = COUNTRY_FLAGS.get(srv["flag"],"🌐")
        self._vpn_selected_lbl.configure(
            text="{} {} — {}  |  {}  port {}".format(
                flag, srv["country"], city, srv["protocol"], srv["port"]),
            fg=ACCENT)

    def _vpn_ping_all(self):
        """Ping all visible servers and update UI."""
        self._vpn_server_count.configure(text="Pinging...")
        visible = [s for _,_,_,_,_,s in self._vpn_server_rows]

        def on_result(i, ms):
            if i < len(self._vpn_server_rows):
                _, _, _, ping_lbl, _, srv = self._vpn_server_rows[i]
                if ms is None:
                    txt, color = "timeout", RED
                elif ms < 50:
                    txt, color = "{}ms".format(ms), GREEN
                elif ms < 120:
                    txt, color = "{}ms".format(ms), AMBER
                else:
                    txt, color = "{}ms".format(ms), RED
                self.after(0, lambda l=ping_lbl, t=txt, c=color:
                           l.configure(text=t, fg=c))

        def done():
            threads = ping_all_servers(visible, callback=on_result)
            for t in threads: t.join()
            count = len(visible)
            self.after(0, lambda: self._vpn_server_count.configure(
                text="{} servers".format(count)))

        threading.Thread(target=done, daemon=True).start()

    def _vpn_connect_fastest(self):
        """Auto-ping and connect to fastest server."""
        self._vpn_server_count.configure(text="Finding fastest...")
        self._vpn_connect_btn.configure(text="CONNECTING...", bg=AMBER, state="disabled")
        servers = [s for _,_,_,_,_,s in self._vpn_server_rows]

        def run():
            # Quick ping all
            ping_all_servers(servers)
            import time; time.sleep(4)
            fastest = get_fastest_server(servers)
            if fastest:
                self.after(0, lambda: self._vpn_connect_server(fastest))
            else:
                self.after(0, lambda: self._vpn_connect_btn.configure(
                    text="CONNECT", bg=GREEN, state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def _vpn_connect_server(self, srv):
        """Connect to a specific server."""
        flag = COUNTRY_FLAGS.get(srv["flag"],"🌐")
        self._vpn_connect_btn.configure(text="CONNECTING...", bg=AMBER, state="disabled")
        self._vpn_dot.configure(fg=AMBER)
        self._vpn_status_big.configure(text="CONNECTING...", fg=AMBER)
        self._vpn_location_lbl.configure(
            text="{} {} — {}".format(flag, srv["country"], srv.get("city","")),
            fg=AMBER)
        # Use Tor as the underlying tunnel
        self._tor_connect()
        # After connection, update location
        self.after(3000, lambda: self._vpn_set_connected(
            srv["country"], srv.get("city",""), srv["flag"]))


    def _vpn_filter_servers(self):
        query = self._vpn_search_var.get().lower().strip()
        if query.startswith("search"): query = ""
        proto = self._vpn_proto_var.get()
        filtered = []
        for srv in FREE_VPN_SERVERS:
            if query and query not in srv["country"].lower() and query not in srv.get("city","").lower():
                continue
            if proto != "ALL" and srv["protocol"] != proto:
                continue
            filtered.append(srv)
        self._vpn_fill_servers(filtered)


    def _vpn_get_selected(self):
        return self._vpn_selected_server


    def _vpn_save_config(self):
        s = self._vpn_get_selected()
        if not s:
            return
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".ovpn",
            initialfile="{}-pyshield.ovpn".format(s["country"].replace(" ","_")),
            filetypes=[("OpenVPN Config","*.ovpn"),("All Files","*.*")]
        )
        if path:
            config = generate_ovpn_config(s)
            Path(path).write_text(config)
            self._vpn_connect_lbl.configure(
                text="Saved to {}".format(Path(path).name), fg=GREEN)

    def _vpn_connect(self):
        s = self._vpn_get_selected()
        if not s:
            return
        ovpn = find_openvpn()
        if not ovpn:
            messagebox.showwarning(
                "OpenVPN Not Found",
                "OpenVPN is not installed.\n\n"
                "Download it free from: https://openvpn.net/community-downloads/\n\n"
                "After installing, click Connect again."
            )
            return

        import tempfile, os
        config = generate_ovpn_config(s)
        tmp    = tempfile.NamedTemporaryFile(mode="w", suffix=".ovpn", delete=False)
        tmp.write(config)
        tmp.close()

        try:
            if platform.system() == "Windows":
                subprocess.Popen(
                    ["runas", "/user:Administrator",
                     ovpn, "--config", tmp.name],
                    creationflags=0x08000000
                )
            else:
                subprocess.Popen(["sudo", ovpn, "--config", tmp.name])
            self._vpn_connect_lbl.configure(
                text="Connecting to {}...".format(s["country"]), fg=AMBER)
        except Exception as e:
            messagebox.showerror("Connect Failed", str(e))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
    # ── Optimizer Page ─────────────────────────
    def _pg_optimizer(self):
        f = tk.Frame(self._content, bg=BG)
        header(f, "PC OPTIMIZER",
               "Speed up your PC, free RAM, kill bloat, boost gaming").pack(
               fill="x", padx=30, pady=(25,15))

        style = ttk.Style()
        style.configure("OPT.TNotebook",     background=BG, borderwidth=0)
        style.configure("OPT.TNotebook.Tab", background=PANEL, foreground=MUTED,
                        padding=[14,8], font=("Consolas",9,"bold"))
        style.map("OPT.TNotebook.Tab",
                  background=[("selected",CARD)],
                  foreground=[("selected",ACCENT)])

        nb = ttk.Notebook(f, style="OPT.TNotebook")
        nb.pack(fill="both", expand=True, padx=30, pady=(0,20))

        nb.add(self._opt_tab_overview(nb),  text="  OVERVIEW  ")
        nb.add(self._opt_tab_processes(nb), text="  PROCESSES  ")
        nb.add(self._opt_tab_gaming(nb),    text="  GAMING  ")
        nb.add(self._opt_tab_cleaner(nb),   text="  CLEANER  ")
        nb.add(self._opt_tab_network(nb),   text="  NETWORK  ")
        nb.add(self._opt_tab_startup(nb),   text="  STARTUP  ")
        nb.add(self._opt_tab_visual(nb),    text="  VISUAL  ")
        return f

    def _opt_tab_overview(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)

        tk.Label(f, text="SYSTEM STATUS", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Live overview of your PC performance",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        # Stats row
        row = tk.Frame(f, bg=CARD)
        row.pack(fill="x", pady=(0,15))
        self._opt_stats = {}
        for label, val, color in [
            ("CPU LOAD", "?%",   ACCENT),
            ("RAM USED", "? GB", AMBER),
            ("RAM FREE", "? GB", GREEN),
            ("OS",       "?",    MUTED),
        ]:
            c = tk.Frame(row, bg=BG, padx=16, pady=14)
            c.pack(side="left", expand=True, fill="both", padx=(0,8))
            tk.Frame(c, bg=color, height=2).pack(fill="x")
            tk.Frame(c, bg=BG, height=6).pack()
            v = tk.Label(c, text=val, font=("Consolas",16,"bold"), bg=BG, fg=color)
            v.pack()
            tk.Label(c, text=label, font=("Consolas",7), bg=BG, fg=MUTED).pack()
            self._opt_stats[label] = v

        self._opt_cpu_lbl = tk.Label(f, text="", font=FM, bg=CARD, fg=MUTED)
        self._opt_cpu_lbl.pack(anchor="w", pady=(0,12))

        # One-click optimize all
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=(0,15))
        tk.Label(f, text="ONE-CLICK OPTIMIZE", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w", pady=(0,8))
        tk.Label(f, text="Kills bloat, clears temp files, flushes DNS, disables animations",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(0,12))

        btn_row = tk.Frame(f, bg=CARD)
        btn_row.pack(anchor="w", pady=(0,15))
        self._opt_all_btn = GlowBtn(btn_row, "◆  OPTIMIZE EVERYTHING", ACCENT,
                                    command=self._opt_do_all)
        self._opt_all_btn.pack(side="left", padx=(0,10))
        GlowBtn(btn_row, "REFRESH STATS", BLUE,
                command=self._opt_refresh_stats).pack(side="left")

        tk.Label(f, text="OUTPUT", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(0,4))
        self._opt_out = OutBox(f, height=8)
        self._opt_out.pack(fill="both", expand=True)

        self._opt_refresh_stats()
        return f

    def _opt_refresh_stats(self):
        def run():
            info = get_system_info()
            ram  = get_ram_info()
            def update():
                self._opt_stats["CPU LOAD"].configure(
                    text=info.get("cpuload","?"))
                self._opt_stats["RAM USED"].configure(
                    text="{}GB".format(ram["used"]))
                self._opt_stats["RAM FREE"].configure(
                    text="{}GB".format(ram["free"]))
                self._opt_stats["OS"].configure(
                    text=info.get("os","?")[:20])
                self._opt_cpu_lbl.configure(
                    text="  CPU: {}".format(info.get("cpu","Unknown")))
            self.after(0, update)
        threading.Thread(target=run, daemon=True).start()

    def _opt_do_all(self):
        self._opt_all_btn.configure(state="disabled", text="Optimizing...")
        self._opt_out.clear()
        self._out_append(self._opt_out, "  Starting full optimization...\n\n", "accent")
        def run():
            # Kill bloat
            self._out_append(self._opt_out, "  Killing bloat processes...\n", "accent")
            killed, _ = kill_bloat_processes(
                log=lambda m,t: self._out_append(self._opt_out, m+"\n", t))
            self._out_append(self._opt_out,
                "  Killed {} processes\n\n".format(len(killed)), "success")
            # Clear temp
            self._out_append(self._opt_out, "  Clearing temp files...\n", "accent")
            c, _ = clear_temp_files(
                log=lambda m,t: self._out_append(self._opt_out, m+"\n", t))
            # Flush DNS
            clear_dns_cache(log=lambda m,t: self._out_append(self._opt_out, m+"\n", t))
            # Disable animations
            disable_animations(log=lambda m,t: self._out_append(self._opt_out, m+"\n", t))
            # Power plan
            ok, msg = set_high_performance_power()
            self._out_append(self._opt_out, "  {}\n".format(msg), "success" if ok else "warn")
            # Free RAM
            free_standby_ram(log=lambda m,t: self._out_append(self._opt_out, m+"\n", t))

            self._out_append(self._opt_out, "\n  All done! Your PC should feel faster.\n", "success")
            self.after(0, lambda: self._opt_all_btn.configure(
                state="normal", text="◆  OPTIMIZE EVERYTHING"))
            self.after(500, self._opt_refresh_stats)
        threading.Thread(target=run, daemon=True).start()

    def _opt_tab_processes(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=0, pady=0)

        top = tk.Frame(f, bg=CARD, padx=24, pady=16)
        top.pack(fill="x")

        # Title row with live process counter
        title_row = tk.Frame(top, bg=CARD)
        title_row.pack(fill="x", anchor="w")
        tk.Label(title_row, text="PROCESS MANAGER",
                 font=("Segoe UI", 11, "bold"),
                 bg=CARD, fg=ACCENT).pack(side="left")

        # Live counter badge
        self._proc_count_badge = tk.Label(
            title_row, text="  ? running",
            font=("Consolas", 10, "bold"),
            bg=ACCENTD, fg=TEXT, padx=10, pady=2)
        self._proc_count_badge.pack(side="left", padx=(12,0))

        tk.Label(top, text="View all running processes sorted by CPU usage",
                 font=("Segoe UI", 9), bg=CARD, fg=TEXT2).pack(anchor="w", pady=(4,12))

        # Stat row — total, high CPU, high RAM
        stat_row = tk.Frame(top, bg=CARD)
        stat_row.pack(fill="x", pady=(0,12))
        for key, label, color in [
            ("_proc_stat_total",   "TOTAL",    ACCENT),
            ("_proc_stat_cpu",     "HIGH CPU", RED),
            ("_proc_stat_ram",     "HIGH RAM", AMBER),
            ("_proc_stat_bloat",   "BLOAT",    "#f97316"),
        ]:
            card = tk.Frame(stat_row, bg=BG, padx=14, pady=10)
            card.pack(side="left", padx=(0,8))
            tk.Frame(card, bg=color, height=2).pack(fill="x")
            tk.Frame(card, bg=BG, height=4).pack()
            v = tk.Label(card, text="—", font=("Segoe UI", 16, "bold"),
                         bg=BG, fg=color)
            v.pack()
            tk.Label(card, text=label, font=("Consolas", 7),
                     bg=BG, fg=TEXT2).pack()
            setattr(self, key, v)

        # Buttons
        br = tk.Frame(top, bg=CARD)
        br.pack(anchor="w", pady=(0,4))
        GlowBtn(br, "↺  REFRESH", ACCENT,
                command=self._opt_refresh_procs).pack(side="left", padx=(0,8))
        GlowBtn(br, "✕  KILL SELECTED", RED,
                command=self._opt_kill_selected).pack(side="left", padx=(0,8))
        GlowBtn(br, "⚡  AUTO-OPTIMIZE", GREEN,
                command=self._opt_auto_optimize).pack(side="left", padx=(0,8))
        GlowBtn(br, "☠  KILL ALL BLOAT", AMBER,
                command=self._opt_kill_bloat).pack(side="left")

        style = ttk.Style()
        style.configure("PROC.Treeview",
                        background=BG, foreground=TEXT,
                        fieldbackground=BG, rowheight=28,
                        font=("Consolas",9), borderwidth=0)
        style.configure("PROC.Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("PROC.Treeview",
                  background=[("selected", BORDER2)],
                  foreground=[("selected", ACCENT)])

        cols = ("Process", "CPU (s)", "RAM (MB)", "Status")
        self._proc_tree = ttk.Treeview(f, columns=cols, show="headings",
                                       style="PROC.Treeview", height=14)
        self._proc_tree.heading("Process",  text="Process Name")
        self._proc_tree.heading("CPU (s)",  text="CPU (s)")
        self._proc_tree.heading("RAM (MB)", text="RAM (MB)")
        self._proc_tree.heading("Status",   text="Status")
        self._proc_tree.column("Process",  width=260)
        self._proc_tree.column("CPU (s)",  width=90)
        self._proc_tree.column("RAM (MB)", width=90)
        self._proc_tree.column("Status",   width=120)

        self._proc_tree.tag_configure("bloat",   foreground="#f97316")
        self._proc_tree.tag_configure("highcpu", foreground="#fb7185")
        self._proc_tree.tag_configure("highram", foreground=AMBER)
        self._proc_tree.tag_configure("normal",  foreground=TEXT2)

        sc = ttk.Scrollbar(f, orient="vertical", command=self._proc_tree.yview)
        self._proc_tree.configure(yscrollcommand=sc.set)
        self._proc_tree.pack(fill="both", expand=True, padx=0)

        # Bottom status bar
        self._proc_status_bar = tk.Label(f, text="",
                                         font=("Segoe UI", 8),
                                         bg=PANEL, fg=TEXT2, anchor="w", padx=16, pady=6)
        self._proc_status_bar.pack(fill="x")

        self._opt_refresh_procs()
        return f

    def _opt_refresh_procs(self):
        self._proc_count_badge.configure(text="  Loading...", bg=MUTED)
        self._proc_status_bar.configure(text="  Refreshing process list...")
        for r in self._proc_tree.get_children():
            self._proc_tree.delete(r)

        from optimizer import BLOAT_PROCESSES
        bloat_names = {b.lower().replace(".exe","") for b in BLOAT_PROCESSES}

        def run():
            real_count = get_process_count()
            procs = get_running_processes()
            high_cpu  = [p for p in procs if p["cpu"]  > 10]
            high_ram  = [p for p in procs if p["ram"]  > 200]
            bloat_found = [p for p in procs
                           if p["name"].lower().replace(".exe","") in bloat_names]

            def update():
                for p in procs:
                    name_lower = p["name"].lower().replace(".exe","")
                    is_bloat   = name_lower in bloat_names
                    is_hcpu    = p["cpu"]  > 10
                    is_hram    = p["ram"]  > 200

                    if is_bloat:
                        status = "Bloat"
                        tag    = "bloat"
                    elif is_hcpu:
                        status = "High CPU"
                        tag    = "highcpu"
                    elif is_hram:
                        status = "High RAM"
                        tag    = "highram"
                    else:
                        status = "Normal"
                        tag    = "normal"

                    self._proc_tree.insert("", "end", values=(
                        p["name"], p["cpu"], p["ram"], status), tags=(tag,))

                total = len(procs)
                display_total = real_count if real_count > 0 else total
                self._proc_count_badge.configure(
                    text="  {} running".format(display_total),
                    bg=ACCENTD if display_total < 150 else RED)
                self._proc_stat_total.configure(text=str(display_total))
                self._proc_stat_cpu.configure(text=str(len(high_cpu)))
                self._proc_stat_ram.configure(text=str(len(high_ram)))
                self._proc_stat_bloat.configure(text=str(len(bloat_found)))
                self._proc_status_bar.configure(
                    text="  {} processes  |  {} high CPU  |  {} high RAM  |  {} bloat processes detected".format(
                        total, len(high_cpu), len(high_ram), len(bloat_found)))
            self.after(0, update)
        threading.Thread(target=run, daemon=True).start()

    def _opt_auto_optimize(self):
        """Kill only confirmed bloat — never touches safe/user processes."""
        try:
            from optimizer import BLOAT_PROCESSES, is_safe_process
        except ImportError:
            messagebox.showerror("Error", "Could not load optimizer module.")
            return

        bloat_names = {b.lower().replace(".exe","") for b in BLOAT_PROCESSES}

        # Only kill processes that are in the explicit BLOAT list
        # AND not in the safe list — never kills based on CPU usage alone
        procs_to_kill = []
        for iid in self._proc_tree.get_children():
            vals = self._proc_tree.item(iid)["values"]
            name = str(vals[0])
            name_lower = name.lower().replace(".exe","")
            if name_lower in bloat_names and not is_safe_process(name):
                procs_to_kill.append(name)

        if not procs_to_kill:
            messagebox.showinfo("Already Optimized",
                "No bloat processes are running!\nYour PC is already clean.")
            return

        msg = "Auto-Optimize found {} bloat processes to kill:\n\n{}\n\nThese are background apps that waste RAM/CPU.\nYour games, Discord, browsers and display drivers\nwill NOT be touched.\n\nContinue?".format(
            len(procs_to_kill),
            "\n".join(procs_to_kill[:15]) + ("\n..." if len(procs_to_kill)>15 else ""))

        if not messagebox.askyesno("Auto-Optimize", msg):
            return

        def run():
            killed = 0
            for name in procs_to_kill:
                ok, _ = kill_process_by_name(name)
                if ok:
                    killed += 1
            self.after(1200, self._opt_refresh_procs)
            self.after(0, lambda: messagebox.showinfo(
                "Optimization Complete",
                "Killed {} bloat processes!\nYour PC should feel faster now.".format(killed)))
        threading.Thread(target=run, daemon=True).start()

    def _opt_kill_selected(self):
        sel = self._proc_tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a process first.")
            return
        name = self._proc_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Kill Process", "Kill {}?".format(name)):
            kill_process_by_name(name)
            self.after(1000, self._opt_refresh_procs)

    def _opt_kill_bloat(self):
        if messagebox.askyesno("Kill Bloat",
            "Kill all known bloat processes?\n(OneDrive, Xbox, Cortana, etc.)"):
            def run():
                killed, _ = kill_bloat_processes()
                self.after(1000, self._opt_refresh_procs)
                messagebox.showinfo("Done", "Killed {} bloat processes!".format(len(killed)))
            threading.Thread(target=run, daemon=True).start()

    def _opt_tab_gaming(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)
        tk.Label(f, text="GAMING OPTIMIZER", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Maximize FPS and minimize input lag",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        tweaks = [
            ("Ultimate Performance Power Plan",
             "Unlocks hidden power plan for max CPU performance",
             set_ultimate_performance_power, GREEN),
            ("High Performance Power Plan",
             "Standard high performance - good balance",
             set_high_performance_power, ACCENT),
            ("Disable Xbox Game Bar",
             "Removes background game recording (frees CPU/RAM)",
             lambda: disable_xbox_game_bar(), AMBER),
            ("Disable Fullscreen Optimizations",
             "Fixes stuttering in fullscreen games",
             lambda: disable_fullscreen_optimizations(), AMBER),
            ("Set Minimum Timer Resolution",
             "Reduces input lag and frame pacing issues",
             lambda: set_timer_resolution(), ACCENT),
        ]

        self._gaming_out = OutBox(f, height=10)

        for name, desc, fn, color in tweaks:
            card = tk.Frame(f, bg=BG, padx=16, pady=12)
            card.pack(fill="x", pady=(0,8))
            left = tk.Frame(card, bg=BG)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text=name, font=FBB, bg=BG, fg=TEXT).pack(anchor="w")
            tk.Label(left, text=desc, font=FS,  bg=BG, fg=MUTED).pack(anchor="w")
            def make_cmd(f=fn, n=name):
                def cmd():
                    ok, msg = f()
                    tag = "success" if ok else "warn"
                    self._gaming_out.append("  [{}] {}: {}\n".format(
                        "OK" if ok else "!!", n, msg), tag)
                return cmd
            GlowBtn(card, "APPLY", color, command=make_cmd()).pack(side="right")

        tk.Label(f, text="OUTPUT", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(12,4))
        self._gaming_out.pack(fill="both", expand=True)
        return f

    def _opt_tab_cleaner(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)
        tk.Label(f, text="DISK CLEANER", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Free up disk space by removing junk files",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,12))

        # Temp size preview
        size_row = tk.Frame(f, bg=BG, padx=16, pady=14)
        size_row.pack(fill="x", pady=(0,15))
        self._temp_size_lbl = tk.Label(size_row, text="Calculating...",
                                       font=("Consolas",18,"bold"), bg=BG, fg=AMBER)
        self._temp_size_lbl.pack(anchor="w")
        tk.Label(size_row, text="in temp files on this PC",
                 font=FM, bg=BG, fg=MUTED).pack(anchor="w")

        tweaks = [
            ("Clear Temp Files",      "Removes %TEMP%, Windows\\Temp, INetCache",
             lambda: clear_temp_files()),
            ("Clear Prefetch",        "Removes old prefetch data (Windows rebuilds it)",
             lambda: clear_prefetch()),
            ("Flush DNS Cache",       "Clears cached DNS entries (fixes slow browsing)",
             lambda: (clear_dns_cache(), (True, "DNS flushed"))[1]),
            ("Free RAM (Standby)",    "Releases RAM held in standby list",
             lambda: (free_standby_ram(), (True, "RAM freed"))[1]),
            ("Windows Disk Cleanup",  "Runs built-in Windows disk cleanup tool",
             lambda: (run_disk_cleanup(), (True, "Cleanup launched"))[1]),
        ]

        self._cleaner_out = OutBox(f, height=8)

        for name, desc, fn in tweaks:
            row = tk.Frame(f, bg=BG, padx=16, pady=10)
            row.pack(fill="x", pady=(0,6))
            left = tk.Frame(row, bg=BG)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text=name, font=FBB, bg=BG, fg=TEXT).pack(anchor="w")
            tk.Label(left, text=desc, font=FS,  bg=BG, fg=MUTED).pack(anchor="w")
            def make_cmd(fn=fn, n=name):
                def cmd():
                    result = fn()
                    self._cleaner_out.append(
                        "  [OK] {}\n".format(n), "success")
                    self.after(500, self._opt_load_temp_size)
                return cmd
            GlowBtn(row, "RUN", ACCENT, command=make_cmd()).pack(side="right")

        tk.Label(f, text="OUTPUT", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(8,4))
        self._cleaner_out.pack(fill="both", expand=True)
        self._opt_load_temp_size()
        return f

    def _opt_load_temp_size(self):
        def run():
            size = get_temp_size()
            self.after(0, lambda: self._temp_size_lbl.configure(
                text="{} MB".format(size),
                fg=RED if size > 500 else AMBER if size > 100 else GREEN))
        threading.Thread(target=run, daemon=True).start()

    def _opt_tab_network(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)
        tk.Label(f, text="NETWORK OPTIMIZER", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Reduce ping, speed up DNS, optimize TCP settings",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        tweaks = [
            ("Optimize All Network Settings",
             "Resets TCP/IP, Winsock, enables RSS and Chimney",
             lambda: (optimize_network(), (True,"Network optimized"))[1]),
            ("Flush DNS Cache",
             "Clears DNS cache - fixes slow site loading",
             lambda: (clear_dns_cache(), (True,"DNS flushed"))[1]),
            ("Pause Windows Update",
             "Stops background updates from eating bandwidth",
             lambda: (disable_auto_updates_temporarily(), (True,"Update paused"))[1]),
            ("Re-enable Windows Update",
             "Turns Windows Update back on",
             lambda: (enable_auto_updates(), (True,"Update enabled"))[1]),
        ]

        self._net_out = OutBox(f, height=12)

        for name, desc, fn in tweaks:
            row = tk.Frame(f, bg=BG, padx=16, pady=10)
            row.pack(fill="x", pady=(0,8))
            left = tk.Frame(row, bg=BG)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text=name, font=FBB, bg=BG, fg=TEXT).pack(anchor="w")
            tk.Label(left, text=desc, font=FS,  bg=BG, fg=MUTED).pack(anchor="w")
            def make_cmd(fn=fn, n=name):
                def cmd():
                    fn()
                    self._net_out.append("  [OK] {}\n".format(n), "success")
                return cmd
            GlowBtn(row, "APPLY", ACCENT, command=make_cmd()).pack(side="right")

        tk.Label(f, text="OUTPUT", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(8,4))
        self._net_out.pack(fill="both", expand=True)
        return f

    def _opt_tab_startup(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=0, pady=0)
        top = tk.Frame(f, bg=CARD, padx=24, pady=16)
        top.pack(fill="x")
        tk.Label(top, text="STARTUP MANAGER", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(top, text="Disable apps that slow down your boot time",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,10))

        br = tk.Frame(top, bg=CARD)
        br.pack(anchor="w")
        GlowBtn(br, "REFRESH", ACCENT, command=self._startup_refresh).pack(side="left", padx=(0,8))
        GlowBtn(br, "DISABLE SELECTED", RED, command=self._startup_disable).pack(side="left")

        warn = tk.Frame(top, bg="#150b00", padx=12, pady=8)
        warn.pack(fill="x", pady=(10,0))
        tk.Label(warn, text="  Only disable apps you recognize and don't need at startup.",
                 font=FS, bg="#150b00", fg=AMBER).pack(anchor="w")

        style = ttk.Style()
        style.configure("ST.Treeview",
                        background=BG, foreground=TEXT,
                        fieldbackground=BG, rowheight=28,
                        font=FM, borderwidth=0)
        style.configure("ST.Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Consolas",9,"bold"), relief="flat")
        style.map("ST.Treeview",
                  background=[("selected",BORDER)],
                  foreground=[("selected",ACCENT)])

        cols = ("Name", "Path", "Location")
        self._startup_tree = ttk.Treeview(f, columns=cols, show="headings",
                                          style="ST.Treeview", height=16)
        self._startup_tree.heading("Name",     text="Name")
        self._startup_tree.heading("Path",     text="Path")
        self._startup_tree.heading("Location", text="Location")
        self._startup_tree.column("Name",     width=180)
        self._startup_tree.column("Path",     width=340)
        self._startup_tree.column("Location", width=80)

        sc = ttk.Scrollbar(f, orient="vertical", command=self._startup_tree.yview)
        self._startup_tree.configure(yscrollcommand=sc.set)
        self._startup_tree.pack(fill="both", expand=True)

        self._startup_refresh()
        return f

    def _startup_refresh(self):
        for r in self._startup_tree.get_children():
            self._startup_tree.delete(r)
        def run():
            items = get_startup_items()
            def update():
                for item in items:
                    self._startup_tree.insert("", "end",
                        iid=item["name"] + "|" + item["hive"],
                        values=(item["name"], item["path"][:60], item["hive"]))
            self.after(0, update)
        threading.Thread(target=run, daemon=True).start()

    def _startup_disable(self):
        sel = self._startup_tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a startup item first.")
            return
        iid  = sel[0]
        vals = self._startup_tree.item(iid)["values"]
        name, hive = vals[0], vals[2]
        items = get_startup_items()
        match = next((i for i in items if i["name"]==name and i["hive"]==hive), None)
        if match and messagebox.askyesno("Disable Startup",
            "Remove '{}' from startup?".format(name)):
            ok, msg = disable_startup_item(name, hive, match["regpath"])
            if ok:
                messagebox.showinfo("Done", "'{}' removed from startup!".format(name))
                self._startup_refresh()
            else:
                messagebox.showerror("Failed", msg)

    def _opt_tab_visual(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)
        tk.Label(f, text="VISUAL & RESPONSIVENESS", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Make Windows feel snappier by reducing visual effects",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        tweaks = [
            ("Best Performance Visual Effects",
             "Sets all visual effects to maximum performance mode",
             lambda: set_best_performance_visual(), ACCENT),
            ("Disable Window Animations",
             "Removes open/close/minimize animations (instant response)",
             lambda: disable_animations(), GREEN),
            ("Re-enable Window Animations",
             "Turns animations back on if you want them",
             lambda: enable_animations(), MUTED),
            ("Disable Transparency Effects",
             "Removes glass/blur effects (frees GPU overhead)",
             lambda: disable_transparency(), AMBER),
        ]

        self._visual_out = OutBox(f, height=10)

        for name, desc, fn, color in tweaks:
            row = tk.Frame(f, bg=BG, padx=16, pady=10)
            row.pack(fill="x", pady=(0,8))
            left = tk.Frame(row, bg=BG)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text=name, font=FBB, bg=BG, fg=TEXT).pack(anchor="w")
            tk.Label(left, text=desc, font=FS,  bg=BG, fg=MUTED).pack(anchor="w")
            def make_cmd(fn=fn, n=name):
                def cmd():
                    result = fn()
                    ok = result[0] if isinstance(result, tuple) else result
                    self._visual_out.append(
                        "  [{}] {}\n".format("OK" if ok else "!!", n),
                        "success" if ok else "warn")
                return cmd
            GlowBtn(row, "APPLY", color, command=make_cmd()).pack(side="right")

        tk.Label(f, text="OUTPUT", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(8,4))
        self._visual_out.pack(fill="both", expand=True)
        return f


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
    def _vpn_tab_leak(self, parent):
        f = tk.Frame(parent, bg=CARD, padx=24, pady=20)

        tk.Label(f, text="IP LEAK PROTECTION",
                 font=("Consolas",10,"bold"), bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Block DNS leaks, WebRTC leaks, and firewall bypass",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,15))

        # Status cards
        status_row = tk.Frame(f, bg=CARD)
        status_row.pack(fill="x", pady=(0,15))
        self._leak_labels = {}
        for key, label, good, bad in [
            ("dns_safe",       "DNS",          "Safe",    "Leaking"),
            ("webrtc_blocked", "WebRTC",       "Blocked", "Exposed"),
            ("firewall_active","Firewall Rules","Active",  "Inactive"),
        ]:
            card = tk.Frame(status_row, bg=BG, padx=16, pady=14)
            card.pack(side="left", expand=True, fill="both", padx=(0,8))
            tk.Label(card, text=label, font=("Consolas",8),
                     bg=BG, fg=MUTED).pack(anchor="w")
            v = tk.Label(card, text="?", font=("Consolas",16,"bold"),
                         bg=BG, fg=MUTED)
            v.pack(anchor="w")
            self._leak_labels[key] = (v, good, bad)

        GlowBtn(f, "CHECK LEAK STATUS", ACCENT,
                command=self._leak_check_status).pack(anchor="w", pady=(0,15))

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=(0,15))

        # DNS section
        tk.Label(f, text="FORCE SAFE DNS", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(f, text="Override your DNS with a private provider to stop DNS leaks",
                 font=FS, bg=CARD, fg=MUTED).pack(anchor="w", pady=(3,10))

        dns_row = tk.Frame(f, bg=CARD)
        dns_row.pack(fill="x", pady=(0,12))
        tk.Label(dns_row, text="Select DNS:", font=FB, bg=CARD, fg=TEXT).pack(side="left", padx=(0,8))
        self._dns_choice = tk.StringVar(value="Cloudflare (Fast + Private)")
        cb = ttk.Combobox(dns_row, textvariable=self._dns_choice,
                          values=list(PRIVACY_DNS_OPTIONS.keys()),
                          state="readonly", width=30, font=FM)
        cb.pack(side="left", padx=(0,10))

        btn_row = tk.Frame(f, bg=CARD)
        btn_row.pack(anchor="w", pady=(0,15))
        GlowBtn(btn_row, "APPLY DNS", GREEN,
                command=self._leak_apply_dns).pack(side="left", padx=(0,10))
        GlowBtn(btn_row, "RESET TO AUTO", MUTED, fg=TEXT,
                command=self._leak_reset_dns).pack(side="left")

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=(0,15))

        # WebRTC + Firewall
        tk.Label(f, text="ADVANCED PROTECTION", font=("Consolas",10,"bold"),
                 bg=CARD, fg=ACCENT).pack(anchor="w", pady=(0,10))

        actions = [
            ("Block WebRTC Leaks",
             "Prevents browsers from exposing your real IP through WebRTC",
             self._leak_block_webrtc, RED),
            ("Re-enable WebRTC",
             "Turns WebRTC back on (needed for video calls like Discord)",
             self._leak_enable_webrtc, MUTED),
            ("Enable Firewall DNS Protection",
             "Blocks all DNS requests except through safe servers",
             self._leak_enable_firewall, RED),
            ("Disable Firewall DNS Protection",
             "Removes the firewall DNS rules",
             self._leak_disable_firewall, MUTED),
        ]

        for name, desc, cmd, color in actions:
            row = tk.Frame(f, bg=BG, padx=14, pady=10)
            row.pack(fill="x", pady=(0,6))
            left = tk.Frame(row, bg=BG)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text=name, font=FBB, bg=BG, fg=TEXT).pack(anchor="w")
            tk.Label(left, text=desc, font=FS,  bg=BG, fg=MUTED).pack(anchor="w")
            GlowBtn(row, "APPLY", color, command=lambda c=cmd: c()).pack(side="right")

        tk.Label(f, text="OUTPUT", font=("Consolas",8,"bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(10,4))
        self._leak_out = OutBox(f, height=6)
        self._leak_out.pack(fill="both", expand=True)

        self._leak_check_status()
        return f

    def _leak_check_status(self):
        for key, (lbl, good, bad) in self._leak_labels.items():
            lbl.configure(text="Checking...", fg=AMBER)
        def run():
            try:
                status = get_leak_status()
            except Exception as e:
                status = {"dns_safe":False,"webrtc_blocked":False,
                          "firewall_active":False,"_err":str(e)}
            def update():
                for key, (lbl, good, bad) in self._leak_labels.items():
                    val = status.get(key, False)
                    lbl.configure(text=good if val else bad,
                                  fg=GREEN if val else RED)
                if "_err" in status:
                    self._leak_out.append(
                        "  Error: {}\n".format(status["_err"]), "warn")
            self.after(0, update)
        threading.Thread(target=run, daemon=True).start()

    def _leak_apply_dns(self):
        choice  = self._dns_choice.get()
        primary, secondary = PRIVACY_DNS_OPTIONS[choice]
        self._leak_out.clear()
        self._leak_out.append("  Applying DNS: {} ({} / {})\n".format(
            choice, primary, secondary), "accent")
        self._leak_out.append("  Setting all network adapters...\n", "muted")
        def run():
            import subprocess, platform
            if platform.system() == "Windows":
                # Use netsh directly - works without full admin for current user adapters
                import subprocess
                ok2, out2 = True, ""
                try:
                    adapters_result = subprocess.run(
                        ["powershell","-Command",
                         "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -ExpandProperty Name"],
                        capture_output=True, text=True, timeout=10
                    )
                    adapters = [a.strip() for a in adapters_result.stdout.strip().splitlines() if a.strip()]
                    if not adapters:
                        adapters = ["Wi-Fi", "Ethernet", "Local Area Connection"]
                    for adapter in adapters:
                        r = subprocess.run(
                            ["netsh","interface","ip","set","dns",
                             adapter, "static", primary, "primary"],
                            capture_output=True, text=True, timeout=8
                        )
                        r2 = subprocess.run(
                            ["netsh","interface","ip","add","dns",
                             adapter, secondary, "index=2"],
                            capture_output=True, text=True, timeout=8
                        )
                        worked = r.returncode == 0
                        self._out_append(self._leak_out,
                            "  {} {}\n".format("[OK]" if worked else "[!!]", adapter),
                            "success" if worked else "warn")
                except Exception as e:
                    self._out_append(self._leak_out, "  Error: {}\n".format(e), "danger")
            self._out_append(self._leak_out,
                "\n  Done! DNS now routes through {}\n  ({} / {})\n".format(
                    choice, primary, secondary), "success")
            self._out_append(self._leak_out,
                "  Tip: Restart browser for DNS change to fully apply.\n", "muted")
            self.after(800, self._leak_check_status)
        threading.Thread(target=run, daemon=True).start()

    def _leak_reset_dns(self):
        self._leak_out.clear()
        def run():
            reset_dns_to_automatic(
                log=lambda m,t: self._out_append(self._leak_out, m+"\n", t))
            self._out_append(self._leak_out, "\n  DNS reset to automatic.\n", "muted")
            self.after(500, self._leak_check_status)
        threading.Thread(target=run, daemon=True).start()

    def _leak_block_webrtc(self):
        self._leak_out.clear()
        self._leak_out.append("  Blocking WebRTC leaks in Chrome and Edge...\n", "accent")
        def run():
            disable_webrtc_leak(
                log=lambda m,t: self._out_append(self._leak_out, m+"\n", t))
            self._out_append(self._leak_out,
                "\n  Done! Restart your browser for changes to take effect.\n", "success")
            self.after(500, self._leak_check_status)
        threading.Thread(target=run, daemon=True).start()

    def _leak_enable_webrtc(self):
        enable_webrtc(log=lambda m,t: self._out_append(self._leak_out, m+"\n", t))
        self._leak_out.append("  WebRTC re-enabled. Restart browser to apply.\n", "muted")
        self.after(500, self._leak_check_status)

    def _leak_enable_firewall(self):
        self._leak_out.clear()
        self._leak_out.append("  Adding firewall DNS leak protection rules...\n", "accent")
        def run():
            block_non_vpn_traffic(
                log=lambda m,t: self._out_append(self._leak_out, m+"\n", t))
            self._out_append(self._leak_out,
                "\n  Firewall rules active! DNS can only go through safe servers.\n", "success")
            self.after(500, self._leak_check_status)
        threading.Thread(target=run, daemon=True).start()

    def _leak_disable_firewall(self):
        remove_leak_firewall_rules(
            log=lambda m,t: self._out_append(self._leak_out, m+"\n", t))
        self._leak_out.append("  Firewall rules removed.\n", "muted")
        self.after(500, self._leak_check_status)

    def _pg_developers(self):
        f = tk.Frame(self._content, bg=BG)

        canvas = tk.Canvas(f, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(f, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        scroll = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=scroll, anchor="nw")
        scroll.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            win_id, width=e.width))
        scroll.bind("<MouseWheel>", lambda e: canvas.yview_scroll(
            -1*(e.delta//120), "units"))

        # ── Header ──
        hdr = tk.Frame(scroll, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(28,0))
        tk.Frame(hdr, bg=PURPLE, width=4).pack(side="left", fill="y")
        hf = tk.Frame(hdr, bg=BG, padx=14)
        hf.pack(side="left")
        tk.Label(hf, text="DEVELOPERS",
                 font=("Consolas", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(hf, text="The people who built PyShield",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT2).pack(anchor="w", pady=(2,0))

        tk.Frame(scroll, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(20,0))

        # ── App info banner ──
        app_card = tk.Frame(scroll, bg=CARD)
        app_card.pack(fill="x", padx=30, pady=(20,0))
        tk.Frame(app_card, bg=ACCENT, height=3).pack(fill="x")
        ab = tk.Frame(app_card, bg=CARD, padx=28, pady=22)
        ab.pack(fill="x")
        al = tk.Frame(ab, bg=CARD)
        al.pack(side="left")
        icon_box2 = tk.Frame(al, bg=ACCENT, padx=14, pady=14)
        icon_box2.pack(side="left")
        tk.Label(icon_box2, text="⬡", font=("Consolas", 28, "bold"),
                 bg=ACCENT, fg=DARK).pack()
        ai = tk.Frame(al, bg=CARD, padx=16)
        ai.pack(side="left")
        tk.Label(ai, text="PYSHIELD",
                 font=("Consolas", 22, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(ai, text="Security Suite  •  v2.0",
                 font=("Consolas", 9), bg=CARD, fg=ACCENT).pack(anchor="w", pady=(2,0))
        tk.Label(ai, text="Antivirus  •  VPN & Privacy  •  PC Optimizer",
                 font=("Segoe UI", 9), bg=CARD, fg=TEXT2).pack(anchor="w", pady=(4,0))
        ar = tk.Frame(ab, bg=CARD)
        ar.pack(side="right")
        for badge_text, badge_color in [("FREE", GREEN), ("WINDOWS 10/11", TEXT2)]:
            b = tk.Frame(ar, bg=CARD, pady=2)
            b.pack(anchor="e")
            tk.Label(b, text=badge_text, font=("Consolas", 8, "bold"),
                     bg=CARD, fg=badge_color).pack(side="right")

        # ── Section header ──
        oh = tk.Frame(scroll, bg=BG)
        oh.pack(fill="x", padx=30, pady=(32,0))
        tk.Frame(oh, bg=PURPLE, width=3).pack(side="left", fill="y")
        of2 = tk.Frame(oh, bg=BG, padx=10)
        of2.pack(side="left")
        tk.Label(of2, text="OWNERS", font=("Consolas", 11, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(of2, text="Core team behind PyShield",
                 font=("Segoe UI", 8), bg=BG, fg=TEXT2).pack(anchor="w")

        # ── Developer cards ──
        devs_row = tk.Frame(scroll, bg=BG)
        devs_row.pack(fill="x", padx=30, pady=(14,0))

        DEVS = [
            {
                "name":      "JONATHAN",
                "avatar":    "J",
                "title":     "Developer & Owner",
                "color":     ACCENT,
                "badge":     "★  OWNER",
                "badge_bg":  "#001a0e",
                "badge_fg":  GREEN,
                "bio":       "Owner of PyShield. Responsible for the app's vision, development, and design. Built the core features and UI from the ground up.",
                "skills":    ["Python", "UI/UX", "Windows", "Optimization"],
            },
            {
                "name":      "HUDSON",
                "avatar":    "H",
                "title":     "Founder & Lead Owner",
                "color":     PURPLE,
                "badge":     "♛  LEAD OWNER",
                "badge_bg":  "#12001a",
                "badge_fg":  PURPLE,
                "bio":       "Founder and Lead Owner of PyShield. Founded the project and leads the overall strategy, security research, and growth of the app.",
                "skills":    ["Security", "Networking", "VPN", "Leadership"],
            },
        ]

        for dev in DEVS:
            card = tk.Frame(devs_row, bg=CARD)
            card.pack(side="left", expand=True, fill="both", padx=(0,14))
            tk.Frame(card, bg=dev["color"], height=4).pack(fill="x")
            body2 = tk.Frame(card, bg=CARD, padx=28, pady=24)
            body2.pack(fill="both", expand=True)

            top_row = tk.Frame(body2, bg=CARD)
            top_row.pack(fill="x")

            av = tk.Frame(top_row, bg=dev["color"])
            av.pack(side="left")
            tk.Label(av, text=dev["avatar"],
                     font=("Consolas", 30, "bold"),
                     bg=dev["color"], fg=DARK,
                     width=3, height=2).pack()

            nf2 = tk.Frame(top_row, bg=CARD, padx=16)
            nf2.pack(side="left")
            tk.Label(nf2, text=dev["name"],
                     font=("Consolas", 20, "bold"),
                     bg=CARD, fg=TEXT).pack(anchor="w")
            tk.Label(nf2, text=dev["title"],
                     font=("Segoe UI", 9), bg=CARD, fg=TEXT2).pack(anchor="w", pady=(2,0))

            badge_f = tk.Frame(top_row, bg=dev["badge_bg"], padx=14)
            badge_f.pack(side="right", anchor="n", pady=4)
            tk.Label(badge_f, text=dev["badge"],
                     font=("Consolas", 9, "bold"),
                     bg=dev["badge_bg"], fg=dev["badge_fg"],
                     pady=8).pack()

            tk.Frame(body2, bg=BORDER2, height=1).pack(fill="x", pady=(20,16))

            tk.Label(body2, text=dev["bio"],
                     font=("Segoe UI", 10), bg=CARD, fg=TEXT2,
                     wraplength=360, justify="left").pack(anchor="w")

            tk.Label(body2, text="SKILLS",
                     font=("Consolas", 8), bg=CARD, fg=MUTED).pack(
                     anchor="w", pady=(16,6))
            skills_row = tk.Frame(body2, bg=CARD)
            skills_row.pack(anchor="w")
            for skill in dev["skills"]:
                sk = tk.Frame(skills_row, bg=CARD3, padx=10, pady=5)
                sk.pack(side="left", padx=(0,6))
                tk.Label(sk, text=skill, font=("Consolas", 8, "bold"),
                         bg=CARD3, fg=dev["color"]).pack()

        # ── Built with ──
        bw = tk.Frame(scroll, bg=CARD2)
        bw.pack(fill="x", padx=30, pady=(32,0))
        tk.Frame(bw, bg=BORDER, height=1).pack(fill="x")
        bwi = tk.Frame(bw, bg=CARD2, padx=28, pady=18)
        bwi.pack(fill="x")
        tk.Label(bwi, text="BUILT WITH",
                 font=("Consolas", 8), bg=CARD2, fg=MUTED).pack(anchor="w")
        tech_row = tk.Frame(bwi, bg=CARD2)
        tech_row.pack(anchor="w", pady=(8,0))
        for tech, color in [
            ("Python 3", ACCENT), ("Tkinter", BLUE),
            ("pynput", AMBER), ("PyInstaller", PURPLE), ("Windows API", TEXT2),
        ]:
            tf2 = tk.Frame(tech_row, bg=CARD3, padx=12, pady=6)
            tf2.pack(side="left", padx=(0,8))
            tk.Label(tf2, text=tech, font=("Consolas", 8, "bold"),
                     bg=CARD3, fg=color).pack()

        # ── Footer ──
        fn = tk.Frame(scroll, bg=BG)
        fn.pack(fill="x", padx=30, pady=(28,40))
        tk.Label(fn,
            text="© 2025 Hudson & Jonathan  •  PyShield Security Suite  •  All rights reserved",
            font=("Consolas", 8), bg=BG, fg=MUTED).pack(anchor="center")

        return f


if __name__ == "__main__":
    if not AV_LOADED:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing File",
            "Could not load antivirus.py\n\n"
            "Make sure antivirus.py is in the same folder as app.py\n\n"
            "Error: " + AV_ERROR
        )
        root.destroy()
        sys.exit(1)

    app = App()
    app.mainloop()

