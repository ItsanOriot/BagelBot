#imports
import customtkinter
from PIL import Image
import time
from typing import Union
import numpy as np
import cv2
import os
#os.environ["BLINKA_FT232H"] = "1"
#import board
#import digitalio
import random
import dxcam
from win32api import GetSystemMetrics
import keyboard
import asyncio
import multiprocessing

#settings
triggerFov = 15
aimFov = 15
width = GetSystemMetrics (0)
height = GetSystemMetrics (1)
maxFov = max(triggerFov,aimFov)
left, top = (width - maxFov) // 2, (height - maxFov) // 2
right, bottom = left + maxFov, top + maxFov
region = (left, top, right, bottom)
camera = dxcam.create(output_idx=0, region = region, output_color="BGR")
camera.start(target_fps=100)
delayPreUpper = 0
delayPreLower = 0
delayBetweenUpper = 0.3
delayBetweenLower = 0.2
delayHoldUpper = 0.08
delayHoldLower = 0.04
bind = "F22"
lowerHSV = np.array([140, 90, 140])
upperHSV = np.array([150, 159, 255])

def update_cam():
    print("update")
    left, top = (width - maxFov) // 2, (height - maxFov) // 2
    right, bottom = left + maxFov, top + maxFov
    region = (int(left), int(top), int(right), int(bottom))
    global camera
    camera.stop()
    del camera
    camera = dxcam.create(output_idx=0, region = region, output_color="BGR")
    camera.start()


def hsv_to_hex(hsv):
    h, s, v = float(hsv[0]), float(hsv[1]), float(hsv[2])
    r, g, b = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2RGB)[0][0]
    return '#%02x%02x%02x' % (r, g, b)

def scan(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerHSV, upperHSV)
    return mask

