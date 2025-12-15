import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import threading

# Try importing winsound (Windows)py
try:
    import winsound
    WINSOUND_AVAILABLE = True
except Exception:
    winsound = None
    WINSOUND_AVAILABLE = False

# -------------------- Constants --------------------
FLASH_JSON = "flashcards.json"
BGM_FILE = "bgm.wav"

# Color scheme
GAME_LOBBY_BG = "#BFD7EA"  # Baby Blue
NAV_BTN_BG = "#F7D6E0"     # Baby Pink
CARD_FRAME_BG = "#DFF5E3"  # Mint Cream
CARD_LABEL_BG = "#E5D9F2"  # Soft Lilac
STATUS_BG = "#FCF7DE"      # Honeydew
TEXT_COLOR = "#000000"
BUTTON_COLOR = "#F7D6E0"
SUBMIT_COLOR = "#3498DB"

FONT_STYLE = ("Helvetica", 18, "bold")
CARD_FONT_STYLE = ("Helvetica", 23, "italic")
SCORE_FONT_STYLE = ("Helvetica", 15)

QUESTION_COLORS = [
    "#F4DF26", "#F79CA6", "#B4E57C",
    "#C2AAEE", "#FCD191", "#F79ABA", "#C7EE9A"
]

FALLBACK_FLASHCARDS = [
    ("What is Python?", "A high-level programming language."),
    ("What is a variable?", "A container that stores data."),
    ("What is a loop?", "A structure that repeats actions."),
    ("What is a function?", "A reusable block of code."),
    ("What planet is known as the Red Planet?", "Mars"),
    ("What is H2O?", "Water"),
]

