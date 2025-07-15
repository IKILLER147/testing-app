import tkinter as tk
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
    root.geometry("600x480")
    root.resizable(False, False)

    theoretical_count = sum(1 for q in ALL_QUESTIONS if q.get("type") == "theoretical")
    practical_count = sum(1 for q in ALL_QUESTIONS if q.get("type") == "practical")
    all_count = len(ALL_QUESTIONS)

    label = tk.Label(root, text="Vyber si, jaký test chceš spustit:", font=("Arial", 16))
    label.pack(pady=30)

    frame = tk.Frame(root)
    frame.pack()

    btn_theoretical = tk.Button(
        frame, text="Pouze teoretické", font=("Arial", 14),
        width=20,
        command=lambda: start_quiz(root, [q for q in ALL_QUESTIONS if q.get("type") == "theoretical"], show_main_menu)
    )
    btn_theoretical.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    lbl_theoretical = tk.Label(frame, text=f"Otázek: {theoretical_count}", font=("Arial", 12))
    lbl_theoretical.grid(row=0, column=1, sticky="w")

    btn_practical = tk.Button(
        frame, text="Pouze praktické", font=("Arial", 14),
        width=20,
        command=lambda: start_quiz(root, [q for q in ALL_QUESTIONS if q.get("type") == "practical"], show_main_menu)
    )
    btn_practical.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    lbl_practical = tk.Label(frame, text=f"Otázek: {practical_count}", font=("Arial", 12))
    lbl_practical.grid(row=1, column=1, sticky="w")

    btn_all = tk.Button(
        frame, text="Všechny otázky", font=("Arial", 14),
        width=20,
        command=lambda: start_quiz(root, ALL_QUESTIONS, show_main_menu)
    )
    btn_all.grid(row=2, column=0, padx=10, pady=10, sticky="e")
    lbl_all = tk.Label(frame, text=f"Otázek: {all_count}", font=("Arial", 12))
    lbl_all.grid(row=2, column=1, sticky="w")

    btn_view = tk.Button(
        frame, text="Pouze prohlížení otázek (se správnými odpověďmi)", font=("Arial", 14),
        width=40,
        command=lambda: start_quiz(root, ALL_QUESTIONS, show_main_menu, view_mode=True)
    )
    btn_view.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

    btn_continue = tk.Button(
        root, text="Pokračovat v testu", font=("Arial", 14),
        width=30,
        state="normal" if session_exists() else "disabled",
        command=lambda: continue_last_test(root, ALL_QUESTIONS, show_main_menu)
    )
    btn_continue.pack(pady=12)

    btn_stats = tk.Button(
        root, text="Statistiky", font=("Arial", 14),
        width=30,
        command=lambda: show_stats_window(
            root, ALL_QUESTIONS, load_stats, save_stats, show_stats_window
        )
    )
    btn_stats.pack(pady=8)

root = tk.Tk()
show_main_menu()
root.mainloop()
