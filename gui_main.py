import shutil, PIL, os, wx, threading, pickle
from sorter import FileSorter
from utils import threadsafe_generator
from custom_exceptions import WhyWouldYou, OutDirNotEmpty, DirMissing


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        # Other Vars ------------------------
        self.is_sorting = False
        self.sorter_thread = None
        self.settings = None
        self.user_values = None
        self.retries = 0
        # Main components ---------------------------------
        wx.Frame.__init__(self, parent, title=title, size=(650,600), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        panel = wx.Panel(self) # Main Panel
        self.SetBackgroundColour('grey')

        # Setting up the menu.
        file_menu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menu_about = file_menu.Append(wx.ID_ABOUT, "&About","Information about this program")
        file_menu.AppendSeparator()
        menu_exit = file_menu.Append(wx.ID_EXIT,"&Exit","Terminate the program")

        options_menu = wx.Menu()

        options_sort_remaining = options_menu.Append(wx.ID_ANY, "&Sort remaining", "Sort remaining files trough size or resolution")

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu,"&File") # Adding the "file_menu" to the MenuBar
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.


        ## Content ---------------------------------------

        # create some sizers
        content_box = wx.BoxSizer(wx.VERTICAL)
        main_grid = wx.GridBagSizer(hgap=10, vgap=5)
        button_grid = wx.GridBagSizer(hgap=34, vgap=1)
        main_box = wx.BoxSizer(wx.HORIZONTAL)

        ### main_grid -----------------------------------
        # Logger
        l_font = wx.Font(13, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.logger = wx.TextCtrl(self, size=(390,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.logger.SetBackgroundColour((3, 62, 78))
        self.logger.SetForegroundColour((172, 180, 182))
        self.logger.SetFont(l_font)

        # Files to sort
        s_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.files_location = None
        self.location = wx.StaticText(panel, label="Source:")
        self.location.SetFont(s_font)
        self.location.SetForegroundColour("MIDNIGHT BLUE")
        main_grid.Add(self.location, pos=(2,0))
        self.location_input = wx.Button(panel, label="Open")
        self.Bind(wx.EVT_BUTTON, self.on_open_location, self.location_input)
        main_grid.Add(self.location_input, pos=(2,1))

        # Sorted destination
        self.files_destination = None
        self.destination = wx.StaticText(self, label="Destination:")
        self.destination.SetFont(s_font)
        self.destination.SetForegroundColour("MIDNIGHT BLUE")
        main_grid.Add(self.destination, pos=(3,0))
        self.destination_input = wx.Button(panel, label="Open")
        self.Bind(wx.EVT_BUTTON, self.on_open_destination, self.destination_input)
        main_grid.Add(self.destination_input, pos=(3,1))

        # Sorting options
        self.sort_option = wx.StaticText(self, label="Sort by:")
        self.sort_option.SetFont(s_font)
        self.sort_option.SetForegroundColour("MIDNIGHT BLUE")
        main_grid.Add(self.sort_option, pos=(4,0))
        sort_options = ["size","res"]
        self.cb = wx.ComboBox(panel,
                              size=wx.DefaultSize,
                              choices=sort_options)
        self.cb.SetSelection(0)
        main_grid.Add(self.cb, pos=(4,1))
        # Run button
        self.run_button = wx.Button(panel, label="Run")
        self.Bind(wx.EVT_BUTTON, self.on_run, self.run_button)
        main_grid.Add(self.run_button, pos=(5,0))


        ### button_grid -----------------------------------

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

        # settings and values pickles
        self.load_settings_and_values()

        # Show
        self.Show()

    ## Functions ------------------------------------------------

    def load_settings(self):
        settings_loaded = False
        if not os.path.isfile("settings.pckl"):
            self.settings = {"Keep values": False}
            pickle.dump(open("settings.pckl", "wb"))
        else:
            self.settings = pickle.load(open("settings.pckl", "rb"))
            try:
                keep = self.settings["Keep values"]
                if keep == True or keep == "False":
                    settings_loaded = True
            except KeyError:
                os.remove("settings.pckl")
                if self.retries >= 5:
                    self.logger.AppendText("Failed to load settings after %s retries" % (self.retries))
                    self.retries = 0
                else:
                    self.load_settings()
        if settings_loaded:
            self.load_values()

    def load_values(self):
        try:
            if self.settings["Keep values"]:
                if not os.path.isfile("values.pckl"):
                    values = {"Source": "", "Dest": "", "Sort by": ""}
                    pickle.dump(open("values.pckl", "wb"))
                else:
                    self.user_values = pickle.load(open("values.pckl", "rb"))
                    self.files_location = self.user_values["Source"]
                    self.files_destination = self.user_values["Dest"]
                    # self.files_location = self.user_values["Source"]
        except KeyError:
            os.remove("values.pckl")
            if self.retries >= 5:
                self.logger.AppendText("Failed to load values after %s retries" % (self.retries))
                self.retries = 0
            else:
                self.load_values()


    # directory dialogs
    def on_open_location(self, _):
         # otherwise ask the user what new file to open
        with wx.DirDialog(self, "Open files location",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as d_dialog:
            if d_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # get the path
            self.files_location = d_dialog.GetPath()
        self.logger.AppendText("Source is:\n%s\n" % self.files_location)

    def on_open_destination(self, _):
         # otherwise ask the user what new file to open
        with wx.DirDialog(self, "Open files destination",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as d_dialog:
            if d_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # get the path
            self.files_destination = d_dialog.GetPath()
        self.logger.AppendText("Destination is:\n%s\n" % self.files_destination)

    # Check required input to run
    def has_required(self):
        option = self.cb.GetStringSelection()
        options = ["size","res"]
        if not self.files_location or not self.files_destination:
            return "Destination or location missing"
        elif not os.path.isdir(self.files_location):
            return "Files location is not a valid path"
        elif option == "" or option not in options:
            return "Option missing or invalid: %s" % option
        else:
            return True

    # a function that is called in a new thread to sort files without
    # stopping the user interface
    def thread_sorter(self):
        sorter = None
        try:
            sorter = FileSorter("TEST_IMAGES", "TEST_OUTPUT")
            for progress in sorter.sort_all():
                self.logger.AppendText(progress)
        except (WhyWouldYou, DirMissing, OutDirNotEmpty) as e:
            if e.__class__.__name__ == "WhyWouldYou":
                self.logger.AppendText("Your source path does not contain any relevant files\n")
            elif e.__class__.__name__ == "DirMissing":
                self.logger.AppendText("Your source path does not exist\n")
            elif e.__class__.__name__ == "OutDirNotEmpty":
                self.logger.AppendText("Destination is not empty, failed to run\n")
        self.logger.AppendText("Stopping sorter\n")
        self.is_sorting = False

    # check if sorter is running
    def is_running_sorter(self):
        if self.sorter_thread:
            if self.sorter_thread.is_alive():
                self.logger.AppendText("Sorter thread is alive\n")
                return True
        if self.is_sorting:
            self.logger.AppendText("Sorter is running\n")
            return True
        else:
            return False

    # Run sorter in a new thread
    def on_run(self, _):
        has_required = self.has_required()
        is_running = self.is_running_sorter()
        if has_required == True:
            if not is_running:
                self.logger.AppendText("Starting sorter\n")
                self.sorter_thread = threading.Thread(target=self.thread_sorter, args=())
                self.sorter_thread.start()
            else:
                self.logger.AppendText("Sorter is running\n")
        else:
            self.logger.AppendText("Failed to run:\n%s\n" % (has_required))

    # Clean log
    def on_clean(self,_):
        self.logger.SetValue("")

    # Clean
    def on_about(self,_):
        dlg = wx.MessageDialog(self, "PhotoSorter, built with python and wxPython", "About PhotoSorter", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    # Exit method
    def on_exit(self,_):
        keyboard.unhook_all()
        self.Close(True)

if __name__ == '__main__':
    app = wx.App()
    frame = MainWindow(None, "PhotoSorter")
    frame.Show()
    app.MainLoop()
