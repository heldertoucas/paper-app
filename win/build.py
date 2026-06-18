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
Tabs.Push(MyGui.Add("Text", "x+10 y12 w30 h25 BackgroundTrans +0x0200", "?"))

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

; Help View (Hidden by default)
MyGui.SetFont("s10 c" TEXT_COLOR, "Segoe UI")
HelpView := MyGui.Add("Text", "x16 y45 w548 h310 Hidden", "")
HelpView.Value := "PAPERCLIP SHORTCUTS`n`n"
    . "GENERAL:`n"
    . "Ctrl+Enter  - Save & Close`n"
    . "Esc         - Hide Window`n"
    . "Ctrl+Esc    - Clear & Hide`n`n"
    . "CAPTURE:`n"
    . "Ctrl+[1-5]  - Switch Domains`n"
    . "Ctrl+Shift+V- Clean Paste (Email fix)`n"
    . "Ctrl+Alt+V  - Paste as Markdown`n"
    . "Ctrl+J      - Templates Menu`n`n"
    . "FORMATTING:`n"
    . "Ctrl+T      - Insert Timestamp`n"
    . "Ctrl+L      - Checklist Item`n"
    . "Ctrl+K      - Wrap in [[Wiki-link]]`n"

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
    
    if (index == 6) { ; Help Tab
        Editor.Visible := false
        HelpView.Visible := true
        StatusBar.Value := "Help Mode"
    } else {
        HelpView.Visible := false
        Editor.Visible := true
        StatusBar.Value := "Domain: " Domains[index] " | Context: " LastProcess
        Editor.Focus()
        
        ; If buffer has YAML, update domain line dynamically
        text := Editor.Value
        if (RegExMatch(text, "m)^domain:.*$")) {
            text := RegExReplace(text, "m)^domain:.*$", "domain: " Domains[index])
            Editor.Value := text
        }
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

; --- New Shortcuts ---
F1::SetTab(6)
^t::InsertText(FormatTime(, "HH:mm") ": ")
^l::InsertText("- [ ] ")
^k::WrapSelection("[[", "]]")
^+v::CleanPaste() ; Ctrl+Shift+V for Clean Paste (removes weird email formatting)
^!v::PasteAsMarkdown() ; Ctrl+Alt+V for Smart Markdown Paste
^j::ShowTemplates() ; Ctrl+J for Templates/Snippets
#HotIf

InsertText(str) {
    SendMessage(0x00C2, 0, StrPtr(str), Editor.Hwnd)
}

WrapSelection(prefix, suffix) {
    ; Get current selection using clipboard
    oldClip := A_Clipboard
    A_Clipboard := ""
    Send("^c")
    if ClipWait(0.2) {
        sel := A_Clipboard
        A_Clipboard := prefix sel suffix
        Send("^v")
    } else {
        InsertText(prefix suffix)
    }
    A_Clipboard := oldClip
}

CleanPaste() {
    text := A_Clipboard
    ; Strip HTML-like artifacts often found in emails or complex docs
    text := RegExReplace(text, "\\r\\n", "`n") ; Normalize line endings
    text := RegExReplace(text, "(\\n){3,}", "`n`n") ; Collapse excessive whitespace
    InsertText(Trim(text))
    StatusBar.Value := "Clean paste applied."
}

PasteAsMarkdown() {
    html := GetClipboardHTML()
    if (html == "") {
        InsertText(A_Clipboard)
        return
    }
    
    ; Basic conversion of HTML fragment to Markdown
    md := html
    ; 1. Links: <a href="...">text</a> -> [text](url)
    md := RegExReplace(md, "is)<a [^>]*href=[\\\\x22\\\\x27]([^\\\\x22\\\\x27]+)[\\\\x22\\\\x27][^>]*>(.*?)</a>", "[$2]($1)")
    ; 2. Bold: <b>, <strong> -> **
    md := RegExReplace(md, "is)<(strong|b)>(.*?)</\\1>", "**$2**")
    ; 3. Italics: <i>, <em> -> *
    md := RegExReplace(md, "is)<(em|i)>(.*?)</\\1>", "*$2*")
    ; 4. Lists: <li> -> - 
    md := RegExReplace(md, "is)<li[^>]*>(.*?)</li>", "- $1`n")
    ; 5. Headers: <h1-6> -> #
    md := RegExReplace(md, "is)<h1[^>]*>(.*?)</h1>", "# $1`n")
    md := RegExReplace(md, "is)<h2[^>]*>(.*?)</h2>", "## $1`n")
    md := RegExReplace(md, "is)<h3[^>]*>(.*?)</h3>", "### $1`n")
    ; 6. Line breaks and Paragraphs
    md := RegExReplace(md, "is)<br\\s*/?>", "`n")
    md := RegExReplace(md, "is)<p[^>]*>(.*?)</p>", "$1`n`n")
    
    ; Strip remaining HTML tags
    md := RegExReplace(md, "<[^>]+>", "")
    
    ; Decode common entities
    md := StrReplace(md, "&nbsp;", " ")
    md := StrReplace(md, "&amp;", "&")
    md := StrReplace(md, "&lt;", "<")
    md := StrReplace(md, "&gt;", ">")
    md := StrReplace(md, "&quot;", '\"')
    
    InsertText(Trim(md))
    StatusBar.Value := "Pasted as Markdown."
}

GetClipboardHTML() {
    cfFormat := DllCall("RegisterClipboardFormat", "Str", "HTML Format", "UInt")
    if !DllCall("IsClipboardFormatAvailable", "UInt", cfFormat)
        return ""
    if !DllCall("OpenClipboard", "Ptr", 0)
        return ""
    if !hData := DllCall("GetClipboardData", "UInt", cfFormat, "Ptr") {
        DllCall("CloseClipboard")
        return ""
    }
    pData := DllCall("GlobalLock", "Ptr", hData, "Ptr")
    html := StrGet(pData, "UTF-8")
    DllCall("GlobalUnlock", "Ptr", hData)
    DllCall("CloseClipboard")
    
    if RegExMatch(html, "s)<!--StartFragment-->(.*)<!--EndFragment-->", &match)
        return match[1]
    return ""
}

ShowTemplates() {
    TemplateMenu := Menu()
    TemplateMenu.Add("Email: Follow-up", (*) => InsertText("Dear [Name],`n`nFollowing up on our conversation regarding..."))
    TemplateMenu.Add("Email: Meeting Minutes", (*) => InsertText("## Meeting Minutes`nDate: " FormatTime(,"yyyy-MM-dd") "`nParticipants: `n`n### Actions:`n- [ ] "))
    TemplateMenu.Add("Code: Task Ref", (*) => InsertText("`n> [!TASK] Ref: " LastProcess "`n> " LastContext "`n"))
    TemplateMenu.Show()
}

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
    if (!RegExMatch(text, "---[\\s\\S]+?---[\\s\\S]*[^\\s]")) {
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
with codecs.open("paperclip.ahk", "w", "utf-8") as f:
    f.write(content)
