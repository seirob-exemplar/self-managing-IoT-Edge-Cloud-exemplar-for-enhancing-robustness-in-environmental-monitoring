from tkinter import *


class ConsoleLogApplication(object):
    def __init__(self, parent, background_color='white', font_color='green', status="..."):
        self.name = StringVar()
        self.parent = parent
        self.scrollbar = Scrollbar(parent)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.messages = Listbox(parent, bd="7", yscrollcommand=self.scrollbar.set, relief=RIDGE,
                                selectbackground=background_color, selectmode=BROWSE, font="bold", fg=font_color)
        self.messages.pack({"side": "top", "expand": "yes", "fill": "both"})

        self.scrollbar.config(command=self.messages.yview)

        self.backgroundColor = background_color
        self.fontColor = font_color

        self.StatusBar = Label(parent, text=status)
        self.StatusBar['background'] = "#FFFFFF"
        self.StatusBar['foreground'] = "blue"
        self.StatusBar.pack({"side": "bottom", "expand": "no", "fill": "x"})

    def print(self, message):
        self.messages.insert(END, message)
        self.messages.see(END)

    def print_warning(self, message):
        self.messages.insert(END, message)
        self.messages.see(END)

    def setStatus(self, message):
        self.StatusBar["text"] = message

