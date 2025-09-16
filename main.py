import speech_recognition as sr
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count
import string
import json
from easygui import buttonbox
from rapidfuzz import process, fuzz


# ---------------- JSON Loader ----------------
def load_isl_phrases(file_path="isl_phrases.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["phrases"]


ISL_PHRASES = load_isl_phrases()
ALPHABETS = list(string.ascii_lowercase)


# ---------------- Speech to Text ----------------
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("🎤 Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio).lower()
        print(f"✅ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand speech.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Could not request results; {e}")
        return None


# ---------------- Preprocess Text ----------------
def preprocess_text(text):
    for c in string.punctuation:
        text = text.replace(c, "")
    return text.strip().lower()


# ---------------- Display ISL GIF ----------------
class ImageLabel(tk.Label):
    """A label that displays images and plays them if they are gifs"""

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info["duration"]
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)


def display_gif(phrase):
    root = tk.Tk()
    lbl = ImageLabel(root)
    lbl.pack()
    gif_file = f"ISL_Gifs/{phrase}.gif"
    lbl.load(gif_file)
    root.mainloop()


# ---------------- Fallback: Spell Letters ----------------
def display_letters(text):
    for char in text:
        if char in ALPHABETS:
            img_path = f"letters/{char}.jpg"
            try:
                image = Image.open(img_path)
                img_array = np.asarray(image)
                plt.imshow(img_array)
                plt.draw()
                plt.pause(0.8)
            except FileNotFoundError:
                print(f"⚠️ Missing letter image: {char}")
    plt.close()


# ---------------- Find Best Match ----------------
def find_best_match(text):
    match, score, _ = process.extractOne(
        text, ISL_PHRASES, scorer=fuzz.token_sort_ratio
    )
    return match, score


# ---------------- Main Translator ----------------
def run_translator():
    while True:
        spoken_text = speech_to_text()
        if not spoken_text:
            continue

        processed_text = preprocess_text(spoken_text)

        if processed_text in ["goodbye", "bye", "good bye", "exit", "quit"]:
            print("👋 Exiting translator...")
            break

        best_match, score = find_best_match(processed_text)
        if score > 80:  # Fuzzy match threshold
            print(f"🔎 Matched '{processed_text}' → '{best_match}' (score: {score})")
            display_gif(best_match)
        else:
            print("🔤 No close match found. Showing letters...")
            display_letters(processed_text)


# ---------------- Entry Point ----------------
if __name__ == "__main__":
    while True:
        image = "signlang.png"  # Optional logo image
        msg = "HEARING IMPAIRMENT ASSISTANT"
        choices = ["🎙 Live Voice", "❌ Exit"]
        reply = buttonbox(msg, image=image, choices=choices)

        if reply == choices[0]:
            run_translator()
        elif reply == choices[1]:
            quit()
