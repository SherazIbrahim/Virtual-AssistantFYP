# Record mouse and keyboard actions and reproduce them identically at will

"""
This module contains all the classes needed to
create the GUI and handle non functionnal event
"""

import os
import sys
from pathlib import Path
import keyboard
from wx.core import BITMAP_TYPE_ANY, Size
import pynput
import control
import pyautogui
import settings
import threading
import wx
import wx.adv
import pyttsx3
import pyaudio
import time
engine = pyttsx3.init("sapi5") 
#Microsoft Speech API (SAPI5) is the technology for voice recognition.
#We have created object of pyttsx3

#Now we will set the voice property of our assistant 

voices = engine.getProperty('voices') 

#By default we have set the voice property to a male voice 
#But we will provide a command below so that user can adjust the voice property (either male or female Voice)
voiceid = settings.CONFIG.getint('DEFAULT', 'voiceid')
engine.setProperty('voice', voices[voiceid].id)


#By default we have set the rate property to 150
rate = engine.getProperty('rate')
engine.setProperty('rate',180)

#By default we have set the volume peoperty to 1
volume = engine.getProperty('volume')
engine.setProperty('volume',2)

#This Speak function will enable our assistant to speak
def speak(audio):
   engine.say(audio) 
   #To convey the message in audio 
   engine.runAndWait() 

