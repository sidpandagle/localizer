import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
from googletrans import Translator
import threading
import json


class LocalizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Localization Text Manager")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        self.translator = Translator()
        self.settings_file = "localizer_settings.json"
        self.settings = self.load_settings()
        self.combination_frames = []
        
        self.languages = {
            "English": "en",
            "French": "fr",
            "Spanish": "es", 
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Chinese (Simplified)": "zh-cn",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Hindi": "hi",
            "Dutch": "nl"
        }
        
        self.setup_gui()
    
    def load_settings(self):
        default_settings = {
            "language_combinations": [
                {"language": "English", "output_path": "english.properties", "enabled": True}
            ]
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return default_settings
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def get_language_combinations(self):
        return self.settings.get("language_combinations", [])
    
    def add_language_combination(self, language, output_path, enabled=True):
        combinations = self.get_language_combinations()
        new_combo = {"language": language, "output_path": output_path, "enabled": enabled}
        
        for combo in combinations:
            if combo["language"] == language and combo["output_path"] == output_path:
                return False
        
        combinations.append(new_combo)
        self.settings["language_combinations"] = combinations
        self.save_settings()
        return True
    
    def remove_language_combination(self, index):
        combinations = self.get_language_combinations()
        if 0 <= index < len(combinations):
            combinations.pop(index)
            self.settings["language_combinations"] = combinations
            self.save_settings()
            return True
        return False
    
    def update_combination_enabled(self, index, enabled):
        combinations = self.get_language_combinations()
        if 0 <= index < len(combinations):
            combinations[index]["enabled"] = enabled
            self.settings["language_combinations"] = combinations
            self.save_settings()
    
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(header_frame, text="Localization Keys:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W
        )
        
        ttk.Button(header_frame, text="⚙️ Settings", command=self.open_settings).grid(
            row=0, column=1, sticky=tk.E
        )
        
        self.text_area = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            width=70,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.text_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        main_frame.rowconfigure(1, weight=1)
        
        self.combinations_frame = ttk.LabelFrame(main_frame, text="Selected Language Outputs", padding="10")
        self.combinations_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.combinations_frame.columnconfigure(0, weight=1)
        
        self.combinations_info = ttk.Label(self.combinations_frame, text="No language outputs configured. Click Settings to add.", 
                                          foreground="gray", font=("Arial", 9, "italic"))
        self.combinations_info.grid(row=0, column=0, pady=10)
        
        self.refresh_combinations_display()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
        self.translate_btn = ttk.Button(
            button_frame, 
            text="Translate & Save", 
            command=self.start_translation,
            style="Accent.TButton"
        )
        self.translate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Text", command=self.clear_text).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=4, column=0, sticky=tk.W)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.progress.grid_remove()
        
        self.load_sample_text()
        
    def load_sample_text(self):
        sample_text = """# 1.4.0HF11 MSList Defect - This is a comment.
test.okay=Okay
test.cancel=Cancel

# User interface messages
app.welcome=Welcome to our application
user.login=Please log in

# Error messages
error.invalid=Invalid input provided"""
        self.text_area.insert(tk.END, sample_text)
    
    def open_settings(self):
        SettingsWindow(self.root, self)
        
    def create_combination_widget(self, combo_data, index):
        language = combo_data["language"]
        output_path = combo_data["output_path"]
        enabled = combo_data.get("enabled", True)
        
        frame = ttk.Frame(self.combinations_frame)
        frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=2)
        frame.columnconfigure(2, weight=1)
        
        var = tk.BooleanVar(value=enabled)
        checkbox = ttk.Checkbutton(frame, variable=var, 
                                 command=lambda: self.update_combination_enabled(index, var.get()))
        checkbox.grid(row=0, column=0, padx=(0, 10))
        
        status_label = ttk.Label(frame, text="●", foreground="green", font=("Arial", 12))
        status_label.grid(row=0, column=1, padx=(0, 5))
        
        text_label = ttk.Label(frame, text=f"{language} → {os.path.basename(output_path)}", font=("Arial", 9))
        text_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        frame_data = {
            'frame': frame,
            'checkbox_var': var,
            'checkbox': checkbox,
            'status_label': status_label,
            'text_label': text_label,
            'language': language,
            'output_path': output_path
        }
        
        return frame_data
    
    def refresh_combinations_display(self):
        for frame_data in self.combination_frames:
            frame_data['frame'].destroy()
        
        self.combination_frames = []
        combinations = self.get_language_combinations()
        
        if not combinations:
            self.combinations_info.grid(row=0, column=0, pady=10)
        else:
            self.combinations_info.grid_remove()
            for i, combo_data in enumerate(combinations):
                frame_data = self.create_combination_widget(combo_data, i)
                self.combination_frames.append(frame_data)
        
        self.combinations_frame.columnconfigure(0, weight=1)
    
    
    
    def get_selected_combinations(self):
        selected = []
        combinations = self.get_language_combinations()
        for i, frame_data in enumerate(self.combination_frames):
            if frame_data['checkbox_var'].get() and i < len(combinations):
                combo = combinations[i]
                selected.append((combo["language"], combo["output_path"]))
        return selected
    
            
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)
        self.root.update()
        
    def start_translation(self):
        if not self.validate_inputs():
            return
            
        self.translate_btn.config(state="disabled")
        self.progress.grid()
        self.progress.start(10)
        self.update_status("Translating...", "blue")
        
        thread = threading.Thread(target=self.translate_and_save)
        thread.daemon = True
        thread.start()
        
    def validate_inputs(self):
        text_content = self.text_area.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showerror("Error", "Please enter localization keys to translate.")
            return False
            
        selected_combinations = self.get_selected_combinations()
        if not selected_combinations:
            messagebox.showerror("Error", "Please select at least one output/language combination.")
            return False
            
        return True
        
    def parse_localization_entries(self, text):
        entries = []
        lines = text.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            if not line:
                entries.append(('__EMPTY_LINE__', ''))
                continue
            elif line.startswith('#'):
                entries.append(('__COMMENT__', original_line))
                continue
                
            match = re.match(r'^([^=]+)=(.*)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                entries.append((key, value))
            else:
                self.update_status(f"Warning: Invalid format on line {line_num}: {line}", "orange")
                
        return entries
        
    def translate_text(self, text, target_lang):
        try:
            result = self.translator.translate(text, dest=target_lang)
            return result.text
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
            
    def translate_and_save(self):
        try:
            text_content = self.text_area.get(1.0, tk.END)
            entries = self.parse_localization_entries(text_content)
            
            if not entries:
                self.update_status("No valid entries found to translate", "red")
                return
                
            selected_combinations = self.get_selected_combinations()
            total_combinations = len(selected_combinations)
            total_entries = len(entries)
            
            for combo_idx, (language, output_path) in enumerate(selected_combinations, 1):
                frame_data = next((fd for fd in self.combination_frames if fd['language'] == language and fd['output_path'] == output_path), None)
                if frame_data:
                    frame_data['status_label'].config(text="⏳", foreground="orange")
                target_lang_code = self.languages[language]
                translated_entries = []
                
                self.update_status(f"Processing {language} ({combo_idx}/{total_combinations})...", "blue")
                
                for i, (key, value) in enumerate(entries, 1):
                    try:
                        if key == '__COMMENT__':
                            translated_entries.append(value)
                        elif key == '__EMPTY_LINE__':
                            translated_entries.append('')
                        else:
                            if language == "English":
                                translated_value = value
                            else:
                                translated_value = self.translate_text(value, target_lang_code)
                            translated_entries.append(f"{key}={translated_value}")
                            self.update_status(f"Processing {language}... ({i}/{total_entries})", "blue")
                    except Exception as e:
                        self.update_status(f"Failed to translate '{key}' for {language}: {str(e)}", "red")
                        if key not in ['__COMMENT__', '__EMPTY_LINE__']:
                            translated_entries.append(f"{key}={value}")
                        
                output_content = '\n'.join(translated_entries) + '\n'
                
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                file_exists = os.path.exists(output_path)
                mode = 'a' if file_exists else 'w'
                
                with open(output_path, mode, encoding='utf-8') as f:
                    if file_exists:
                        f.write('\n')
                    f.write(output_content)
                    
                if frame_data:
                    frame_data['status_label'].config(text="✓", foreground="green")
                    
            self.update_status(f"Successfully translated and saved {len(entries)} entries to {total_combinations} files!", "green")
            messagebox.showinfo("Success", f"Translation completed!\n{len(entries)} entries saved to {total_combinations} files.")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            
        finally:
            self.progress.stop()
            self.progress.grid_remove()
            self.translate_btn.config(state="normal")
            for frame_data in self.combination_frames:
                if frame_data['status_label'].cget('text') == '⏳':
                    frame_data['status_label'].config(text="●", foreground="green")


class SettingsWindow:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Language Output Settings")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_combinations()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Language Output Combinations", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(list_frame, columns=("Language", "Output Path"), show="headings", height=12)
        self.tree.heading("Language", text="Language")
        self.tree.heading("Output Path", text="Output File")
        self.tree.column("Language", width=150)
        self.tree.column("Output Path", width=350)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        add_frame = ttk.LabelFrame(main_frame, text="Add New Combination", padding="10")
        add_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        add_frame.columnconfigure(2, weight=1)
        
        ttk.Label(add_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.language_combo = ttk.Combobox(
            add_frame,
            values=list(self.main_app.languages.keys()),
            state="readonly",
            width=20
        )
        self.language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.language_combo.set("French")
        
        ttk.Label(add_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(add_frame, textvariable=self.output_path_var)
        self.output_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        entry_buttons_frame = ttk.Frame(add_frame)
        entry_buttons_frame.grid(row=1, column=3, padx=(0, 0), pady=(10, 0))
        
        ttk.Button(entry_buttons_frame, text="Browse", command=self.browse_output_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(entry_buttons_frame, text="Add", command=self.add_combination).pack(side=tk.LEFT)
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(buttons_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Close", command=self.close_window).pack(side=tk.RIGHT)
        
    def load_combinations(self):
        self.tree.delete(*self.tree.get_children())
        combinations = self.main_app.get_language_combinations()
        
        for combo in combinations:
            self.tree.insert("", tk.END, values=(combo["language"], combo["output_path"]))
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Select Output File",
            defaultextension=".properties",
            filetypes=[
                ("Properties files", "*.properties"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_path_var.set(filename)
    
    def add_combination(self):
        language = self.language_combo.get()
        output_path = self.output_path_var.get()
        
        if not language:
            messagebox.showerror("Error", "Please select a language.")
            return
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        if self.main_app.add_language_combination(language, output_path):
            self.load_combinations()
            self.main_app.refresh_combinations_display()
            self.output_path_var.set("")
            messagebox.showinfo("Success", "Language combination added successfully!")
        else:
            messagebox.showwarning("Warning", "This combination already exists.")
    
    def remove_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a combination to remove.")
            return
        
        for item in selected_items:
            index = self.tree.index(item)
            if self.main_app.remove_language_combination(index):
                self.tree.delete(item)
        
        self.main_app.refresh_combinations_display()
        messagebox.showinfo("Success", "Selected combinations removed successfully!")
    
    def close_window(self):
        self.window.destroy()


def main():
    root = tk.Tk()
    app = LocalizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()