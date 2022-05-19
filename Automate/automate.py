
"""Main File Of Automation Module"""

import gui

import wx

class Automate(wx.App):
    """Main class of the program."""

    def OnInit(self):
        """Initialize the main Window."""
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.main = gui.MainDialog(None, wx.ID_ANY, "Automate")
        gui.main = self.main
        self.SetTopWindow(self.main)
        self.main.Show()
        return True
#app = Automate(0)
#app.MainLoop()