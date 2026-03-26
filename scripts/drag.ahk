#Requires AutoHotkey v2.0
SendMode "Event"
SetMouseDelay 20
CoordMode "Mouse", "Screen"

if (A_Args.Length < 4)
    ExitApp

startX := A_Args[1]
startY := A_Args[2]
endX := A_Args[3]
endY := A_Args[4]

; 1. Move to item
MouseMove(startX, startY, 1)
Sleep(10)

; 2. Click down
Click("Down Left")
Sleep(10)

; 3. The "Micro-Drag" (Staged Grab)
MouseMove(startX + 10, startY + 10, 25)
Sleep(10)

; 4. Final Glide to destination
MouseMove(endX, endY, 1)
Sleep(10)

; 5. Release
Click("Up Left")
Sleep(10)
