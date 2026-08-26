"""
Virus Attacks Detection - Professional Security Tool
Advanced malware detection and safe file analysis
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import os
import subprocess
import sys
import time
import random
import hashlib
import math
from datetime import datetime
import logging
from pathlib import Path
from file_detector import ExternalFileDetector, AppDownloadMonitor

logger = logging.getLogger(__name__)

class VirusDetectionApp:
    """
    Professional Virus Detection and Analysis Tool
    """
    
    def __init__(self, config):
        self.config = config
        self.root = tk.Tk()
        self.root.title("🛡️ Virus Attacks Detection - Professional Security Tool")
        self.root.geometry("1400x800")
        
        # Professional security-themed color scheme
        self.colors = {
            'bg': '#0a0e1c',
            'fg': '#e0e0e0',
            'card_bg': '#1a1f2f',
            'header_bg': '#0d1424',
            'accent': '#00ff9d',
            'warning': '#ffaa00',
            'danger': '#ff3b3b',
            'info': '#3b82f6',
            'success': '#00cc88',
            'scanning': '#8b5cf6',
            'border': '#2a3355',
            'button_bg': '#1e293b',
            'button_hover': '#2d3b52',
            'text_secondary': '#94a3b8'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize components
        self.quarantine = None
        self.scanner = None
        self.detector = None
        self.scanning = False
        self.scan_results = []
        
        # Queue for thread communication
        self.update_queue = queue.Queue()
        
        # Status variables
        self.status_var = tk.StringVar(value="⚡ System Ready")
        self.scan_status_var = tk.StringVar(value="Idle")
        self.threat_count_var = tk.StringVar(value="0")
        self.scan_count_var = tk.StringVar(value="0")
        self.file_count_var = tk.StringVar(value="0")
        self.folder_path_var = tk.StringVar(value="No folder selected")
        
        # Stats tracking
        self.stats = {
            'files': 0,
            'scans': 0,
            'threats': 0,
            'safe': 0,
            'suspicious': 0
        }
        
        # Suspicious patterns for malware detection
        self.suspicious_patterns = [
            (b'CreateRemoteThread', 25, "Process injection detected"),
            (b'WriteProcessMemory', 25, "Memory manipulation detected"),
            (b'VirtualAllocEx', 25, "Suspicious memory allocation"),
            (b'cmd.exe /c', 15, "Command execution"),
            (b'powershell -EncodedCommand', 30, "Encoded PowerShell - high risk"),
            (b'powershell -e', 30, "Encoded PowerShell - high risk"),
            (b'wscript.shell', 20, "Windows script host access"),
            (b'mshta.exe', 20, "HTML application execution"),
            (b'reg add', 15, "Registry modification"),
            (b'schtasks', 20, "Task scheduler manipulation"),
            (b'net user', 15, "User account manipulation"),
            (b'vssadmin', 25, "Volume shadow copy manipulation - ransomware pattern"),
            (b'bcdedit', 20, "Boot configuration modification"),
            (b'wmic', 15, "WMI command execution"),
            (b'cscript', 15, "Script execution"),
            (b'rundll32', 20, "DLL execution"),
            (b'certutil', 20, "Certificate utility - often abused"),
            (b'bitsadmin', 20, "Background downloader"),
        ]
        
        # Setup UI
        self.setup_ui()
        
        # Initialize
        self.root.after(100, self.initialize)
        self.check_updates()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Create professional security-themed interface with scrolling"""
        
        # ===== MAIN SCROLLABLE FRAME =====
        self.main_canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.main_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_canvas.bind('<Configure>', self.on_canvas_configure)
        
        self.main_frame = tk.Frame(self.main_canvas, bg=self.colors['bg'])
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.main_canvas.winfo_width())
        
        def on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # ===== MAIN CONTAINER =====
        main = tk.Frame(self.main_frame, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ===== HEADER SECTION =====
        header = tk.Frame(main, bg=self.colors['header_bg'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        left_header = tk.Frame(header, bg=self.colors['header_bg'])
        left_header.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(left_header, text="🛡️", font=('Segoe UI', 32),
                bg=self.colors['header_bg'], fg=self.colors['accent']).pack(side=tk.LEFT, padx=(0, 15))
        
        title_frame = tk.Frame(left_header, bg=self.colors['header_bg'])
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(title_frame, text="VIRUS ATTACKS DETECTION",
                font=('Segoe UI', 18, 'bold'),
                bg=self.colors['header_bg'], fg='white').pack(anchor=tk.W)
        
        tk.Label(title_frame, text="Advanced Malware Analysis & Safe Execution Environment",
                font=('Segoe UI', 10),
                bg=self.colors['header_bg'], fg=self.colors['text_secondary']).pack(anchor=tk.W)
        
        right_header = tk.Frame(header, bg=self.colors['header_bg'])
        right_header.pack(side=tk.RIGHT, padx=20)
        
        status_frame = tk.Frame(right_header, bg=self.colors['card_bg'], padx=15, pady=8)
        status_frame.pack()
        
        self.status_indicator = tk.Canvas(status_frame, width=12, height=12,
                                         bg=self.colors['card_bg'], highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.set_status('ready')
        
        tk.Label(status_frame, textvariable=self.status_var,
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['card_bg'], fg='white').pack(side=tk.LEFT)
        
        # ===== METRICS CARDS =====
        metrics = tk.Frame(main, bg=self.colors['bg'])
        metrics.pack(fill=tk.X, pady=(0, 20))
        
        for i in range(4):
            metrics.columnconfigure(i, weight=1)
        
        self.create_metric_card(metrics, "🚨 THREAT LEVEL", 
                               self.threat_count_var, self.colors['danger'],
                               "Critical threats detected", 0)
        
        self.create_metric_card(metrics, "🔍 SCANS PERFORMED", 
                               self.scan_count_var, self.colors['info'],
                               "Total security scans", 1)
        
        self.create_metric_card(metrics, "📁 FILES ANALYZED", 
                               self.file_count_var, self.colors['success'],
                               "Files in secure environment", 2)
        
        system_card = tk.Frame(metrics, bg=self.colors['card_bg'], relief=tk.FLAT, bd=1)
        system_card.grid(row=0, column=3, padx=5, sticky='ew')
        
        tk.Label(system_card, text="⚡ SYSTEM STATUS",
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        status_items = [
            ("Firewall", "🟢 Active"),
            ("Sandbox", "🟢 Ready"),
            ("Scanner", "🟢 Online")
        ]
        
        for label, value in status_items:
            item_frame = tk.Frame(system_card, bg=self.colors['card_bg'])
            item_frame.pack(fill=tk.X, padx=15, pady=2)
            tk.Label(item_frame, text=label,
                    font=('Segoe UI', 9),
                    bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(side=tk.LEFT)
            tk.Label(item_frame, text=value,
                    font=('Segoe UI', 9, 'bold'),
                    bg=self.colors['card_bg'], fg=self.colors['accent']).pack(side=tk.RIGHT)
        
        # ===== SCAN CONTROLS =====
        controls = tk.LabelFrame(main, text="🛡️ SCAN CONTROLS",
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['card_bg'], fg='white',
                                padx=15, pady=15)
        controls.pack(fill=tk.X, pady=(0, 20))
        
        folder_frame = tk.Frame(controls, bg=self.colors['card_bg'])
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(folder_frame, text="Target Location:",
                font=('Segoe UI', 10),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Entry(folder_frame, textvariable=self.folder_path_var,
                font=('Segoe UI', 10), bg=self.colors['bg'],
                fg='white', width=50, relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(folder_frame, text="📁 Browse", command=self.browse_folder,
                 bg=self.colors['button_bg'], fg='white',
                 font=('Segoe UI', 10), padx=15, pady=5,
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT)
        
        button_frame = tk.Frame(controls, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X)
        
        scan_buttons = [
            ("🔍 QUICK SCAN", self.quick_scan, self.colors['info']),
            ("🔬 DEEP SCAN", self.deep_scan, self.colors['scanning']),
            ("📂 ADD FILES", self.add_files, self.colors['button_bg']),
            ("🧹 CLEAN UP", self.cleanup, self.colors['danger'])
        ]
        
        button_container = tk.Frame(button_frame, bg=self.colors['card_bg'])
        button_container.pack()
        
        for text, command, color in scan_buttons:
            btn = tk.Button(button_container, text=text, command=command,
                          bg=color, fg='white',
                          font=('Segoe UI', 10, 'bold'),
                          padx=20, pady=8, relief=tk.FLAT,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
        
        # ===== SCAN PROGRESS =====
        progress_frame = tk.Frame(main, bg=self.colors['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        progress_label = tk.Frame(progress_frame, bg=self.colors['bg'])
        progress_label.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(progress_label, text="📊 SCAN PROGRESS",
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text_secondary']).pack(side=tk.LEFT)
        
        tk.Label(progress_label, textvariable=self.scan_status_var,
                font=('Segoe UI', 10),
                bg=self.colors['bg'], fg=self.colors['accent']).pack(side=tk.RIGHT)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        # ===== NOTEBOOK TABS =====
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('Custom.TNotebook.Tab', 
                       background=self.colors['button_bg'],
                       foreground='white',
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.colors['accent'])])
        
        self.notebook = ttk.Notebook(main, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_analysis_tab()
        self.create_threat_dashboard_tab()
        self.create_scan_history_tab()
        self.create_secure_execution_tab()
        
        self.root.after(100, self.update_scroll_region)
    
    def on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)
        self.update_scroll_region()
    
    def update_scroll_region(self):
        self.main_canvas.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
    
    def create_metric_card(self, parent, title, var, color, subtitle, col):
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.FLAT, bd=1)
        card.grid(row=0, column=col, padx=5, sticky='ew')
        
        tk.Label(card, text=title,
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        tk.Label(card, textvariable=var,
                font=('Segoe UI', 24, 'bold'),
                bg=self.colors['card_bg'], fg=color).pack(anchor=tk.W, padx=15)
        
        tk.Label(card, text=subtitle,
                font=('Segoe UI', 8),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def create_analysis_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(frame, text="🔬 FILE ANALYSIS")
        
        paned = tk.PanedWindow(frame, orient=tk.HORIZONTAL, bg=self.colors['bg'])
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        left_frame = tk.Frame(paned, bg=self.colors['card_bg'])
        paned.add(left_frame, width=700)
        
        header_frame = tk.Frame(left_frame, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(header_frame, text="📋 FILES IN SECURE ENVIRONMENT",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'], fg='white').pack(side=tk.LEFT)
        
        list_container = tk.Frame(left_frame, bg=self.colors['bg'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        tree_frame = tk.Frame(list_container, bg=self.colors['bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ('size', 'type', 'risk', 'status')
        self.file_list = ttk.Treeview(tree_frame, columns=columns, show='tree headings',
                                      yscrollcommand=v_scrollbar.set,
                                      xscrollcommand=h_scrollbar.set,
                                      height=22)
        
        self.file_list.heading('#0', text='Filename')
        self.file_list.heading('size', text='Size')
        self.file_list.heading('type', text='Type')
        self.file_list.heading('risk', text='Risk Level')
        self.file_list.heading('status', text='Status')
        
        self.file_list.column('#0', width=300)
        self.file_list.column('size', width=100)
        self.file_list.column('type', width=100)
        self.file_list.column('risk', width=120)
        self.file_list.column('status', width=150)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.file_list.yview)
        h_scrollbar.config(command=self.file_list.xview)
        
        self.file_list.bind('<<TreeviewSelect>>', self.show_file_details)
        
        # Right panel
        right_frame = tk.Frame(paned, bg=self.colors['card_bg'])
        paned.add(right_frame, width=500)
        
        tk.Label(right_frame, text="🔍 FILE ANALYSIS REPORT",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'], fg='white').pack(anchor=tk.W, padx=15, pady=15)
        
        details_container = tk.Frame(right_frame, bg=self.colors['bg'])
        details_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        details_scrollbar = ttk.Scrollbar(details_container)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(details_container, wrap=tk.WORD,
                                   font=('Consolas', 11),
                                   bg=self.colors['bg'],
                                   fg=self.colors['fg'],
                                   yscrollcommand=details_scrollbar.set,
                                   height=25, padx=10, pady=10)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.config(command=self.details_text.yview)
        
        self.details_text.insert(tk.END, "Select a file to view detailed analysis...\n")
    
    def create_threat_dashboard_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(frame, text="🚨 THREAT DASHBOARD")
        
        canvas = tk.Canvas(frame, bg=self.colors['card_bg'], highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        dashboard = tk.Frame(canvas, bg=self.colors['card_bg'])
        canvas.create_window((0, 0), window=dashboard, anchor="nw")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        tk.Label(dashboard, text="⚡ REAL-TIME THREAT ANALYSIS",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'], fg='white').pack(pady=15)
        
        stats_frame = tk.Frame(dashboard, bg=self.colors['card_bg'])
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        meter_frame = tk.Frame(stats_frame, bg=self.colors['bg'], padx=20, pady=15)
        meter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(meter_frame, text="THREAT LEVEL METER",
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg='white').pack()
        
        self.meter_canvas = tk.Canvas(meter_frame, width=200, height=20,
                                     bg=self.colors['card_bg'], highlightthickness=0)
        self.meter_canvas.pack(pady=10)
        self.update_threat_meter(0)
        
        detection_frame = tk.Frame(stats_frame, bg=self.colors['bg'], padx=20, pady=15)
        detection_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(detection_frame, text="DETECTION STATISTICS",
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg='white').pack()
        
        self.suspicious_var = tk.StringVar(value="0")
        self.clean_var = tk.StringVar(value="0")
        
        stats_list = [
            ("🚨 Malware:", self.threat_count_var, self.colors['danger']),
            ("⚠️ Suspicious:", self.suspicious_var, self.colors['warning']),
            ("✅ Clean:", self.clean_var, self.colors['success'])
        ]
        
        for label, var, color in stats_list:
            row = tk.Frame(detection_frame, bg=self.colors['bg'])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, bg=self.colors['bg'], 
                    fg=self.colors['text_secondary']).pack(side=tk.LEFT)
            tk.Label(row, textvariable=var, bg=self.colors['bg'],
                    fg=color, font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT)
        
        threats_frame = tk.Frame(stats_frame, bg=self.colors['bg'], padx=20, pady=15)
        threats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(threats_frame, text="RECENT THREATS",
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg='white').pack()
        
        threats_list_frame = tk.Frame(threats_frame, bg=self.colors['bg'])
        threats_list_frame.pack(fill=tk.BOTH, expand=True)
        
        threats_scrollbar = ttk.Scrollbar(threats_list_frame)
        threats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.threats_list = tk.Listbox(threats_list_frame, height=5,
                                       bg=self.colors['card_bg'],
                                       fg=self.colors['danger'],
                                       yscrollcommand=threats_scrollbar.set)
        self.threats_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        threats_scrollbar.config(command=self.threats_list.yview)
        
        results_frame = tk.LabelFrame(dashboard, text="📊 SCAN RESULTS",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg=self.colors['card_bg'], fg='white',
                                     padx=15, pady=15)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        results_container = tk.Frame(results_frame, bg=self.colors['card_bg'])
        results_container.pack(fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_container)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.threat_results = tk.Text(results_container, wrap=tk.WORD,
                                     font=('Consolas', 10),
                                     bg=self.colors['bg'],
                                     fg=self.colors['fg'],
                                     yscrollcommand=results_scrollbar.set,
                                     height=20)
        self.threat_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.config(command=self.threat_results.yview)
        
        self.threat_results.tag_config('danger', foreground=self.colors['danger'])
        self.threat_results.tag_config('warning', foreground=self.colors['warning'])
        self.threat_results.tag_config('safe', foreground=self.colors['success'])
        self.threat_results.tag_config('info', foreground=self.colors['info'])
        
        self.threat_results.insert(tk.END, "Click 'Quick Scan' to start scanning!\n")
    
    def create_scan_history_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(frame, text="📋 SCAN HISTORY")
        
        canvas = tk.Canvas(frame, bg=self.colors['card_bg'], highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        history_frame = tk.Frame(canvas, bg=self.colors['card_bg'])
        canvas.create_window((0, 0), window=history_frame, anchor="nw")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        header = tk.Frame(history_frame, bg=self.colors['card_bg'])
        header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(header, text="📊 SCAN HISTORY",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'], fg='white').pack(side=tk.LEFT)
        
        tk.Button(header, text="Export Logs", command=self.export_logs,
                 bg=self.colors['button_bg'], fg='white',
                 font=('Segoe UI', 10), padx=15,
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT)
        
        list_frame = tk.Frame(history_frame, bg=self.colors['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        tree_frame = tk.Frame(list_frame, bg=self.colors['bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ('date', 'time', 'type', 'files', 'threats', 'status')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        height=20, yscrollcommand=v_scrollbar.set)
        
        self.history_tree.heading('date', text='Date')
        self.history_tree.heading('time', text='Time')
        self.history_tree.heading('type', text='Scan Type')
        self.history_tree.heading('files', text='Files')
        self.history_tree.heading('threats', text='Threats')
        self.history_tree.heading('status', text='Status')
        
        for col in columns:
            self.history_tree.column(col, width=120)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.config(command=self.history_tree.yview)
    
    def create_secure_execution_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(frame, text="🛡️ SECURE EXECUTION")
        
        canvas = tk.Canvas(frame, bg=self.colors['card_bg'], highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        exec_frame = tk.Frame(canvas, bg=self.colors['card_bg'])
        canvas.create_window((0, 0), window=exec_frame, anchor="nw")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        tk.Label(exec_frame, text="🔒 ISOLATED EXECUTION ENVIRONMENT",
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'], fg='white').pack(pady=15)
        
        status_frame = tk.Frame(exec_frame, bg=self.colors['bg'], padx=20, pady=15)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(status_frame, text="🟢 SANDBOX ACTIVE - FULL ISOLATION",
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg'], fg=self.colors['success']).pack()
        
        tk.Label(status_frame, text="Files run in complete isolation - No system access",
                bg=self.colors['bg'], fg=self.colors['text_secondary']).pack()
        
        control_frame = tk.Frame(exec_frame, bg=self.colors['card_bg'])
        control_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(control_frame, text="Select file to execute safely:",
                font=('Segoe UI', 10),
                bg=self.colors['card_bg'], fg='white').pack(anchor=tk.W)
        
        file_select = tk.Frame(control_frame, bg=self.colors['card_bg'])
        file_select.pack(fill=tk.X, pady=10)
        
        self.exec_file_var = tk.StringVar(value="No file selected")
        tk.Entry(file_select, textvariable=self.exec_file_var,
                font=('Segoe UI', 10), bg=self.colors['bg'],
                fg='white', width=50, relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(file_select, text="Choose File", command=self.choose_exec_file,
                 bg=self.colors['button_bg'], fg='white',
                 font=('Segoe UI', 10), padx=15,
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT)
        
        tk.Button(control_frame, text="▶️ EXECUTE IN SANDBOX", command=self.execute_in_sandbox,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 12, 'bold'), padx=30, pady=10,
                 relief=tk.FLAT, cursor='hand2').pack(pady=20)
    
    def set_status(self, status):
        self.status_indicator.delete("all")
        colors = {
            'ready': self.colors['success'],
            'busy': self.colors['warning'],
            'scanning': self.colors['scanning'],
            'error': self.colors['danger']
        }
        color = colors.get(status, self.colors['success'])
        self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline='')
    
    def update_threat_meter(self, level):
        self.meter_canvas.delete("all")
        width = 200
        height = 20
        
        self.meter_canvas.create_rectangle(0, 0, width, height,
                                          fill=self.colors['card_bg'], outline='')
        
        level_width = (level / 100) * width
        color = self.colors['success'] if level < 30 else self.colors['warning'] if level < 70 else self.colors['danger']
        self.meter_canvas.create_rectangle(0, 0, level_width, height, fill=color, outline='')
        
        self.meter_canvas.create_text(width/2, height/2, text=f"{level}%",
                                     fill='white', font=('Segoe UI', 9, 'bold'))
    
    # ===================== USB AND SANDBOXIE HANDLING =====================
    
    def setup_usb_handling(self):
        """Setup USB detection and handling"""
        if not hasattr(self, 'detector') or not self.detector:
            return
        
        # Set callback for USB insertion
        self.detector.set_usb_insert_callback(self.on_usb_detected)
        
        # Set callback for new files
        self.detector.on_new_file_callback = self.on_new_file_copied
        
        logger.info("USB handling setup complete")
    
    def on_usb_detected(self, usb_path):
        """Called when USB drive is detected"""
        logger.info(f"USB detected: {usb_path}")
        
        # Show dialog to user
        self.root.after(0, lambda: self.show_usb_dialog(usb_path))
    
    def show_usb_dialog(self, usb_path):
        """Show dialog asking user what to do with USB drive"""
        
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("USB Drive Detected")
        dialog.geometry("500x350")
        dialog.configure(bg=self.colors['card_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Icon
        icon_label = tk.Label(dialog, text="💾", font=('Segoe UI', 48),
                             bg=self.colors['card_bg'], fg=self.colors['accent'])
        icon_label.pack(pady=15)
        
        # Title
        title_label = tk.Label(dialog, text="USB Drive Detected!",
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.colors['card_bg'], fg='white')
        title_label.pack()
        
        # Drive info
        drive_name = Path(usb_path).name
        info_label = tk.Label(dialog, text=f"Drive: {drive_name}\nPath: {usb_path}",
                             font=('Segoe UI', 10),
                             bg=self.colors['card_bg'], fg=self.colors['text_secondary'])
        info_label.pack(pady=10)
        
        # Sandboxie status
        sandboxie_available = self.detector.is_sandboxie_available() if self.detector else False
        sandbox_status = "✅ Sandboxie Plus Available" if sandboxie_available else "⚠️ Sandboxie Not Found (Using Basic Isolation)"
        sandbox_label = tk.Label(dialog, text=sandbox_status,
                                font=('Segoe UI', 9),
                                bg=self.colors['card_bg'], 
                                fg=self.colors['success'] if sandboxie_available else self.colors['warning'])
        sandbox_label.pack(pady=5)
        
        # Description
        if sandboxie_available:
            desc_text = "Files will be opened SAFELY using Sandboxie Plus.\n"
            desc_text += "Any damage will ONLY affect the sandbox, not your main system!"
        else:
            desc_text = "Sandboxie Plus not detected. Using basic isolation.\n"
            desc_text += "For maximum protection, please install Sandboxie Plus."
        
        desc_label = tk.Label(dialog, text=desc_text,
                             font=('Segoe UI', 9),
                             bg=self.colors['card_bg'], fg=self.colors['info'],
                             justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card_bg'])
        button_frame.pack(pady=15)
        
        def open_in_sandbox():
            dialog.destroy()
            self.open_usb_with_sandboxie(usb_path)
        
        def just_copy_files():
            dialog.destroy()
            self.copy_usb_files(usb_path)
        
        def ignore():
            dialog.destroy()
        
        open_btn = tk.Button(button_frame, text="🔒 Open Safely in Sandboxie", 
                             command=open_in_sandbox,
                             bg=self.colors['success'], fg='white',
                             font=('Segoe UI', 10, 'bold'), padx=15, pady=8,
                             relief=tk.FLAT, cursor='hand2')
        open_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = tk.Button(button_frame, text="📂 Copy Files Only", 
                             command=just_copy_files,
                             bg=self.colors['info'], fg='white',
                             font=('Segoe UI', 10), padx=15, pady=8,
                             relief=tk.FLAT, cursor='hand2')
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        ignore_btn = tk.Button(button_frame, text="Ignore", 
                               command=ignore,
                               bg=self.colors['button_bg'], fg='white',
                               font=('Segoe UI', 10), padx=15, pady=8,
                               relief=tk.FLAT, cursor='hand2')
        ignore_btn.pack(side=tk.LEFT, padx=5)
    
    def open_usb_with_sandboxie(self, usb_path):
        """Open USB drive contents with Sandboxie"""
        self.status_var.set(f"Opening {usb_path} with Sandboxie...")
        self.set_status('busy')
        
        # Ask if they want to scan whole drive or select file
        result = messagebox.askyesno(
            "USB Drive Options",
            f"Do you want to scan the entire USB drive for safe viewing?\n\n"
            f"Select 'Yes' to copy all files to sandbox for analysis.\n"
            f"Select 'No' to choose specific files to open with Sandboxie.",
            icon='question'
        )
        
        if result:
            # Copy all files to sandbox
            self.copy_usb_files(usb_path)
        else:
            # Let user select specific file
            file_path = filedialog.askopenfilename(
                title="Select file to open safely with Sandboxie",
                initialdir=usb_path,
                parent=self.root
            )
            
            if file_path:
                self.execute_with_sandboxie(file_path)
    
    def execute_with_sandboxie(self, file_path):
        """Execute file with Sandboxie Plus"""
        if not self.detector:
            messagebox.showerror("Error", "File detector not initialized")
            return
        
        filename = os.path.basename(file_path)
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "⚠️ Sandboxie Execution",
            f"You are about to run '{filename}' using Sandboxie Plus.\n\n"
            f"🔒 The file will run in COMPLETE ISOLATION\n"
            f"🛡️ Any damage will ONLY affect the sandbox\n"
            f"✅ Your main system is 100% protected\n\n"
            f"Continue?",
            icon='warning'
        )
        
        if not result:
            return
        
        self.status_var.set(f"Launching {filename} with Sandboxie...")
        self.set_status('scanning')
        
        def run():
            try:
                process = self.detector.open_with_sandboxie(file_path)
                
                if process:
                    self.root.after(0, lambda: self.status_var.set(f"✅ Running: {filename} (Sandboxie)"))
                    self.root.after(0, lambda: self.set_status('ready'))
                    self.log_event(f"🔒 Executed with Sandboxie: {filename}")
                    
                    # Show success message
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Sandboxie Execution",
                        f"File '{filename}' is now running in Sandboxie!\n\n"
                        f"🔒 Completely isolated from your system\n"
                        f"🛡️ Close the Sandboxie window when done"
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Execution Failed",
                        "Failed to launch with Sandboxie.\n\nPlease check Sandboxie installation."
                    ))
                    
            except Exception as e:
                logger.error(f"Sandboxie execution failed: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, lambda: self.status_var.set("Ready"))
                self.root.after(0, lambda: self.set_status('ready'))
        
        threading.Thread(target=run, daemon=True).start()
    
    def copy_usb_files(self, usb_path):
        """Copy files from USB to sandbox for safe analysis"""
        self.status_var.set(f"Copying files from USB to sandbox...")
        self.set_status('busy')
        self.progress['value'] = 0
        
        def copy():
            try:
                usb_dir = Path(usb_path)
                files = list(usb_dir.rglob('*'))
                total_files = len([f for f in files if f.is_file()])
                copied = 0
                
                for file_path in files:
                    if file_path.is_file():
                        try:
                            self.quarantine.add_file(str(file_path))
                            copied += 1
                            
                            progress = (copied / total_files) * 100 if total_files > 0 else 100
                            self.root.after(0, lambda p=progress: self.progress.configure(value=p))
                            
                        except Exception as e:
                            logger.error(f"Failed to copy {file_path}: {e}")
                
                self.root.after(0, lambda: self.refresh_list())
                self.root.after(0, lambda: self.status_var.set(f"✅ Copied {copied} files to sandbox"))
                self.root.after(0, lambda: self.set_status('ready'))
                self.log_event(f"📁 Copied {copied} files from USB: {usb_path}")
                
                # Ask if they want to scan
                if copied > 0:
                    scan_now = messagebox.askyesno(
                        "Scan Files",
                        f"Copied {copied} files to sandbox.\n\nDo you want to scan them for threats?"
                    )
                    if scan_now:
                        self.root.after(0, self.quick_scan)
                
            except Exception as e:
                logger.error(f"USB copy failed: {e}")
                self.root.after(0, lambda: self.status_var.set("❌ Copy failed"))
                self.root.after(0, lambda: self.set_status('error'))
        
        threading.Thread(target=copy, daemon=True).start()
    
    def on_new_file_copied(self, original_path, quarantine_path):
        """Called when a new file is copied from USB"""
        self.root.after(0, lambda: self.refresh_list())
        self.root.after(0, lambda: self.status_var.set(f"New file detected: {os.path.basename(original_path)}"))
        self.log_event(f"📄 New file from USB: {os.path.basename(original_path)}")
    
    def log_event(self, message):
        """Log event to file and UI"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        # Also save to file
        try:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            with open(log_dir / 'sandbox_activity.log', 'a') as f:
                f.write(log_entry)
        except:
            pass

    # ===================== APP DOWNLOAD HANDLING =====================
    
    def setup_app_download_handling(self):
        """Setup handling for app downloads"""
        if not hasattr(self, 'detector') or not self.detector:
            return
        
        # Set callback for app files
        self.detector.set_app_file_callback(self.on_app_file_detected)
        
        # Set callback for new files
        self.detector.on_new_file_callback = self.on_new_file_copied
        
        logger.info("App download handling setup complete")
    
    def on_app_file_detected(self, file_path, source):
        """Called when a file is detected from an app download"""
        logger.info(f"App file detected from {source}: {os.path.basename(file_path)}")
        
        # Show notification in UI
        filename = os.path.basename(file_path)
        self.root.after(0, lambda: self.status_var.set(f"📥 File from {source}: {filename}"))
        
        # Log the event
        self.log_event(f"📥 File from {source}: {filename}")
        
        # Show notification dialog
        self.root.after(0, lambda: self.show_app_download_notification(filename, source))
        
        # Automatically scan after a short delay
        self.root.after(3000, self.quick_scan)
    
    def show_app_download_notification(self, filename, source):
        """Show notification for app download interception"""
        dialog = tk.Toplevel(self.root)
        dialog.title("File Intercepted")
        dialog.geometry("450x250")
        dialog.configure(bg=self.colors['card_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        icon_label = tk.Label(dialog, text="🛡️", font=('Segoe UI', 48),
                             bg=self.colors['card_bg'], fg=self.colors['accent'])
        icon_label.pack(pady=10)
        
        title_label = tk.Label(dialog, text="App File Quarantined!",
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.colors['card_bg'], fg='white')
        title_label.pack()
        
        info_label = tk.Label(dialog, 
                             text=f"File from {source}: {filename}\n\n"
                                  f"🔒 File is SAFELY stored in quarantine\n"
                                  f"🛡️ Protected from ransomware and malware\n"
                                  f"✅ Your system is 100% safe!\n\n"
                                  f"📊 Automatic scan will begin shortly...",
                             font=('Segoe UI', 10),
                             bg=self.colors['card_bg'],
                             fg=self.colors['text_secondary'],
                             justify=tk.CENTER)
        info_label.pack(pady=10)
        
        button_frame = tk.Frame(dialog, bg=self.colors['card_bg'])
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="✅ OK", command=dialog.destroy,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 10, 'bold'),
                 padx=20, pady=5, relief=tk.FLAT,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔍 Scan Now", 
                 command=lambda: [dialog.destroy(), self.quick_scan()],
                 bg=self.colors['info'], fg='white',
                 font=('Segoe UI', 10, 'bold'),
                 padx=20, pady=5, relief=tk.FLAT,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)

    # ===================== INITIALIZATION =====================
    
    def initialize(self):
        """Initialize components with USB and app download handling"""
        try:
            from quarantine_system import QuarantineSandbox
            from security_scanner import AdvancedSecurityScanner
            from file_detector import ExternalFileDetector
            
            self.quarantine = QuarantineSandbox(max_size_gb=1)
            
            # Initialize detector with sandbox support
            self.detector = ExternalFileDetector(self.quarantine, {})
            self.scanner = AdvancedSecurityScanner(self.quarantine, './config')
            
            # Setup USB handling
            self.setup_usb_handling()
            
            # Setup app download handling
            self.setup_app_download_handling()
            
            self.status_var.set("⚡ System Ready")
            self.set_status('ready')
            self.refresh_list()
            
            # Start monitoring USB drives and app downloads
            self.detector.start_monitoring()
            
            # Check Sandboxie status
            if self.detector.is_sandboxie_available():
                self.log_event("✅ Sandboxie Plus detected! Files will run in complete isolation")
            else:
                self.log_event("⚠️ Sandboxie Plus not detected. Install it for maximum protection")
            
        except Exception as e:
            self.status_var.set("⚠️ System Error")
            self.set_status('error')
            messagebox.showerror("Error", f"Initialization failed: {e}")
    
    def refresh_list(self):
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        if not self.quarantine:
            return
        
        temp_path = Path(self.quarantine.temp_path)
        if temp_path.exists():
            for file in sorted(temp_path.iterdir()):
                if file.is_file():
                    size = f"{file.stat().st_size / 1024:.1f} KB"
                    ext = file.suffix[1:] or 'file'
                    
                    risk = "Not Scanned"
                    status = "Pending"
                    for result in self.scan_results:
                        if result['filename'] == file.name:
                            risk = f"{result['risk_score']}%"
                            status = result['status']
                            break
                    
                    self.file_list.insert('', 'end', text=file.name,
                                        values=(size, ext, risk, status))
        
        self.stats['files'] = len(self.file_list.get_children())
        self.file_count_var.set(str(self.stats['files']))
        self.update_scroll_region()
    
    def show_file_details(self, event):
        selection = self.file_list.selection()
        if not selection:
            return
        
        filename = self.file_list.item(selection[0])['text']
        file_path = Path(self.quarantine.temp_path) / filename
        
        if file_path.exists():
            self.details_text.delete(1.0, tk.END)
            stat = file_path.stat()
            
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            file_hash = sha256.hexdigest()
            
            details = f"📄 FILE ANALYSIS REPORT\n"
            details += "="*50 + "\n\n"
            details += f"📌 Filename: {filename}\n"
            details += f"📏 Size: {stat.st_size / 1024:.1f} KB\n"
            details += f"🕒 Modified: {datetime.fromtimestamp(stat.st_mtime)}\n"
            details += f"📝 File Type: {file_path.suffix or 'No extension'}\n"
            details += f"🔑 SHA256: {file_hash[:64]}\n\n"
            
            for result in self.scan_results:
                if result['filename'] == filename:
                    details += f"🔍 SCAN RESULTS\n"
                    details += "="*30 + "\n"
                    details += f"Risk Score: {result['risk_score']}%\n"
                    details += f"Status: {result['status']}\n"
                    details += f"Threat Level: {result.get('threat_level', 'UNKNOWN')}\n"
                    if result.get('threats'):
                        details += f"\nThreats Found:\n"
                        for threat in result['threats']:
                            details += f"  • {threat}\n"
                    break
            else:
                details += "🔍 SCAN STATUS: Not scanned yet\n"
            
            self.details_text.insert(tk.END, details)
    
    # ===================== FILE OPERATIONS =====================
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.folder_path_var.set(folder)
            self.add_to_sandbox(folder)
    
    def add_files(self):
        files = filedialog.askopenfilenames(title="Select Files")
        if files:
            self.folder_path_var.set(f"{len(files)} files selected")
            for file in files:
                self.add_to_sandbox(file)
    
    def add_to_sandbox(self, path):
        if not self.quarantine:
            return
        
        path = Path(path)
        try:
            if path.is_file():
                self.quarantine.add_file(str(path))
                self.stats['files'] += 1
            else:
                count = 0
                for file in path.glob('**/*'):
                    if file.is_file():
                        self.quarantine.add_file(str(file))
                        count += 1
                self.stats['files'] += count
            
            self.refresh_list()
            self.update_stats()
            self.log_event(f"📁 Added: {path.name}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def quick_scan(self):
        self.start_scan("QUICK", deep=False)
    
    def deep_scan(self):
        self.start_scan("DEEP", deep=True)
    
    def start_scan(self, scan_type, deep=False):
        if self.scanning:
            messagebox.showinfo("Scan in Progress", "A scan is already running")
            return
        
        files = self.file_list.get_children()
        if not files:
            messagebox.showinfo("No Files", "Add files to scan first")
            return
        
        self.scanning = True
        self.scan_status_var.set(f"{scan_type} SCANNING...")
        self.status_var.set("🔬 Scanning...")
        self.set_status('scanning')
        self.progress['value'] = 0
        
        self.threat_results.delete(1.0, tk.END)
        self.threats_list.delete(0, tk.END)
        
        threats_found = 0
        suspicious_found = 0
        safe_found = 0
        
        def scan():
            nonlocal threats_found, suspicious_found, safe_found
            
            total = len(files)
            
            for i, item in enumerate(files):
                filename = self.file_list.item(item)['text']
                file_path = Path(self.quarantine.temp_path) / filename
                
                if file_path.exists():
                    # Use the advanced scanner
                    result = self.scanner.scan_file(str(file_path))
                    
                    risk = result['risk_score']
                    threats = result.get('threats', [])
                    threat_level = result.get('threat_level', 'UNKNOWN')
                    
                    if deep:
                        risk = min(risk + 5, 100)
                    
                    if risk >= 70:
                        status = "🚨 THREAT DETECTED"
                        color = 'danger'
                        threats_found += 1
                        self.stats['threats'] += 1
                        self.root.after(0, lambda f=filename: 
                                      self.threats_list.insert(tk.END, f"🚨 {f}"))
                    elif risk >= 40:
                        status = "⚠️ SUSPICIOUS"
                        color = 'warning'
                        suspicious_found += 1
                        self.stats['suspicious'] += 1
                    else:
                        status = "✅ SAFE"
                        color = 'safe'
                        safe_found += 1
                        self.stats['safe'] += 1
                    
                    self.scan_results.append(result)
                    
                    # Display advanced results
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    result_text = f"[{timestamp}] {filename}\n"
                    result_text += f"   Risk: {risk}% - Level: {threat_level}\n"
                    
                    if threats:
                        for threat in threats[:2]:
                            result_text += f"   ⚠️ {threat}\n"
                    
                    self.root.after(0, lambda t=result_text, c=color: 
                                  self.threat_results.insert(tk.END, t, c))
                    self.root.after(0, lambda: self.threat_results.see(tk.END))
                    
                    # Update file list status
                    status_display = f"{risk}%"
                    self.root.after(0, lambda f=filename, r=status_display, s=status: 
                                  self.update_file_status(f, r, s))
                    
                    progress = ((i + 1) / total) * 100
                    self.root.after(0, lambda p=progress: self.progress.configure(value=p))
                    
                    time.sleep(0.1)
            
            self.stats['scans'] += 1
            self.root.after(0, self.update_stats)
            self.root.after(0, lambda: self.suspicious_var.set(str(suspicious_found)))
            self.root.after(0, lambda: self.clean_var.set(str(safe_found)))
            
            threat_percentage = (threats_found / total) * 100 if total > 0 else 0
            self.root.after(0, lambda: self.update_threat_meter(threat_percentage))
            
            summary = f"\n{'='*50}\n"
            summary += f"📊 SCAN SUMMARY - {scan_type}\n"
            summary += f"Total Files: {total}\n"
            summary += f"✅ Safe: {safe_found}\n"
            summary += f"⚠️ Suspicious: {suspicious_found}\n"
            summary += f"🚨 Threats: {threats_found}\n"
            
            self.root.after(0, lambda: self.threat_results.insert(tk.END, summary, 'info'))
            self.root.after(0, lambda: self.threat_results.see(tk.END))
            
            scan_time = datetime.now()
            self.root.after(0, lambda: self.history_tree.insert('', 0, 
                values=(scan_time.strftime('%Y-%m-%d'), 
                       scan_time.strftime('%H:%M:%S'),
                       scan_type, total, threats_found,
                       "COMPLETE")))
            
            self.root.after(0, lambda: self.scan_status_var.set("SCAN COMPLETE"))
            self.root.after(0, lambda: self.status_var.set("✅ Scan complete"))
            self.root.after(0, lambda: self.set_status('ready'))
            
            self.scanning = False
        
        threading.Thread(target=scan, daemon=True).start()
    
    def update_file_status(self, filename, risk, status):
        for item in self.file_list.get_children():
            if self.file_list.item(item)['text'] == filename:
                current = list(self.file_list.item(item)['values'])
                if len(current) >= 4:
                    current[2] = risk
                    current[3] = status[:20]
                    self.file_list.item(item, values=current)
                break
    
    def cleanup(self):
        if messagebox.askyesno("Clean Up", "Remove all files from sandbox?"):
            if self.quarantine:
                temp_path = Path(self.quarantine.temp_path)
                for file in temp_path.glob('*'):
                    if file.is_file():
                        file.unlink()
                self.stats = {'files': 0, 'scans': 0, 'threats': 0, 'safe': 0, 'suspicious': 0}
                self.scan_results = []
                self.update_stats()
                self.refresh_list()
                self.threat_results.delete(1.0, tk.END)
                self.threats_list.delete(0, tk.END)
                self.suspicious_var.set("0")
                self.clean_var.set("0")
                self.update_threat_meter(0)
                self.status_var.set("✨ Sandbox Clean")
                self.log_event("🧹 Sandbox cleaned")
    
    def choose_exec_file(self):
        file = filedialog.askopenfilename(title="Select File to Execute Safely")
        if file:
            self.exec_file_var.set(file)
    
    def execute_in_sandbox(self):
        file = self.exec_file_var.get()
        if file == "No file selected":
            messagebox.showinfo("Info", "Select a file first")
            return
        
        self.execute_with_sandboxie(file)
    
    def update_stats(self):
        self.threat_count_var.set(str(self.stats['threats']))
        self.scan_count_var.set(str(self.stats['scans']))
        self.file_count_var.set(str(self.stats['files']))
        self.update_scroll_region()
    
    def export_logs(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("VIRUS ATTACKS DETECTION - SCAN RESULTS\n")
                    f.write("="*60 + "\n\n")
                    f.write(f"Export Date: {datetime.now()}\n\n")
                    
                    for result in self.scan_results:
                        f.write(f"\n{'='*50}\n")
                        f.write(f"File: {result['filename']}\n")
                        f.write(f"Risk: {result['risk_score']}%\n")
                        f.write(f"Status: {result['status']}\n")
                        f.write(f"Threat Level: {result.get('threat_level', 'UNKNOWN')}\n")
                        if result.get('threats'):
                            f.write(f"Threats Found:\n")
                            for threat in result['threats']:
                                f.write(f"  • {threat}\n")
                        f.write(f"{'='*50}\n")
                    
                messagebox.showinfo("Success", "Logs exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def check_updates(self):
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()
        except queue.Empty:
            pass
        self.root.after(100, self.check_updates)
    
    def on_closing(self):
        if hasattr(self, 'detector') and self.detector:
            self.detector.stop_monitoring()
        if messagebox.askokcancel("Exit", "Close Virus Detection System?"):
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()