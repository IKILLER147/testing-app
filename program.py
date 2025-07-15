import tkinter as tk
from tkinter import messagebox
import random
import json
import os
import string
from tkinter import ttk  # na Treeview

SESSION_FILE = "last_session.json"

def make_json_serializable(obj):
    """ Rekurzivně převádí všechny sety na listy v dictu/listu. """
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj

def load_questions_from_json(filename):
    if not os.path.exists(filename):
        messagebox.showerror("Chyba", f"Soubor {filename} neexistuje!")
        return []
    with open(filename, "r", encoding="utf-8") as f:
        raw = json.load(f)
        for q in raw:
            q["answer"] = set(q["answer"])
        return raw

ALL_QUESTIONS = load_questions_from_json("merged_questions.json")
if not ALL_QUESTIONS:
    exit("Nebyl nalezen platný JSON se zadáním otázek!")

STATS_FILE = "stats.json"

def load_stats(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(filename, stats):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

# -- SESSION SAVE/LOAD
def save_session(data):
    data = make_json_serializable(data)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# ---- Statistiky ----

def show_stats_window():
    stats = load_stats(STATS_FILE)
    stats_win = tk.Toplevel(root)
    stats_win.title("Statistiky otázek")
    stats_win.geometry("980x600")
    stats_win.resizable(True, True)

    # Hlavní rámec a spodní panel
    main_frame = tk.Frame(stats_win)
    main_frame.pack(side="top", fill="both", expand=True)
    bottom_panel = tk.Frame(stats_win)
    bottom_panel.pack(side="bottom", fill="x")

    # Propojení ID s texty otázek
    id_to_question = {str(q.get("id")): q for q in ALL_QUESTIONS}
    total, correct, wrong = 0, 0, 0

    # Tabulka s otázkami
    columns = ("ID", "Otázka", "Celkem", "Správně", "Špatně", "Úspěšnost")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="browse")
    tree.pack(fill="both", expand=True)
    
    tree.heading("ID", text="ID")
    tree.heading("Otázka", text="Otázka (zkrácená)")
    tree.heading("Celkem", text="Celkem")
    tree.heading("Správně", text="Správně")
    tree.heading("Špatně", text="Špatně")
    tree.heading("Úspěšnost", text="Úspěšnost")
    tree.column("ID", width=60, anchor="center")
    tree.column("Otázka", width=550, anchor="w")
    tree.column("Celkem", width=70, anchor="center")
    tree.column("Správně", width=70, anchor="center")
    tree.column("Špatně", width=70, anchor="center")
    tree.column("Úspěšnost", width=100, anchor="center")

    # Data do tabulky
    for qid in sorted(stats, key=lambda x: int(x)):
        stat = stats[qid]
        q_text = id_to_question.get(qid, {}).get("question", "??")
        q_short = (q_text[:65] + "...") if len(q_text) > 65 else q_text
        percent = 0
        if stat["total"] > 0:
            percent = 100 * stat["correct"] / stat["total"]
        total += stat["total"]
        correct += stat["correct"]
        wrong += stat["wrong"]
        tree.insert("", "end", values=(qid, q_short, stat["total"], stat["correct"], stat["wrong"], f"{percent:.1f} %"))

    # Souhrnné statistiky dole v bottom_panel
    total_percent = 100 * correct / total if total > 0 else 0
    summary_text = (
        f"Celkem odpovědí: {total}\n"
        f"Správně: {correct}\n"
        f"Špatně: {wrong}\n"
        f"Průměrná úspěšnost: {total_percent:.1f} %"
    )
    summary_label = tk.Label(bottom_panel, text=summary_text, font=("Arial", 12, "bold"), fg="blue", anchor="w", justify="left")
    summary_label.pack(anchor="w", padx=10, pady=2)

    # Top 10 nejhorších otázek
    worst_questions = []
    for qid in stats:
        stat = stats[qid]
        total_ans = stat["total"]
        correct_ans = stat["correct"]
        if total_ans > 0:
            success = 100 * correct_ans / total_ans
            q_text = id_to_question.get(qid, {}).get("question", "??")
            q_short = (q_text[:85] + "...") if len(q_text) > 85 else q_text
            worst_questions.append((success, qid, q_short, total_ans))
    worst_questions.sort()  # od nejnižší úspěšnosti nahoru

    top_n = 10
    worst_label_text = "Top 10 nejhorších otázek:\n"
    for idx, (success, qid, q_short, total_ans) in enumerate(worst_questions[:top_n], 1):
        worst_label_text += f"{idx}. [ID {qid}] {q_short} ({success:.1f} %, pokusy: {total_ans})\n"

    worst_label = tk.Label(bottom_panel, text=worst_label_text, font=("Arial", 11), fg="black", anchor="w", justify="left")
    worst_label.pack(anchor="w", padx=10, pady=(2, 2))

    # --- Tlačítka Reset a Zavřít dole ---
    btns = tk.Frame(bottom_panel)
    btns.pack(anchor="center", pady=7)
    def reset_stats():
        if messagebox.askyesno("Potvrdit reset", "Opravdu chceš vymazat všechny statistiky?"):
            save_stats(STATS_FILE, {})
            stats_win.destroy()
            show_stats_window()
    btn_reset = tk.Button(btns, text="Resetovat statistiky", font=("Arial", 11), command=reset_stats)
    btn_reset.pack(side="left", padx=10)
    btn_close = tk.Button(btns, text="Zavřít", font=("Arial", 11), command=stats_win.destroy)
    btn_close.pack(side="left", padx=10)

    # --- Detail otázky po kliknutí na řádek ---
    def on_tree_select(event):
        item_id = tree.focus()
        if not item_id:
            return
        values = tree.item(item_id, "values")
        qid = values[0]
        q = id_to_question.get(str(qid))
        if not q:
            messagebox.showerror("Chyba", f"Otázka s ID {qid} nebyla nalezena.")
            return

        # Otevřít nové okno s detailním zobrazením otázky + správných odpovědí
        detail_win = tk.Toplevel(stats_win)
        detail_win.title(f"Otázka {qid} – Detail")
        detail_win.geometry("950x500")

        lbl_question = tk.Label(detail_win, text=q["question"], font=("Arial", 14), wraplength=900, justify="left")
        lbl_question.pack(pady=15)

        if "table" in q:
            table = q["table"]
            table_frame = tk.Frame(detail_win)
            table_frame.pack(pady=5)
            for col, val in enumerate(table["header"]):
                l = tk.Label(table_frame, text=str(val), font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padx=4, pady=2)
                l.grid(row=0, column=col, sticky="nsew")
            for row_idx, row in enumerate(table["rows"], 1):
                for col, val in enumerate(row):
                    l = tk.Label(table_frame, text=str(val), font=("Arial", 10), borderwidth=1, relief="solid", padx=4, pady=2)
                    l.grid(row=row_idx, column=col, sticky="nsew")

        option_keys = list(string.ascii_lowercase)
        original_options = list(q["options"].items())
        for idx, (orig_key, value) in enumerate(original_options):
            is_correct = orig_key in q["answer"]
            mark = "✅" if is_correct else ""
            color = "green" if is_correct else "black"
            frame = tk.Frame(detail_win)
            frame.pack(fill="x", anchor="w", pady=2)
            lbl = tk.Label(
                frame,
                text=f"{mark} {option_keys[idx]}) {value}",
                fg=color,
                font=("Arial", 12),
                anchor="w",
                justify="left",
                wraplength=900
            )
            lbl.pack(side="left", fill="x", expand=True, anchor="w")

        # ---- Zobrazení vysvětlení pod možnostmi ----
        if q.get("explanation"):
            explanation_label = tk.Label(
                detail_win,
                text=f"Vysvětlení: {q['explanation']}",
                font=("Arial", 11, "italic"),
                fg="gray20",
                wraplength=900,
                justify="left"
            )
            explanation_label.pack(pady=(8, 12), anchor="w")

    tree.bind("<Double-1>", on_tree_select)

