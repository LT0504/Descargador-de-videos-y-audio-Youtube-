from tkinter import*
import customtkinter
from PIL import Image, ImageTk
import requests
from pytube import YouTube
from io import BytesIO
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import os
import threading
from moviepy.audio.io.AudioFileClip import AudioFileClip
import subprocess
from CTkMessagebox import CTkMessagebox

def hilo_mostrar_detalles():
        url = url_video.get()
        proceso1 = threading.Thread(target=obtener_datos, args=(url,))
        proceso1.start()
        
def hilo_descargar():
    proceso = threading.Thread(target=descargar)
    proceso.start()
    
def obtener_miniatura():
    url_miniatura = ytObject.thumbnail_url
    response = requests.get(url_miniatura)
    img_data = BytesIO(response.content)
    img = Image.open(img_data)
    img.thumbnail((250, 150))
    img_tk = ImageTk.PhotoImage(img)
    miniatura = Label(miniatura_frame, image=img_tk, border=0)
    miniatura.image = img_tk
    miniatura.place(x=5, y=5)

def obtener_datos(url):
    global resoluciones_disponibles, bitrates_disponibles
    try:
        global yt, titulo, ytObject
        ytObject = YouTube(url, on_progress_callback=progreso)
        
        yt = ytObject.streams
        video = ytObject.streams.filter(file_extension="mp4").first()
        titulo = video.default_filename
        horas = int(ytObject.length//3600)
        minutos = int(ytObject.length%3600)//60
        segundos = int(ytObject.length%60)
        fecha = str(ytObject.publish_date)
        titulo_video.configure(info_frame, text="Titulo: "+titulo, wraplength=200)
        duracion_video.configure(info_frame, text="Duracion: "+ str(horas)+":"+str(minutos)+":"+str(segundos))
        fecha_subida.configure(info_frame, text="Fecha de subida: "+ fecha[0:10])
        
        proceso2 = threading.Thread(target=obtener_miniatura)
        proceso2.start()
        
        resoluciones_disponibles= []
        
        available_streams = ytObject.streams.filter()

        for stream in available_streams:
            resoluciones = ["144p","360p", "480p", "720p", "1080p"]
            if stream.resolution in resoluciones:
                if not(stream.resolution in resoluciones_disponibles):
                    resoluciones_disponibles.append(stream.resolution)
        resoluciones_disponibles = sorted(resoluciones_disponibles, key=ordenar_listas)
        
        bitrates_disponibles = []

        available_audio_streams = ytObject.streams.filter(only_audio=True)
        
        for stream in available_audio_streams:
            bitrates = ["48kbps","50kbps", "70kbps","128kbps", "160kbps kbps"]
            if stream.abr in bitrates:
                if not(stream.abr in bitrates_disponibles):
                    bitrates_disponibles.append(stream.abr)
        
        vid_aud.configure(values=["Video", "Audio"], command=imprimir_datos)
        
    except Exception:
        CTkMessagebox(title="Error", message="Video no disponible o URL no valido", icon="cancel", width=10, height=40)
        
def ordenar_listas(lista):
    return int(lista[:-1])
        
def imprimir_datos(option):
    Formato.set("--")
    calidad.set("--")
    if vid_aud.get() == "Video":
        Formato.configure(values=['Mp4'])
        calidad.configure(values=resoluciones_disponibles)
    else:
        Formato.configure(values=['Mp3'])
        calidad.configure(values=bitrates_disponibles)      
        
def descargar():
    try:
        titulo_descargando.configure(text="Titulo: "+ titulo.split(".")[0])
        estado.configure(text="Estado: Descargando...")
        ruta_videos = os.path.join('Descargas','Videos')
        os.makedirs(ruta_videos, exist_ok=True)
            
        ruta_audios = os.path.join('Descargas','Audios')
        os.makedirs(ruta_audios, exist_ok=True)

        if vid_aud.get() == "Video":
            audio = yt.filter(mime_type='audio/mp4', abr="128kbps")
            audio.first().download(output_path='Descargas/Videos', filename=titulo.split(".")[0] + "_audio.mp4")
            subprocess.check_call(['attrib', '+H', ruta_videos+'/'+titulo.split(".")[0] + "_audio.mp4"])
                
            video = yt.filter(only_video=True, mime_type='video/mp4', res=calidad.get())
            video.first().download(output_path='Descargas/Videos', filename=titulo.split(".")[0] + "_video.mp4")
            subprocess.check_call(['attrib', '+H', ruta_videos+'/'+titulo.split(".")[0] + "_video.mp4"])
            videos_and_audio()
                
        else:
            filtered_streams = yt.filter(mime_type='audio/mp4', abr=calidad.get())
            filtered_streams.first().download(output_path=ruta_audios, filename=titulo.split(".")[0] + "_audio.mp4")
            convertir_mp3()
    except Exception:
         CTkMessagebox(title="Error", message="No se pudo descargar.", icon="cancel", width=10, height=40)
    
def progreso(stream, chunk: bytes, bytes_remaining = int):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    barra_progreso.set(percentage/100)
    porcentaje_progreso.configure(progreso_frame, text=str(round(percentage,1))+'%')
    progreso_frame.update()

def convertir_mp3():
    estado.configure(text="Estado: Convirtiendo...")
    audio = AudioFileClip('Descargas/Audios/'+titulo.split(".")[0]+"_audio.mp4")
    audio.write_audiofile('Descargas/Audios/'+titulo.split(".")[0]+".mp3", codec='libmp3lame')
    while True:
        if os.path.isfile('Descargas/Audios/'+titulo.split(".")[0]+".mp3"):
            os.remove('Descargas/Audios/'+titulo.split(".")[0]+"_audio.mp4")
            estado.configure(text="Estado: Guardado exitosamente en Descargas/Audios.")
            break
    
def videos_and_audio():
    estado.configure(text="Estado: Conviertiendo...")
    clip_video = VideoFileClip('Descargas/Videos/'+titulo.split(".")[0]+"_video.mp4")
    clip_audio = AudioFileClip('Descargas/Videos/'+titulo.split(".")[0]+"_audio.mp4")
    video_final = clip_video.set_audio(clip_audio)
    video_final.write_videofile('Descargas/Videos/'+titulo)
    while True:
        if os.path.isfile('Descargas/Videos/'+titulo):
            os.remove('Descargas/Videos/'+titulo.split(".")[0]+"_video.mp4")
            os.remove('Descargas/Videos/'+titulo.split(".")[0]+"_audio.mp4")
            estado.configure(text="Estado: Guardado exitosamente en Descargas/Videos.")
            break
    
#INTERFAZ
raiz = customtkinter.CTk()
raiz.geometry("700x520")
raiz.title("Descargador de Video/Audio (YouTube)")
raiz.iconbitmap('resources/icono.ico')
raiz.resizable(0,0)
customtkinter.set_default_color_theme("dark-blue")

#URL DEL VIDEO
url_frame = customtkinter.CTkFrame(raiz, border_width=3)
url_frame.configure(width=700, height=82)#152
url_frame.place(x=0,y=0)

customtkinter.CTkLabel(url_frame, text="URL del video", font=("Arial",15)).place(x=30, y=25)

url_video = customtkinter.CTkEntry(raiz, width=350, height=30)
url_video.grid(row=0, column=1, padx=5, pady=5)
url_video.place(x=150, y=25)
customtkinter.CTkButton(url_frame, text="Buscar", command=hilo_mostrar_detalles).place(x=540, y=25)

#INFORMACION DEL VIDEO
info_frame = customtkinter.CTkFrame(raiz, border_width=3)
info_frame.configure(width=502, height=302)
info_frame.place(x=0,y=80)

customtkinter.CTkLabel(info_frame, text="INFORMACION DEL VIDEO").place(x=30, y=30)
titulo_video = customtkinter.CTkLabel(info_frame, text="Titulo: ")
titulo_video.place(x=300, y=65)
duracion_video = customtkinter.CTkLabel(info_frame, text="Duracion:")
duracion_video.place(x=300, y=150)
fecha_subida= customtkinter.CTkLabel(info_frame, text="Fecha de subida:")
fecha_subida.place(x=300, y=195)
customtkinter.CTkLabel(info_frame, text= "Nota: Posibles fallos al descargar audio..").place(x=30, y= 250)

#MINIATURA
miniatura_frame = customtkinter.CTkFrame(raiz, fg_color="Black")
miniatura_frame.configure(width=260, height=153)
miniatura_frame.place(x=30,y=150)

#CALIDADES DE VIDEO
calidades_frame = customtkinter.CTkFrame(raiz, border_width=3)
calidades_frame.configure(width=200, height=302)
calidades_frame.place(x=500,y=80)
customtkinter.CTkLabel(calidades_frame, text="Video/Audio:").place(x=10, y=20)
customtkinter.CTkLabel(calidades_frame, text="Formato:").place(x=10, y=90)
customtkinter.CTkLabel(calidades_frame, text="Calidad:").place(x=10, y=160)
customtkinter.CTkButton(calidades_frame, text="DESCARGAR", command=hilo_descargar).place(x=35, y=250)

vid_aud = customtkinter.CTkComboBox(calidades_frame, values=[])
vid_aud.set("--")
vid_aud.place(x=10, y=50)

Formato = customtkinter.CTkComboBox(calidades_frame, values=[])
Formato.set("--")
Formato.place(x=10, y=120)

calidad = customtkinter.CTkComboBox(calidades_frame, values=[])
calidad.set("--")
calidad.place(x=10, y=190)

#PROGRESO
progreso_frame = customtkinter.CTkFrame(raiz, border_width=3)
progreso_frame.configure(width=700, height=150)
progreso_frame.place(x=0,y=370)
#barra
barra_progreso = customtkinter.CTkProgressBar(progreso_frame, orientation="horizontal", width=570, height=13)
barra_progreso.place(x=75, y=67)
barra_progreso.set(0)

titulo_descargando = customtkinter.CTkLabel(progreso_frame, text="Titulo: ", wraplength=650)
titulo_descargando.place(x=30, y=20)

estado = customtkinter.CTkLabel(progreso_frame, text="Estado: ")
estado.place(x=30, y=100)

porcentaje_progreso = customtkinter.CTkLabel(progreso_frame, text=str(barra_progreso.get())+'%')
porcentaje_progreso.place(x=30, y=59)

raiz.mainloop()
