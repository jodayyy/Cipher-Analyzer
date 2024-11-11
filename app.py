import tkinter as tk
from tkinter import messagebox, ttk
from collections import Counter

# Define total columns for centering the substitution entries
total_columns = 52

# Styling constants
FONT_LARGE = ('Arial', 12)
FONT_MEDIUM = ('Arial', 10)
FONT_SMALL = ('Arial', 8)
BG_COLOR = '#eddaa6'
BUTTON_COLOR = '#f9f3e4'
TEXT_COLOR = '#000000'

# Function to count the frequency of characters, digrams, or trigrams
def count_frequency(text, n=1):
    if n == 1:
        counts = Counter(text)
    else:
        counts = Counter(text[i:i+n] for i in range(len(text)-n+1))
    total = sum(counts.values())
    return {k: v / total * 100 for k, v in counts.items()}

# Function to perform frequency analysis and update displays
def analyze_frequency():
    text = ciphertext_entry.get("1.0", "end-1c").replace(" ", "").upper()

    # Enable widgets, clear existing content, and update
    for display in [single_char_display, digram_display, trigram_display]:
        display.config(state='normal')
        display.delete('1.0', tk.END)

    # Single Characters
    single_frequencies = count_frequency(text, 1)
    for k, v in sorted(single_frequencies.items(), key=lambda item: item[1], reverse=True):
        single_char_display.insert(tk.END, f"{k: <8}| {v: >8.2f}%\n")

    # Digrams
    digram_frequencies = count_frequency(text, 2)
    for k, v in sorted(digram_frequencies.items(), key=lambda item: item[1], reverse=True):
        digram_display.insert(tk.END, f"{k: <8}| {v: >8.2f}%\n")

    # Trigrams
    trigram_frequencies = count_frequency(text, 3)
    for k, v in sorted(trigram_frequencies.items(), key=lambda item: item[1], reverse=True):
        trigram_display.insert(tk.END, f"{k: <8}| {v: >8.2f}%\n")

    # Center text and disable widgets
    for display in [single_char_display, digram_display, trigram_display]:
        display.tag_configure("center", justify='center')
        display.tag_add("center", "1.0", "end")
        display.config(state='disabled')

# Function to update the decrypted text maintaining the original case
def update_decrypted_text(*args):
    ciphertext = ciphertext_entry.get("1.0", "end-1c")
    plaintext = list(ciphertext)
    for i, char in enumerate(ciphertext):
        if char.upper() in substitutions:
            substitute = substitutions[char.upper()].get()
            if substitute:
                plaintext[i] = substitute.upper() if char.isupper() else substitute.lower()
            else:
                plaintext[i] = char
    plaintext_display.delete('1.0', tk.END)
    plaintext_display.insert(tk.END, ''.join(plaintext))

def validate_entry(P, entry_widget):
    if len(P) > 1 or (P and not P.isalpha()):  # Allow only a single alphabetic character or empty
        return False
    if P == "":  # Bypass the check if the entry is being cleared
        return True
    for letter, entry in substitutions.items():
        if entry is not entry_widget and entry.get().upper() == P.upper():  # Check if character is already used
            messagebox.showerror("Error", f"Character '{P.upper()}' is already used in another substitution.")
            return False
    return True

