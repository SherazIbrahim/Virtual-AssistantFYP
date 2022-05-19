"""Control actions triggered by the GUI."""

import os
import py_compile
import shutil
import sys
import tempfile
import time
import pyperclip
from datetime import date
from pathlib import Path
import pyautogui
from pynput import keyboard, mouse
import gui
import settings

import wx
import wx.adv
import wx.lib.newevent as NE


TMP_PATH = os.path.join(tempfile.gettempdir(),
                        "automate-" + date.today().strftime("%Y%m%d"))
TMP_PATH_IM = os.path.join(tempfile.gettempdir(),
                        "automateimg-" + date.today().strftime("%Y%m%d")+".png")
DEFAULT_DIR = os.path.join (os.environ.get("APPDATA"),"automate")
if os.path.exists(DEFAULT_DIR) == False:
    #Directory Will created
    os.mkdir(DEFAULT_DIR)
    os.mkdir(os.path.join(DEFAULT_DIR,"images"))

#multiline string start of the script
HEADER = (
    f"import pyautogui\n"
    f"import time\n"
    f"pyautogui.FAILSAFE = False\n"

)

LOOKUP_SPECIAL_KEY = {}


class FileChooserCtrl:
    """Control class for both the open capture and save capture options.

    Keyword arguments:
    capture -- content of the temporary file
    parent -- the parent Frame
    """

    capture = str()

    def __init__(self, parent):
        """Set the parent frame."""
        self.parent = parent

    def load_content(self, path):
        """Load the temp file capture from disk."""
        if not path or not os.path.isfile(path):
            return None
        with open(path, 'r') as f:
            return f.read()

    def load_file(self, event):
        """Load a capture manually chosen by the user."""
        title = "Choose a capture file:"
        dlg = wx.FileDialog(self.parent,
                            message=title,
                            defaultDir=DEFAULT_DIR,
                            defaultFile="capture",
                            style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self._capture = self.load_content(dlg.GetPath())
            with open(TMP_PATH, 'w') as f:
                f.write(self._capture)
        event.EventObject.Parent.panel.SetFocus()
        dlg.Destroy()

    def save_file(self, event):
        """Save the capture currently loaded."""
        event.EventObject.Parent.panel.SetFocus()

        with wx.FileDialog(self.parent, "Save capture file", wildcard="*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog.SetDirectory(DEFAULT_DIR)

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                shutil.copy(TMP_PATH, pathname)
            except IOError:
                wx.LogError(f"Cannot save current data in file {pathname}.")


class RecordCtrl:
    """Control class for the record button.

    Keyword arguments:
    capture -- current recording
    mouse_sensibility -- granularity for mouse capture
    """

    def __init__(self):
        """Initialize a new record."""
        self._header = HEADER

        self._capture = [self._header]
        self._lastx, self._lasty = pyautogui.position()
        self.mouse_sensibility = settings.CONFIG.getint('DEFAULT', 'mouse_sensibility')
        if getattr(sys, 'frozen', False):
            self.path = sys._MEIPASS
        else:
            self.path = Path(__file__).parent.absolute()

        LOOKUP_SPECIAL_KEY[str(keyboard.Key.alt)] = 'alt'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.alt_l)] = 'altleft'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.alt_r)] = 'altright'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.alt_gr)] = 'altright'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.backspace)] = 'backspace'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.caps_lock)] = 'capslock'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.cmd)] = 'winleft'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.cmd_r)] = 'winright'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.ctrl)] = 'ctrl'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.ctrl_l)] = 'ctrlleft'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.ctrl_r)] = 'ctrlright'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.delete)] = 'delete'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.down)] = 'down'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.end)] = 'end'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.enter)] = 'enter'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.esc)] = 'esc'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f1)] = 'f1'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f2)] = 'f2'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f3)] = 'f3'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f4)] = 'f4'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f5)] = 'f5'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f6)] = 'f6'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f7)] = 'f7'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f8)] = 'f8'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f9)] = 'f9'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f10)] = 'f10'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f11)] = 'f11'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.f12)] = 'f12'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.home)] = 'home'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.left)] = 'left'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.page_down)] = 'pagedown'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.page_up)] = 'pageup'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.right)] = 'right'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.shift)] = 'shift'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.shift_l)] = 'shiftleft'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.shift_r)] = 'shiftright'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.space)] = 'space'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.tab)] = 'tab'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.up)] = 'up'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.media_play_pause)] = 'playpause'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.insert)] = 'insert'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.num_lock)] = 'numlock'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.pause)] = 'pause'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.print_screen)] = 'printscreen'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.scroll_lock)] = 'scrolllock'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.media_volume_mute)]  = 'volumemute'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.media_volume_down)] = 'volumedown'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.media_volume_up)] = 'volumeup'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.media_previous)] = 'prevtrack'
        LOOKUP_SPECIAL_KEY[str(keyboard.Key.media_next)] = 'nexttrack'
        LOOKUP_SPECIAL_KEY["<12>"] = ''
        LOOKUP_SPECIAL_KEY["'\\x01'"] = "'ctrl','a'"
        LOOKUP_SPECIAL_KEY["'\\x02'"] = "'ctrl','b'"
        LOOKUP_SPECIAL_KEY["'\\x03'"] = "'ctrl','c'"
        LOOKUP_SPECIAL_KEY["'\\x04'"] = "'ctrl','d'"
        LOOKUP_SPECIAL_KEY["'\\x05'"] = "'ctrl','e'"
        LOOKUP_SPECIAL_KEY["'\\x06'"] = "'ctrl','f'"
        LOOKUP_SPECIAL_KEY["'\\x07'"] = "'ctrl','g'"
        LOOKUP_SPECIAL_KEY["'\\x08'"] = "'ctrl','h'"
        LOOKUP_SPECIAL_KEY["'\\t'"] = "'ctrl','i'"
        LOOKUP_SPECIAL_KEY["'\\n'"] = "'ctrl','j'"
        LOOKUP_SPECIAL_KEY["'\\x0b'"] = "'ctrl','k'"
        LOOKUP_SPECIAL_KEY["'\\x0c'"] = "'ctrl','l'"
        LOOKUP_SPECIAL_KEY["'\\r'"] = "'ctrl','m'"
        LOOKUP_SPECIAL_KEY["'\\x0e'"] = "'ctrl','n'"
        LOOKUP_SPECIAL_KEY["'\\x0f'"] = "'ctrl','o'"
        LOOKUP_SPECIAL_KEY["'\\x10'"] = "'ctrl','p'"
        LOOKUP_SPECIAL_KEY["'\\x11'"] = "'ctrl','q'"
        LOOKUP_SPECIAL_KEY["'\\x12'"] = "'ctrl','r'"
        LOOKUP_SPECIAL_KEY["'\\x13'"] = "'ctrl','s'"
        LOOKUP_SPECIAL_KEY["'\\x14'"] = "'ctrl','t'"
        LOOKUP_SPECIAL_KEY["'\\x15'"] = "'ctrl','u'"
        LOOKUP_SPECIAL_KEY["'\\x16'"] = "'ctrl','v'"
        LOOKUP_SPECIAL_KEY["'\\x17'"] = "'ctrl','w'"
        LOOKUP_SPECIAL_KEY["'\\x18'"] = "'ctrl','x'"
        LOOKUP_SPECIAL_KEY["'\\x19'"] = "'ctrl','y'"
        LOOKUP_SPECIAL_KEY["'\\x1a'"] = "'ctrl','z'"
        LOOKUP_SPECIAL_KEY["'\\x1b'"] = "'ctrl','['"
        LOOKUP_SPECIAL_KEY["'\\x1d'"] = "'ctrl',']'"
        LOOKUP_SPECIAL_KEY["'\\x1c'"] = "'ctrl','\'"
        LOOKUP_SPECIAL_KEY["<192>"] = "'ctrl','`'"
        LOOKUP_SPECIAL_KEY["<49>"] = "'ctrl','1'"
        LOOKUP_SPECIAL_KEY["<50>"] = "'ctrl','2'"
        LOOKUP_SPECIAL_KEY["<51>"] = "'ctrl','3'"
        LOOKUP_SPECIAL_KEY["<52>"] = "'ctrl','4'"
        LOOKUP_SPECIAL_KEY["<53>"] = "'ctrl','5'"
        LOOKUP_SPECIAL_KEY["<54>"] = "'ctrl','6'"
        LOOKUP_SPECIAL_KEY["<55>"] = "'ctrl','7'"
        LOOKUP_SPECIAL_KEY["<56>"] = "'ctrl','8'"
        LOOKUP_SPECIAL_KEY["<57>"] = "'ctrl','9'"
        LOOKUP_SPECIAL_KEY["<48>"] = "'ctrl','0'"
        LOOKUP_SPECIAL_KEY["<189>"] = "'ctrl','-'"
        LOOKUP_SPECIAL_KEY["<187>"] = "'ctrl','+'"
        LOOKUP_SPECIAL_KEY["<111>"] = "'ctrl','/'"
        LOOKUP_SPECIAL_KEY["<106>"] = "'ctrl','*'"
        LOOKUP_SPECIAL_KEY["<109>"] = "'ctrl','-'"
        LOOKUP_SPECIAL_KEY["<107>"] = "'ctrl','+'"
        LOOKUP_SPECIAL_KEY["<96>"] = "0"
        LOOKUP_SPECIAL_KEY["<97>"] = "1"
        LOOKUP_SPECIAL_KEY["<98>"] = "2"
        LOOKUP_SPECIAL_KEY["<99>"] = "3"
        LOOKUP_SPECIAL_KEY["<100>"] = "4"
        LOOKUP_SPECIAL_KEY["<101>"] = "5"
        LOOKUP_SPECIAL_KEY["<102>"] = "6"
        LOOKUP_SPECIAL_KEY["<103>"] = "7"
        LOOKUP_SPECIAL_KEY["<104>"] = "8"
        LOOKUP_SPECIAL_KEY["<105>"] = "9"
        LOOKUP_SPECIAL_KEY["<110>"] = "."
        LOOKUP_SPECIAL_KEY["<186>"] = "'ctrl',';'"
        LOOKUP_SPECIAL_KEY["<222>"] = "'ctrl','''"
        LOOKUP_SPECIAL_KEY["<188>"] = "'ctrl',','"
        LOOKUP_SPECIAL_KEY["<190>"] = "'ctrl','.'"
        LOOKUP_SPECIAL_KEY["<1>"] = "'ctrl','/'"
        LOOKUP_SPECIAL_KEY["'\\\\'"] = "'alt','\'"
        LOOKUP_SPECIAL_KEY["<65>"] = "'ctrl','alt','a'"
        LOOKUP_SPECIAL_KEY["<66>"] = "'ctrl','alt','b'"
        LOOKUP_SPECIAL_KEY["<67>"] = "'ctrl','alt','c'"
        LOOKUP_SPECIAL_KEY["<68>"] = "'ctrl','alt','d'"
        LOOKUP_SPECIAL_KEY["<69>"] = "'ctrl','alt','e'"
        LOOKUP_SPECIAL_KEY["<70>"] = "'ctrl','alt','f'"
        LOOKUP_SPECIAL_KEY["<71>"] = "'ctrl','alt','g'"
        LOOKUP_SPECIAL_KEY["<72>"] = "'ctrl','alt','h'"
        LOOKUP_SPECIAL_KEY["<73>"] = "'ctrl','alt','i'"
        LOOKUP_SPECIAL_KEY["<74>"] = "'ctrl','alt','j'"
        LOOKUP_SPECIAL_KEY["<75>"] = "'ctrl','alt','k'"
        LOOKUP_SPECIAL_KEY["<76>"] = "'ctrl','alt','l'"
        LOOKUP_SPECIAL_KEY["<77>"] = "'ctrl','alt','m'"
        LOOKUP_SPECIAL_KEY["<78>"] = "'ctrl','alt','n'"
        LOOKUP_SPECIAL_KEY["<79>"] = "'ctrl','alt','o'"
        LOOKUP_SPECIAL_KEY["<80>"] = "'ctrl','alt','p'"
        LOOKUP_SPECIAL_KEY["<81>"] = "'ctrl','alt','q'"
        LOOKUP_SPECIAL_KEY["<82>"] = "'ctrl','alt','r'"
        LOOKUP_SPECIAL_KEY["<83>"] = "'ctrl','alt','s'"
        LOOKUP_SPECIAL_KEY["<84>"] = "'ctrl','alt','t'"
        LOOKUP_SPECIAL_KEY["<85>"] = "'ctrl','alt','u'"
        LOOKUP_SPECIAL_KEY["<86>"] = "'ctrl','alt','v'"
        LOOKUP_SPECIAL_KEY["<87>"] = "'ctrl','alt','w'"
        LOOKUP_SPECIAL_KEY["<88>"] = "'ctrl','alt','x'"
        LOOKUP_SPECIAL_KEY["<89>"] = "'ctrl','alt','y'"
        LOOKUP_SPECIAL_KEY["<90>"] = "'ctrl','alt','z'"
        LOOKUP_SPECIAL_KEY["<219>"] = "'ctrl','alt','['"
        LOOKUP_SPECIAL_KEY["<220>"] = "'ctrl','alt','\'"
        LOOKUP_SPECIAL_KEY["<221>"] = "'ctrl','alt',']'"
        LOOKUP_SPECIAL_KEY["<191>"] = "'ctrl','alt','/'"
        LOOKUP_SPECIAL_KEY["<170>"] = "winleft"
        LOOKUP_SPECIAL_KEY["<255>"] = ""
        

    def write_mouse_action(self, engine="pyautogui", move="", parameters=""):
        """Append a new mouse move to capture.

        Keyword arguments:
        engine -- the replay library used (default pyautogui)
        move -- the mouse movement (mouseDown, mouseUp, scroll, moveTo)
        parameters -- the details of the movement
        """
        def isinteger(s):
            try:
                int(s)
                return True
            except:
                return False

        if move == "moveTo":
            coordinates = [int(s)
                           for s in parameters.split(", ") if isinteger(s)]
            if abs(coordinates[0] - self._lastx) < self.mouse_sensibility \
               and abs(coordinates[1] - self._lasty) < self.mouse_sensibility:
                return
            else:
                self._lastx, self._lasty = coordinates
        self._capture.append(engine + "." + move + '(' + parameters + ')')

    def write_keyboard_action(self, engine="pyautogui", move="", key=""):
        """Append keyboard actions to the class variable capture.

        Keyword arguments:
        - engine: the module which will be used for the replay
        - move: keyDown | keyUp
        - key: The key pressed
        """
       
        suffix = "(" + repr(key) + ")"
        #if move == "keyDown":
            # Corner case: Multiple successive keyDown
            #if move + suffix in self._capture[-1]:
                #move = 'press'
                #self._capture[-1] = engine + "." + move + suffix
            
        if move + suffix == "keyDown('shiftleft')":
                if self._capture[-1] == engine + "." + move + "('esc')":
                    gui.MainDialog.startthread(gui.main)

        self._capture.append(engine + "." + move + suffix)
    def write_keyboard_actionctrl(self, engine="pyautogui", move="", key=""):
        """Append keyboard actions to the class variable capture.

        Keyword arguments:
        - engine: the module which will be used for the replay
        - move: keyDown | keyUp
        - key: The key pressed
        """
        suffix = "(" + key + ")"
        self._capture.append(engine + "." + move + suffix)
    

    def on_move(self, x, y):
        """Triggered by a mouse move."""
        if not self.recording:
            return False
        b = time.perf_counter()
        timeout = int(b - self.last_time)
        if timeout > 0:
            self._capture.append(f"time.sleep({timeout})")
        self.last_time = b
        self.write_mouse_action(move="moveTo", parameters=f"{x}, {y}")

    def on_click(self, x, y, button, pressed):
        """Triggered by a mouse click."""
        if not self.recording:
            return False
        if pressed:
            if button == mouse.Button.left:
                self.write_mouse_action(
                    move="mouseDown", parameters=f"{x}, {y}, 'left'")
            elif button == mouse.Button.right:
                self.write_mouse_action(
                    move="mouseDown", parameters=f"{x}, {y}, 'right'")
            elif button == mouse.Button.middle:
                self.write_mouse_action(
                    move="mouseDown", parameters=f"{x}, {y}, 'middle'")
            else:
                wx.LogError("Mouse Button not recognized")
        else:
            if button == mouse.Button.left:
                self.write_mouse_action(
                    move="mouseUp", parameters=f"{x}, {y}, 'left'")
            elif button == mouse.Button.right:
                self.write_mouse_action(
                    move="mouseUp", parameters=f"{x}, {y}, 'right'")
            elif button == mouse.Button.middle:
                self.write_mouse_action(
                    move="mouseUp", parameters=f"{x}, {y}, 'middle'")
            else:
                wx.LogError("Mouse Button not recognized")

    def on_scroll(self, x, y, dx, dy):
        """Triggered by a mouse wheel scroll."""
        if not self.recording:
            return False
        self.write_mouse_action(move="scroll", parameters=f"{y}")

    def on_press(self, key):
        """Triggered by a key press."""
        b = time.perf_counter()
        timeout = int(b - self.last_time)
        if timeout > 0:
            self._capture.append(f"time.sleep({timeout})")
        self.last_time = b
        try:
            # Ignore presses on Fn key
            if key.char:
                if (str(key) in LOOKUP_SPECIAL_KEY.keys() ):
                    if (LOOKUP_SPECIAL_KEY[str(key)].find(",") )!= -1:
                        self.write_keyboard_actionctrl(move="hotkey",
                                       key=LOOKUP_SPECIAL_KEY[str(key)])
                    
                else:
                    self.write_keyboard_action(move='keyDown', key=key.char)
                

            else:
                self.write_keyboard_actionctrl(move="hotkey",
                                       key=LOOKUP_SPECIAL_KEY[str(key)])
        except AttributeError:
                self.write_keyboard_action(move="keyDown",
                                       key=LOOKUP_SPECIAL_KEY[str(key)])

            

    def on_release(self, key):
       """Triggered by a key released."""

       if not self.recording:
            return False
       else:
            if len(str(key)) <= 3:
                self.write_keyboard_action(move='keyUp', key=key)
            else:
                self.write_keyboard_action(move="keyUp",
                                           key=LOOKUP_SPECIAL_KEY[str(key)])
                    

    def action(self, event):
        """Triggered when the recording button is clicked on the GUI."""
        self.mouse_sensibility = settings.CONFIG.getint('DEFAULT', 'mouse_sensibility')
        listener_mouse = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        listener_keyboard = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        if event.EventObject.Value:
            listener_keyboard.start()
            listener_mouse.start()
            self.last_time = time.perf_counter()
            self.recording = True
            recording_state = wx.Icon(os.path.join(
                self.path, "img", "icon-recording.png"))
        else:
            self.recording = False
            with open(TMP_PATH, 'w') as f:
                self.write_keyboard_action(move="keyUp",
                                           key=LOOKUP_SPECIAL_KEY[str(keyboard.Key.shift_l)])
                self.write_keyboard_action(move="keyUp",
                                           key=LOOKUP_SPECIAL_KEY[str(keyboard.Key.esc)])
                f.seek(0)
                f.write("\n".join(self._capture))
                f.truncate()
            self._capture = [self._header]
            recording_state = wx.Icon(
                os.path.join(self.path, "img", "icon.png"))
        event.GetEventObject().GetParent().taskbar.SetIcon(recording_state)

