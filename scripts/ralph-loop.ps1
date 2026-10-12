<#
.SYNOPSIS
    Ralph Loop autonomous execution helper script for Windows PowerShell.
.DESCRIPTION
    Runs or initializes the Ralph Loop file-based execution environment.
.PARAMETER Prompt
    Task description or prompt to guide the loop.
.PARAMETER MaxIterations
    Maximum number of iterations before pausing (default: 20).
.PARAMETER CompletionPromise
    Completion promise token to detect (default: DONE).
.PARAMETER TaskFile
    File containing task checklist (default: TODO.md).
#>

param (
    [string]$Prompt = "",
    [int]$MaxIterations = 20,
    [string]$CompletionPromise = "DONE",
    [string]$TaskFile = "TODO.md"
)

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "         RALPH LOOP CONTROLLER FOR AGENT         " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Ensure progress.txt exists
if (-not (Test-Path "progress.txt")) {
    $header = @"
# Ralph Loop Progress Log
Started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Goal: $Prompt
Completion Promise: $CompletionPromise
=================================================
"@
    Set-Content -Path "progress.txt" -Value $header -Encoding UTF8
    Write-Host "[+] Initialized progress.txt" -ForegroundColor Green
}

# Ensure TaskFile exists
if (-not (Test-Path $TaskFile)) {
    $initialTasks = @"
# Task List

- [ ] Initialize project baseline
- [ ] Implement core functionality for: $Prompt
- [ ] Add verification tests
- [ ] Review and polish
"@
    Set-Content -Path $TaskFile -Value $initialTasks -Encoding UTF8
    Write-Host "[+] Created template $TaskFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "Status:" -ForegroundColor Yellow
Write-Host "  Task File:           $TaskFile"
Write-Host "  Progress File:       progress.txt"
Write-Host "  Max Iterations:      $MaxIterations"
Write-Host "  Completion Promise:  $CompletionPromise"
Write-Host ""
Write-Host "Run `/ralph-loop` in Antigravity chat to begin autonomous iteration." -ForegroundColor Cyan
