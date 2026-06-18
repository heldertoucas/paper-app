#Requires AutoHotkey v2.0
#SingleInstance Force

; Validation Script for Project Paperclip AHK Features

TrayTip "Paperclip Validation", "Press Ctrl+Shift+F1 to test context extraction."

^+f1:: {
    ; Test 1: Previous Window Detection
    ; We hide ourselves (if visible) to see what was behind
    prevTitle := WinGetTitle("A")
    prevProcess := WinGetProcessName("A")
    
    ; Test 2: Basic UIA Attempt (Simplified for validation)
    ; In a real app, we'd use a dedicated UIA library, 
    ; but let's see if we can get the text of the address bar via basic WinGet commands first.
    MsgBox "Context Extracted:`nTitle: " prevTitle "`nProcess: " prevProcess "`n`nDrop some files on the next window to test Drag-and-Drop."
    
    ShowTestGui()
}

ShowTestGui() {
    myGui := Gui("+AlwaysOnTop -Caption +Border", "Paperclip Test")
    myGui.BackColor := "101010"
    myGui.SetFont("s12 cE0E0E0", "Consolas")
    
    myGui.Add("Text", "Center w300", "DRAG FILES HERE")
    editBox := myGui.Add("Edit", "r5 w280 Background161616 cE0E0E0")
    
    myGui.OnEvent("DropFiles", Gui_DropFiles)
    myGui.Show("w300 h200")
    
    Gui_DropFiles(GuiObj, GuiCtrlObj, FileArray, *) {
        for i, file in FileArray {
            editBox.Value .= file "`n"
        }
        MsgBox "Files Dropped: " FileArray.Length
    }
}

Esc:: ExitApp
