import shutil, PIL
import wx

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        # Main components ---------------------------------
        wx.Frame.__init__(self, parent, title=title, size=(500,600))
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        panel = wx.Panel(self) # Main Panel
        self.SetBackgroundColour('grey')

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menu_about = filemenu.Append(wx.ID_ABOUT, "&About","Information about this program")
        filemenu.AppendSeparator()
        menu_exit = filemenu.Append(wx.ID_EXIT,"&Exit","Terminate the program")

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.


        ## Content ---------------------------------------

        # create some sizers
        content_box = wx.BoxSizer(wx.VERTICAL)
        main_grid = wx.GridBagSizer(hgap=10, vgap=5)
        button_grid = wx.GridBagSizer(hgap=24, vgap=1)
        main_box = wx.BoxSizer(wx.HORIZONTAL)

        ## main_grid -----------------------------------
        # Logger
        self.logger = wx.TextCtrl(self, size=(300,225), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.logger.SetBackgroundColour((3, 62, 78))
        self.logger.SetForegroundColour((172, 180, 182))

        # Files to sort
        self.location = wx.StaticText(panel, label="Location:")
        self.location.SetForegroundColour("MIDNIGHT BLUE")
        main_grid.Add(self.location, pos=(2,0))
        self.location_input = wx.Button(panel, label="Open")
        self.Bind(wx.EVT_BUTTON, self.on_open_location, self.location_input)
        main_grid.Add(self.location_input, pos=(2,1))

        # Sorted destination
        self.destination = wx.StaticText(self, label="Destination:")
        self.destination.SetForegroundColour("MIDNIGHT BLUE")
        main_grid.Add(self.destination, pos=(3,0))
        self.destination_input = wx.Button(panel, label="Open")
        self.Bind(wx.EVT_BUTTON, self.on_open_destination, self.destination_input)
        main_grid.Add(self.destination_input, pos=(3,1))


        ## button_grid -----------------------------------

        # Clean log button
        self.clean_button = wx.Button(panel, label="Clean")
        self.Bind(wx.EVT_BUTTON, self.on_clean,self.clean_button)
        button_grid.Add(self.clean_button, pos=(0,5))

        # Add everything to content_box
        main_box.Add(main_grid, 0, wx.ALL, 5)
        main_box.Add(self.logger)
        content_box.Add(main_box, 0, wx.ALL, 5)
        content_box.Add(button_grid, 0, wx.ALL, 5)
        self.SetSizerAndFit(content_box)

        ## Events -------------------
        self.Bind(wx.EVT_MENU, self.on_about, menu_about)
        self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)

        # Show
        self.Show()


     # File dialog for cheats file
    def on_open_location(self, e):
         # otherwise ask the user what new file to open
        with wx.DirDialog(self, "Open files location",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # get the path
            self.files_location = fileDialog.GetPath()
        self.logger.AppendText("Location is:\n%s\n" % self.files_location)

    def on_open_destination(self, e):
         # otherwise ask the user what new file to open
        with wx.DirDialog(self, "Open files destination",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as d_dialog:
            if d_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # get the path
            self.files_destination = d_dialog.GetPath()
        self.logger.AppendText("Destination is:\n%s\n" % self.files_destination)

    def on_clean(self,e):
        self.logger.SetValue("")

    def on_about(self,e):
        dlg = wx.MessageDialog(self, "PhotoSorter, built with python and wxpython", "About PhotoSorter", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    # Exit method
    def on_exit(self,e):
        keyboard.unhook_all()
        self.Close(True)


if __name__ == '__main__':
    app = wx.App()
    frame = MainWindow(None, "PhotoSorter")
    frame.Show()
    app.MainLoop()
