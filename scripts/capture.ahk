#Requires AutoHotkey v2.0
CoordMode("Mouse", "Screen")

; Capture Source
ToolTip("1. Hover over ITEM... press F9")
KeyWait("F9", "D")
MouseGetPos(&sX, &sY)
ToolTip("")
KeyWait("F9")

; Capture Destination
ToolTip("2. Hover over SLOT... press F9")
KeyWait("F9", "D")
MouseGetPos(&dX, &dY)
ToolTip("")
KeyWait("F9")

; Output coordinates back to Python
FileAppend(sX "," sY "," dX "," dY, "*")