# -------------------- Helpers --------------------
def safe_load_flashcards():
    cards = []
    if os.path.exists(FLASH_JSON):
        try:
            with open(FLASH_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    cards.append({"q": str(item[0]), "a": str(item[1]), "answered": False})
                elif isinstance(item, dict):
                    q = item.get("question") or item.get("q")
                    a = item.get("answer") or item.get("a")
                    if q and a:
                        cards.append({"q": str(q), "a": str(a), "answered": False})
        except:
            pass
    if not cards:
        for q, a in FALLBACK_FLASHCARDS:
            cards.append({"q": q, "a": a, "answered": False})
    return cards

def safe_save_flashcards(cards):
    try:
        with open(FLASH_JSON, "w", encoding="utf-8") as f:
            json.dump([[c["q"], c["a"]] for c in cards], f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save:\n{e}")

def play_wrong_sound():
    if WINSOUND_AVAILABLE:
        try: winsound.Beep(800, 250)
        except: pass

def play_correct_sound():
    if WINSOUND_AVAILABLE:
        try: winsound.Beep(700, 250)
        except: pass

# -------------------- Music Handler --------------------
class MusicThread:
    def __init__(self, filename):
        self.file = filename
        self.running = False
        self.muted = False

    def start(self):
        if not WINSOUND_AVAILABLE or not self.file:
            return
        if not os.path.exists(self.file):
            return
        try:
            winsound.PlaySound(self.file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            self.running = True
            self.muted = False
        except:
            self.running = False

    def stop(self):
        if not WINSOUND_AVAILABLE:
            return
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
        self.running = False

    def toggle_mute(self):
        if not WINSOUND_AVAILABLE:
            return
        if not self.running:
            if self.file and os.path.exists(self.file):
                try:
                    winsound.PlaySound(self.file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                    self.running = True
                    self.muted = False
                except:
                    self.running = False
            return

        if self.muted:
            if self.file and os.path.exists(self.file):
                try:
                    winsound.PlaySound(self.file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                    self.muted = False
                    self.running = True
                except:
                    self.muted = True
        else:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
                self.muted = True
                self.running = False
            except:
                pass

# -------------------- Main App --------------------
class FlashcardApp:
    def __init__(self):
        self.flashcards = safe_load_flashcards()
        random.shuffle(self.flashcards)

        self.score = 0
        self.card_index = 0

        global EXTRA_MUSIC_PATH
        try:
            EXTRA_MUSIC_PATH
        except NameError:
            EXTRA_MUSIC_PATH = None

        music_file = None
        if os.path.exists(BGM_FILE):
            music_file = BGM_FILE
        elif EXTRA_MUSIC_PATH and os.path.exists(EXTRA_MUSIC_PATH):
            music_file = EXTRA_MUSIC_PATH

        self.music = MusicThread(music_file)
        self.music.start()

        self.show_intro()

    # -------------------- START PROGRAM --------------------
    def start_program(self):
        self.intro.destroy()
        self.main_window()

    # -------------------- INTRO --------------------
    def show_intro(self):
        self.intro = tk.Tk()
        self.intro.title("StudyStack")
        self.intro.geometry("900x600")
        self.intro.config(bg=GAME_LOBBY_BG)

        mid_frame = tk.Frame(self.intro, bg=GAME_LOBBY_BG)
        mid_frame.pack(fill="both", expand=True)

        emoji_lbl = tk.Label(mid_frame, text="🎓📚✨", font=("Helvetica", 48),
                             bg=GAME_LOBBY_BG, fg="#E66D89")
        emoji_lbl.pack(pady=40)

        lbl = tk.Label(mid_frame, text="Welcome to StudyStack",
                       font=("Helvetica", 48, "bold"),
                       fg="#30475E", bg=GAME_LOBBY_BG)
        lbl.pack(pady=20)

        slogan = tk.Label(mid_frame, text="Learn. Play. Remember.",
                          font=("Helvetica", 28, "italic"),
                          fg="#34495E", bg=GAME_LOBBY_BG)
        slogan.pack(pady=10)

        start_btn = tk.Button(mid_frame, text="Start Game",
                              font=("Helvetica", 26, "bold"),
                              bg=CARD_FRAME_BG, fg="#2D455E",
                              width=20, command=self.start_program)
        start_btn.pack(pady=10)

        instr_btn = tk.Button(mid_frame, text="Instructions",
                              font=("Helvetica", 22, "bold"),
                              bg=CARD_LABEL_BG, fg="#324C65",
                              width=20, command=self.show_instructions)
        instr_btn.pack(pady=10)

        about_btn = tk.Button(mid_frame, text="About",
                              font=("Helvetica", 22, "bold"),
                              bg=NAV_BTN_BG, fg="#34495E",
                              width=20, command=self.show_about)
        about_btn.pack(pady=10)

        exit_btn = tk.Button(mid_frame, text="Exit",
                             font=("Helvetica", 22, "bold"),
                             bg=STATUS_BG, fg="#34495E",
                             width=20, command=self.intro.destroy)
        exit_btn.pack(pady=10)

        self.intro.mainloop()

    # -------------------- INSTRUCTIONS --------------------
    def show_instructions(self):
        messagebox.showinfo(
            "Instructions",
            "HOW TO USE STUDYSTACK:\n\n"
            "1. Click START to begin the flashcard quiz.\n"
            "2. A question appears on the card.\n"
            "3. Type your answer in the box and press SUBMIT.\n"
            "4. The card flips and shows if you are correct.\n"
            "5. Navigate cards using NEXT and PREV.\n"
            "6. Add new flashcards using 'Add Card'.\n"
            "7. Delete flashcards using 'Delete Card'.\n"
            "8. Enjoy learning!"
        )

    # -------------------- ABOUT --------------------
    def show_about(self):
        messagebox.showinfo(
            "About",
            "STUDYSTACK FLASHCARD APP\n\n"
            "Created for learning and review.\n\n"
            "StudyStack is a Python-based flashcard system designed to support efficient learning and self-assessment." \
            " By allowing users to add, view, and delete questions, the program offers a flexible and personalized study experience. Whether preparing for exams, " \
            "reviewing lessons, or simply testing one’s general knowledge, StudyStack provides an interactive and visually clear way to learn and retain information. " \
            "Its simple structure makes it accessible for all types of learners who want a convenient tool to practice anytime "
            " Developed by:\n"
            "• Mauna Kea B. Ordas\n"
            "• Gerold Santillan\n"
            "• Therence Trance"
        )

    # -------------------- BACK TO INTRO --------------------
    def back_to_intro(self):
        if messagebox.askyesno("Exit", "Are you sure you want to go back to the main menu?"):
            self.root.destroy()
            self.show_intro()

    # -------------------- RESTART GAME --------------------
    def restart_game(self):
        if messagebox.askyesno("Restart", "Restart the game and reset score?"):
            self.score = 0
            self.card_index = 0
            for c in self.flashcards:
                c["answered"] = False
                c.pop("answered_correctly", None)
            random.shuffle(self.flashcards)
            self.score_label.config(text=f"Score: {self.score}")
            self.display_card()

    # -------------------- MAIN WINDOW --------------------
    def main_window(self):
        self.root = tk.Tk()
        self.root.title("Flashcards")
        self.root.geometry("900x700")
        self.root.config(bg=GAME_LOBBY_BG)

        exit_btn = tk.Button(self.root, text="⏴ Back to Menu",
                             font=("Helvetica", 12, "bold"),
                             bg="#E74C3C", fg="white",
                             command=self.back_to_intro)
        exit_btn.place(x=10, y=10)

        restart_btn = tk.Button(self.root, text="🔄 Restart", font=("Helvetica", 12, "bold"),
                                bg="#3498DB", fg="white", command=self.restart_game)
        restart_btn.place(x=1430, y=10)

        if WINSOUND_AVAILABLE and self.music.file and os.path.exists(self.music.file):
            mute_text = "🔊 Mute" if not self.music.muted else "🔈 Unmute"
            self.mute_btn = tk.Button(self.root, text=mute_text, font=("Helvetica", 12, "bold"),
                                      bg="#95A5A6", fg="white",
                                      command=self.toggle_mute)
        else:
            self.mute_btn = tk.Button(self.root, text="No Sound", font=("Helvetica", 12, "bold"),
                                      bg="#95A5A6", fg="white", state=tk.DISABLED)
        self.mute_btn.place(x=1320, y=10)

        top = tk.Frame(self.root, bg=GAME_LOBBY_BG)
        top.pack(pady=20)

        self.score_label = tk.Label(top, text=f"Score: {self.score}",
                                    font=SCORE_FONT_STYLE, fg=TEXT_COLOR, bg=GAME_LOBBY_BG)
        self.score_label.pack(side="left", padx=10)

        self.card_index_label = tk.Label(self.root, text="", font=("Helvetica", 18, "bold"),
                                         bg=GAME_LOBBY_BG, fg=TEXT_COLOR)
        self.card_index_label.pack(pady=5)

        self.card_frame = tk.Frame(self.root, width=819, height=293, bg=CARD_FRAME_BG,
                                   bd=3, relief="raised")
        self.card_frame.pack(pady=10)
        self.card_frame.pack_propagate(False)

        self.card_label = tk.Label(self.card_frame, text="", font=CARD_FONT_STYLE,
                                   bg=CARD_LABEL_BG, fg=TEXT_COLOR, wraplength=753)
        self.card_label.place(relx=0.5, rely=0.5, anchor="center")

        input_frame = tk.Frame(self.root, bg=GAME_LOBBY_BG)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Your Answer:",
                 font=FONT_STYLE, fg=TEXT_COLOR, bg=GAME_LOBBY_BG).grid(row=0, column=0)

        self.answer_entry = tk.Entry(input_frame, width=44, font=("Helvetica", 20))
        self.answer_entry.grid(row=0, column=4, padx=12)

        submit_btn = tk.Button(self.root, text="SUBMIT ANSWER",
                               font=FONT_STYLE, bg=SUBMIT_COLOR, fg="white",
                               width=29, height=2, command=self.submit_answer)
        submit_btn.pack(pady=10)

        nav = tk.Frame(self.root, bg=GAME_LOBBY_BG)
        nav.pack(pady=10)

        # Save button references for easy enabling/disabling
        self.prev_btn = tk.Button(nav, text="<< Prev", bg=NAV_BTN_BG, fg=TEXT_COLOR,
                                  font=FONT_STYLE, width=15, height=2, command=self.prev_card)
        self.prev_btn.grid(row=0, column=0, padx=8)

        self.next_btn = tk.Button(nav, text="Next >>", bg=NAV_BTN_BG, fg=TEXT_COLOR,
                                  font=FONT_STYLE, width=15, height=2, command=self.next_card)
        self.next_btn.grid(row=0, column=1, padx=8)

        manage = tk.Frame(self.root, bg=GAME_LOBBY_BG)
        manage.pack(pady=10)

        tk.Button(manage, text="Add Card", bg="#53D489", fg="white",
                  font=("Helvetica", 18, "bold"), width=15, height=2,
                  command=self.add_card_window).grid(row=0, column=0, padx=10)

        tk.Button(manage, text="Delete Card", bg="#E7695B", fg="white",
                  font=("Helvetica", 18, "bold"), width=15, height=2,
                  command=self.delete_card).grid(row=0, column=1, padx=10)

        self.status = tk.Label(self.root, text="", fg=TEXT_COLOR, bg=STATUS_BG, font=SCORE_FONT_STYLE)
        self.status.pack()

        self.display_card(initial=True)
        self.root.mainloop()

    # -------------------- MUTE BUTTON CALLBACK --------------------
    def toggle_mute(self):
        self.music.toggle_mute()
        if not WINSOUND_AVAILABLE or not self.music.file:
            return
        if self.music.muted or not self.music.running:
            self.mute_btn.config(text="🔈 Unmute")
        else:
            self.mute_btn.config(text="🔊 Mute")

    # -------------------- DISPLAY CARD --------------------
    def display_card(self, initial=False):
        if not self.flashcards:
            self.card_label.config(text="No flashcards available.")
            self.card_index_label.config(text="")
            self.update_nav_buttons()
            return

        if all(c["answered"] for c in self.flashcards):
            correct_count = sum(c.get("answered_correctly", False) for c in self.flashcards)
            self.card_frame.config(bg=CARD_FRAME_BG)
            self.card_label.config(
                bg=CARD_LABEL_BG,
                fg=TEXT_COLOR,
                text=f"🏁 Finished!\n\nYou answered {correct_count} correct out of {len(self.flashcards)}."
            )
            self.answer_entry.delete(0, tk.END)
            self.card_index_label.config(text="All cards answered")
            self.update_nav_buttons()
            return

        q = self.flashcards[self.card_index]["q"]

        self.card_frame.config(bg=CARD_FRAME_BG)
        self.card_label.config(bg=CARD_LABEL_BG, text=q, fg=TEXT_COLOR)
        self.card_index_label.config(text=f"Card {self.card_index + 1} / {len(self.flashcards)}")
        self.answer_entry.delete(0, tk.END)
        self.status.config(text="")

        # Update navigation buttons
        self.update_nav_buttons()

    # -------------------- NAVIGATION BUTTON STATE --------------------
    def update_nav_buttons(self):
        """Enable or disable next/prev buttons based on current card index."""
        if not self.flashcards or len(self.flashcards) == 0:
            self.next_btn.config(state="disabled")
            self.prev_btn.config(state="disabled")
            return

        # Disable Prev if at first card
        if self.card_index == 0:
            self.prev_btn.config(state="disabled")
        else:
            self.prev_btn.config(state="normal")

        # Disable Next if at last card
        if self.card_index >= len(self.flashcards) - 1:
            self.next_btn.config(state="disabled")
        else:
            self.next_btn.config(state="normal")

    # -------------------- NAVIGATION --------------------
    def next_card(self):
        if not self.flashcards:
            return
        start_index = self.card_index
        while True:
            if self.card_index < len(self.flashcards) - 1:
                self.card_index += 1
            else:
                messagebox.showinfo("Info", "No more unanswered cards ahead.")
                self.card_index = start_index
                return
            if not self.flashcards[self.card_index]["answered"]:
                break
        self.display_card()

    def prev_card(self):
        if not self.flashcards:
            return
        start_index = self.card_index
        while True:
            if self.card_index > 0:
                self.card_index -= 1
            else:
                messagebox.showinfo("Info", "No more unanswered cards behind.")
                self.card_index = start_index
                return
            if not self.flashcards[self.card_index]["answered"]:
                break
        self.display_card()

    # -------------------- FLIP ANIMATION --------------------
    def flip_card_horizontal(self, callback, steps=15, delay=30):
        original_width = self.card_frame.winfo_width()

        def shrink(step=0):
            if step <= steps:
                factor = 1 - (step / steps)
                self.card_frame.config(width=int(max(1, original_width * factor)))
                self.root.after(delay, shrink, step + 1)
            else:
                callback()
                expand()

        def expand(step=0):
            if step <= steps:
                factor = step / steps
                self.card_frame.config(width=int(max(1, original_width * factor)))
                self.root.after(delay, expand, step + 1)
            else:
                self.card_frame.config(width=original_width)

        shrink()

    # -------------------- CHECK ANSWER --------------------
    def submit_answer(self):
        user = self.answer_entry.get().strip()
        if not user:
            messagebox.showerror("Error", "Please enter an answer before submitting.")
            return

        card = self.flashcards[self.card_index]
        correct = card["a"]

        def norm(s): return "".join(s.lower().split())

        def reveal_result():
            if norm(user) == norm(correct):
                play_correct_sound()
                self.score += 1
                card["answered_correctly"] = True
                self.score_label.config(text=f"Score: {self.score}")
                self.card_frame.config(bg="#2ecc71")
                self.card_label.config(bg="#2ecc71", fg="white",
                                        text=f"Correct!\nAnswer: {correct}")
            else:
                play_wrong_sound()
                card["answered_correctly"] = False
                self.card_frame.config(bg="#e74c3c")
                self.card_label.config(bg="#e74c3c", fg="white",
                                        text=f"The correct\nAnswer is: {correct}")

            card["answered"] = True

            if all(c["answered"] for c in self.flashcards):
                self.root.after(1500, self.display_card)
            else:
                self.root.after(3000, self.next_card)

        self.flip_card_horizontal(reveal_result)

    # -------------------- ADD / DELETE --------------------
    def add_card_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Flashcard")
        win.geometry("500x300")

        tk.Label(win, text="Question:", font=("Helvetica", 18)).pack(pady=5)
        q_entry = tk.Text(win, height=4, width=50)
        q_entry.pack()

        tk.Label(win, text="Answer:", font=("Helvetica", 18)).pack(pady=5)
        a_entry = tk.Entry(win, width=36, font=("Helvetica", 16))
        a_entry.pack()

        def save():
            q = q_entry.get("1.0", "end").strip()
            a = a_entry.get().strip()
            if not q or not a:
                messagebox.showerror("Error", "Both fields required.")
                return
            self.flashcards.append({"q": q, "a": a, "answered": False})
            safe_save_flashcards(self.flashcards)
            messagebox.showinfo("Saved", "Flashcard added!")
            win.destroy()
            self.card_index = len(self.flashcards) - 1
            self.display_card()

        tk.Button(win, text="Save", bg=SUBMIT_COLOR, fg="white",
                  font=("Helvetica", 12, "bold"), command=save).pack(pady=10)

    def delete_card(self):
        if not self.flashcards:
            return
        card = self.flashcards[self.card_index]
        if messagebox.askyesno("Delete", f"Delete this card?\n\n{card['q']}\n{card['a']}"):
            del self.flashcards[self.card_index]
            safe_save_flashcards(self.flashcards)
            if self.card_index >= len(self.flashcards):
                self.card_index = max(0, len(self.flashcards) - 1)
            self.display_card()


# -------------------- RUN --------------------
if __name__ == "__main__":
    FlashcardApp()
