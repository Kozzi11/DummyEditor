# -*- coding: utf-8 -*-

__author__ = 'kozzi'

import wx
import wx.richtext

import os.path

DUMMY_EDITOR_FILE_TYPE = 6


class DummyEditorDataObjectComposite(wx.DataObjectComposite):
    def __init__(self):
        super(DummyEditorDataObjectComposite, self).__init__()
        self.file_data = wx.FileDataObject()
        self.text_data = wx.TextDataObject()
        self.Add(self.file_data, True)
        self.Add(self.text_data)

    # noinspection PyMethodOverriding
    def GetObject(self, receive_format, direction=wx.DataObject.Get):
        format_type = receive_format.GetType()
        if format_type == wx.DF_FILENAME:
            return self.file_data
        elif format_type == wx.DF_TEXT or format_type == wx.DF_UNICODETEXT:
            return self.text_data
        return None


class DummyEditorMultiDropTarget(wx.DropTarget):
    def __init__(self, owner):
        super(DummyEditorMultiDropTarget, self).__init__()

        self.data_object = DummyEditorDataObjectComposite()
        self.SetDataObject(self.data_object)
        self.owner = owner

    def OnData(self, x, y, drag_result):
        self.GetData()
        receive_format = self.data_object.GetReceivedFormat()
        format_type = receive_format.GetType()
        data = self.data_object.GetObject(receive_format)
        if format_type == wx.DF_FILENAME:
            files = data.GetFilenames()
            for f in files:
                if os.path.splitext(f)[1] == ".txt":
                    child = DummyEditorChildFrame(self.owner.GetParent(), f, (400, 300))
                    child.Show()
        elif format_type == wx.DF_TEXT or format_type == wx.DF_UNICODETEXT:
            self.owner.m_text_editor.WriteText(data.GetText())
        else:
            print format_type

        return drag_result


class DummyEditorFileDropTarget(wx.FileDropTarget):
    def __init__(self, owner):
        super(DummyEditorFileDropTarget, self).__init__()
        self.owner = owner

    # noinspection PyMethodOverriding
    def OnDropFiles(self, x_coord, y_coord, files):
        for f in files:
            if os.path.splitext(f)[1] == ".txt":
                child = DummyEditorChildFrame(self.owner, f, (400, 300))
                child.Show()


class DummyEditorFileFormatHandler(wx.richtext.RichTextHTMLHandler):
    def __init__(self):
        super(DummyEditorFileFormatHandler, self).__init__("HTML", "html", wx.richtext.RICHTEXT_TYPE_HTML)

    def LoadFile(*args, **kwargs):
        print "kkkk"

    def CanHandle(*args, **kwargs):
        print "kkkk"

    def CanLoad(*args, **kwargs):
        print "kkkk"

    def GetExtension(*args, **kwargs):
        print "kkkk"


