import os
import re

import wx

from . import dialog_base


def pop_error(msg):
    wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)


class SettingsDialog(dialog_base.SettingsDialogBase):
    def __init__(self, extra_data_func, extra_data_wildcard, config_save_func,
                 file_name_format_hint, version):
        dialog_base.SettingsDialogBase.__init__(self, None)
        self.panel = SettingsDialogPanel(
            self, extra_data_func, extra_data_wildcard, config_save_func,
            file_name_format_hint)
        best_size = self.panel.BestSize
        # hack for some gtk themes that incorrectly calculate best size
        best_size.IncBy(dx=0, dy=30)
        self.SetClientSize(best_size)
        self.SetTitle('InteractiveHtmlBom %s' % version)

    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        try:
            # wxPython 4
            super(SettingsDialog, self).SetSizeHints(sz1, sz2)
        except TypeError:
            # wxPython 3
            self.SetSizeHintsSz(sz1, sz2)

    def set_extra_data_path(self, extra_data_file):
        self.panel.extra.extraDataFilePicker.Path = extra_data_file
        self.panel.extra.OnNetlistFileChanged(None)


# Implementing settings_dialog
class SettingsDialogPanel(dialog_base.SettingsDialogPanel):
    def __init__(self, parent, extra_data_func, extra_data_wildcard,
                 config_save_func, file_name_format_hint):
        self.config_save_func = config_save_func
        dialog_base.SettingsDialogPanel.__init__(self, parent)
        self.general = GeneralSettingsPanel(self.notebook,
                                            file_name_format_hint)
        self.html = HtmlSettingsPanel(self.notebook)
        self.extra = ExtraFieldsPanel(self.notebook, extra_data_func,
                                      extra_data_wildcard)
        self.notebook.AddPage(self.general, "常规")
        self.notebook.AddPage(self.html, "HTML 默认值")
        self.notebook.AddPage(self.extra, "额外字段")

    def OnExit(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnSaveSettings(self, event):
        self.config_save_func(self)

    def OnGenerateBom(self, event):
        self.GetParent().EndModal(wx.ID_OK)

    def finish_init(self):
        self.html.OnBoardRotationSlider(None)


# Implementing HtmlSettingsPanelBase
class HtmlSettingsPanel(dialog_base.HtmlSettingsPanelBase):
    def __init__(self, parent):
        dialog_base.HtmlSettingsPanelBase.__init__(self, parent)

    # Handlers for HtmlSettingsPanelBase events.
    def OnBoardRotationSlider(self, event):
        degrees = self.boardRotationSlider.Value * 5
        self.rotationDegreeLabel.LabelText = u"{}\u00B0".format(degrees)


# Implementing GeneralSettingsPanelBase
class GeneralSettingsPanel(dialog_base.GeneralSettingsPanelBase):

    def __init__(self, parent, file_name_format_hint):
        dialog_base.GeneralSettingsPanelBase.__init__(self, parent)
        self.file_name_format_hint = file_name_format_hint
        bitmaps = os.path.join(os.path.dirname(__file__), "bitmaps")
        self.m_btnSortUp.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-arrow-up.png"), wx.BITMAP_TYPE_PNG))
        self.m_btnSortDown.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-arrow-down.png"), wx.BITMAP_TYPE_PNG))
        self.m_btnSortAdd.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-plus.png"), wx.BITMAP_TYPE_PNG))
        self.m_btnSortRemove.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-minus.png"), wx.BITMAP_TYPE_PNG))
        self.m_bpButton5.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-question.png"), wx.BITMAP_TYPE_PNG))
        self.m_btnBlacklistAdd.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-plus.png"), wx.BITMAP_TYPE_PNG))
        self.m_btnBlacklistRemove.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-minus.png"), wx.BITMAP_TYPE_PNG))

    # Handlers for GeneralSettingsPanelBase events.
    def OnComponentSortOrderUp(self, event):
        selection = self.componentSortOrderBox.Selection
        if selection != wx.NOT_FOUND and selection > 0:
            item = self.componentSortOrderBox.GetString(selection)
            self.componentSortOrderBox.Delete(selection)
            self.componentSortOrderBox.Insert(item, selection - 1)
            self.componentSortOrderBox.SetSelection(selection - 1)

    def OnComponentSortOrderDown(self, event):
        selection = self.componentSortOrderBox.Selection
        size = self.componentSortOrderBox.Count
        if selection != wx.NOT_FOUND and selection < size - 1:
            item = self.componentSortOrderBox.GetString(selection)
            self.componentSortOrderBox.Delete(selection)
            self.componentSortOrderBox.Insert(item, selection + 1)
            self.componentSortOrderBox.SetSelection(selection + 1)

    def OnComponentSortOrderAdd(self, event):
        item = wx.GetTextFromUser(
            "A-Z 以外的字符将被忽略。",
            "添加排序项")
        item = re.sub('[^A-Z]', '', item.upper())
        if item == '':
            return
        found = self.componentSortOrderBox.FindString(item)
        if found != wx.NOT_FOUND:
            self.componentSortOrderBox.SetSelection(found)
            return
        self.componentSortOrderBox.Append(item)
        self.componentSortOrderBox.SetSelection(
            self.componentSortOrderBox.Count - 1)

    def OnComponentSortOrderRemove(self, event):
        selection = self.componentSortOrderBox.Selection
        if selection != wx.NOT_FOUND:
            item = self.componentSortOrderBox.GetString(selection)
            if item == '~':
                pop_error("你不能删除 '~' 项")
                return
            self.componentSortOrderBox.Delete(selection)
            if self.componentSortOrderBox.Count > 0:
                self.componentSortOrderBox.SetSelection(max(selection - 1, 0))

    def OnComponentBlacklistAdd(self, event):
        item = wx.GetTextFromUser(
            "A-Z 0-9 和 * 以外的字符将被忽略。",
            "添加黑名单项")
        item = re.sub('[^A-Z0-9*]', '', item.upper())
        if item == '':
            return
        found = self.blacklistBox.FindString(item)
        if found != wx.NOT_FOUND:
            self.blacklistBox.SetSelection(found)
            return
        self.blacklistBox.Append(item)
        self.blacklistBox.SetSelection(self.blacklistBox.Count - 1)

    def OnComponentBlacklistRemove(self, event):
        selection = self.blacklistBox.Selection
        if selection != wx.NOT_FOUND:
            self.blacklistBox.Delete(selection)
            if self.blacklistBox.Count > 0:
                self.blacklistBox.SetSelection(max(selection - 1, 0))

    def OnNameFormatHintClick(self, event):
        wx.MessageBox(self.file_name_format_hint, '文件名称格式帮助',
                      style=wx.ICON_NONE | wx.OK)

    def OnSize(self, event):
        # Trick the listCheckBox best size calculations
        tmp = self.componentSortOrderBox.GetStrings()
        self.componentSortOrderBox.SetItems([])
        self.Layout()
        self.componentSortOrderBox.SetItems(tmp)


# Implementing ExtraFieldsPanelBase
class ExtraFieldsPanel(dialog_base.ExtraFieldsPanelBase):
    NONE_STRING = '<none>'

    def __init__(self, parent, extra_data_func, extra_data_wildcard):
        dialog_base.ExtraFieldsPanelBase.__init__(self, parent)
        self.extra_data_func = extra_data_func
        self.extra_field_data = None
        bitmaps = os.path.join(os.path.dirname(__file__), "bitmaps")
        self.m_btnUp.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-arrow-up.png"), wx.BITMAP_TYPE_PNG))
        self.m_btnDown.SetBitmap(wx.Bitmap(
            os.path.join(bitmaps, "btn-arrow-down.png"), wx.BITMAP_TYPE_PNG))
        self.set_file_picker_wildcard(extra_data_wildcard)

    def set_file_picker_wildcard(self, extra_data_wildcard):
        if extra_data_wildcard is None:
            self.extraDataFilePicker.Disable()
            return

        # wxFilePickerCtrl doesn't support changing wildcard at runtime
        # so we have to replace it
        picker_parent = self.extraDataFilePicker.GetParent()
        new_picker = wx.FilePickerCtrl(
            picker_parent, wx.ID_ANY, wx.EmptyString,
            u"选择一个文件",
            extra_data_wildcard,
            wx.DefaultPosition, wx.DefaultSize,
            (wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST | wx.FLP_OPEN |
             wx.FLP_SMALL | wx.FLP_USE_TEXTCTRL | wx.BORDER_SIMPLE))
        self.GetSizer().Replace(self.extraDataFilePicker, new_picker,
                                recursive=True)
        self.extraDataFilePicker.Destroy()
        self.extraDataFilePicker = new_picker
        self.Layout()

    # Handlers for ExtraFieldsPanelBase events.
    def OnExtraFieldsUp(self, event):
        selection = self.extraFieldsList.Selection
        if selection != wx.NOT_FOUND and selection > 0:
            item = self.extraFieldsList.GetString(selection)
            checked = self.extraFieldsList.IsChecked(selection)
            self.extraFieldsList.Delete(selection)
            self.extraFieldsList.Insert(item, selection - 1)
            if checked:
                self.extraFieldsList.Check(selection - 1)
            self.extraFieldsList.SetSelection(selection - 1)

    def OnExtraFieldsDown(self, event):
        selection = self.extraFieldsList.Selection
        size = self.extraFieldsList.Count
        if selection != wx.NOT_FOUND and selection < size - 1:
            item = self.extraFieldsList.GetString(selection)
            checked = self.extraFieldsList.IsChecked(selection)
            self.extraFieldsList.Delete(selection)
            self.extraFieldsList.Insert(item, selection + 1)
            if checked:
                self.extraFieldsList.Check(selection + 1)
            self.extraFieldsList.SetSelection(selection + 1)

    def OnNetlistFileChanged(self, event):
        extra_data_file = self.extraDataFilePicker.Path
        if not os.path.isfile(extra_data_file):
            return
        self.extra_field_data = None
        try:
            self.extra_field_data = self.extra_data_func(
                extra_data_file, self.normalizeCaseCheckbox.Value)
        except Exception as e:
            pop_error(
                "未能解析文件 %s\n\n%s" % (extra_data_file, e))
            self.extraDataFilePicker.Path = ''
        if self.extra_field_data is not None:
            field_list = list(self.extra_field_data[0])
            self.extraFieldsList.SetItems(field_list)
            field_list.append(self.NONE_STRING)
            self.boardVariantFieldBox.SetItems(field_list)
            self.boardVariantFieldBox.SetStringSelection(self.NONE_STRING)
            self.boardVariantWhitelist.Clear()
            self.boardVariantBlacklist.Clear()
            self.dnpFieldBox.SetItems(field_list)
            self.dnpFieldBox.SetStringSelection(self.NONE_STRING)

    def OnBoardVariantFieldChange(self, event):
        selection = self.boardVariantFieldBox.Value
        if not selection or selection == self.NONE_STRING \
                or self.extra_field_data is None:
            self.boardVariantWhitelist.Clear()
            self.boardVariantBlacklist.Clear()
            return
        variant_set = set()
        for _, field_dict in self.extra_field_data[1].items():
            if selection in field_dict:
                variant_set.add(field_dict[selection])
        self.boardVariantWhitelist.SetItems(list(variant_set))
        self.boardVariantBlacklist.SetItems(list(variant_set))

    def OnSize(self, event):
        # Trick the listCheckBox best size calculations
        items = self.extraFieldsList.GetStrings()
        checked_items = self.extraFieldsList.GetCheckedStrings()
        self.extraFieldsList.SetItems([])
        self.Layout()
        self.extraFieldsList.SetItems(items)
        self.extraFieldsList.SetCheckedStrings(checked_items)
