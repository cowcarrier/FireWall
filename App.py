import tkinter as tk
from tkinter import ttk
import tkinter.font
from tkinter.scrolledtext import ScrolledText
import threading
from Status import SpooferStatus

'''
A class that handles the gui of the application
'''


class App:
    def __init__(self, spoofer):
        self.scroll_packets = None
        self.active_ips_label = None
        self.status_label = None
        self.status_text = None
        self.text = None
        self.top = None
        self.stop_button = None
        self.space_label3 = None
        self.show_button = None
        self.space_label2 = None
        self.enter_url = None
        self.add_button = None
        self.space_label1 = None
        self.url_entry = None
        self.hello_label = None
        self.start_button = None
        self.menu = None
        self.app = tk.Tk()
        self.app.protocol("WM_DELETE_WINDOW", self.exit)
        self.font = tk.font.Font(family="Helvetica")
        self.chosen_mode = tk.StringVar(value="Choose a mode")
        self.spoofer = spoofer
        self.on = False

    '''
    A function that creates the home page of the app and starts the mainloop
    '''

    def create(self):
        self.on = True

        self.app.title("Homat HaEsh")
        self.app.configure(bg="#001933")
        self.app.geometry("800x600")

        hello_txt = "Hi and welcome to Homat HaEsh\n1. Add forbidden sites.\n2. Select a mode.\n3. Press start.\n"
        self.hello_label = tk.Label(self.app, text=hello_txt)
        self.hello_label.configure(bg="#001933", font=(None, 24))
        self.hello_label.pack()

        self.enter_url = tk.Label(self.app, text="Enter URL")
        self.enter_url.configure(bg="#001933", font=(None, 16))
        self.enter_url.pack()

        self.url_entry = tk.Entry(self.app)
        self.url_entry.pack()

        self.space_label1 = tk.Label(self.app, text="\n")
        self.space_label1.configure(bg="#001933", font=(None, 10))
        self.space_label1.pack()

        add_icon = tk.PhotoImage(file='add.png').subsample(12, 12)
        self.add_button = ttk.Button(self.app, image=add_icon, text="Add URL", compound=tk.LEFT, command=self.add, )
        self.add_button.image = add_icon
        self.add_button.pack()

        self.space_label2 = tk.Label(self.app, text="\n")
        self.space_label2.configure(bg="#001933", font=(None, 10))
        self.space_label2.pack()

        show_icon = tk.PhotoImage(file='show.png').subsample(5, 5)
        self.show_button = ttk.Button(self.app, image=show_icon, text="Show forbidden URLs", compound=tk.LEFT,
                                      command=self.show, )
        self.show_button.image = show_icon
        self.show_button.pack()

        self.space_label3 = tk.Label(self.app, text="\n")
        self.space_label3.configure(bg="#001933", font=(None, 10))
        self.space_label3.pack()

        options = list(["Supervisor", "Blocker"])
        self.menu = tk.OptionMenu(self.app, self.chosen_mode, *options)
        self.menu.configure(bg="#001933", font=(None, 15))
        self.menu.pack()

        start_icon = tk.PhotoImage(file='start.png').subsample(15, 15)
        self.start_button = ttk.Button(self.app, image=start_icon, text="Start", compound=tk.LEFT, command=self.start,
                                       state=tk.DISABLED)
        self.start_button.image = start_icon
        threading.Thread(target=self.activate_button).start()
        self.start_button.pack(side=tkinter.BOTTOM)

        stop_icon = tk.PhotoImage(file='stop.png').subsample(15, 15)
        self.stop_button = ttk.Button(self.app, image=stop_icon, text="stop", compound=tk.LEFT, command=self.stop)
        self.stop_button.image = stop_icon

        self.app.mainloop()

    '''
    A function that adds forbidden urls to the list.
    '''

    def add(self):
        url = self.url_entry.get()
        self.url_entry.delete(0, tk.END)
        if not self.spoofer.add_host(url):
            tk.messagebox.showerror("Error", "URL was not found")

    '''
    A function that shows the list of forbidden urls
    '''

    def show(self):
        self.top = tk.Toplevel(self.app)
        self.top.geometry('500x350')
        self.top.title("forbidden URLs")
        self.text = tk.StringVar()
        self.text.set("\n".join(self.spoofer.forbidden_urls))
        label = tk.Label(self.top, textvariable=self.text)
        label.configure(font=(None, 16))
        label.pack()

    '''
    A function that checks that the user selected a mode before starting the spoofing.
    '''

    def activate_button(self):

        while self.on and self.chosen_mode.get() == "Choose a mode":
            self.app.update()

        if self.on:
            self.start_button.configure(state=tk.NORMAL)

    '''
    A function that start the spoofing and creates the monitoring app page.
    '''

    def start(self):
        self.start_button.destroy()
        self.menu.destroy()
        self.hello_label.destroy()
        self.enter_url.destroy()
        self.url_entry.destroy()
        self.add_button.destroy()
        self.show_button.destroy()
        self.space_label1.destroy()
        self.space_label2.destroy()
        self.space_label3.destroy()

        self.spoofer.mode = self.chosen_mode.get()

        threading.Thread(target=self.spoofer.host_updater).start()
        threading.Thread(target=self.spoofer.thread_starter).start()
        self.stop_button.pack(side=tkinter.BOTTOM)

        self.status_text = tk.StringVar()
        self.status_text.set(self.spoofer.status.name)

        self.status_label = tk.Label(self.app, textvariable=self.status_text)
        self.status_label.configure(bg="#001933", font=(None, 10))
        self.status_label.pack(side=tkinter.TOP)

        active_ips = tk.StringVar()
        active_ips.set(self.spoofer.network.active_ips)

        self.active_ips_label = tk.Label(self.app, textvariable=active_ips)
        self.active_ips_label.configure(bg="#001933", font=(None, 10))
        self.active_ips_label.pack(side=tkinter.TOP)

        self.scroll_packets = ScrolledText(self.app)

        self.space_label3 = tk.Label(self.app, text="\n")
        self.space_label3.configure(bg="#001933", font=(None, 10))
        self.space_label3.pack()

        self.scroll_packets.insert(tk.INSERT, self.spoofer.forbidden_packets)
        self.scroll_packets.configure(state=tk.DISABLED)
        self.scroll_packets.pack()

        while self.on and self.spoofer.status is not SpooferStatus.OFF:
            self.status_text.set(self.spoofer.status.name)
            active_ips.set(self.spoofer.network.active_ips)

            if self.spoofer.forbidden_packets:
                self.scroll_packets.configure(state=tk.NORMAL)
                self.scroll_packets.insert(tk.INSERT, self.spoofer.forbidden_packets[0])
                self.scroll_packets.configure(state=tk.DISABLED)
                self.spoofer.forbidden_packets.pop(0)
            self.app.update()

    '''
    A function that stops the the spoofing.
    '''

    def stop(self):
        self.spoofer.turn_off()
        self.stop_button.destroy()
        self.active_ips_label.destroy()
        self.status_text.set(self.spoofer.status.name)
        self.app.update()

    '''
    A function that close all the threads after closing the app.
    '''
    def exit(self):
        self.on = False
        self.spoofer.turn_off()
        self.app.destroy()
