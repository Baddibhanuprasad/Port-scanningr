import tkinter as tk
from tkinter import ttk


class GuardianDashboard(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Guardian AV Dashboard")
        self.geometry("860x560")
        self.minsize(820, 520)
        self.configure(bg="#0f172a")

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#111827", padx=20, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        title = tk.Label(header, text="Guardian AV", fg="#f8fafc", bg="#111827", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(header, text="Defensive file isolation and monitoring", fg="#94a3b8", bg="#111827", font=("Segoe UI", 10))
        subtitle.grid(row=1, column=0, sticky="w")

        status_badge = tk.Label(header, text="Service: Active", fg="#dcfce7", bg="#166534", padx=10, pady=4, font=("Segoe UI", 10, "bold"))
        status_badge.grid(row=0, column=1, sticky="e", rowspan=2)

        content = tk.Frame(self, bg="#0f172a")
        content.grid(row=1, column=0, sticky="nsew", padx=16, pady=14)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        summary = tk.Frame(content, bg="#111827", padx=16, pady=12)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        summary.columnconfigure(0, weight=1)
        summary.columnconfigure(1, weight=1)
        summary.columnconfigure(2, weight=1)

        cards = [
            ("Pending", "3", "#38bdf8"),
            ("Held", "2", "#f59e0b"),
            ("Released", "12", "#22c55e"),
        ]
        for index, (label, value, color) in enumerate(cards):
            card = tk.Frame(summary, bg="#1f2937", padx=14, pady=12)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < 2 else (0, 0))
            tk.Label(card, text=label, fg="#cbd5e1", bg="#1f2937", font=("Segoe UI", 10)).pack(anchor="w")
            tk.Label(card, text=value, fg=color, bg="#1f2937", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(6, 0))

        notebook = ttk.Notebook(content)
        notebook.grid(row=1, column=0, sticky="nsew")

        inbox_frame = tk.Frame(notebook, bg="#111827", padx=12, pady=12)
        alerts_frame = tk.Frame(notebook, bg="#111827", padx=12, pady=12)
        settings_frame = tk.Frame(notebook, bg="#111827", padx=12, pady=12)

        notebook.add(inbox_frame, text="Sandbox Inbox")
        notebook.add(alerts_frame, text="Alerts")
        notebook.add(settings_frame, text="Settings")

        tk.Label(inbox_frame, text="Pending files", fg="#f8fafc", bg="#111827", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        items = [
            ("setup.exe", "Executable", "2h 14m left"),
            ("invoice.pdf", "Fast", "Scan complete"),
        ]
        for name, tier, status in items:
            row = tk.Frame(inbox_frame, bg="#1f2937", padx=10, pady=8)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=name, fg="#f8fafc", bg="#1f2937", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(row, text=f"{tier} • {status}", fg="#94a3b8", bg="#1f2937", font=("Segoe UI", 9)).pack(anchor="w")

        tk.Label(alerts_frame, text="Recent alerts", fg="#f8fafc", bg="#111827", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        alerts = [
            "Executable held for behavioral observation",
            "Archive unpacking requested",
            "Static scan completed for PDF",
        ]
        for message in alerts:
            tk.Label(alerts_frame, text="• " + message, fg="#cbd5e1", bg="#111827", anchor="w", justify="left", padx=4, pady=3).pack(anchor="w")

        tk.Label(settings_frame, text="Policy controls", fg="#f8fafc", bg="#111827", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(settings_frame, text="• Hold executable files for 48h by default\n• Allow early release for trusted signatures\n• Route sandbox traffic through a local proxy", fg="#cbd5e1", bg="#111827", justify="left", anchor="w").pack(anchor="w", pady=8)


def main() -> None:
    app = GuardianDashboard()
    app.mainloop()


if __name__ == "__main__":
    main()
