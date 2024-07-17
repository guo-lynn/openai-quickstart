import tkinter as tk
from tkinter import filedialog
from translator import PDFTranslator
import threading
import queue
from translator_api import getModel
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("*.doc", "*.pdf")])
    if file_path:
        entry_translator_file.delete(0, tk.END)
        entry_translator_file.insert(0, file_path)
def select_target_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        target_translator_path.delete(0, tk.END)  
        target_translator_path.insert(0, folder_path)  
def start_translation():
    file_path = entry_translator_file.get()
    if file_path:
        message_queue.put(('in_process', file_path))
        threading.Thread(target=perform_translation).start()
    else:
        message_queue.put(('error', 'No file found'))
message_queue = queue.Queue()
def check_queue():
    while not message_queue.empty():
        message_type, message = message_queue.get()
        if message_type == 'success':
            result_text.insert(tk.END, f"Translation Result:\n{message}\n\n", 'success')
        elif message_type == 'error':
            result_text.insert(tk.END, f"Error: {message}\n\n", 'error')
        elif message_type == 'in_process':
            result_text.insert(tk.END, f"In process: {message}\n\n", 'in_process')
    root.after(100, check_queue)


def perform_translation():
    file_path = entry_translator_file.get() 
    target_folder_path = target_translator_path.get() or None
    file_format = entry_file_format.get() or 'PDF'
    target_language = entry_target_language.get() or '中文'
    model_name = '-'.join(model_var.get().split('-')[1:])
    model = getModel(model_name)
    translator = PDFTranslator(model)
    
    try:
        translation_result = translator.translate_pdf(file_path, file_format, target_language,target_folder_path)
        message_queue.put(('success', translation_result))
    except Exception as e:
        message_queue.put(('error', str(e))) 
root = tk.Tk()
root.title('OpenAi Translator')
window_width = 600
window_height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

uniform_width = 50
label_width = 20  

model_options = ['OpenAIModel-gpt-3.5-turbo', 'OpenAIModel-gpt-4', 'OpenAIModel-gpt-4-1106-preview']
model_var = tk.StringVar(root)
model_var.set(model_options[0])
model_frame = tk.Frame(root)
model_frame.pack(fill=tk.X)
label_model = tk.Label(model_frame, text='Model Type:', width=label_width, anchor='w')
label_model.pack(side=tk.LEFT)
option_model = tk.OptionMenu(model_frame, model_var, *model_options)
option_model.config(width=uniform_width)  
option_model.pack(side=tk.LEFT)

file_frame = tk.Frame(root)
file_frame.pack(fill=tk.X)
label_pdf = tk.Label(file_frame, text='File Path:', width=label_width, anchor='w')
label_pdf.pack(side=tk.LEFT)
entry_translator_file = tk.Entry(file_frame, width=uniform_width)
entry_translator_file.pack(side=tk.LEFT)
button_select = tk.Button(file_frame, text='Select File', command=select_file)
button_select.pack(side=tk.LEFT)

format_frame = tk.Frame(root)
format_frame.pack(fill=tk.X)
label_file_format = tk.Label(format_frame, text='Target Format:', width=label_width, anchor='w')
label_file_format.pack(side=tk.LEFT)
entry_file_format = tk.Entry(format_frame, width=uniform_width)
entry_file_format.pack(side=tk.LEFT)

language_frame = tk.Frame(root)
language_frame.pack(fill=tk.X)
label_target_language = tk.Label(language_frame, text='Target Language:', width=label_width, anchor='w')
label_target_language.pack(side=tk.LEFT)
entry_target_language = tk.Entry(language_frame, width=uniform_width)
entry_target_language.pack(side=tk.LEFT)

file_frame = tk.Frame(root)
file_frame.pack(fill=tk.X)
target_file_path = tk.Label(file_frame, text='Target Path:', width=label_width, anchor='w')
target_file_path.pack(side=tk.LEFT)
target_translator_path = tk.Entry(file_frame, width=uniform_width)
target_translator_path.pack(side=tk.LEFT)
button_select = tk.Button(file_frame, text='Select Folder', command=select_target_folder)
button_select.pack(side=tk.LEFT)

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X)
button_translate = tk.Button(button_frame, text='Translate', command=start_translation)
button_translate.pack(side=tk.RIGHT, padx=10, pady=10, anchor='e')

result_frame = tk.Frame(root)
result_frame.pack(fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text = tk.Text(result_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=result_text.yview)
result_text.tag_config('success', foreground='green')
result_text.tag_config('error', foreground='red')
result_text.tag_config('in_process', foreground='blue')

root.after(100, check_queue)

root.mainloop()