class PlayCtrl:
    """Control class for the play button."""

    global TMP_PATH

    def __init__(self):
        self.count = settings.CONFIG.getint('DEFAULT', 'Repeat Count')
        self.count_was_updated = False
        self.ThreadEndEvent, self.EVT_THREAD_END = NE.NewEvent()

    def action(self, event):
        """Replay a `count` number of time."""
        toggle_button = event.GetEventObject()
        toggle_button.Parent.panel.SetFocus()
        if toggle_button.Value:
            self.count = settings.CONFIG.getint('DEFAULT', 'Repeat Count')
            if TMP_PATH is None or not os.path.isfile(TMP_PATH):
                wx.LogError("No capture loaded")
                event = self.ThreadEndEvent(
                    count=self.count, toggle_value=False)
                wx.PostEvent(toggle_button.Parent, event)
                return
            '''with open(TMP_PATH, 'r') as f:
                capture = f.readlines()'''
            capture = py_compile.compile(TMP_PATH)
            if self.count > 0:
                for x in range(self.count):
                        os.system(capture)
            toggle_button.SetValue(False)
        else:
            settings.save_config()

class CompileCtrl:
    """Produce an executable Python bytecode file."""

    @staticmethod
    def compile(event):
        """Return a compiled version of the capture currently loaded.

         It only returns a bytecode file.
        """
        try:
            bytecode_path = py_compile.compile(TMP_PATH)
        except:
            wx.LogError("No capture loaded")
            return
        default_file = "capture.pyc"
        event.EventObject.Parent.panel.SetFocus()
        with wx.FileDialog(parent=event.GetEventObject().Parent, message="Save capture executable",
                           defaultDir=os.path.expanduser("~"), defaultFile=default_file, wildcard="*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog.SetDirectory(DEFAULT_DIR)
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed his/her mind
            pathname = fileDialog.GetPath()
            try:
                shutil.copy(bytecode_path, pathname)
            except IOError:
                wx.LogError(f"Cannot save current data in file {pathname}.")


class SettingsCtrl:
    """Control class for the settings."""

    def __init__(self, main_dialog):
        """Copy the reference of the main Window."""
        self.main_dialog = main_dialog
    
    def mouse_sensitivity(self, event):
        """Set the mouse sensitivity."""
        current_value = settings.CONFIG.getint('DEFAULT', 'mouse_sensibility')
        dialog = wx.NumberEntryDialog(None, message="Set Mouse Senstivity (Input Should Number):",
                                      prompt="", caption="Mouse Sensitivity", value=current_value, min=5, max=80)
        dialog.ShowModal()
        new_value = str(dialog.Value)
        dialog.Destroy()
        settings.CONFIG['DEFAULT']['mouse_sensibility'] = new_value
        settings.save_config()
    def repeat_count(self, event):
        """Set the repeat count."""
        current_value = settings.CONFIG.getint('DEFAULT', 'Repeat Count')
        dialog = wx.NumberEntryDialog(None, message="Choose a repeat count",
                                      prompt="", caption="Repeat Count", value=current_value, min=1, max=999)
        dialog.ShowModal()
        new_value = str(dialog.Value)
        dialog.Destroy()
        settings.CONFIG['DEFAULT']['Repeat Count'] = new_value
        settings.save_config()
        self.main_dialog.remaining_plays.Label = new_value
    @staticmethod
    def recording_hotkey(event):
        """Show the recording hotkey."""
        pyautogui.alert(text="Recording Hot Key : ctrl+alt+r",title='Error Message',button='OK')
    @staticmethod
    def playback_hotkey(event):
        """Show the playback hotkey."""
        pyautogui.alert(text="PlayBack Hot Key : ctrl+alt+p",title='Error Message',button='OK')

class ScreenshotCtrl:
    """Control class for the screenshots."""
   
    def __init__(self,parent):
         self.parent = parent
         self.x1 = 0
         self.y1 = 0
         self.x2 = 10
         self.y2 = 10
         self.count = 1
         self.listener_mouse = mouse.Listener(
            on_click= self.on_click)

    def take_screenshot(self):
        """takes screenshots."""
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        if self.width == 0:
            self.width = 1
        if self.height == 0:
            self.height = 1
        pyautogui.screenshot(TMP_PATH_IM,region=(self.x1,self.y1,self.width,self.height))

    def on_click(self, x, y, button, pressed):
        """Triggered by a mouse click."""
        if pressed:
            if button == mouse.Button.left:
                if self.count == 1:
                    self.x1 = x
                    self.y1 = y
                    self.count = 2
                            
                elif self.count == 2:
                    self.x2 = x
                    self.y2 = y
                    self.count = 3
                    self.listener_mouse.stop()
                    if self.x1 > self.x2:
                        temp = self.x2
                        self.x2 = self.x1
                        self.x1 = temp
                    if self.y1 > self.y2:
                        temp = self.y2
                        self.y2 = self.y1
                        self.y1 = temp
                    self.take_screenshot()
                    with wx.FileDialog(self.parent, "Save capture file", wildcard="*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                        fileDialog.SetDirectory(os.path.join(DEFAULT_DIR,"images"))
                        if fileDialog.ShowModal() == wx.ID_CANCEL:
                            return     # the user changed their mind
                        # save the current contents in the file
                        pathname = fileDialog.GetPath()
                        try:
                            shutil.copy(TMP_PATH_IM, pathname)
                        except IOError:
                            wx.LogError(f"Cannot save current data in file {pathname}.")
                    
    def action_screenshot(self,event):
        self.count = 1
        self.listener_mouse.start()
    def action_open(self,event):
        os.startfile(TMP_PATH)
    def action_click(self,event):
        title = "Choose a Screenshot file:"
        dlg = wx.FileDialog(self.parent,
                            message=title,
                            defaultDir="~",
                            defaultFile="img.png",
                            style=wx.DD_DEFAULT_STYLE)
        dlg.SetDirectory(os.path.join(DEFAULT_DIR,"images"))
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            wait = pyautogui.prompt(text='How long(seconds) should script wait if image not found?(Input Should be a number)', title='Waiting Time If Image Not Found!' , default='30')
            if (wait.isnumeric() == False) | (int(wait) < 30) :
                wait = "30"
            str = "i = 0\n"
            str += 'path = r"'+path+'"\n'
            str += "while(True):\n"
            str += "\tloc = pyautogui.locateCenterOnScreen(path,grayscale=False,confidence=.8)\n"
            str += "\tif loc!= None:\n"
            str += "\t\tx,y = loc\n"
            str += "\t\tpyautogui.click(x,y)\n"
            str += "\t\tbreak\n"
            str += "\telse:\n"
            str += "\t\tif(i==0):\n"
            str += "\t\t\ti+=1\n"
            str += "\t\t\ttime.sleep("+wait+")\n"
            str += "\t\telse:\n"
            str += "\t\t\tpyautogui.alert(text='Error Occcurred!',title='Error Message',button='OK')\n"
            str += "\t\t\tquit()\n"
            pyperclip.copy(str)
            msgdialog = wx.MessageDialog(self.parent, 'Code copied to clipboard!', caption='Add Condition To Script',style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION , pos=wx.DefaultPosition)
            msgdialog.ShowModal()
  
    def action_doubleclick(self,event):
        title = "Choose a Screenshot file:"
        dlg = wx.FileDialog(self.parent,
                            message=title,
                            defaultDir="~",
                            defaultFile="img.png",
                            style=wx.DD_DEFAULT_STYLE)
        dlg.SetDirectory(os.path.join(DEFAULT_DIR,"images"))
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            wait = pyautogui.prompt(text='How long(seconds) should script wait if image not found?(Input Should be a number)', title='Waiting Time If Image Not Found!' , default='30')
            if (wait.isnumeric() == False) | (int(wait) < 30):
                wait = "30"  
            str = "i = 0\n"
            str += 'path = r"'+path+'"\n'
            str += "while(True):\n"
            str += "\tloc = pyautogui.locateCenterOnScreen(path,grayscale=False,confidence=.8)\n"
            str += "\tif loc!= None:\n"
            str += "\t\tx,y = loc\n"
            str += "\t\tpyautogui.doubleClick(x,y)\n"
            str += "\t\tbreak\n"
            str += "\telse:\n"
            str += "\t\tif(i==0):\n"
            str += "\t\t\ti+=1\n"
            str += "\t\t\ttime.sleep("+wait+")\n"
            str += "\t\telse:\n"
            str += "\t\t\tpyautogui.alert(text='Error Occcurred!',title='Error Message',button='OK')\n"
            str += "\t\t\tquit()\n"
            pyperclip.copy(str)
            msgdialog = wx.MessageDialog(self.parent, 'Code copied to clipboard!', caption='Add Condition To Script',style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION , pos=wx.DefaultPosition)
            msgdialog.ShowModal() 
    def action_locate(self,event):
        title = "Choose a Screenshot file:"
        dlg = wx.FileDialog(self.parent,
                            message=title,
                            defaultDir="~",
                            defaultFile="img.png",
                            style=wx.DD_DEFAULT_STYLE)
        dlg.SetDirectory(os.path.join(DEFAULT_DIR,"images"))
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            wait = pyautogui.prompt(text='How long(seconds) should script wait if image not found?(Input Should be a number)', title='Waiting Time If Image Not Found!' , default='30')
            if (wait.isnumeric() == False) | (int(wait) < 30):
                wait = "30"
            str = "i = 0\n"
            str += 'path = r"'+path+'"\n'
            str += "while(True):\n"
            str += "\tloc = pyautogui.locateCenterOnScreen(path,grayscale=False,confidence=.8)\n"
            str += "\tif loc!= None:\n"
            str += "\t\tbreak\n"
            str += "\telse:\n"
            str += "\t\tif(i==0):\n"
            str += "\t\t\ti+=1\n"
            str += "\t\t\ttime.sleep("+wait+")\n"
            str += "\t\telse:\n"
            str += "\t\t\tpyautogui.alert(text='Error Occcurred!',title='Error Message',button='OK')\n"
            str += "\t\t\tquit()\n"
            pyperclip.copy(str)
            msgdialog = wx.MessageDialog(self.parent, 'Code copied to clipboard!', caption='Add Condition To Script',style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION , pos=wx.DefaultPosition)
            msgdialog.ShowModal()  
    def action_locateexit(self,event):
        title = "Choose a Screenshot file:"
        dlg = wx.FileDialog(self.parent,
                            message=title,
                            defaultDir="~",
                            defaultFile="img.png",
                            style=wx.DD_DEFAULT_STYLE)
        dlg.SetDirectory(os.path.join(DEFAULT_DIR,"images"))
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
            wait = pyautogui.prompt(text='How long(seconds) should script wait if image not found?(Input Should be a number)', title='Waiting Time If Image Not Found!' , default='30')
            if (wait.isnumeric() == False) | (int(wait) < 30):
                wait = "30"
            str = "i = 0\n"
            str += 'path = r"'+path+'"\n'
            str += "while(True):\n"
            str += "\tloc = pyautogui.locateCenterOnScreen(path,grayscale=False,confidence=.8)\n"
            str += "\tif loc != None:\n"
            str += "\t\tif(i==0):\n"
            str += "\t\t\ti+=1\n"
            str += "\t\t\ttime.sleep("+wait+")\n"
            str += "\t\telse:\n"
            str += "\t\t\tpyautogui.alert(text='Required Image Found!',title='Exit Message',button='OK')\n"
            str += "\t\t\tquit()\n"
            str += "\telse:\n"
            str += "\t\tbreak\n"
            pyperclip.copy(str)
            msgdialog = wx.MessageDialog(self.parent, 'Code copied to clipboard!', caption='Add Condition To Script',style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION , pos=wx.DefaultPosition)
            msgdialog.ShowModal()  
    def action_setspeed(self,event):
        speed = pyautogui.prompt(text='Enter Speed (Input Should be a number (Small number => high speed)) : ', title='Speed Of Script To be Executed:!' , default='0.2')
        if self.isfloat(speed) == False:
            speed = "0.2"
        str = "pyautogui.PAUSE = "+speed+"\n"
        pyperclip.copy(str)
        msgdialog = wx.MessageDialog(self.parent, 'Code copied to clipboard!', caption='Add Code To Script',style=wx.OK|wx.CENTRE|wx.ICON_INFORMATION , pos=wx.DefaultPosition)
        msgdialog.ShowModal()
    def isfloat(self,num):
        try:
            float (num)
            return True
        except:
            return False