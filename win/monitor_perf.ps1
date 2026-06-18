$logFile = "C:\Users\helder.toucas\Dev\paperclip\perf_log.txt"
"Timestamp, RAM_MB" | Out-File $logFile
while($true) {
    $proc = Get-Process AutoHotkey* -ErrorAction SilentlyContinue
    if ($proc) {
        $ram = [math]::Round($proc.WorkingSet / 1MB, 2)
        "$(Get-Date -Format 'HH:mm:ss'), $ram" | Out-File $logFile -Append
    }
    Start-Sleep -Seconds 10
}
