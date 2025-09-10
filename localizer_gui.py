import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
from googletrans import Translator
import threading


class LocalizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Localization Text Manager")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        self.translator = Translator()
        self.output_combinations = []
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
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Localization Keys:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.text_area = scrolledtext.ScrolledText(
            main_frame, 
            height=10, 
            width=70,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.text_area.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        combinations_header_frame = ttk.Frame(main_frame)
        combinations_header_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        ttk.Label(combinations_header_frame, text="Output/Language Combinations:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        header_buttons_frame = ttk.Frame(combinations_header_frame)
        header_buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(header_buttons_frame, text="Select All", command=self.select_all_combinations).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(header_buttons_frame, text="Deselect All", command=self.deselect_all_combinations).pack(side=tk.LEFT)
        
        self.combinations_container = ttk.Frame(main_frame)
        self.combinations_container.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.combinations_container.columnconfigure(0, weight=1)
        
        self.combinations_canvas = tk.Canvas(self.combinations_container, height=120, bg="white", highlightthickness=1, highlightcolor="#cccccc")
        self.combinations_scrollbar = ttk.Scrollbar(self.combinations_container, orient="vertical", command=self.combinations_canvas.yview)
        self.combinations_scrollable_frame = ttk.Frame(self.combinations_canvas)
        
        self.combinations_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.combinations_canvas.configure(scrollregion=self.combinations_canvas.bbox("all"))
        )
        
        self.combinations_canvas.create_window((0, 0), window=self.combinations_scrollable_frame, anchor="nw")
        self.combinations_canvas.configure(yscrollcommand=self.combinations_scrollbar.set)
        
        self.combinations_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.combinations_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.combinations_container.rowconfigure(0, weight=1)
        
        add_frame = ttk.Frame(main_frame)
        add_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        add_frame.columnconfigure(1, weight=1)
        
        ttk.Label(add_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.language_combo = ttk.Combobox(
            add_frame,
            values=list(self.languages.keys()),
            state="readonly",
            width=20
        )
        self.language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.language_combo.set("French")
        
        ttk.Label(add_frame, text="Output File:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(add_frame, textvariable=self.output_path_var, width=30)
        self.output_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(add_frame, text="Browse", command=self.browse_output_file).grid(row=0, column=4)
        ttk.Button(add_frame, text="Add", command=self.add_combination).grid(row=0, column=5, padx=(5, 0))
        
        add_frame.columnconfigure(3, weight=1)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        self.translate_btn = ttk.Button(
            button_frame, 
            text="Translate & Save", 
            command=self.start_translation,
            style="Accent.TButton"
        )
        self.translate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Text", command=self.clear_text).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.progress.grid_remove()
        
        self.load_sample_text()
        
        self.add_default_english_combination()
        
    def load_sample_text(self):
        sample_text = """test.okay=Okay
test.cancel=Cancel
app.welcome=Welcome to our application
user.login=Please log in
error.invalid=Invalid input provided"""
        self.text_area.insert(tk.END, sample_text)
    
    def add_default_english_combination(self):
        import os
        default_path = os.path.join(os.getcwd(), "english.properties")
        self.output_combinations.append(("English", default_path))
        self.refresh_combinations_display()
        
    def create_combination_widget(self, language, output_path, index):
        frame = ttk.Frame(self.combinations_scrollable_frame)
        frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=2, padx=5)
        frame.columnconfigure(2, weight=1)
        
        var = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(frame, variable=var)
        checkbox.grid(row=0, column=0, padx=(0, 10))
        
        status_label = ttk.Label(frame, text="●", foreground="green", font=("Arial", 12))
        status_label.grid(row=0, column=1, padx=(0, 5))
        
        text_label = ttk.Label(frame, text=f"{language} → {output_path}", font=("Arial", 9))
        text_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        delete_btn = ttk.Button(frame, text="❌", width=3, command=lambda: self.remove_combination(index))
        delete_btn.grid(row=0, column=3, padx=(5, 0))
        
        frame_data = {
            'frame': frame,
            'checkbox_var': var,
            'checkbox': checkbox,
            'status_label': status_label,
            'text_label': text_label,
            'delete_btn': delete_btn,
            'language': language,
            'output_path': output_path
        }
        
        return frame_data
    
    def refresh_combinations_display(self):
        for frame_data in self.combination_frames:
            frame_data['frame'].destroy()
        
        self.combination_frames = []
        
        for i, (language, output_path) in enumerate(self.output_combinations):
            frame_data = self.create_combination_widget(language, output_path, i)
            self.combination_frames.append(frame_data)
        
        self.combinations_scrollable_frame.columnconfigure(0, weight=1)
    
    def add_combination(self):
        language = self.language_combo.get()
        output_path = self.output_path_var.get()
        
        if not language:
            messagebox.showerror("Error", "Please select a language.")
            return
        if not output_path:
            messagebox.showerror("Error", "Please select an output file.")
            return
            
        combination = (language, output_path)
        if combination not in self.output_combinations:
            self.output_combinations.append(combination)
            self.refresh_combinations_display()
            self.output_path_var.set("")
        else:
            messagebox.showwarning("Warning", "This combination already exists.")
    
    def remove_combination(self, index):
        if 0 <= index < len(self.output_combinations):
            del self.output_combinations[index]
            self.refresh_combinations_display()
    
    def select_all_combinations(self):
        for frame_data in self.combination_frames:
            frame_data['checkbox_var'].set(True)
    
    def deselect_all_combinations(self):
        for frame_data in self.combination_frames:
            frame_data['checkbox_var'].set(False)
    
    def get_selected_combinations(self):
        selected = []
        for i, frame_data in enumerate(self.combination_frames):
            if frame_data['checkbox_var'].get():
                selected.append(self.output_combinations[i])
        return selected
    
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
            line = line.strip()
            if not line or line.startswith('#'):
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
                        if language == "English":
                            translated_value = value
                        else:
                            translated_value = self.translate_text(value, target_lang_code)
                        translated_entries.append(f"{key}={translated_value}")
                        self.update_status(f"Processing {language}... ({i}/{total_entries})", "blue")
                    except Exception as e:
                        self.update_status(f"Failed to translate '{key}' for {language}: {str(e)}", "red")
                        translated_entries.append(f"{key}={value}")
                        
                output_content = '\n'.join(translated_entries) + '\n'
                
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
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


def main():
    root = tk.Tk()
    app = LocalizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()