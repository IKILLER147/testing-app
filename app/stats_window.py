# stats_window.py

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import string

def show_stats_window(root, ALL_QUESTIONS, load_stats, save_stats, show_stats_window_ref):
    stats = load_stats()
    stats_win = tk.Toplevel(root)
    stats_win.title("Statistiky otázek")
    stats_win.geometry("980x600")
    stats_win.resizable(True, True)

    main_frame = tk.Frame(stats_win)
    main_frame.pack(side="top", fill="both", expand=True)
    bottom_panel = tk.Frame(stats_win)
    bottom_panel.pack(side="bottom", fill="x")

    id_to_question = {str(q.get("id")): q for q in ALL_QUESTIONS}
    total, correct, wrong = 0, 0, 0

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

    total_percent = 100 * correct / total if total > 0 else 0
    summary_text = (
        f"Celkem odpovědí: {total}\n"
        f"Správně: {correct}\n"
        f"Špatně: {wrong}\n"
        f"Průměrná úspěšnost: {total_percent:.1f} %"
    )
    summary_label = tk.Label(bottom_panel, text=summary_text, font=("Arial", 12, "bold"), fg="blue", anchor="w", justify="left")
    summary_label.pack(anchor="w", padx=10, pady=2)

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
    worst_questions.sort()

    top_n = 10
    worst_label_text = "Top 10 nejhorších otázek:\n"
    for idx, (success, qid, q_short, total_ans) in enumerate(worst_questions[:top_n], 1):
        worst_label_text += f"{idx}. [ID {qid}] {q_short} ({success:.1f} %, pokusy: {total_ans})\n"

    worst_label = tk.Label(bottom_panel, text=worst_label_text, font=("Arial", 11), fg="black", anchor="w", justify="left")
    worst_label.pack(anchor="w", padx=10, pady=(2, 2))

    btns = tk.Frame(bottom_panel)
    btns.pack(anchor="center", pady=7)
    def reset_stats():
        if messagebox.askyesno("Potvrdit reset", "Opravdu chceš vymazat všechny statistiky?"):
            save_stats({})
            stats_win.destroy()
            # Rekurzivní volání (musí být referencované přes show_stats_window_ref kvůli cyklickému importu)
            show_stats_window_ref(root, ALL_QUESTIONS, load_stats, save_stats, show_stats_window_ref)
    btn_reset = tk.Button(btns, text="Resetovat statistiky", font=("Arial", 11), command=reset_stats)
    btn_reset.pack(side="left", padx=10)
    btn_close = tk.Button(btns, text="Zavřít", font=("Arial", 11), command=stats_win.destroy)
    btn_close.pack(side="left", padx=10)

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