def create_substitution_entries(frame):
    entries = {}
    total_letters = len('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    padding_columns = (total_columns - total_letters) // 2  # Calculate padding on each side

    # Padding on the left
    for i in range(padding_columns):
        frame.grid_columnconfigure(i, weight=1)

    for index, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        column_index = padding_columns + index
        label = tk.Label(frame, text=letter, width=2)
        entry = tk.Entry(frame, width=2, justify='center')
        validate_cmd = root.register(lambda P, entry=entry: validate_entry(P, entry))
        entry.config(validate='key', validatecommand=(validate_cmd, '%P'))
        label.config(font=FONT_MEDIUM, bg=BG_COLOR, fg=TEXT_COLOR)
        entry.config(font=FONT_MEDIUM, bg='white', fg='black')
        entry.bind('<KeyRelease>', update_decrypted_text)
        entries[letter] = entry
        label.grid(row=0, column=column_index)
        entry.grid(row=1, column=column_index)

    # Padding on the right
    for i in range(padding_columns + total_letters, total_columns):
        frame.grid_columnconfigure(i, weight=1)

    return entries

def reset_substitutions():
    for letter, entry in substitutions.items():
        entry.delete(0, tk.END)
    update_decrypted_text()  # Update the decrypted text after resetting substitutions

# Function to reset all fields
def reset_all():
    ciphertext_entry.delete('1.0', tk.END)
    plaintext_display.delete('1.0', tk.END)
    single_char_display.delete('1.0', tk.END)
    digram_display.delete('1.0', tk.END)
    trigram_display.delete('1.0', tk.END)
    reset_substitutions()

# Function to remove spaces from the ciphertext and update decrypted text
def remove_spaces():
    text = ciphertext_entry.get("1.0", "end-1c").replace(" ", "")
    ciphertext_entry.delete('1.0', tk.END)
    ciphertext_entry.insert(tk.END, text)
    update_decrypted_text()  # Update the decrypted text after removing spaces

# Function to decrypt based on the key
def decrypt_with_key():
    key = int(key_option.get())
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        shifted_letter = chr((ord(letter) - 65 - key) % 26 + 65)
        substitutions[letter].delete(0, tk.END)
        substitutions[letter].insert(0, shifted_letter)
    update_decrypted_text()

# Set up the GUI
root = tk.Tk()
root.title("Frequency Analysis Tool")
root.geometry("800x800")
root.configure(bg=BG_COLOR)

# Ciphertext input
ciphertext_label = tk.Label(root, text="Ciphertext (input by user):", font=FONT_MEDIUM, bg=BG_COLOR, fg=TEXT_COLOR)
ciphertext_label.grid(row=0, column=0, sticky='ew')
ciphertext_entry = tk.Text(root, height=10, font=FONT_SMALL)
ciphertext_entry.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

# Frequency analysis controls
frequency_analysis_frame = tk.Frame(root, bg=BG_COLOR)
frequency_analysis_frame.grid(row=2, column=0, sticky='ew', padx=5)

# Configure columns for centering the button
frequency_analysis_frame.grid_columnconfigure(0, weight=1)  # Empty space on left
frequency_analysis_frame.grid_columnconfigure(2, weight=1)  # Empty space on right

# Create and place the "Count Frequencies" button in the center
count_freq_button = tk.Button(frequency_analysis_frame, text="Count Frequencies", command=analyze_frequency, font=FONT_SMALL, bg=BUTTON_COLOR)
count_freq_button.grid(row=0, column=1)  # Placed in the middle column

# Frequency analysis display setup
frequency_analysis_display_frame = tk.Frame(root, bg=BG_COLOR)
frequency_analysis_display_frame.grid(row=4, column=0, sticky='nsew', padx=5)

# Labels for frequency displays
single_char_label = tk.Label(frequency_analysis_display_frame, text="Single Characters", font=FONT_SMALL, bg=BG_COLOR, fg=TEXT_COLOR)
digram_label = tk.Label(frequency_analysis_display_frame, text="Digrams", font=FONT_SMALL, bg=BG_COLOR, fg=TEXT_COLOR)
trigram_label = tk.Label(frequency_analysis_display_frame, text="Trigrams", font=FONT_SMALL, bg=BG_COLOR, fg=TEXT_COLOR)

single_char_label.grid(row=0, column=0, sticky='n', padx=5)
digram_label.grid(row=0, column=1, sticky='n', padx=5)
trigram_label.grid(row=0, column=2, sticky='n', padx=5)

# Create three text widgets for single, digram, and trigram frequencies
single_char_display = tk.Text(frequency_analysis_display_frame, height=10, width=40, font=FONT_MEDIUM, state='disabled')
digram_display = tk.Text(frequency_analysis_display_frame, height=10, width=40, font=FONT_MEDIUM, state='disabled')
trigram_display = tk.Text(frequency_analysis_display_frame, height=10, width=40, font=FONT_MEDIUM, state='disabled')

single_char_display.grid(row=1, column=0, padx=5, pady=5, sticky='n')
digram_display.grid(row=1, column=1, padx=5, pady=5, sticky='n')
trigram_display.grid(row=1, column=2, padx=5, pady=5, sticky='n')

# Configure column weights to ensure equal spacing
frequency_analysis_display_frame.grid_columnconfigure(0, weight=1)
frequency_analysis_display_frame.grid_columnconfigure(1, weight=1)
frequency_analysis_display_frame.grid_columnconfigure(2, weight=1)

# Decryptor section
decryptor_frame = tk.Frame(root, bg=BG_COLOR)
decryptor_frame.grid(row=5, column=0, sticky='ew', padx=5, pady=5)

# Configure the columns for layout
decryptor_frame.grid_columnconfigure(0, weight=1)
decryptor_frame.grid_columnconfigure(1, weight=0) # for "Key:" label
decryptor_frame.grid_columnconfigure(2, weight=0) # for key options
decryptor_frame.grid_columnconfigure(3, weight=0) # for "Decrypt" button
decryptor_frame.grid_columnconfigure(4, weight=1)

# Centered "Decryptor" label
decryptor_label = tk.Label(decryptor_frame, text="Decryptor (For Caesar Cipher)", font=FONT_MEDIUM, bg=BG_COLOR, fg=TEXT_COLOR)
decryptor_label.grid(row=0, column=0, columnspan=5, sticky='ew')

# Key label and option
key_label = tk.Label(decryptor_frame, text="Key:", font=FONT_SMALL, bg=BG_COLOR, fg=TEXT_COLOR)
key_label.grid(row=1, column=1, sticky='e')

key_option = ttk.Combobox(decryptor_frame, values=[str(i) for i in range(1, 27)], width=3, state="readonly", font=FONT_SMALL)
key_option.grid(row=1, column=2, sticky='w', padx=5)
key_option.set('1')

# Decrypt Button
decrypt_button = tk.Button(decryptor_frame, text="Decrypt", command=decrypt_with_key, font=FONT_SMALL, bg=BUTTON_COLOR)
decrypt_button.grid(row=1, column=3, padx=10)

# Substitution entries frame
substitution_frame = tk.Frame(root, bg=BG_COLOR)
substitution_frame.grid(row=6, column=0, sticky='ew', padx=5, pady=5)
substitutions = create_substitution_entries(substitution_frame)

# Reset Substitutions button
reset_substitutions_button = tk.Button(substitution_frame, text="Reset Substitutions", command=reset_substitutions, font=FONT_SMALL, bg=BUTTON_COLOR)
reset_substitutions_button.grid(row=2, column=0, columnspan=total_columns, pady=5)

# Plaintext display
plaintext_display_label = tk.Label(root, text="Decrypted Text:", font=FONT_MEDIUM, bg=BG_COLOR, fg=TEXT_COLOR)
plaintext_display_label.grid(row=7, column=0, sticky='ew', padx=5, pady=5)
plaintext_display = tk.Text(root, height=10, font=FONT_SMALL)
plaintext_display.grid(row=8, column=0, sticky='nsew', padx=5, pady=5)

# Control buttons
control_frame = tk.Frame(root, bg=BG_COLOR)
control_frame.grid(row=9, column=0, sticky='ew', padx=5)
tk.Button(control_frame, text="Remove Spaces", command=remove_spaces, font=FONT_SMALL, bg=BUTTON_COLOR).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Reset All", command=reset_all, font=FONT_SMALL, bg=BUTTON_COLOR).pack(side=tk.LEFT, padx=5)

# Exit button
exit_button = tk.Button(root, text='Exit', command=root.destroy, font=FONT_SMALL, bg=BUTTON_COLOR)
exit_button.grid(row=10, column=0, sticky='ew', padx=5, pady=5)

# Initially update the decrypted text
ciphertext_entry.bind('<KeyRelease>', lambda e: update_decrypted_text())
update_decrypted_text()

# Configure the grid for resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Run the GUI loop
root.mainloop()