import customtkinter
import os
from PIL import Image
import time


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("bagelbot.py")
        self.geometry("600x350")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        self.logo_image = customtkinter.CTkImage(light_image=Image.open("logoLight.png"), dark_image=Image.open("logoDark.png"), size=(150, 26))
        self.color_image = customtkinter.CTkImage(light_image=Image.open("colorLight.png"), dark_image=Image.open("colorDark.png"), size=(40, 40))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open("timeLight.png"), dark_image=Image.open("timeDark.png"), size=(30, 30))
        self.settings_image = customtkinter.CTkImage(light_image=Image.open("settingsLight.png"), dark_image=Image.open("settingsDark.png"), size=(30, 30))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        #Draw logo
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)


        #Colors tab
        self.color_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Colors",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.color_image, anchor="w", command=self.color_button_event)
        self.color_button.grid(row=1, column=0, sticky="ew")

        #Delays tab
        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Delays",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        #Settings tab
        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.settings_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        #Brightness mode
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create color frame
        self.color_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.color_frame.grid_columnconfigure(0, weight=1)


        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("color")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.color_button.configure(fg_color=("gray75", "gray25") if name == "color" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "color":
            self.color_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.color_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def color_button_event(self):
        self.select_frame_by_name("color")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()

