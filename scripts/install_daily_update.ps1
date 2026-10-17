$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$taskName = 'Bangkok Condo Local Listing Update'
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { throw 'Python 3 was not found. Install Python, then run this script again.' }
$runner = Join-Path $PSScriptRoot 'run_daily_update.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -Python `"$python`" -Repository `"$repo`""
$trigger = New-ScheduledTaskTrigger -Daily -At '8:00 AM'
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description 'Read DDproperty/PropertyHub listing alert emails from Outlook and refresh the local Bangkok Condo map.' -Force | Out-Null
Write-Output "Daily 08:00 local update task created: $taskName"
Write-Output 'The computer must be on and signed in. Enable DDproperty listing email alerts first.'
