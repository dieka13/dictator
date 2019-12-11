import os

import wx
import wx.richtext as rt

import helper as h


class MainWindow(wx.Frame):

    START_TAG_TMPL = '<{}>'
    END_TAG_TMPL = '</{}>'

    TAGS = ['Per', 'Tit', 'Org', 'Loc', 'Date']
    SHORTCUT_MAP = {t[0]: i for i, t in enumerate(TAGS)}

    tag_hist = h.TagHistory()

    def __init__(self, parent, title):
        self.dirname = ''

        wx.Frame.__init__(self, parent, title=title)

        # Init main layout sizer
        self.init_menubar()
        self.init_statusbar()
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # --- Left Side ---
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_NOHIDESEL)
        # self.text_ctrl = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL)
        self.text_ctrl.SetFont(
            wx.Font(wx.FontInfo(18).Family(wx.FONTFAMILY_MODERN))
        )
        self.text_ctrl.SetEditable(False)
        self.main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.LEFT, 2)

        # --- Right Side ---
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer.SetMinSize(150, -1)
        self.main_sizer.Add(self.right_sizer, 0, wx.RIGHT | wx.LEFT, 2)

        box = wx.StaticBox(self, wx.ID_ANY, "StaticBox")
        topBorder, otherBorder = box.GetBordersForSizer()
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.AddSpacer(topBorder - 10)
        text = wx.StaticText(box, wx.ID_ANY, "This window is a child of the staticbox")
        box_sizer.Add(text, 1, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, otherBorder + 30)
        text2 = wx.StaticText(box, wx.ID_ANY, "This window is a child of the staticbox")
        box_sizer.Add(text2, 1, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, otherBorder + 30)
        box.SetSizer(box_sizer)
        self.right_sizer.Add(box, 1, wx.EXPAND|wx.ALL, 2)

        # buttons
        self.buttons = []
        self.buttons.append(wx.Button(self, -1, 'Tag'))
        self.buttons.append(wx.Button(self, -1, 'Remove Tag'))
        for b in self.buttons:
            self.right_sizer.Add(b, 0, wx.EXPAND)

        #
        self.edit_toggle = wx.CheckBox(self, -1, "Allow Edit (suspend tagging)")
        self.right_sizer.Add(self.edit_toggle)
        self.suggestion_toggle = wx.CheckBox(self, -1, "Tag Suggestion")
        self.right_sizer.Add(self.suggestion_toggle)
        self.tag_hide_toggle = wx.CheckBox(self, -1, "Hide tagged")
        self.right_sizer.Add(self.tag_hide_toggle)

        #Layout sizers
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)
        self.main_sizer.Fit(self)

        #
        self.init_bindings()
        self.init_color()

    def init_menubar(self):

        # Setting up the menu.
        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, '&Open', ' Open a file to edit')
        menuAbout = filemenu.Append(wx.ID_ABOUT, '&About', ' Information about this program')
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, 'E&xit', ' Terminate the program')

        configMenu = wx.Menu()
        menuTagConfig = configMenu.Append(0, '&Tag Configuration', ' Configure tags settings')
        menuEditorConfig = configMenu.Append(0, '&Editor Configuration', ' Configure editor settings')

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, 'F&ile')  # Adding the 'filemenu' to the MenuBar
        menuBar.Append(configMenu, 'C&onfiguration')  # Adding the 'filemenu' to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

    def init_statusbar(self):
        # add status bar
        self.status_bar = self.CreateStatusBar(2)  # A Statusbar in the bottom of the window
        self.status_bar.SetStatusWidths((-1, 300))
        self.SetStatusText('No File Loaded', 0)
        self.SetStatusText('Row: 0, Col: 0, Selection: (0, 0)', 1)

    def init_bindings(self):

        self.edit_toggle.Bind(wx.EVT_CHECKBOX, self.on_edit_toggle)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_editor_change)
        self.buttons[0].Bind(wx.EVT_BUTTON, self.on_tag_apply)
        self.buttons[1].Bind(wx.EVT_BUTTON, self.on_tag_remove)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_text_keyevt)
        self.text_ctrl.Bind(wx.EVT_LEFT_UP, self.on_text_click)

    def init_color(self):

        # define apply_tag background style
        self.TAG_STYLE = wx.TextAttr()
        self.TAG_STYLE.SetBackgroundColour(wx.Colour(145, 221, 254))
        self.TAG_STYLE.SetTextColour(wx.WHITE)


    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, ' A sample editor \n in wxPython', 'About Sample Editor', wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
        ''' Open a file'''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', '*.txt', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            path = os.path.join(self.dirname, self.filename)
            with open(path, 'r', encoding='utf-8') as f:
                self.text_ctrl.SetValue(f.read())
            self.SetStatusText('File: {} Loaded!'.format(path))
            self.SetTitle(self.GetTitle() + ' ({})'.format(self.filename))
        dlg.Destroy()

    def on_edit_toggle(self, evt):
        state = not self.text_ctrl.IsEditable()
        self.text_ctrl.SetEditable(state)

        if state:
            self.text_ctrl.SetBackgroundColour(wx.Colour(247, 225, 126))
        else:
            self.text_ctrl.SetBackgroundColour(wx.Colour('WHITE'))

    def on_editor_change(self, evt):
        # print('textctl event')
        pass

    def apply_tag(self, selected_tag, tag_style=None):

        # do nothing if no selection
        if self.text_ctrl.GetStringSelection() == '':
            self.text_ctrl.SetFocus()
            return

        if tag_style is None:
            tag_style = self.TAG_STYLE

        #
        sel_start, sel_end = self.text_ctrl.GetSelection()
        text = self.text_ctrl.GetStringSelection()
        s_tag = self.START_TAG_TMPL.format(selected_tag)
        e_tag = self.END_TAG_TMPL.format(selected_tag)
        sel_end_after = sel_end + len(s_tag) + len(e_tag)

        #
        if not self.tag_hist.add_hist((sel_start, sel_end_after), selected_tag):
            return

        #
        self.text_ctrl.Replace(sel_start, sel_end, '{}{}{}'.format(s_tag, text, e_tag))
        self.text_ctrl.SetStyle(sel_start, sel_end_after, tag_style)
        self.text_ctrl.SetInsertionPoint(sel_end_after)
        self.text_ctrl.SetFocus()


        return sel_start, sel_end_after, text

    def on_tag_apply(self, evt):

        # show modal to select tags
        tag_dlg = wx.SingleChoiceDialog(self, 'Select apply_tag you want to apply :'.title(), 'Select Tag', self.TAGS)
        tag_dlg.SetSize((150, 300))
        if tag_dlg.ShowModal() == wx.ID_OK:
            selected_tag = tag_dlg.GetStringSelection()
        else:
            return
        tag_dlg.Destroy()

        self.apply_tag(selected_tag)

    def on_tag_remove(self, evt):
        pos, tag = self.tag_hist.pop_hist()
        pos_b, pos_e = pos
        sel_end_after = pos_e - len(self.END_TAG_TMPL.format(tag))

        text = self.text_ctrl.GetRange(pos_b + len(self.START_TAG_TMPL.format(tag)), sel_end_after)
        self.text_ctrl.Replace(pos_b, pos_e, text)
        self.text_ctrl.SetStyle(pos_b, sel_end_after, self.text_ctrl.GetDefaultStyle())
        self.text_ctrl.SetInsertionPoint(pos_b)
        self.text_ctrl.SetFocus()

        print(self.tag_hist.history)


    def on_text_keyevt(self, evt):

        if self.text_ctrl.IsEditable():
            evt.Skip()
            return

        pressed_key = h.key_name(evt.GetUnicodeKey())
        if pressed_key in self.SHORTCUT_MAP:
            selected_tag = self.TAGS[self.SHORTCUT_MAP[pressed_key]]
            self.apply_tag(selected_tag)
            print(pressed_key, selected_tag)

        evt.Skip()

    def on_text_click(self, evt):
        cur_pos = self.text_ctrl.GetInsertionPoint()
        cur_sel = self.text_ctrl.GetSelection()
        self.SetStatusText('Pos: {}, Sel: ({}, {})'.format(cur_pos, *cur_sel), 1)
        evt.Skip()



if __name__ == '__main__':
    import wx.lib.inspection

    app = wx.App(False)
    frame = MainWindow(None, 'Annotator')
    frame.SetSize((1000, 500))
    frame.Centre()
    frame.Show()
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

