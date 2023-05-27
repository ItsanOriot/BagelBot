import tkinter
import tkinter.messagebox
import customtkinter
import time
import os
from PIL import Image

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("gui-theme.json")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("BagelBot")
        self.geometry(f"{600}x{350}")

         #sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=80, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        #logo
        self.logo_image = customtkinter.CTkImage(light_image=Image.open("logoLight.jpg"), dark_image=Image.open("logoDark.jpg"), size=(150, 26))
        self.image_label = customtkinter.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        self.image_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.hide_window)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        
        #appearance mode
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=380)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(5, 0), sticky="nsew")

        #Colors tab
        self.tabview.add("Colors")
        self.tabview.tab("Colors").grid_columnconfigure(0, weight=1)
        self.label_tab_1 = customtkinter.CTkLabel(self.tabview.tab("Colors"), text="Outline Color")
        self.label_tab_1.grid(row=0, column=0, padx=20, pady=(0, 0))
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("Colors"), dynamic_resizing=False,
                                                        values=["Purple", "Yellow", "Red"])
        self.optionmenu_1.grid(row=1, column=0, padx=20, pady=(0, 10))
        


        #Delays tab
        self.tabview.add("Delays")
        self.tabview.tab("Delays").grid_columnconfigure(0, weight=1)
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Delays"), text="CTkLabel on Delays")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        self.slider_between = customtkinter.CTkSlider(self.tabview.tab("Delays"), from_=0, to=1000, number_of_steps=1000)
        self.slider_between.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        
        #FOV tab
        self.tabview.add("FOV")

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def sidebar_button_event(self):
        print("sidebar_button click")
    
    def hide_window(self):
            dialog = customtkinter.CTkInputDialog(text="For how long would you like to hide the window?", title="CTkInputDialog")
            sleepTime = int(dialog.get_input())
            self.withdraw()
            time.sleep(sleepTime)
            self.deiconify()


if __name__ == "__main__":
    app = App()
    app.mainloop()
