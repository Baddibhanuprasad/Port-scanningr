import os
import ctypes
import tkinter as tk
from PIL import Image, ImageTk
import time
import sys
import tempfile
import winreg

# --- CONFIGURATION ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
LOCKED_EXTENSION = ".locked"

# Find images in different locations
def find_image(filename):
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.path.dirname(sys.executable), filename),
        os.path.join(os.path.dirname(sys.argv[0]), filename),
        os.path.join(tempfile.gettempdir(), filename),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Find both images
BG_IMAGE_PATH = find_image("bg.jpg")
LOCK_IMAGE_PATH = find_image("in.jpg")
PASSWORD = "vasavi143"

# Window Size
IMG_WIDTH = 600
IMG_HEIGHT = 650

# Global variable to store original wallpaper path
ORIGINAL_WALLPAPER = None

def get_current_wallpaper():
    """Get the current wallpaper path from Windows registry"""
    try:
        # Open the registry key for desktop wallpaper
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                             r"Control Panel\Desktop", 
                             0, 
                             winreg.KEY_READ)
        
        # Get the wallpaper path
        wallpaper_path, _ = winreg.QueryValueEx(key, "WallPaper")
        winreg.CloseKey(key)
        
        # Check if wallpaper is a specific file or system default
        if wallpaper_path and os.path.exists(wallpaper_path):
            return wallpaper_path
        else:
            # If registry doesn't have a specific wallpaper, get from SystemParametersInfo
            return get_wallpaper_from_system()
    except Exception as e:
        print(f"Error getting wallpaper: {e}")
        return get_wallpaper_from_system()

def get_wallpaper_from_system():
    """Get wallpaper using Windows API"""
    try:
        # Get wallpaper using SystemParametersInfo
        import ctypes.wintypes
        
        # Get wallpaper path
        buffer = ctypes.create_unicode_buffer(260)  # MAX_PATH
        ctypes.windll.user32.SystemParametersInfoW(0x0073, 260, buffer, 0)  # SPI_GETDESKWALLPAPER
        wallpaper_path = buffer.value
        
        if wallpaper_path and os.path.exists(wallpaper_path):
            return wallpaper_path
    except:
        pass
    
    return None

def set_wallpaper(image_path):
    """Set the desktop wallpaper"""
    try:
        # Convert to absolute path if needed
        if not os.path.isabs(image_path):
            image_path = os.path.abspath(image_path)
        
        # Using Windows API to set wallpaper
        SPI_SETDESKWALLPAPER = 0x0014
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDWININICHANGE = 0x02
        
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            image_path,
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        )
        return True
    except Exception as e:
        print(f"Wallpaper error: {e}")
        return False

def save_original_wallpaper():
    """Save the current wallpaper path before changing it"""
    global ORIGINAL_WALLPAPER
    
    # Get current wallpaper
    current_wallpaper = get_current_wallpaper()
    
    if current_wallpaper and os.path.exists(current_wallpaper):
        ORIGINAL_WALLPAPER = current_wallpaper
        print(f"Original wallpaper saved: {ORIGINAL_WALLPAPER}")
    else:
        # If we can't get the current wallpaper, use a Windows default
        ORIGINAL_WALLPAPER = None
        print("Could not get original wallpaper path")

def restore_original_wallpaper():
    """Restore the original wallpaper"""
    global ORIGINAL_WALLPAPER
    
    if ORIGINAL_WALLPAPER and os.path.exists(ORIGINAL_WALLPAPER):
        print(f"Restoring original wallpaper: {ORIGINAL_WALLPAPER}")
        set_wallpaper(ORIGINAL_WALLPAPER)
    else:
        # If we don't have the original, try to use Windows default
        print("Original wallpaper not found, using Windows default")
        # Windows 11/10 default wallpaper paths
        default_wallpapers = [
            r"C:\Windows\Web\Wallpaper\Windows\img0.jpg",  # Windows 10/11 default
            r"C:\Windows\Web\Wallpaper\Windows\img0_256x256.jpg",
            r"C:\Windows\Web\Wallpaper\Windows\img0_1024x768.jpg",
        ]
        
        for wall in default_wallpapers:
            if os.path.exists(wall):
                set_wallpaper(wall)
                break