async def image_processing(queue):
    while True:
        await asyncio.sleep(0.05)
        image = np.array(camera.get_latest_frame())
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lowerHSV, upperHSV)
        
        # Put the processed image in the queue
        await queue.put(mask)

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
        self.geometry("600x360")
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
        self.saturation_upper_label.grid(row=3, column=0, padx=0, pady=(0,65))
        self.saturation_upper_spinbox = FloatSpinbox(self.hue_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.saturation_upper_spinbox_event)
        self.saturation_upper_spinbox.grid(row=3, column=0, padx=0, pady=0)
        self.saturation_upper_spinbox.set(159)
        self.value_upper_label = customtkinter.CTkLabel(self.hue_tabview.tab("Upper Limit"), text="Value")
        self.value_upper_label.grid(row=4, column=0, padx=0, pady=0)
        self.value_upper_spinbox = FloatSpinbox(self.hue_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.value_upper_spinbox_event)
        self.value_upper_spinbox.grid(row=5, column=0, padx=0, pady=0)
        self.value_upper_spinbox.set(255)
        #Upper Preview
        self.upper_preview_label = customtkinter.CTkLabel(self.hue_tabview.tab("Upper Limit"), text="Upper Limit Preview")
        self.upper_preview_label.grid(row=2, column=3, padx=0, pady=0)
        self.upper_preview_frame = customtkinter.CTkFrame(self.hue_tabview.tab("Upper Limit"), width=75, height=75, corner_radius=4, fg_color=hsv_to_hex(upperHSV), border_color="black")
        self.upper_preview_frame.grid(row=3, column=3, padx=50, pady=0)
        #Lower
        self.hue_tabview.add("Lower Limit")
        self.hue_tabview.tab("Lower Limit").grid_columnconfigure(0, weight=1)
        self.hue_lower_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Hue")
        self.hue_lower_label.grid(row=0, column=0, padx=0, pady=0)
        self.hue_lower_spinbox = FloatSpinbox(self.hue_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.hue_lower_spinbox_event)
        self.hue_lower_spinbox.grid(row=1, column=0, padx=0, pady=0)
        self.hue_lower_spinbox.set(140)
        self.saturation_lower_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Saturation")
        self.saturation_lower_label.grid(row=3, column=0, padx=0, pady=(0,65))
        self.saturation_lower_spinbox = FloatSpinbox(self.hue_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.saturation_lower_spinbox_event)
        self.saturation_lower_spinbox.grid(row=3, column=0, padx=0, pady=0)
        self.saturation_lower_spinbox.set(90)
        self.value_lower_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Value")
        self.value_lower_label.grid(row=4, column=0, padx=0, pady=0)
        self.value_lower_spinbox = FloatSpinbox(self.hue_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.value_lower_spinbox_event)
        self.value_lower_spinbox.grid(row=5, column=0, padx=0, pady=0)
        self.value_lower_spinbox.set(140)
        #Lower Preview
        self.lower_preview_label = customtkinter.CTkLabel(self.hue_tabview.tab("Lower Limit"), text="Lower Limit Preview")
        self.lower_preview_label.grid(row=2, column=3, padx=0, pady=0)
        self.lower_preview_frame = customtkinter.CTkFrame(self.hue_tabview.tab("Lower Limit"), width=75, height=75, corner_radius=4, fg_color=hsv_to_hex(lowerHSV), border_color="black")
        self.lower_preview_frame.grid(row=3, column=3, padx=50, pady=0)


        #Triggerbot tab
        # create triggerbot frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Triggerbot",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        #Delay TabView
        self.delay_tabview = customtkinter.CTkTabview(self.second_frame, width=250)
        self.delay_tabview.grid(row=0, column=0, padx=(75, 20), pady=(20, 0), sticky="nsew")
        #Upper
        self.delay_tabview.add("Upper Limit")
        self.delay_tabview.tab("Upper Limit").grid_columnconfigure(0, weight=1)
        self.pre_upper_label = customtkinter.CTkLabel(self.delay_tabview.tab("Upper Limit"), text="Delay (ms)")
        self.pre_upper_label.grid(row=0, column=0, padx=0, pady=0)
        self.pre_upper_spinbox = FloatSpinbox(self.delay_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.pre_upper_spinbox_event)
        self.pre_upper_spinbox.grid(row=1, column=0, padx=0, pady=(0,15))
        self.pre_upper_spinbox.set(50)
        self.post_upper_label = customtkinter.CTkLabel(self.delay_tabview.tab("Upper Limit"), text="Time Between Shots (ms)")
        self.post_upper_label.grid(row=2, column=0, padx=0, pady=0)
        self.post_upper_spinbox = FloatSpinbox(self.delay_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.post_upper_spinbox_event)
        self.post_upper_spinbox.grid(row=3, column=0, padx=0, pady=(0,15))
        self.post_upper_spinbox.set(300)
        self.hold_upper_label = customtkinter.CTkLabel(self.delay_tabview.tab("Upper Limit"), text="Mouse Hold Time (ms)")
        self.hold_upper_label.grid(row=4, column=0, padx=0, pady=0)
        self.hold_upper_spinbox = FloatSpinbox(self.delay_tabview.tab("Upper Limit"), width=150, step_size=1, command=self.hold_upper_spinbox_event)
        self.hold_upper_spinbox.grid(row=5, column=0, padx=0, pady=(0,15))
        self.hold_upper_spinbox.set(50)
        #Lower
        self.delay_tabview.add("Lower Limit")
        self.delay_tabview.tab("Lower Limit").grid_columnconfigure(0, weight=1)
        self.pre_lower_label = customtkinter.CTkLabel(self.delay_tabview.tab("Lower Limit"), text="Delay (ms)")
        self.pre_lower_label.grid(row=0, column=0, padx=0, pady=0)
        self.pre_lower_spinbox = FloatSpinbox(self.delay_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.pre_lower_spinbox_event)
        self.pre_lower_spinbox.grid(row=1, column=0, padx=0, pady=0)
        self.pre_lower_spinbox.set(50)
        self.post_lower_label = customtkinter.CTkLabel(self.delay_tabview.tab("Lower Limit"), text="Time Between Shots (ms)")
        self.post_lower_label.grid(row=2, column=0, padx=0, pady=0)
        self.post_lower_spinbox = FloatSpinbox(self.delay_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.post_lower_spinbox_event)
        self.post_lower_spinbox.grid(row=3, column=0, padx=0, pady=0)
        self.post_lower_spinbox.set(200)
        self.hold_lower_label = customtkinter.CTkLabel(self.delay_tabview.tab("Lower Limit"), text="Mouse Hold Time (ms)")
        self.hold_lower_label.grid(row=4, column=0, padx=0, pady=0)
        self.hold_lower_spinbox = FloatSpinbox(self.delay_tabview.tab("Lower Limit"), width=150, step_size=1, command=self.hold_lower_spinbox_event)
        self.hold_lower_spinbox.grid(row=5, column=0, padx=0, pady=0)
        self.hold_lower_spinbox.set(20)
        
        #Settings tab
        # create settings frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.settings_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")
        #fov spinboxes
        self.trigger_fov_label = customtkinter.CTkLabel(self.third_frame, text="Triggerbot FOV")
        self.trigger_fov_label.grid(row=0, column=0, padx=20, pady=0)
        self.trigger_fov_spinbox = FloatSpinbox(self.third_frame, width=150, step_size=1, command=self.trigger_fov_spinbox_event)
        self.trigger_fov_spinbox.grid(row=1, column=0, padx=20, pady=0)
        self.trigger_fov_spinbox.set(15)
        self.trigger_fov_preview_frame = customtkinter.CTkFrame(self.third_frame, width=maxFov, height=maxFov, corner_radius=0, fg_color="transparent", border_color="#00FF00", border_width=1)
        self.trigger_fov_preview_frame.grid(row=2, column=0, padx=0, pady=10)

        self.aim_fov_label = customtkinter.CTkLabel(self.third_frame, text="Aimbot FOV")
        self.aim_fov_label.grid(row=0, column=2, padx=20, pady=0)
        self.aim_fov_spinbox = FloatSpinbox(self.third_frame, width=150, step_size=1, command=self.aim_fov_spinbox_event)
        self.aim_fov_spinbox.grid(row=1, column=2, padx=20, pady=0)
        self.aim_fov_spinbox.set(15)
        self.aim_fov_preview_frame = customtkinter.CTkFrame(self.third_frame, width=maxFov, height=maxFov, corner_radius=0, fg_color="transparent", border_color="#00FF00", border_width=1)
        self.aim_fov_preview_frame.grid(row=2, column=2, padx=0, pady=10)
        
        #Keybind window
        self.bind_label = customtkinter.CTkLabel(self.third_frame, text=("Current Keybind: " + bind))
        self.bind_label.grid(row=4, column=0, padx=20, pady=0)
        self.bind_button = customtkinter.CTkButton(self.third_frame, text="Change Keybind", command=self.bind_button_click_event)
        self.bind_button.grid(row=5, column=0, padx=20, pady=0)

        #Masking Preview
        self.bind_button = customtkinter.CTkButton(self.third_frame, text="Preview Masking", command=self.preview_mask_click_event)
        self.bind_button.grid(row=3, column=0, padx=20, pady=0)

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

    #upper hsv spinbox events
    def hue_upper_spinbox_event(self):
        if self.hue_upper_spinbox.get() > 179:
            self.hue_upper_spinbox.set(179)
        if self.hue_upper_spinbox.get() <= self.hue_lower_spinbox.get():
            self.hue_upper_spinbox.set(self.hue_lower_spinbox.get() + 1)
        upperHSV[0] = self.hue_upper_spinbox.get()
        self.upper_preview_frame.configure(fg_color=hsv_to_hex(upperHSV))
    def saturation_upper_spinbox_event(self):
        if self.saturation_upper_spinbox.get() > 255:
            self.saturation_upper_spinbox.set(255)
        if self.saturation_upper_spinbox.get() <= self.saturation_lower_spinbox.get():
            self.saturation_upper_spinbox.set(self.saturation_lower_spinbox.get() + 1)
        upperHSV[1] = self.saturation_upper_spinbox.get()
        self.upper_preview_frame.configure(fg_color=hsv_to_hex(upperHSV))
    def value_upper_spinbox_event(self):
        if self.value_upper_spinbox.get() > 255:
            self.value_upper_spinbox.set(255)
        if self.value_upper_spinbox.get() <= self.value_lower_spinbox.get():
            self.value_upper_spinbox.set(self.value_lower_spinbox.get() + 1)
        upperHSV[2] = self.value_upper_spinbox.get()
        self.upper_preview_frame.configure(fg_color=hsv_to_hex(upperHSV))

    #lower hsv spinbox events
    def hue_lower_spinbox_event(self):
        if self.hue_lower_spinbox.get() > 179:
            self.hue_lower_spinbox.set(179)
        if self.hue_lower_spinbox.get() >= self.hue_upper_spinbox.get():
            self.hue_lower_spinbox.set(self.hue_upper_spinbox.get() - 1)
        lowerHSV[0] = self.hue_lower_spinbox.get()
        self.lower_preview_frame.configure(fg_color=hsv_to_hex(lowerHSV))
    def saturation_lower_spinbox_event(self):
        if self.saturation_lower_spinbox.get() > 255:
            self.saturation_lower_spinbox.set(255)
        if self.saturation_lower_spinbox.get() >= self.saturation_upper_spinbox.get():
            self.saturation_lower_spinbox.set(self.saturation_upper_spinbox.get() - 1)
        lowerHSV[1] = self.saturation_lower_spinbox.get()
        self.lower_preview_frame.configure(fg_color=hsv_to_hex(lowerHSV))
    def value_lower_spinbox_event(self):
        if self.value_lower_spinbox.get() > 255:
            self.value_lower_spinbox.set(255)
        if self.value_lower_spinbox.get() >= self.value_upper_spinbox.get():
            self.value_lower_spinbox.set(self.value_upper_spinbox.get() - 1)
        lowerHSV[2] = self.value_lower_spinbox.get()
        self.lower_preview_frame.configure(fg_color=hsv_to_hex(lowerHSV))

    #upper delay spinbox events
    def pre_upper_spinbox_event(self):
        if self.pre_upper_spinbox.get() < self.pre_lower_spinbox.get():
            self.pre_upper_spinbox.set(self.pre_lower_spinbox.get())
        delayPreUpper = self.pre_upper_spinbox.get() - 50
    def post_upper_spinbox_event(self):
        if self.post_upper_spinbox.get() <= self.post_lower_spinbox.get():
            self.post_upper_spinbox.set(self.post_lower_spinbox.get() + 1)
        delayPostUpper = self.post_upper_spinbox.get()
    def hold_upper_spinbox_event(self):
        if self.hold_upper_spinbox.get() <= self.hold_lower_spinbox.get():
            self.hold_upper_spinbox.set(self.hold_lower_spinbox.get() + 1)
        delayHoldUpper = self.hold_upper_spinbox.get()

    #lower delay spinbox events
    def pre_lower_spinbox_event(self):
        if self.pre_lower_spinbox.get() < 0:
            self.pre_lower_spinbox.set(0)
        if self.pre_lower_spinbox.get() >= self.pre_lower_spinbox.get():
            self.pre_lower_spinbox.set(self.pre_upper_spinbox.get())
        delayPrelower = self.pre_lower_spinbox.get() - 50
    def post_lower_spinbox_event(self):
        if self.post_lower_spinbox.get() < 0:
            self.post_lower_spinbox.set(0)
        if self.post_lower_spinbox.get() >= self.post_lower_spinbox.get():
            self.post_lower_spinbox.set(self.post_upper_spinbox.get() - 1)
        delayPostlower = self.post_lower_spinbox.get()
    def hold_lower_spinbox_event(self):
        if self.hold_lower_spinbox.get() < 0:
            self.hold_lower_spinbox.set(0)
        if self.hold_lower_spinbox.get() >= self.hold_lower_spinbox.get():
            self.hold_lower_spinbox.set(self.hold_upper_spinbox.get() - 1)
        delayHoldlower = self.hold_lower_spinbox.get()
    
    def trigger_fov_spinbox_event(self):
        if self.trigger_fov_spinbox.get() < 1:
            self.trigger_fov_spinbox.set(1)
        global triggerFov
        fov = self.trigger_fov_spinbox.get()
        self.trigger_fov_preview_frame.configure(width=fov, height=fov)

    def aim_fov_spinbox_event(self):
        if self.aim_fov_spinbox.get() < 1:
            self.aim_fov_spinbox.set(1)
        global aimFov
        fov = self.aim_fov_spinbox.get()
        self.aim_fov_preview_frame.configure(width=fov, height=fov)

    def bind_button_click_event(self):
        dialog = customtkinter.CTkInputDialog(text="Which Key Would you like to use? Special keys must be spelled out. Ex: F5, ctrl, alt", title="Test")
        bind = dialog.get_input()
        print(bind)
        self.bind_label.configure(text=("Current Keybind: " + bind))

    def preview_mask_click_event(self):
        update_cam()
        print("under construction")
        #task = asyncio.create_task(display_preview())


    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


async def main():
    processed_image_queue = multiprocessing.Queue()
    asyncio.create_task(image_processing(processed_image_queue))

def display_process(queue):
    while True:
        mask = queue.get()  # Get the processed image from the queue
        
        # Display the image only if it's valid
        if mask is not None:
            cv2.imshow('Video', mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    # Create a multiprocessing queue for processed images
    processed_image_queue = multiprocessing.Queue()

    # Create and start the display process
    display_process_instance = multiprocessing.Process(target=display_process, args=(processed_image_queue,))
    display_process_instance.start()

    # Run the main asynchronous loop
    asyncio.run(main())

    # Cleanup after exiting the loop
    cv2.destroyAllWindows()

    app = App()
    app.mainloop()
