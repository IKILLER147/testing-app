import tkinter as tk
from tkinter import messagebox
import random
import string

from data import save_stats, save_session, load_session, clear_session

def clear_widgets(container):
    for widget in container.winfo_children():
        widget.destroy()

def restore_answers(q_list):
    for q in q_list:
        if isinstance(q.get("answer"), list):
            q["answer"] = set(q["answer"])
    return q_list

class QuizApp:
    def __init__(self, master, questions, view_mode=False, show_main_menu=None, resume_data=None):
        from data import load_stats
        self.stats = load_stats()
        self.master = master
        self.show_main_menu = show_main_menu
        self.view_mode = view_mode
        self.option_keys = list(string.ascii_lowercase)
        self.master.title("Quiz")
        self.master.geometry("1080x820")
        self.master.resizable(False, False)
        self._setup_widgets()
        self.all_questions = questions.copy()
        self.current_options = []
        self.elapsed_seconds = 0
        self._timer_running = False
        if resume_data:
            self._load_session(resume_data)
        else:
            self._reset_quiz()
        self._show_question()

    def _setup_widgets(self):
        self.counter_label = tk.Label(self.master, font=("Arial", 12))
        self.counter_label.pack(pady=2)
        self.round_label = tk.Label(self.master, font=("Arial", 11, "italic"))
        self.round_label.pack(pady=2)
        # Timer label bude vytvořen vždy, ale zobrazen pouze v testovacím režimu
        self.timer_label = tk.Label(self.master, font=("Arial", 12), fg="blue")
        if not self.view_mode:
            self.timer_label.pack(pady=2)
        self.question_label = tk.Label(self.master, font=("Arial", 14), wraplength=1000)
        self.question_label.pack(pady=10)
        self.options_frame = tk.Frame(self.master)
        self.options_frame.pack()
        self.feedback_label = tk.Label(self.master, font=("Arial", 12))
        self.feedback_label.pack(pady=10)
        self.button = tk.Button(self.master, command=self._check_answer)
        self.button.pack(pady=5)
        self.restart_button = tk.Button(self.master, text="Nový test", command=self._restart, state="disabled")
        self.restart_button.pack(pady=2)
        self.menu_button = tk.Button(self.master, text="Zpět do hlavního menu", font=("Arial", 12), command=self._back_to_menu)
        self.menu_button.pack(pady=8)
        self.master.bind('<Return>', lambda event: self.button.invoke())
        self.master.bind('<Escape>', lambda event: self._back_to_menu())

    def _start_timer(self):
        if not self._timer_running or self.view_mode:
            return
        mins, secs = divmod(self.elapsed_seconds, 60)
        self.timer_label.config(text=f"Doba trvání testu: {mins:02}:{secs:02}")
        self.elapsed_seconds += 1
        # Zajistí, že se další volání provede přesně po 1 sekundě
        self.master.after(1000, self._start_timer)

    def _back_to_menu(self):
        clear_widgets(self.master)
        self._timer_running = False
        if self.show_main_menu:
            self.show_main_menu()

    def _reset_quiz(self):
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
        self.current_options = []
        self.elapsed_seconds = 0
        self._timer_running = not self.view_mode
        if not self.view_mode:
            self._start_timer()

    def _load_session(self, data):
        self.question_list = data["question_list"]
        self.question_index = data["question_index"]
        self.kolo = data["kolo"]
        self.mode = data["mode"]
        self.score = data["score"]
        self.wrong_questions = data["wrong_questions"]
        self.all_questions = data["all_questions"]
        self.vars = {}
        self.current_options = data.get("current_options", [])
        self.elapsed_seconds = data.get("elapsed_seconds", 0)
        self._timer_running = not self.view_mode
        if not self.view_mode:
            self._start_timer()

    def _get_session_data(self):
        return {
            "question_list": self.question_list,
            "question_index": self.question_index,
            "kolo": self.kolo,
            "mode": self.mode,
            "score": self.score,
            "wrong_questions": self.wrong_questions,
            "all_questions": self.all_questions,
            "current_options": self.current_options,
            "elapsed_seconds": self.elapsed_seconds,
        }

    def _save_progress(self):
        if not self.view_mode:
            save_session(self._get_session_data())

    def _show_options(self, mark_correct=None, user_selected=None):
        clear_widgets(self.options_frame)
        self.vars = {}
        option_labels = self.option_keys[:len(self.current_options)]
        for idx, (orig_key, value) in enumerate(self.current_options):
            key = option_labels[idx]
            var = tk.BooleanVar()
            frame = tk.Frame(self.options_frame)
            frame.pack(fill="x", anchor="w", pady=2)
            cb = tk.Checkbutton(frame, variable=var)
            cb.pack(side="left")
            color = "black"
            mark = ""
            if mark_correct is not None:
                is_correct = orig_key in self.q["answer"]
                checked = user_selected and key in user_selected
                if is_correct and checked:
                    mark, color = "✅", "green"
                elif is_correct and not checked:
                    mark, color = "➕", "orange"
                elif not is_correct and checked:
                    mark, color = "❌", "red"
            lbl = tk.Label(frame, text=f"{mark} {key}) {value}", font=("Arial", 12), fg=color, anchor="w", justify="left", wraplength=950)
            lbl.pack(side="left", fill="x", expand=True)
            self.vars[key] = var
        return option_labels

    def _show_question(self):
        self._save_progress()
        self.feedback_label.config(text="", fg="black")
        self.q = self.question_list[self.question_index]
        total = len(self.question_list)
        self.counter_label.config(text=f"Otázka {self.question_index + 1} / {total}")
        self.round_label.config(text="První kolo" if self.mode == "first_run" else f"Opakovací kolo {self.kolo - 1}")
        self.question_label.config(text=self.q["question"])
        if "table" in self.q:
            pass
        self.current_options = list(self.q["options"].items())
        random.shuffle(self.current_options)
        self._show_options()
        if self.view_mode:
            self._show_correct_answers()
            self.button.config(text="Další", command=self._next_question)
            self.restart_button.config(state="disabled")
        else:
            self.button.config(text="Odpovědět", state="normal")
            self.restart_button.config(state="disabled")

    def _show_correct_answers(self):
        clear_widgets(self.options_frame)
        option_labels = self.option_keys[:len(self.current_options)]
        for idx, (orig_key, value) in enumerate(self.current_options):
            is_correct = orig_key in self.q["answer"]
            mark = "✅" if is_correct else ""
            color = "green" if is_correct else "black"
            text = f"{mark} {option_labels[idx]}) {value}"
            lbl = tk.Label(self.options_frame, text=text, fg=color, font=("Arial", 12), anchor="w")
            lbl.pack(fill="x", anchor="w")
        self.feedback_label.config(text="Správná odpověď je zvýrazněná.", fg="blue")
        if self.q.get("explanation"):
            explanation_label = tk.Label(
                self.options_frame,
                text=f"Vysvětlení: {self.q['explanation']}",
                font=("Arial", 11, "italic"),
                fg="gray20",
                wraplength=950,
                justify="left"
            )
            explanation_label.pack(fill="x", anchor="w", pady=(6, 0))

    def _check_answer(self):
        if self.view_mode:
            self._next_question()
            return
        question_id = self.q.get("id")
        if question_id is not None:
            str_id = str(question_id)
            self.stats.setdefault(str_id, {"total": 0, "correct": 0, "wrong": 0})
            self.stats[str_id]["total"] += 1
        option_labels = self.option_keys[:len(self.current_options)]
        user_selected = {k for k, v in self.vars.items() if v.get()}
        user_set = {self.current_options[option_labels.index(k)][0] for k in user_selected}
        correct = user_set == self.q["answer"]
        self._show_options(mark_correct=True, user_selected=user_selected)
        if correct:
            self.feedback_label.config(text="Správně!", fg="green")
            self.score += 1
            if question_id is not None:
                self.stats[str_id]["correct"] += 1
        else:
            self.feedback_label.config(text="Špatně!", fg="red")
            if self.q not in self.wrong_questions:
                self.wrong_questions.append(self.q)
            if question_id is not None:
                self.stats[str_id]["wrong"] += 1
        save_stats(self.stats)
        if self.q.get("explanation"):
            explanation_label = tk.Label(
                self.options_frame,
                text=f"Vysvětlení: {self.q['explanation']}",
                font=("Arial", 11, "italic"),
                fg="gray20",
                wraplength=950,
                justify="left"
            )
            explanation_label.pack(fill="x", anchor="w", pady=(6, 0))
        self.button.config(text="Další", command=self._next_question)
        self._save_progress()

    def _next_question(self):
        self.question_index += 1
        if self.question_index < len(self.question_list):
            self._show_question()
            self.button.config(text="Odpovědět", command=self._check_answer)
        else:
            if self.wrong_questions:
                self.kolo += 1
                self.question_list = self.wrong_questions.copy()
                self.wrong_questions = []
                self.question_index = 0
                if self.mode == "first_run":
                    self.mode = "repeat_wrong"
                messagebox.showinfo("Opakování", f"Teď si zopakuješ špatně zodpovězené otázky!\n(Opakovací kolo {self.kolo - 1})")
                self._show_question()
                self.button.config(text="Odpovědět", command=self._check_answer)
            else:
                self._end_quiz()

    def _end_quiz(self):
        clear_widgets(self.options_frame)
        self._timer_running = False
        self.question_label.config(text="🥳", font=("Arial", 48), pady=20)
        self.counter_label.config(text="")
        self.round_label.config(text="")
        text = f"Hotovo! Zvládl/a jsi správně odpovědět na všechny otázky.\n"
        text += f"Počet kol (včetně prvního): {self.kolo}\n"
        if not self.view_mode:
            mins, secs = divmod(self.elapsed_seconds, 60)
            text += f"Celkový čas: {mins:02}:{secs:02}"
            self.stats["latest_duration"] = self.elapsed_seconds
            save_stats(self.stats)
        self.feedback_label.config(text=text, fg="blue")
        self.button.config(state="disabled")
        self.menu_button.config(state="normal")
        if self.view_mode:
            self.restart_button.config(state="disabled")
        else:
            self.restart_button.config(state="normal")
            clear_session()

    def _restart(self):
        self._reset_quiz()
        self._show_question()
        self.button.config(state="normal")
        self.feedback_label.config(text="")
        self.restart_button.config(state="disabled")
        clear_session()

def start_quiz(root, selected_questions, show_main_menu, view_mode=False, resume_data=None):
    clear_session()
    for widget in root.winfo_children():
        widget.destroy()
    QuizApp(root, selected_questions, view_mode=view_mode, show_main_menu=show_main_menu, resume_data=resume_data)

def continue_last_test(root, ALL_QUESTIONS, show_main_menu):
    data = load_session()
    if not data:
        messagebox.showerror("Chyba", "Nenalezena rozpracovaná session.")
        return
    data["question_list"] = restore_answers(data["question_list"])
    data["all_questions"] = restore_answers(data["all_questions"])
    data["wrong_questions"] = restore_answers(data["wrong_questions"])
    start_quiz(
        root,
        data["all_questions"],
        show_main_menu,
        view_mode=False,
        resume_data=data
    )