def toggle_desktop_files(lock=True):
    """Lock or unlock desktop items"""
    count = 0
    
    for item in os.listdir(DESKTOP_PATH):
        # Skip system files and the lock file itself
        if item.startswith('.'):
            continue
            
        item_path = os.path.join(DESKTOP_PATH, item)
        
        try:
            if lock and not item.endswith(LOCKED_EXTENSION):
                # Lock
                new_path = item_path + LOCKED_EXTENSION
                if os.path.exists(new_path):
                    if os.path.isfile(new_path):
                        os.remove(new_path)
                    else:
                        import shutil
                        shutil.rmtree(new_path)
                os.rename(item_path, new_path)
                count += 1
                
            elif not lock and item.endswith(LOCKED_EXTENSION):
                # Unlock
                original_path = item_path.replace(LOCKED_EXTENSION, "")
                if os.path.exists(original_path):
                    if os.path.isfile(original_path):
                        os.remove(original_path)
                    else:
                        import shutil
                        shutil.rmtree(original_path)
                os.rename(item_path, original_path)
                count += 1
        except:
            pass
    
    # Refresh desktop
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except:
        pass
    
    return count

class LockScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Capcut Pro - System Lock")
        self.root.attributes("-topmost", True)
        self.root.configure(bg='black')
        
        # Try to set icon for the window
        try:
            icon_path = os.path.join(os.path.dirname(sys.executable), "capcut_pro.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Center window
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw // 2) - (IMG_WIDTH // 2)
        y = (sh // 2) - (IMG_HEIGHT // 2)
        self.root.geometry(f"{IMG_WIDTH}x{IMG_HEIGHT}+{x}+{y}")
        
        # Dragging
        self._offsetx = 0
        self._offsety = 0
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)
        
        # PREVENT ALL CLOSING METHODS
        self.root.bind('<Control-w>', self.prevent_close)
        self.root.bind('<Control-q>', self.prevent_close)
        self.root.bind('<Control-W>', self.prevent_close)
        self.root.bind('<Control-Q>', self.prevent_close)
        self.root.bind('<Escape>', self.prevent_close)
        self.root.bind('<Alt-space>', self.prevent_close)
        
        # Override the window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
        
        # Disable the system menu
        self.disable_system_menu()
        
        self.setup_ui()
        
        # Save original wallpaper and set new one
        save_original_wallpaper()
        if LOCK_IMAGE_PATH and os.path.exists(LOCK_IMAGE_PATH):
            set_wallpaper(LOCK_IMAGE_PATH)

    def disable_system_menu(self):
        """Disable the system menu completely"""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.SetWindowLongW(hwnd, -16, 0x96000000)
        except:
            pass

    def prevent_close(self, event=None):
        """Prevent any closing action"""
        return "break"

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._offsetx
        y = self.root.winfo_y() + event.y - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Main frame
        main = tk.Frame(self.root, bg='black')
        main.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Branding
        brand_frame = tk.Frame(main, bg='black')
        brand_frame.pack(pady=(0, 10))
        
        tk.Label(brand_frame, text="Capcut Pro", fg="#FF0000", bg="black",
                font=("Arial", 28, "bold")).pack()
        tk.Label(brand_frame, text="Security Edition", fg="white", bg="black",
                font=("Arial", 10)).pack()
        
        # Try to load bg.jpg for the lock screen
        if BG_IMAGE_PATH and os.path.exists(BG_IMAGE_PATH):
            try:
                img = Image.open(BG_IMAGE_PATH)
                img = img.resize((550, 250), Image.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(img)
                img_label = tk.Label(main, image=self.tk_img, bg='black')
                img_label.pack(pady=5)
                img_label.bind('<Button-1>', self.start_move)
                img_label.bind('<B1-Motion>', self.do_move)
            except Exception as e:
                print(f"Error loading bg.jpg: {e}")
                self.show_fallback(main)
        else:
            print("bg.jpg not found, using fallback")
            self.show_fallback(main)
        
        # Title
        title_frame = tk.Frame(main, bg='#FF0000')
        title_frame.pack(pady=10, fill='x', padx=50)
        tk.Label(title_frame, text="🔒 SYSTEM LOCKED", fg="white", bg='#FF0000',
                font=("Arial", 16, "bold")).pack(pady=5)
        
        # Info
        tk.Label(main, text="All desktop files are hidden", fg="yellow", bg="black",
                font=("Arial", 11)).pack()
        
        # Password section
        password_frame = tk.Frame(main, bg='#333333', relief='raised', bd=2)
        password_frame.pack(pady=20, padx=50, fill='x')
        
        tk.Label(password_frame, text="🔑 ENTER PASSWORD", fg="#FF0000", bg='#333333',
                font=("Arial", 12, "bold")).pack(pady=(10,5))
        
        self.password = tk.Entry(password_frame, show="*", font=("Arial", 14), 
                                 width=20, justify='center', bg='white')
        self.password.pack(pady=5, padx=20)
        self.password.focus()
        
        self.root.bind('<Return>', self.check_password)
        
        # Button
        tk.Button(password_frame, text="UNLOCK", command=self.check_password,
                 bg='#FF0000', fg='white', font=("Arial", 11, "bold"),
                 width=15, cursor='hand2', relief='flat').pack(pady=(10,15))
        
        # Status
        self.status = tk.Label(main, text="", fg="red", bg="black", font=("Arial", 10))
        self.status.pack()
        
        # Footer
        tk.Label(main, text="Drag window to move • Enter password to unlock", 
                fg="gray", bg="black", font=("Arial", 8)).pack()
        tk.Label(main, text="Capcut Pro Security v1.0", fg="gray", bg="black",
                font=("Arial", 8)).pack(side='bottom', pady=5)

    def show_fallback(self, parent):
        """Show fallback icon if bg.jpg not found"""
        fallback_frame = tk.Frame(parent, bg='black')
        fallback_frame.pack(pady=10)
        
        # Capcut style logo
        play_button = tk.Canvas(fallback_frame, width=100, height=100, bg='black', highlightthickness=0)
        play_button.create_rectangle(20, 20, 80, 80, outline='#FF0000', width=3, fill='#FF0000')
        play_button.create_text(50, 50, text="▶", fill='white', font=("Arial", 30))
        play_button.pack()
        
        play_button.bind('<Button-1>', self.start_move)
        play_button.bind('<B1-Motion>', self.do_move)

    def check_password(self, event=None):
        if self.password.get() == PASSWORD:
            self.status.config(text="✓ Correct! Unlocking...", fg="#00FF00")
            self.root.update()
            time.sleep(1)
            
            # Restore original wallpaper before closing
            restore_original_wallpaper()
            
            self.root.quit()
        else:
            self.password.delete(0, tk.END)
            self.status.config(text="✗ Wrong password!", fg="#FF0000")
            self.flash_password_frame()

    def flash_password_frame(self):
        """Flash the password frame on wrong password"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                try:
                    original = widget.cget('bg')
                    widget.configure(bg='#FF0000')
                    self.root.update()
                    self.root.after(100, lambda: widget.configure(bg=original))
                except:
                    pass

    def run(self):
        try:
            self.root.mainloop()
        except:
            toggle_desktop_files(lock=False)
            restore_original_wallpaper()

def main():
    try:
        # Lock desktop
        toggle_desktop_files(lock=True)
        
        # Show lock screen
        app = LockScreen()
        app.run()
    finally:
        # Always unlock when done
        toggle_desktop_files(lock=False)
        # Ensure wallpaper is restored even if something goes wrong
        restore_original_wallpaper()

if __name__ == "__main__":
    main()