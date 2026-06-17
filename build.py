import codecs

content = r"""#Requires AutoHotkey v2.0
#SingleInstance Force

; ==============================================================================
; PROJECT PAPERCLIP: Windows Desktop Edition
; ==============================================================================

GLOBAL_HOTKEY := "^+Space"
DESTINATION_DIR := A_ScriptDir "\obsidian-ht\00-inbox\pc\"
WINDOW_WIDTH := 580
WINDOW_HEIGHT := 400
BG_COLOR := "FDFBF7"
EDITOR_BG := "FDFBF7"
TEXT_COLOR := "2C2825"
ACCENT_COLOR := "D97706"
MUTED_COLOR := "8C867D"

Domains := ["system", "pessoal", "cmlisboa", "cmlisboa", "freelance"]
CurrentDomainIndex := 1
LastContext := ""
LastProcess := ""
LastSavedHash := ""

if !DirExist(DESTINATION_DIR)
    DirCreate(DESTINATION_DIR)

MyGui := Gui("+AlwaysOnTop -Caption +Border", "Paperclip")
MyGui.BackColor := BG_COLOR
MyGui.SetFont("s10 c" MUTED_COLOR, "Segoe UI")

; Custom Tabs (Text controls for better styling)
Tabs := []
Tabs.Push(MyGui.Add("Text", "x16 y12 w80 h25 BackgroundTrans +0x0200", "1: INBOX"))
Tabs.Push(MyGui.Add("Text", "x+10 y12 w80 h25 BackgroundTrans +0x0200", "2: FAMÍLIA"))
Tabs.Push(MyGui.Add("Text", "x+10 y12 w100 h25 BackgroundTrans +0x0200", "3: PASSAPORTE"))
Tabs.Push(MyGui.Add("Text", "x+10 y12 w80 h25 BackgroundTrans +0x0200", "4: FUTURO"))
Tabs.Push(MyGui.Add("Text", "x+10 y12 w90 h25 BackgroundTrans +0x0200", "5: FREELANCE"))

for index, tabBtn in Tabs {
    tabBtn.OnEvent("Click", SetTab.Bind(index))
}

; Close Button
CloseBtn := MyGui.Add("Text", "x540 y12 w24 h24 Center BackgroundTrans +0x0200 c" TEXT_COLOR, "✕")
CloseBtn.SetFont("s14 bold")
CloseBtn.OnEvent("Click", (*) => MyGui.Hide())

; Editor
MyGui.SetFont("s11 c" TEXT_COLOR, "Consolas")
Editor := MyGui.Add("Edit", "x16 y45 w548 h310 -VScroll Multi Background" EDITOR_BG " c" TEXT_COLOR, "")
; Add internal margins to Editor (EM_SETMARGINS)
SendMessage(0xD3, 3, (12 & 0xFFFF) | (12 << 16), Editor.Hwnd)

; Status Bar
MyGui.SetFont("s9 c" MUTED_COLOR, "Segoe UI")
StatusBar := MyGui.Add("Text", "x16 y365 w548 h25 +0x0200", "Ready")

MyGui.OnEvent("DropFiles", Gui_DropFiles)
SetTab(1)

OnMessage(0x0201, WM_LBUTTONDOWN)
WM_LBUTTONDOWN(wParam, lParam, msg, hwnd) {
    if (hwnd == MyGui.Hwnd)
        PostMessage(0xA1, 2,,, "ahk_id " MyGui.Hwnd)
}

Hotkey GLOBAL_HOTKEY, ToggleWindow

ToggleWindow(*) {
    if WinActive("ahk_id " MyGui.Hwnd) {
        MyGui.Hide()
    } else {
        CaptureContext()
        MyGui.Show("w" WINDOW_WIDTH " h" WINDOW_HEIGHT " Center")
        if (Trim(Editor.Value) == "")
            PopulateYAML()
        Editor.Focus()
        ; Set Caret to end
        SendMessage(0xB1, -1, -1, Editor.Hwnd)
    }
}

SetTab(index, *) {
    global CurrentDomainIndex := index
    for i, tabBtn in Tabs {
        if (i == index) {
            tabBtn.SetFont("bold c" ACCENT_COLOR)
        } else {
            tabBtn.SetFont("norm c" MUTED_COLOR)
        }
    }
    StatusBar.Value := "Domain: " Domains[index] " | Context: " LastProcess
    
    ; If buffer has YAML, update domain line dynamically
    text := Editor.Value
    if (RegExMatch(text, "m)^domain:.*$")) {
        text := RegExReplace(text, "m)^domain:.*$", "domain: " Domains[index])
        Editor.Value := text
    }
}

CaptureContext() {
    global LastContext, LastProcess
    prevHwnd := WinGetID("A")
    if (prevHwnd == MyGui.Hwnd)
        return

    LastProcess := WinGetProcessName("ahk_id " prevHwnd)
    
    if (LastProcess ~= "i)chrome|msedge|brave") {
        url := GetBrowserURL(prevHwnd)
        if (url) {
            LastContext := url
            return
        }
    }
    LastContext := WinGetTitle("ahk_id " prevHwnd)
}

PopulateYAML() {
    yaml := "---`n"
    yaml .= "title: `n"
    yaml .= "type: source`n"
    yaml .= "domain: " Domains[CurrentDomainIndex] "`n"
    yaml .= "context: " LastProcess "`n"
    if (LastContext ~= "^http")
        yaml .= "source: " LastContext "`n"
    yaml .= "status: draft`n"
    yaml .= "created: " FormatTime(, "yyyy-MM-dd") "`n"
    yaml .= "---`n`n"
    
    Editor.Value := yaml
}

#HotIf WinActive("ahk_id " MyGui.Hwnd)
^Enter::SaveNote()
Esc::MyGui.Hide()
^Esc:: {
    Editor.Value := ""
    StatusBar.Value := "Buffer cleared."
    MyGui.Hide()
}
^1:: SetTab(1)
^2:: SetTab(2)
^3:: SetTab(3)
^4:: SetTab(4)
^5:: SetTab(5)
#HotIf

Gui_DropFiles(GuiObj, GuiCtrlObj, FileArray, *) {
    for i, file in FileArray {
        Editor.Value .= "`n[File](" file ")"
    }
    StatusBar.Value := "Files appended."
    SendMessage(0xB1, -1, -1, Editor.Hwnd)
}

SaveNote() {
    global LastSavedHash
    text := Editor.Value
    
    if (text == LastSavedHash) {
        StatusBar.Value := "Duplicate blocked."
        MyGui.Hide()
        return
    }

    ; Require some content outside the YAML
    if (!RegExMatch(text, "---[\s\S]+?---[\s\S]*[^\s]")) {
        StatusBar.Value := "Error: Empty note."
        return
    }
    
    ts := FormatTime(, "yyyyMMdd-HHmmss")
    filename := ts "-pc.md"
    filepath := DESTINATION_DIR filename
    
    try {
        FileAppend(text, filepath, "UTF-8")
        LastSavedHash := text
        Editor.Value := ""
        MyGui.Hide()
        TrayTip "Paperclip", "Note saved: " filename
    } catch Error as e {
        StatusBar.Value := "Error saving: " e.Message
    }
}

GetBrowserURL(hWnd) {
    try {
        UIA := ComObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", "{30cbe57d-d9d0-452a-ab13-7ac5ac4825ee}")
        ComCall(6, UIA, "ptr", hWnd, "ptr*", &elementMain := 0)
        names := ["Address and search bar", "Barra de endereço e pesquisa", "Address bar"]
        for name in names {
            pStr := DllCall("oleaut32\SysAllocString", "str", name, "ptr")
            varName := Buffer(8 + 2 * A_PtrSize, 0)
            NumPut("ushort", 8, varName, 0)
            NumPut("ptr", pStr, varName, 8)
            ComCall(23, UIA, "int", 30005, "ptr", varName, "ptr*", &condition := 0)
            ComCall(5, elementMain, "int", 0x4, "ptr", condition, "ptr*", &elementAddr := 0)
            if (elementAddr) {
                varValue := Buffer(24, 0)
                ComCall(10, elementAddr, "int", 30045, "ptr", varValue)
                url := StrGet(NumGet(varValue, 8, "ptr"), "UTF-16")
                return url
            }
        }
    }
    return ""
}
"""
with codecs.open("monolith.ahk", "w", "utf-8") as f:
    f.write(content)
