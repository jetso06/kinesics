import tkinter as tk
import subprocess
import webbrowser
import os

def open_classic_mode():
    subprocess.Popen(['python', 'classic/classic_mode.py'])
    minimize_after_delay()

def open_driving_mode():
    subprocess.Popen(['python', 'driving/driving_mode.py'])
    minimize_after_delay()

def open_advanced_mode():
    subprocess.Popen(['python', 'advanced/advanced_mode.py'])
    minimize_after_delay()

def minimize_after_delay():
    root.after(5000, root.iconify)  # Minimize the window after 5 seconds

# Functions to open HTML files
def open_about():
    webbrowser.open('file://' + os.path.abspath("about_us.html"))

def open_contact():
    webbrowser.open('file://' + os.path.abspath("contact_us.html"))

def open_help():
    webbrowser.open('file://' + os.path.abspath("help.html"))

# Create the main window
root = tk.Tk()
root.title("Mode Selector")
root.attributes('-fullscreen', True)  # Set to full screen
root.configure(bg="#181C14")  # Set background color

# Set font and button styles
heading_font = ("Helvetica", 24, "bold")  # Font for the heading
button_font = ("Helvetica", 14, "bold")
link_font = ("Helvetica", 10, "underline")  # Underlined font for links
button_bg = "#3C3D37"  # Green color
button_fg = "#ECDFCC"   # White text
button_active_bg = "#697565"  # Darker green when pressed

# Create a frame to center both the heading and buttons together
center_frame = tk.Frame(root, bg="#181C14")
center_frame.pack(expand=True)

# Create heading at the top of the center frame
heading_label = tk.Label(center_frame, text="Kinesics", font=heading_font, fg="#ffffff", bg="#181C14")
heading_label.pack(pady=20)

# Create a frame for the buttons to center them within the center frame
button_frame = tk.Frame(center_frame, bg="#181C14")
button_frame.pack()

# Create buttons for each mode and add them to the button frame
classic_button = tk.Button(button_frame, text="Classic Mode", command=open_classic_mode, 
                           font=button_font, bg=button_bg, fg=button_fg,
                           activebackground=button_active_bg, width=20, bd=0, pady=5)
driving_button = tk.Button(button_frame, text="Driving Mode", command=open_driving_mode, 
                           font=button_font, bg=button_bg, fg=button_fg,
                           activebackground=button_active_bg, width=20, bd=0, pady=5)
advanced_button = tk.Button(button_frame, text="Advanced Mode", command=open_advanced_mode, 
                            font=button_font, bg=button_bg, fg=button_fg,
                            activebackground=button_active_bg, width=20, bd=0, pady=5)

# Create the Exit button below the Advanced Mode button
exit_button = tk.Button(button_frame, text="Exit", command=root.quit, 
                        font=button_font, bg="#d9534f", fg="#ffffff", activebackground="#c9302c", 
                        width=20, bd=0, pady=5)

# Pack the buttons onto the button frame with spacing
classic_button.pack(pady=10)
driving_button.pack(pady=10)
advanced_button.pack(pady=10)
exit_button.pack(pady=10)

# Create a frame for hyperlinks in the bottom-right corner
link_frame = tk.Frame(root, bg="#181C14")
link_frame.place(x=root.winfo_screenwidth() - 220, y=root.winfo_screenheight() - 30)

# Add hyperlinks to the frame
about_link = tk.Label(link_frame, text="About Us", font=link_font, fg="#00b0ff", bg="#181C14", cursor="hand2")
about_link.bind("<Button-1>", lambda e: open_about())
about_link.pack(side="left", padx=5)

contact_link = tk.Label(link_frame, text="Contact Us", font=link_font, fg="#00b0ff", bg="#181C14", cursor="hand2")
contact_link.bind("<Button-1>", lambda e: open_contact())
contact_link.pack(side="left", padx=5)

help_link = tk.Label(link_frame, text="Help", font=link_font, fg="#00b0ff", bg="#181C14", cursor="hand2")
help_link.bind("<Button-1>", lambda e: open_help())
help_link.pack(side="left", padx=5)

# Run the application
root.mainloop()
