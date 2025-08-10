import os
import re
import whisper 
from fpdf import FPDF
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMNI_API_KEY"))  # Replace with your actual API key
model = genai.GenerativeModel("models/gemini-1.5-flash")


def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


def transcribe_audio(mp3_path):
    status_var.set("🔊 Transcribing MP3 with Whisper...")
    progress_var.set(20)
    model = whisper.load_model("base")
    result = model.transcribe(mp3_path)
    return result["text"]


def summarize_text(transcript, subject):
    status_var.set("🧠 Summarizing with Gemini...")
    progress_var.set(60)
    prompt = (
        f"You are an expert assistant helping a student with lecture notes.\n"
        f"The subject is: {subject}.\n\n"
        f"Based on the lecture transcript below, generate clean, structured bullet-point notes. "
        f"If the subject is mathematical or technical, include formulas, flowcharts, or diagrams in text form where appropriate:\n\n"
        f"{transcript}"
    )
    response = model.generate_content(prompt)
    return response.text


def save_as_pdf(subject, summary, diagrams=None, filename="Summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

 
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Neuro Notes - {subject}", ln=True, align="C")

   
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Summary:\n" + remove_emojis(summary))

  
    if diagrams:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, txt="Generated Diagrams / Flowcharts:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=remove_emojis(diagrams))

    pdf.output(filename)
    filepath = os.path.abspath(filename)
    status_var.set(f"✅ PDF saved successfully: {filepath}")
    progress_var.set(100)


    webbrowser.open(f"file://{filepath}")


def neuro_notes(mp3_file_path, subject):
    if not mp3_file_path.endswith(".mp3"):
        messagebox.showerror("Error", "Please select a valid MP3 file.")
        return

    try:
        transcript = transcribe_audio(mp3_file_path)
        summary = summarize_text(transcript, subject)
        diagrams = None
        save_as_pdf(subject, summary, diagrams)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_var.set("❌ An error occurred")
        progress_var.set(0)


app = tk.Tk()
app.title("🧠 Neuro Notes")
app.geometry("500x400")
app.resizable(False, False)
app.configure(bg="#f0f4f8")

file_path_var = tk.StringVar()
subject_var = tk.StringVar()
status_var = tk.StringVar(value="Ready")
progress_var = tk.IntVar(value=0)


tk.Label(app, text="Neuro Notes - AI Lecture Summarizer", font=("Helvetica", 16, "bold"), bg="#f0f4f8").pack(pady=20)

frame = tk.Frame(app, bg="#f0f4f8")
frame.pack(pady=10)

tk.Label(frame, text="🎧 Select MP3 File:", bg="#f0f4f8").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=file_path_var, width=40).grid(row=1, column=0, padx=5)
tk.Button(frame, text="Browse", command=lambda: file_path_var.set(filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")]))).grid(row=1, column=1, padx=5)

tk.Label(frame, text="📚 Enter Subject:", bg="#f0f4f8").grid(row=2, column=0, sticky="w", pady=(10, 0))
tk.Entry(frame, textvariable=subject_var, width=40).grid(row=3, column=0, padx=5)

tk.Button(app, text="📝 Generate Notes", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", command=lambda: threading.Thread(target=lambda: neuro_notes(file_path_var.get(), subject_var.get())).start()).pack(pady=20)

progress = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress.pack(pady=10)

status_label = tk.Label(app, textvariable=status_var, bg="#f0f4f8", fg="gray")
status_label.pack()

app.mainloop()