class DummyEditorChildFrame(wx.MDIChildFrame):
    def __init__(self, parent, file_path, winsize):
        file_name = u"Bez názvu"
        if file_path:
            file_name = os.path.basename(file_path)
        super(DummyEditorChildFrame, self).__init__(parent, title=file_name, size=winsize)
        self.parent = parent

        self.find_replace_data = wx.FindReplaceData()
        self.font_data = wx.FontData()
        self.font_color_data = wx.ColourData()

        self.Bind(wx.EVT_SET_FOCUS, self.on_activate, self, self.GetId())
        self.Bind(wx.EVT_ACTIVATE, self.on_activate, self, self.GetId())
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.m_text_editor = wx.richtext.RichTextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                                      wx.DefaultSize,  wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER |
                                                      wx.WANTS_CHARS|wx.richtext.RE_MULTILINE)

        self.m_text_editor.SetDropTarget(DummyEditorMultiDropTarget(self))
        if file_path:
            self.m_text_editor.LoadFile(file_path, wx.richtext.RICHTEXT_TYPE_ANY)
        main_sizer.Add(self.m_text_editor, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(main_sizer)

    def on_activate(self, event):
        self.m_text_editor.SetFocus()

    # noinspection PyMethodOverriding
    def GetParent(self):
        return self.parent


class DummyEditorFrame(wx.MDIParentFrame):
    def __init__(self, title):
        super(DummyEditorFrame, self).__init__(None, title=title, pos=(150, 150), size=(800, 600))
        self.open_windows = None
        self.menu_bar = wx.MenuBar()
        self.create_menu()
        self.SetMenuBar(self.menu_bar)
        self.bind_events()
        self.color_dialog = None
        self.SetDropTarget(DummyEditorFileDropTarget(self))

    def create_menu(self):
        self.create_file_menu()
        self.create_edit_menu()
        self.create_find_menu()

    def create_file_menu(self):
        menu = wx.Menu()
        menu.Append(wx.ID_NEW, u"Nový soubor")
        menu.AppendSeparator()
        menu.Append(wx.ID_OPEN, u"Otevřít soubor")
        menu.AppendSeparator()
        menu.Append(wx.ID_SAVE, u"Uložit")
        menu.Append(wx.ID_SAVEAS, u"Uložit jako")
        menu.Append(wx.ID_REFRESH, u"Znovu načíst soubor\tCTRL+R")
        menu.AppendSeparator()
        menu.Append(wx.ID_CLOSE, u"Zavřít")
        menu.Append(wx.ID_CLOSE_ALL, u"Zavřít všechny")
        menu_item_close_others = menu.Append(wx.ID_ANY, u"Zavřít ostatní")
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, u"Ukončit")

        self.Bind(wx.EVT_MENU, self.on_new_menu, None, wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_quit_menu, None, wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_open_menu, None, wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_reload_menu, None, wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.on_save_menu, None, wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_save_as_menu, None, wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_close_menu, None, wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.on_close_all_menu, None, wx.ID_CLOSE_ALL)
        self.Bind(wx.EVT_MENU, self.on_close_others_menu, None, menu_item_close_others.GetId())
        self.Bind(wx.EVT_CLOSE, self.on_quit_menu, None, wx.ID_ANY)

        self.menu_bar.Append(menu, u"&Soubor")

    def create_edit_menu(self):
        menu = wx.Menu()
        menu.Append(wx.ID_SELECT_FONT, u"Styl písma")
        menu.Append(wx.ID_SELECT_COLOR, u"Barva písma")

        self.Bind(wx.EVT_MENU, self.on_font_format_menu, None, wx.ID_SELECT_FONT)
        self.Bind(wx.EVT_MENU, self.on_font_color_menu, None, wx.ID_SELECT_COLOR)

        self.menu_bar.Append(menu, u"Úp&ravy")

    def create_find_menu(self):
        menu = wx.Menu()
        menu.Append(wx.ID_FIND, u"Najít...\tCTRL+F")
        menu.Append(wx.ID_REPLACE, u"Nahradit\tCTRL+H")

        self.Bind(wx.EVT_MENU, self.on_find_menu, None, wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_find_replace_menu, None, wx.ID_REPLACE)
        self.menu_bar.Append(menu, u"&Hledat")

    def on_quit_menu(self, event):
        self.on_close_all_menu(event)
        self.Destroy()

    def on_close_menu(self, event):
        self.close_child(self.get_active_child())

    def on_close_all_menu(self, event):
        for item in self.GetClientWindow().GetChildren():
            self.close_child(item)

    def on_close_others_menu(self, event):
        active_child = self.get_active_child()
        for item in self.GetClientWindow().GetChildren():
            if item is not active_child:
                self.close_child(item)

    def close_child(self, close_child=None):
        if close_child is None:
            return
        close_child.Activate()
        self.SetFocus()
        ret = None
        file_path = close_child.m_text_editor.GetFilename()
        if close_child.m_text_editor.IsModified():
            file_name = u"Bez názvu"
            if file_path is not None and file_path != "":
                file_name = file_path

            msg = wx.MessageDialog(self, u"Soubor " + unicode(file_name) + u" byl změněn, chcete změny uložit",
                                   style=wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            ret = msg.ShowModal()

        if ret != wx.ID_CANCEL:
            if ret == wx.ID_YES:
                if file_path is not None and file_path != "":
                    close_child.m_text_editor.SaveFile(file_path)
                else:
                    self.on_save_as_menu(None)
            close_child.DestroyChildren()
            close_child.Destroy()
            active_child = self.GetActiveChild()
            if active_child is not None:
                active_child.SetFocus()

    def on_new_menu(self, event):
        child = DummyEditorChildFrame(self, None, (400, 300))
        child.Show()

    def on_open_menu(self, event):
        file_path = wx.LoadFileSelector(u"Zvolte soubor", u"TXT formát (*.txt)|*.txt|Dummy formát text (*.html)|*.html")
        if file_path:
            child = DummyEditorChildFrame(self, file_path, (400, 300))
            child.Show()

    def get_active_child(self):
        """:rtype : DummyEditorChildFrame"""
        return super(DummyEditorFrame, self).GetActiveChild()

    def on_save_as_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            file_path = wx.SaveFileSelector(u"Uložit jako", u"TXT formát (*.txt)|*.txt|Dummy formát text (*.html)|*.html")
            if file_path:
                active_child.m_text_editor.SaveFile(file_path)
                active_child.m_text_editor.SetFilename(file_path)
                active_child.SetTitle(os.path.basename(file_path))

    def on_save_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            file_path = active_child.m_text_editor.GetFilename()
            if file_path:
                active_child.m_text_editor.SaveFile(file_path)
            else:
                self.on_save_as_menu(event)

    def on_reload_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            file_path = active_child.m_text_editor.GetFilename()
            if file_path:
                active_child.m_text_editor.LoadFile(file_path)

    def on_font_format_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            dlg = wx.FontDialog(self, active_child.font_data)
            if dlg.ShowModal() == wx.ID_OK:
                font = dlg.GetFontData().GetChosenFont()
                active_child.font_data.SetInitialFont(font)
                active_child.m_text_editor.BeginFont(font)

    def on_font_color_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            dlg = wx.ColourDialog(self, active_child.font_color_data)
            if dlg.ShowModal() == wx.ID_OK:
                color = dlg.GetColourData().GetColour()
                active_child.font_color_data.SetColour(color)
                active_child.m_text_editor.BeginTextColour(color)

    def on_find_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            dlg = wx.FindReplaceDialog(self, active_child.find_replace_data, u"Najít")
            dlg.Show()

    def on_find_replace_menu(self, event):
        active_child = self.get_active_child()
        if active_child is not None:
            dlg = wx.FindReplaceDialog(self, active_child.find_replace_data, u"Nahradit", wx.FR_REPLACEDIALOG)
            dlg.Show()

    def on_find(self, event):
        print "find"

    def on_find_next(self, event):
        print "find next"

    def on_find_replace(self, event):
        print "find replace"

    def on_find_replace_all(self, event):
        print "find replace all"

    def bind_events(self):
        self.Bind(wx.EVT_FIND, self.on_find, None, wx.ID_ANY)
        self.Bind(wx.EVT_FIND_NEXT, self.on_find_next, None, wx.ID_ANY)
        self.Bind(wx.EVT_FIND_REPLACE, self.on_find_replace, None, wx.ID_ANY)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.on_find_replace_all, None, wx.ID_ANY)


class DummyEditor(wx.App):
    def OnInit(self):
        wx.richtext.RichTextBuffer.AddHandler(DummyEditorFileFormatHandler())
        frame = DummyEditorFrame("Dummy Editor")
        frame.Show()
        return True


if __name__ == "__main__":
    app = DummyEditor()
    app.MainLoop()