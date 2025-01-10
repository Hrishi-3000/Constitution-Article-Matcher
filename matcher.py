import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import difflib
import threading
from tkinter.font import Font

# Function to read the text from a PDF with better extraction handling
def read_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    text += "\n[Image or Non-Readable Content on Page]\n"
    except Exception as e:
        messagebox.showerror("Error", f"Could not read the PDF: {e}")
    return text

# Function to find matching section, case-insensitive, with context around match
def find_match(input_text, constitution_text, context_lines=2):
    lines = constitution_text.splitlines()
    input_text = input_text.lower()  # Case-insensitive search
    matches = []
    
    for i, line in enumerate(lines):
        if input_text in line.lower():
            # Collect surrounding context
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            match_context = "\n".join(lines[start:end])
            matches.append(f"• {match_context}")  # Prepend bullet point
    
    return matches

# Function to highlight matching text in the result box
def highlight_text(text_widget, search_word):
    text_widget.tag_remove('highlight', '1.0', tk.END)
    if search_word:
        start_pos = '1.0'
        while True:
            start_pos = text_widget.search(search_word, start_pos, stopindex=tk.END, nocase=1)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_word)}c"
            text_widget.tag_add('highlight', start_pos, end_pos)
            start_pos = end_pos
        text_widget.tag_config('highlight', background='yellow', foreground='black')

# GUI code for browsing and reading the PDF
def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")], title="Choose the Constitution PDF"
    )
    if file_path:
        global constitution_text
        progress.start()  # Start progress indicator
        threading.Thread(target=load_pdf_thread, args=(file_path,)).start()

# Threaded loading of the PDF to avoid freezing the UI
def load_pdf_thread(file_path):
    global constitution_text
    constitution_text = read_pdf(file_path)
    progress.stop()  # Stop progress indicator
    messagebox.showinfo("Success", "PDF loaded successfully!")

# Function to check matches in a separate thread
def check_match():
    input_text = input_text_box.get("1.0", tk.END).strip()
    if not constitution_text:
        messagebox.showwarning("Error", "Please load a Constitution PDF first!")
        return
    
    if not input_text:
        messagebox.showwarning("Error", "Please enter text to check!")
        return

    progress.start()  # Start progress indicator
    threading.Thread(target=match_thread, args=(input_text,)).start()

# Threaded function to find matches and display them
def match_thread(input_text):
    matches = find_match(input_text, constitution_text)
    
    result_text_box.delete("1.0", tk.END)
    if matches:
        result_text_box.insert(tk.END, "\n\n".join(matches))
        highlight_text(result_text_box, input_text)  # Highlight the matches
    else:
        result_text_box.insert(tk.END, "No relevant article or amendment found.")
    
    progress.stop()  # Stop progress indicator

# Function to save results to a text file
def save_results():
    if not result_text_box.get("1.0", tk.END).strip():
        messagebox.showwarning("Error", "No results to save!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(result_text_box.get("1.0", tk.END))
        messagebox.showinfo("Success", "Results saved successfully!")

# Help function to display guidance
def show_help():
    help_text = (
        "Welcome to the Constitution Article Matcher!\n\n"
        "Instructions:\n"
        "1. Load the Constitution PDF file using the 'Load Constitution PDF' button.\n"
        "2. Enter the text you want to check in the input box.\n"
        "3. Click 'Check Match' to find relevant articles or amendments.\n"
        "4. You can save the results using the 'Save Results' button.\n\n"
        "Tip: You can use the 'Fuzzy Match' for more flexible search results."
    )
    messagebox.showinfo("Help", help_text)

# Initialize Tkinter window
root = tk.Tk()
root.title("Constitution Article Matcher by Hrishikesh")
root.geometry("800x720")
root.resizable(True, True)

# Apply styling with ttk and default themes
style = ttk.Style()
style.theme_use("clam")

# Adding a parchment-like background color
root.configure(background="#f5f5dc")  # Light tan color resembling parchment

# Diplomatic UI elements
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Adding Help Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="How to Use", command=show_help)

# Status bar
status = tk.StringVar()
status.set("Ready")
status_bar = ttk.Label(root, textvariable=status, relief=tk.SUNKEN, anchor=tk.W, background="#f5f5dc")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

constitution_text = ""

# Create a main frame with padding for better layout
main_frame = ttk.Frame(root, padding="10 10 10 10", style='TFrame')
main_frame.pack(fill=tk.BOTH, expand=True)

# Add title label with bigger font
title_font = Font(family="Helvetica", size=20, weight="bold")
title_label = ttk.Label(main_frame, text="Constitution Article Matcher", font=title_font, background="#f5f5dc")
title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

# Input text label and box
input_label = ttk.Label(main_frame, text="Enter text to check:", background="#f5f5dc")
input_label.grid(row=1, column=0, sticky="w")

input_text_box = tk.Text(main_frame, height=5, width=70, wrap=tk.WORD, font=("Helvetica", 12), bg="#fffaf0")
input_text_box.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Button to load PDF
load_button = ttk.Button(main_frame, text="Load Constitution PDF", command=browse_file)
load_button.grid(row=3, column=0, pady=10, sticky="e")

# Button to check match
check_button = ttk.Button(main_frame, text="Check Match", command=check_match)
check_button.grid(row=3, column=1, pady=10, sticky="w")

# Result label and box
result_label = ttk.Label(main_frame, text="Matching Article/Amendment:", background="#f5f5dc")
result_label.grid(row=4, column=0, columnspan=2, sticky="w")

result_text_box = tk.Text(main_frame, height=10, width=70, wrap=tk.WORD, font=("Helvetica", 12), bg="#fffaf0")
result_text_box.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Save results button
save_button = ttk.Button(main_frame, text="Save Results", command=save_results)
save_button.grid(row=6, column=0, columnspan=2, pady=10)

# Progress bar with a cleaner style
progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode="indeterminate", length=400)
progress.grid(row=7, column=0, columnspan=2, pady=10)

# Add some padding to the components
for widget in main_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

# Start the GUI loop
root.mainloop()
