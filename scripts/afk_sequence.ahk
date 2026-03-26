#Requires AutoHotkey v2.0
SendMode "Event"
SetMouseDelay 20
CoordMode "Mouse", "Screen"

startTime := A_TickCount
keys := ["w", "a", "s", "d"]

; Simulate walking for roughly 5 seconds
while ((A_TickCount - startTime) < 5000) {
    k := keys[Random(1, 4)]
    SendEvent("{" k " Down}")
    Sleep(Random(120, 400))
    SendEvent("{" k " Up}")
    Sleep(Random(100, 350))
    
    ; Random mouse movement (1/3 chance)
    if (Random(1, 3) == 1) {
        sweepX := (Random(0, 1) ? 1 : -1) * Random(4000, 8000)
        sweepY := (Random(0, 1) ? 1 : -1) * Random(2000, 4000)
        
        steps := 30
        xStep := sweepX / steps
        yStep := sweepY / steps
        
        Loop steps {
            MouseMove(xStep, yStep, 2, "R")
            Sleep(10)
        }
        Sleep(Random(40, 120))
        Loop steps {
            MouseMove(-xStep, -yStep, 2, "R")
            Sleep(10)
        }
    }
}

; Always reload at the end
Sleep(3000)
SendEvent("{r Down}")
Sleep(Random(60, 120))
SendEvent("{r Up}")