# ---- QuizApp třída, start_quiz a show_main_menu (beze změn) ----

class QuizApp:
    def __init__(self, master, questions, view_mode=False, show_main_menu=None, resume_data=None):
        self.stats = load_stats(STATS_FILE)
        self.master = master
        self.master.title("Quiz")
        self.master.geometry("1080x820")
        self.master.resizable(False, False)
        self.kolo = 1
        self.counter_label = tk.Label(master, text="", font=("Arial", 12))
        self.counter_label.pack(pady=2)
        self.round_label = tk.Label(master, text="", font=("Arial", 11, "italic"))
        self.round_label.pack(pady=2)
        self.question_label = tk.Label(master, text="", font=("Arial", 14), wraplength=1000)
        self.question_label.pack(pady=10)
        self.options_frame = tk.Frame(master)
        self.options_frame.pack()
        self.feedback_label = tk.Label(master, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=10)
        self.button = tk.Button(master, text="Odpovědět", command=self.check_answer)
        self.button.pack(pady=5)
        self.restart_button = tk.Button(master, text="Nový test", command=self.restart, state="disabled")
        self.restart_button.pack(pady=2)
        self.menu_button = tk.Button(master, text="Zpět do hlavního menu", font=("Arial", 12), command=self._back_to_menu)
        self.menu_button.pack(pady=8)
        self.all_questions = questions.copy()
        self.view_mode = view_mode
        self.show_main_menu = show_main_menu
        self.master.bind('<Return>', lambda event: self.button.invoke())
        self.master.bind('<Escape>', lambda event: self._back_to_menu())
        self.option_keys = list(string.ascii_lowercase)
        self.current_option_mapping = {}
        if resume_data:
            self.load_from_session(resume_data)
        else:
            self.reset_quiz()
        self.show_question()

    def _back_to_menu(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        if self.show_main_menu:
            self.show_main_menu()

    def reset_quiz(self):
        self.question_list = self.all_questions.copy()
        random.shuffle(self.question_list)
        self.question_index = 0
        self.score = 0
        self.vars = {}
        self.wrong_questions = []
        self.mode = "first_run"
        self.kolo = 1
        self.round_label.config(text="")
        self.question_label.config(font=("Arial", 14), pady=0)

    def load_from_session(self, data):
        self.question_list = data["question_list"]
        self.question_index = data["question_index"]
        self.kolo = data["kolo"]
        self.mode = data["mode"]
        self.score = data["score"]
        self.wrong_questions = data["wrong_questions"]
        self.all_questions = data["all_questions"]
        self.vars = {}
        self.round_label.config(text="")

    def get_session_data(self):
        return {
            "question_list": self.question_list,
            "question_index": self.question_index,
            "kolo": self.kolo,
            "mode": self.mode,
            "score": self.score,
            "wrong_questions": self.wrong_questions,
            "all_questions": self.all_questions,
        }

    def save_progress(self):
        if not self.view_mode:
            save_session(self.get_session_data())

    def show_question(self):
        self.save_progress()
        self.vars.clear()
        self.current_option_mapping = {}
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.feedback_label.config(text="", fg="black")
        q = self.question_list[self.question_index]
        total = len(self.question_list)
        self.counter_label.config(text=f"Otázka {self.question_index + 1} / {total}")
        if self.mode == "first_run":
            self.round_label.config(text="První kolo")
        else:
            self.round_label.config(text=f"Opakovací kolo {self.kolo - 1}")
        self.question_label.config(text=q["question"])

        if "table" in q:
            table = q["table"]
            table_frame = tk.Frame(self.options_frame)
            table_frame.pack(pady=5, fill="x", expand=True)
            for col, val in enumerate(table["header"]):
                l = tk.Label(table_frame, text=str(val), font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padx=4, pady=2)
                l.grid(row=0, column=col, sticky="nsew")
            for row_idx, row in enumerate(table["rows"], 1):
                for col, val in enumerate(row):
                    l = tk.Label(table_frame, text=str(val), font=("Arial", 10), borderwidth=1, relief="solid", padx=4, pady=2)
                    l.grid(row=row_idx, column=col, sticky="nsew")

        original_options = list(q["options"].items())
        random.shuffle(original_options)
        option_labels = self.option_keys[:len(original_options)]
        self.current_option_mapping = {}
        for idx, (orig_key, value) in enumerate(original_options):
            new_key = option_labels[idx]
            self.current_option_mapping[new_key] = orig_key
            var = tk.BooleanVar()
            frame = tk.Frame(self.options_frame)
            frame.pack(fill="x", anchor="w", pady=2)
            cb = tk.Checkbutton(frame, variable=var)
            cb.pack(side="left")
            lbl = tk.Label(
                frame,
                text=f"{new_key}) {value}",
                font=("Arial", 12),
                anchor="w",
                justify="left",
                wraplength=950
            )
            lbl.pack(side="left", fill="x", expand=True)
            self.vars[new_key] = var

        if self.view_mode:
            self.show_correct_answers()
            self.button.config(text="Další", command=self.next_question)
            self.restart_button.config(state="disabled")
        else:
            self.button.config(text="Odpovědět", state="normal")
            self.restart_button.config(state="disabled")

    def show_correct_answers(self):
        q = self.question_list[self.question_index]
        correct_set = q["answer"]
        display_keys = list(self.vars.keys())
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        for key in display_keys:
            original_key = self.current_option_mapping[key]
            is_correct = original_key in correct_set
            if is_correct:
                mark = "✅"
                color = "green"
            else:
                mark = ""
                color = "black"
            text = f"{mark} {key}) {q['options'][original_key]}"
            lbl = tk.Label(self.options_frame, text=text, fg=color, font=("Arial", 12), anchor="w")
            lbl.pack(fill="x", anchor="w")
        self.feedback_label.config(text="Správná odpověď je zvýrazněná.", fg="blue")
        if q.get("explanation"):
            explanation_label = tk.Label(
                self.options_frame,
                text=f"Vysvětlení: {q['explanation']}",
                font=("Arial", 11, "italic"),
                fg="gray20",
                wraplength=950,
                justify="left"
            )
            explanation_label.pack(fill="x", anchor="w", pady=(6, 0))

    def check_answer(self):
        if self.view_mode:
            self.next_question()
            return
        q = self.question_list[self.question_index]
        question_id = q.get("id")
        if question_id is not None:
            str_id = str(question_id)
            if str_id not in self.stats:
                self.stats[str_id] = {"total": 0, "correct": 0, "wrong": 0}
            self.stats[str_id]["total"] += 1

        user_selected_new = {k for k, v in self.vars.items() if v.get()}
        user_set = {self.current_option_mapping[k] for k in user_selected_new}
        correct_set = q["answer"]
        display_keys = list(self.vars.keys())
        correct = user_set == correct_set

        for widget in self.options_frame.winfo_children():
            widget.destroy()
        for key in display_keys:
            original_key = self.current_option_mapping[key]
            is_correct = original_key in correct_set
            checked = key in user_selected_new
            if is_correct and checked:
                mark = "✅"
                color = "green"
            elif is_correct and not checked:
                mark = "➕"
                color = "orange"
            elif not is_correct and checked:
                mark = "❌"
                color = "red"
            else:
                mark = ""
                color = "black"
            frame = tk.Frame(self.options_frame)
            frame.pack(fill="x", anchor="w", pady=1)
            lbl = tk.Label(
                frame,
                text=f"{mark} {key}) {q['options'][original_key]}",
                fg=color,
                font=("Arial", 12),
                anchor="w",
                justify="left",
                wraplength=900
            )
            lbl.pack(side="left", fill="x", expand=True, anchor="w")

        if correct:
            self.feedback_label.config(text="Správně!", fg="green")
            self.score += 1
            if question_id is not None:
                self.stats[str_id]["correct"] += 1
        else:
            self.feedback_label.config(text="Špatně!", fg="red")
            if q not in self.wrong_questions:
                self.wrong_questions.append(q)
            if question_id is not None:
                self.stats[str_id]["wrong"] += 1

        save_stats(STATS_FILE, self.stats)
        if q.get("explanation"):
            explanation_label = tk.Label(
                self.options_frame,
                text=f"Vysvětlení: {q['explanation']}",
                font=("Arial", 11, "italic"),
                fg="gray20",
                wraplength=950,
                justify="left"
            )
            explanation_label.pack(fill="x", anchor="w", pady=(6, 0))
        self.button.config(text="Další", command=self.next_question)
        self.save_progress()

    def next_question(self):
        self.question_index += 1
        if self.question_index < len(self.question_list):
            self.show_question()
            self.button.config(text="Odpovědět", command=self.check_answer)
        else:
            if self.wrong_questions:
                self.kolo += 1
                self.question_list = self.wrong_questions.copy()
                self.wrong_questions = []
                self.question_index = 0
                if self.mode == "first_run":
                    self.mode = "repeat_wrong"
                messagebox.showinfo("Opakování", f"Teď si zopakuješ špatně zodpovězené otázky!\n(Opakovací kolo {self.kolo - 1})")
                self.show_question()
                self.button.config(text="Odpovědět", command=self.check_answer)
            else:
                self.end_quiz()

    def end_quiz(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.question_label.config(text="🥳", font=("Arial", 48), pady=20)
        self.counter_label.config(text="")
        self.round_label.config(text="")
        text = f"Hotovo! Zvládl/a jsi správně odpovědět na všechny otázky.\n"
        text += f"Počet kol (včetně prvního): {self.kolo}"
        self.feedback_label.config(text=text, fg="blue")
        self.button.config(state="disabled")
        self.menu_button.config(state="normal")
        if self.view_mode:
            self.restart_button.config(state="disabled")
        else:
            self.restart_button.config(state="normal")
            clear_session()  # Po dokončení vymaž session

    def restart(self):
        self.reset_quiz()
        self.show_question()
        self.button.config(state="normal")
        self.feedback_label.config(text="")
        self.restart_button.config(state="disabled")
        clear_session()

def start_quiz(selected_questions, view_mode=False, resume_data=None):
    clear_session()   # smaže případný progres před začátkem nového testu
    for widget in root.winfo_children():
        widget.destroy()
    app = QuizApp(root, selected_questions, view_mode=view_mode, show_main_menu=show_main_menu, resume_data=resume_data)

def continue_last_test():
    data = load_session()
    if not data:
        messagebox.showerror("Chyba", "Nenalezena rozpracovaná session.")
        return
    # Převod všech dictů zpět na set pro "answer"
    def restore_answers(q_list):
        for q in q_list:
            if isinstance(q.get("answer"), list):
                q["answer"] = set(q["answer"])
        return q_list
    data["question_list"] = restore_answers(data["question_list"])
    data["all_questions"] = restore_answers(data["all_questions"])
    data["wrong_questions"] = restore_answers(data["wrong_questions"])
    start_quiz(data["all_questions"], view_mode=False, resume_data=data)

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
        command=lambda: start_quiz([q for q in ALL_QUESTIONS if q.get("type") == "theoretical"])
    )
    btn_theoretical.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    lbl_theoretical = tk.Label(frame, text=f"Otázek: {theoretical_count}", font=("Arial", 12))
    lbl_theoretical.grid(row=0, column=1, sticky="w")

    btn_practical = tk.Button(
        frame, text="Pouze praktické", font=("Arial", 14),
        width=20,
        command=lambda: start_quiz([q for q in ALL_QUESTIONS if q.get("type") == "practical"])
    )
    btn_practical.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    lbl_practical = tk.Label(frame, text=f"Otázek: {practical_count}", font=("Arial", 12))
    lbl_practical.grid(row=1, column=1, sticky="w")

    btn_all = tk.Button(
        frame, text="Všechny otázky", font=("Arial", 14),
        width=20,
        command=lambda: start_quiz(ALL_QUESTIONS)
    )
    btn_all.grid(row=2, column=0, padx=10, pady=10, sticky="e")
    lbl_all = tk.Label(frame, text=f"Otázek: {all_count}", font=("Arial", 12))
    lbl_all.grid(row=2, column=1, sticky="w")

    btn_view = tk.Button(
        frame, text="Pouze prohlížení otázek (se správnými odpověďmi)", font=("Arial", 14),
        width=40,
        command=lambda: start_quiz(ALL_QUESTIONS, view_mode=True)
    )
    btn_view.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

    # Nové tlačítko "Pokračovat v testu"
    session_exists = os.path.exists(SESSION_FILE)
    btn_continue = tk.Button(
        root, text="Pokračovat v testu", font=("Arial", 14),
        width=30,
        state="normal" if session_exists else "disabled",
        command=continue_last_test
    )
    btn_continue.pack(pady=12)

    btn_stats = tk.Button(
        root, text="Statistiky", font=("Arial", 14),
        width=30,
        command=show_stats_window
    )
    btn_stats.pack(pady=8)

# ---- Start aplikace ----

root = tk.Tk()
show_main_menu()
root.mainloop()
