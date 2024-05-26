import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from threading import Thread
import yt_dlp


# Função para lembrar a última pasta usada
def load_last_directory():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('last_directory', os.getcwd())
    except FileNotFoundError:
        return os.getcwd()


def save_last_directory(directory):
    with open('config.json', 'w') as f:
        json.dump({'last_directory': directory}, f)


# Função para selecionar a pasta de destino
def select_destination():
    folder_selected = filedialog.askdirectory(initialdir=load_last_directory())
    if folder_selected:
        destination_entry.delete(0, tk.END)
        destination_entry.insert(0, folder_selected)
        save_last_directory(folder_selected)


# Função para atualizar a barra de progresso
def update_progress_bar(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or 0
        downloaded_bytes = d.get('downloaded_bytes') or 0
        speed = d.get('speed') or 0
        eta = d.get('eta') or 0
        percent_str = d.get('_percent_str', '0.0%').strip('%')

        # Atualiza a barra de progresso
        progress_bar['value'] = float(percent_str)

        # Converte bytes para megabytes
        total_mb = total_bytes / (1024 * 1024) if total_bytes else 0
        downloaded_mb = downloaded_bytes / (1024 * 1024)
        speed_mb = speed / (1024 * 1024)

        # Atualiza os labels
        progress_label.config(text=f'{percent_str}% ({downloaded_mb:.2f} MB de {total_mb:.2f} MB)')
        speed_label.config(text=f'Velocidade: {speed_mb:.2f} MB/s')
        eta_label.config(text=f'Tempo restante: {eta}s')

        root.update_idletasks()


# Função para baixar o vídeo ou áudio
def download_video():
    url = url_entry.get()
    destination = destination_entry.get()
    if not url or not destination:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    output_template = os.path.join(destination, '%(title)s.%(ext)s')
    format_choice = format_var.get()
    quality_choice = quality_var.get()

    if format_choice == 'video':
        if quality_choice == '480p':
            ydl_format = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
        elif quality_choice == '720p':
            ydl_format = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        elif quality_choice == '1080p':
            ydl_format = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif quality_choice == '4k':
            ydl_format = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
        else:
            ydl_format = 'bestvideo+bestaudio/best'
    elif format_choice == 'audio':
        ydl_format = 'bestaudio'

    ydl_opts = {
        'format': ydl_format,
        'outtmpl': output_template,
        'merge_output_format': 'mp4' if format_choice == 'video' else 'mp3',
        'progress_hooks': [update_progress_bar],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if format_choice == 'audio' else []
    }

    def run_yt_dlp():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Sucesso", "Download completo!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar o vídeo: {str(e)}")

    Thread(target=run_yt_dlp).start()


root = tk.Tk()
root.title("YouTube Video Downloader")

tk.Label(root, text="URL do Vídeo:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Pasta de Destino:").grid(row=1, column=0, padx=10, pady=10)
destination_entry = tk.Entry(root, width=50)
destination_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Selecionar", command=select_destination).grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Formato:").grid(row=2, column=0, padx=10, pady=10)
format_var = tk.StringVar(value='video')
tk.Radiobutton(root, text="Vídeo", variable=format_var, value='video').grid(row=2, column=1)
tk.Radiobutton(root, text="Áudio (MP3)", variable=format_var, value='audio').grid(row=2, column=2)

tk.Label(root, text="Qualidade:").grid(row=3, column=0, padx=10, pady=10)
quality_var = tk.StringVar(value='720p')
qualities = ["480p", "720p", "1080p", "4k"]
quality_menu = tk.OptionMenu(root, quality_var, *qualities)
quality_menu.grid(row=3, column=1, columnspan=2)

tk.Button(root, text="Baixar", command=download_video).grid(row=4, column=1, pady=20)

progress_bar = Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=5, column=0, columnspan=3, pady=10)

progress_label = tk.Label(root, text="Progresso: 0% (0 MB de 0 MB)")
progress_label.grid(row=6, column=0, columnspan=3)

speed_label = tk.Label(root, text="Velocidade: 0 MB/s")
speed_label.grid(row=7, column=0, columnspan=3)

eta_label = tk.Label(root, text="Tempo restante: 0s")
eta_label.grid(row=8, column=0, columnspan=3)

root.mainloop()
