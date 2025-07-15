import tkinter as tk
import random
from tkinter import messagebox
from data import (
    load_questions_from_json,
    session_exists,
    load_stats,
    save_stats,
)
from stats_window import show_stats_window
from quiz_app import start_quiz, continue_last_test

ALL_QUESTIONS = load_questions_from_json("merged_questions.json")
if not ALL_QUESTIONS:
    exit("Nebyl nalezen platný JSON se zadáním otázek!")

def show_main_menu():
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Testovací program")
    root.geometry("720x520")
    root.resizable(False, False)

    theoretical = [q for q in ALL_QUESTIONS if q.get("type") == "theoretical"]
    practical = [q for q in ALL_QUESTIONS if q.get("type") == "practical"]
    theoretical_count = len(theoretical)
    practical_count = len(practical)
    all_count = len(ALL_QUESTIONS)

    label = tk.Label(root, text="Vyber si, jaký test chceš spustit:", font=("Arial", 16))
    label.pack(pady=30)

    frame = tk.Frame(root)
    frame.pack()

    # Jedno pole pro výběr počtu otázek
    entry_label = tk.Label(frame, text="Počet otázek (prázdné = všechny):", font=("Arial", 12))
    entry_label.grid(row=0, column=0, sticky="e", padx=(0,6))
    entry_count = tk.Entry(frame, width=7, font=("Arial", 12))
    entry_count.grid(row=0, column=1, sticky="w")
    entry_count.insert(0, "")

    def get_count(max_count):
        val = entry_count.get().strip()
        if not val:
            return max_count
        try:
            val = int(val)
            if val <= 0:
                raise ValueError
            return min(val, max_count)
        except ValueError:
            messagebox.showerror("Chyba", "Zadej platný počet otázek.")
            return None

    def start_test(questions):
        count = get_count(len(questions))
        if count is None or len(questions) == 0:
            return
        if count < len(questions):
            questions = random.sample(questions, count)
        start_quiz(root, questions, show_main_menu)

    def start_view(questions):
        count = get_count(len(questions))
        if count is None or len(questions) == 0:
            return
        if count < len(questions):
            questions = random.sample(questions, count)
        start_quiz(root, questions, show_main_menu, view_mode=True)

    btn_theoretical = tk.Button(
        frame, text=f"Teoretické ({theoretical_count})", font=("Arial", 14), width=22,
        command=lambda: start_test(theoretical),
        state="normal" if theoretical_count > 0 else "disabled"
    )
    btn_theoretical.grid(row=1, column=0, columnspan=2, padx=6, pady=8)

    btn_practical = tk.Button(
        frame, text=f"Praktické ({practical_count})", font=("Arial", 14), width=22,
        command=lambda: start_test(practical),
        state="normal" if practical_count > 0 else "disabled"
    )
    btn_practical.grid(row=2, column=0, columnspan=2, padx=6, pady=8)

    btn_all = tk.Button(
        frame, text=f"Všechny otázky ({all_count})", font=("Arial", 14), width=22,
        command=lambda: start_test(ALL_QUESTIONS),
        state="normal" if all_count > 0 else "disabled"
    )
    btn_all.grid(row=3, column=0, columnspan=2, padx=6, pady=8)

    btn_random = tk.Button(
        frame, text="Náhodný výběr ze všech", font=("Arial", 14), width=22,
        command=lambda: start_test(ALL_QUESTIONS),
        state="normal" if all_count > 0 else "disabled"
    )
    btn_random.grid(row=4, column=0, columnspan=2, padx=6, pady=8)

    btn_view = tk.Button(
        frame, text="Pouze prohlížení (se správnými odpověďmi)", font=("Arial", 13), width=42,
        command=lambda: start_view(ALL_QUESTIONS),
        state="normal" if all_count > 0 else "disabled"
    )
    btn_view.grid(row=5, column=0, columnspan=2, pady=(18, 6))

    # Dolní panel pro pokračování/statistiky
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(pady=(30, 0))

    btn_continue = tk.Button(
        bottom_frame, text="Pokračovat v testu", font=("Arial", 14),
        width=30,
        state="normal" if session_exists() else "disabled",
        command=lambda: continue_last_test(root, ALL_QUESTIONS, show_main_menu)
    )
    btn_continue.pack(pady=7)

    btn_stats = tk.Button(
        bottom_frame, text="Statistiky", font=("Arial", 14),
        width=30,
        command=lambda: show_stats_window(
            root, ALL_QUESTIONS, load_stats, save_stats, show_stats_window
        )
    )
    btn_stats.pack(pady=7)

root = tk.Tk()
show_main_menu()
root.mainloop()
