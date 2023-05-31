import customtkinter
import os
from PIL import Image
import time
from typing import Union
import numpy as np
lowerHSV = np.array([140, 90, 140])
upperHSV = np.array([150, 159, 255])

class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 command: callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0.0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[float, None]:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("bagelbot.py")
        self.geometry("600x350")
        customtkinter.set_appearance_mode("Dark")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        self.logo_image = customtkinter.CTkImage(light_image=Image.open("logoLight.png"), dark_image=Image.open("logoDark.png"), size=(150, 26))
        self.color_image = customtkinter.CTkImage(light_image=Image.open("colorLight.png"), dark_image=Image.open("colorDark.png"), size=(50, 50))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open("timeLight.png"), dark_image=Image.open("timeDark.png"), size=(35, 35))
        self.settings_image = customtkinter.CTkImage(light_image=Image.open("settingsLight.png"), dark_image=Image.open("settingsDark.png"), size=(35, 35))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        #Draw logo
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)


        #Colors tab
        # create color frame
        self.color_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.color_frame.grid_columnconfigure(0, weight=1)
        self.color_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Colors",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.color_image, anchor="w", command=self.color_button_event)
        self.color_button.grid(row=1, column=0, sticky="ew")
        #Hue TabView
        self.hue_tabview = customtkinter.CTkTabview(self.color_frame, width=250)
        self.hue_tabview.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        #Upper
        self.hue_tabview.add("Upper Limit")
        self.hue_tabview.tab("Upper Limit").grid_columnconfigure(0, weight=1)
        self.hue_upper_label = customtkinter.CTkLabel(self.hue_tabview.tab("Upper Limit"), text="Hue")
        self.hue_upper_label.grid(row=0, column=0, padx=0, pady=0)
        self.hue_upper_spinbox = FloatSpinbox(self.hue_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.hue_upper_spinbox_event)
        self.hue_upper_spinbox.grid(row=1, column=0, padx=0, pady=0)
        self.hue_upper_spinbox.set(150)
        self.saturation_upper_label = customtkinter.CTkLabel(self.hue_tabview.tab("Upper Limit"), text="Saturation")
        self.saturation_upper_label.grid(row=2, column=0, padx=0, pady=15)
        self.saturation_upper_spinbox = FloatSpinbox(self.hue_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.saturation_upper_spinbox_event)
        self.saturation_upper_spinbox.grid(row=3, column=0, padx=0, pady=0)
        self.saturation_upper_spinbox.set(159)
        self.value_upper_label = customtkinter.CTkLabel(self.hue_tabview.tab("Upper Limit"), text="Value")
        self.value_upper_label.grid(row=4, column=0, padx=0, pady=15)
        self.value_upper_spinbox = FloatSpinbox(self.hue_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.value_upper_spinbox_event)
        self.value_upper_spinbox.grid(row=5, column=0, padx=0, pady=0)
        self.value_upper_spinbox.set(255)
        #Lower
        self.hue_tabview.add("Lower Limit")
        self.hue_tabview.tab("Lower Limit").grid_columnconfigure(0, weight=1)
        self.hue_lower_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Hue")
        self.hue_lower_label.grid(row=0, column=0, padx=0, pady=0)
        self.hue_lower_spinbox = FloatSpinbox(self.hue_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.hue_lower_spinbox_event)
        self.hue_lower_spinbox.grid(row=1, column=0, padx=0, pady=0)
        self.hue_lower_spinbox.set(140)
        self.saturation_lower_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Saturation")
        self.saturation_lower_label.grid(row=2, column=0, padx=0, pady=15)
        self.saturation_lower_spinbox = FloatSpinbox(self.hue_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.saturation_lower_spinbox_event)
        self.saturation_lower_spinbox.grid(row=3, column=0, padx=0, pady=0)
        self.saturation_lower_spinbox.set(90)
        self.value_lower_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Value")
        self.value_lower_label.grid(row=4, column=0, padx=0, pady=15)
        self.value_lower_spinbox = FloatSpinbox(self.hue_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.value_lower_spinbox_event)
        self.value_lower_spinbox.grid(row=5, column=0, padx=0, pady=0)
        self.value_lower_spinbox.set(140)


        #Delays tab
        # create delays frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Delays",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        #Settings tab
        # create settings frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.settings_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        #Brightness mode
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=10, sticky="s")

        #Scaling size
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["100%", "125%", "150%", "175%", "200%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(0, 20))

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

    #upper spinbox events
    def hue_upper_spinbox_event(self):
        if self.hue_upper_spinbox.get() > 179:
            self.hue_upper_spinbox.set(179)
        upperHSV[0] = self.hue_upper_spinbox.get()
    def saturation_upper_spinbox_event(self):
        if self.saturation_upper_spinbox.get() > 255:
            self.saturation_upper_spinbox.set(255)
        upperHSV[1] = self.saturation_upper_spinbox.get()
    def value_upper_spinbox_event(self):
        if self.value_upper_spinbox.get() > 255:
            self.value_upper_spinbox.set(255)
        upperHSV[2] = self.value_upper_spinbox.get()

    #lower spinbox events
    def hue_lower_spinbox_event(self):
        if self.hue_lower_spinbox.get() > 179:
            self.hue_lower_spinbox.set(179)
        lowerHSV[0] = self.hue_lower_spinbox.get()
    def saturation_lower_spinbox_event(self):
        if self.saturation_lower_spinbox.get() > 255:
            self.saturation_lower_spinbox.set(255)
        lowerHSV[1] = self.saturation_lower_spinbox.get()
    def value_lower_spinbox_event(self):
        if self.value_lower_spinbox.get() > 255:
            self.value_lower_spinbox.set(255)
        lowerHSV[2] = self.value_lower_spinbox.get()

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = App()
    app.mainloop()