class MainDialog(wx.Dialog, wx.MiniFrame):
    """Main Window, a dialog to display the app correctly even on tiling WMs."""
    
    app_text = ["Load Capture", "Save", "Start/Stop Capture", "Play", "Compile to executable",
                "Preferences"]
    settings_text = ["Set &Repeat Count", "Recording &Hotkey",
                     "&Playback Hotkey", "&Exit"]

    def on_settings_click(self, event):
        """Triggered when the popup menu is clicked."""
        self.settings_popup()
        event.GetEventObject().PopupMenu(self.settings_popup())
        event.EventObject.Parent.panel.SetFocus()
        event.Skip()

    def settings_popup(self):
        """Build the popup menu."""
        menu = wx.Menu()
        # Repeat count
        self.Bind(wx.EVT_MENU, self.sc.repeat_count,
                  menu.Append(wx.ID_ANY, self.settings_text[0]))
        menu.AppendSeparator()
        # Mouse Sensitivity
        self.Bind(wx.EVT_MENU, self.sc.mouse_sensitivity,
                  menu.Append(wx.ID_ANY, "Change Mouse Sensitivity"))
        menu.AppendSeparator()

        # Recording hotkey
        self.Bind(wx.EVT_MENU,
                  control.SettingsCtrl.recording_hotkey,
                  menu.Append(wx.ID_ANY, self.settings_text[1]))

        # Playback hotkey
        self.Bind(wx.EVT_MENU,
                  control.SettingsCtrl.playback_hotkey,
                  menu.Append(wx.ID_ANY, self.settings_text[2]))
        menu.AppendSeparator()

      
        submenu = wx.Menu()

        #takescreenshot
        self.scrn = control.ScreenshotCtrl(self)
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_screenshot,
                  menu.Append(wx.ID_ANY, "Take Screenshot"))

        #clickscreenshot
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_click,
                  menu.Append(wx.ID_ANY, "Get Click Screenshot Code"))

        #doubleclickscreenshot
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_doubleclick,
                  menu.Append(wx.ID_ANY, "Get DoubleClick Screenshot Code"))
        #locatescreenshot
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_locate,
                  menu.Append(wx.ID_ANY, "Get Find Screenshot Code"))
        #locateexitscreenshot
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_locateexit,
                  menu.Append(wx.ID_ANY, "Get Locate Screenshot And Exit Code"))
        #SetSpeed 
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_setspeed,
                  menu.Append(wx.ID_ANY, "Set Speed Code"))
        #open script file
        self.Bind(wx.EVT_MENU,
                  self.scrn.action_open,
                  menu.Append(wx.ID_ANY, "Open Script File"))
        #Exit
        self.Bind(wx.EVT_MENU,
                  self.on_exit_app,
                  menu.Append(wx.ID_ANY, self.settings_text[3]))
        return menu

    def __init__(self, *args, **kwds):
        """Build the interface."""

        if getattr(sys, 'frozen', False):
            self.path = sys._MEIPASS
        else: 
            self.path = Path(__file__).parent.absolute()
        wx.DEFAULT_DIALOG_STYLE
        style = wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX)
        kwds["style"] = kwds.get("style", 0) | style
        wx.Dialog.__init__(self, *args, **kwds)
        self.panel = wx.Panel(self)
        self.icon = wx.Icon(os.path.join(self.path, "img", "icon.png"))
        self.SetIcon(self.icon)
        self.taskbar = TaskBarIcon(self)
        self.taskbar.SetIcon(self.icon, "Automate")

        locale = self.__load_locale()
        self.app_text, self.settings_text = locale[:6], locale[6:]
        self.file_open_button = wx.BitmapButton(self,
                                                wx.ID_ANY,
                                                wx.Bitmap(os.path.join(self.path, "img", "file-upload.png"),
                                                          wx.BITMAP_TYPE_ANY))
        self.file_open_button.SetToolTip(self.app_text[0])
        self.file_open_button.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.save_button = wx.BitmapButton(self,
                                           wx.ID_ANY,
                                           wx.Bitmap(os.path.join(self.path, "img", "save.png"),
                                                     wx.BITMAP_TYPE_ANY))
        self.save_button.SetToolTip(self.app_text[1])
        self.save_button.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.record_button = wx.BitmapToggleButton(self,
                                                   wx.ID_ANY,
                                                   wx.Bitmap(os.path.join(self.path, "img", "video.png"),
                                                             wx.BITMAP_TYPE_ANY))
        self.record_button.SetToolTip(self.app_text[2])
        self.record_button.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.play_button = wx.BitmapToggleButton(self,
                                                 wx.ID_ANY,
                                                 wx.Bitmap(os.path.join(self.path, "img", "play-circle.png"),
                                                           wx.BITMAP_TYPE_ANY))
        self.play_button.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.remaining_plays = wx.StaticText(self, label=settings.CONFIG.get("DEFAULT", "Repeat Count"),
                                             style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.play_button.SetToolTip(self.app_text[3])

        self.compile_button = wx.BitmapButton(self,
                                              wx.ID_ANY,
                                              wx.Bitmap(os.path.join(self.path, "img", "download.png"),
                                                        wx.BITMAP_TYPE_ANY))
        self.compile_button.SetToolTip(self.app_text[4])
        self.compile_button.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.settings_button = wx.BitmapButton(self,
                                               wx.ID_ANY,
                                               wx.Bitmap(os.path.join(self.path, "img", "cog.png"),
                                                         wx.BITMAP_TYPE_ANY))
        self.settings_button.SetToolTip(self.app_text[5])
        self.settings_button.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        self.__add_bindings()
        self.__set_properties()
        self.__do_layout()
    def __load_locale(self):
        """Load the interface in english language."""
        try:
            lang = "en"
            locale = open(os.path.join(self.path, "lang", lang)
                          ).read().splitlines()
        except:
            return self.app_text + self.settings_text

        return locale

    def __add_bindings(self):
        # file_save_ctrl
        self.fsc = control.FileChooserCtrl(self)
        self.Bind(wx.EVT_BUTTON, self.fsc.load_file, self.file_open_button)
        self.Bind(wx.EVT_BUTTON, self.fsc.save_file, self.save_button)

        # record_button_ctrl
        self.rbc = control.RecordCtrl()
        self.Bind(wx.EVT_TOGGLEBUTTON, self.rbc.action, self.record_button)

        # play_button_ctrl
        self.pbc = control.PlayCtrl()
        self.Bind(wx.EVT_TOGGLEBUTTON, self.pbc.action, self.play_button)
       
        # compile_button_ctrl
        self.Bind(wx.EVT_BUTTON, control.CompileCtrl.compile,
                  self.compile_button)

        # settings_button_ctrl
        self.Bind(wx.EVT_BUTTON, self.on_settings_click, self.settings_button)
        self.sc = control.SettingsCtrl(self)

        self.Bind(wx.EVT_CLOSE, self.on_close_dialog)

        self.startthread()


        self.panel.SetFocus()

    def startthread(self):
        # Handle keyboard shortcuts
        self.keythread = threading.Thread(target=self.on_key_press)
        self.keythread.setDaemon(True)
        self.keythread.start()

    def __set_properties(self):
        self.file_open_button.SetSize(self.file_open_button.GetBestSize())
        self.save_button.SetSize(self.save_button.GetBestSize())
        self.record_button.SetSize(self.record_button.GetBestSize())
        self.play_button.SetSize(self.play_button.GetBestSize())
        self.compile_button.SetSize(self.compile_button.GetBestSize())
        self.settings_button.SetSize(self.settings_button.GetBestSize())

    def __do_layout(self):
        self.remaining_plays.Position = (225, 0)
        self.remaining_plays.SetBackgroundColour((255, 0, 0))
        self.remaining_plays.SetForegroundColour((255, 255, 255))
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.panel)
        main_sizer.Add(self.file_open_button, 0, 0, 0)
        main_sizer.Add(self.save_button, 0, 0, 0)
        main_sizer.Add(self.record_button, 0, 0, 0)
        main_sizer.Add(self.play_button, 0, 0, 0)
        main_sizer.Add(self.compile_button, 0, 0, 0)
        main_sizer.Add(self.settings_button, 0, 0, 0)
        self.SetSizer(main_sizer)
        self.Centre()
        main_sizer.Fit(self)
        self.Layout()

    
    def on_key_press(self):
        """ Create manually the event when the correct key is pressed."""
        while(True):
          
            if keyboard.is_pressed("esc+shift"):
                btn_event = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON)
                btn_event.EventObject = self.record_button
                if not self.record_button.Value:
                    self.record_button.SetValue(True)
                    self.rbc.action(btn_event)
                    speak("Start Now!")
                    break
                else:
                    self.record_button.SetValue(False)
                    self.rbc.action(btn_event)
                    speak("wait a moment please!")
                    time.sleep(1)
                    speak("Recorded All the Actions!")
            elif keyboard.is_pressed("esc+ctrl"):
                btn_event = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON)
                btn_event.EventObject = self.play_button
                if not self.play_button.Value:
                    speak("Executing the Script!")
                    self.play_button.SetValue( True)
                    self.pbc.action(btn_event)

    def on_exit_app(self, event):
        """Clean exit saving the settings."""
        settings.save_config()
        self.Destroy()
        self.taskbar.Destroy()

    def on_close_dialog(self, event):
        """Confirm exit."""
        dialog = wx.MessageDialog(self,
                                  message="Are you sure you want to quit?",
                                  caption="Confirm Exit",
                                  style=wx.YES_NO,
                                  pos=wx.DefaultPosition)
        response = dialog.ShowModal()

        if (response == wx.ID_YES):
            self.on_exit_app(event)
        else:
            event.StopPropagation()

class TaskBarIcon(wx.adv.TaskBarIcon):
    """Taskbar showing the state of the recording."""

    def __init__(self, parent):
        self.parent = parent
        super(TaskBarIcon, self).__init__()

main = ""