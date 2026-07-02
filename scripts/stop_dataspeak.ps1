$ErrorActionPreference = "Stop"

$ProjectFolder = [string]([char]0x9879) + [string]([char]0x76EE)
$ExpectedRoot = "C:\Users\24607\Desktop\${ProjectFolder}\DataSpeak"

function Write-Stage {
    param([string]$Title)
    Write-Host ""
    Write-Host "==== $Title ====" -ForegroundColor Cyan
}

function Get-ListeningProcessIds {
    param([int]$Port)

    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if (-not $connections) {
            return @()
        }
        return @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
    } catch {
        Write-Host "Could not inspect port $Port with Get-NetTCPConnection: $($_.Exception.Message)" -ForegroundColor Yellow
        return @()
    }
}

function Stop-PortProcess {
    param(
        [int]$Port,
        [string]$ServiceName
    )

    Write-Stage "Stop $ServiceName on port $Port"
    $processIds = @(Get-ListeningProcessIds -Port $Port)

    if ($processIds.Count -eq 0) {
        Write-Host "Port $Port is not in LISTEN state. Nothing to stop."
        return
    }

    foreach ($processId in $processIds) {
        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            Write-Host "Stopping PID $processId ($($process.ProcessName)) listening on port $Port."
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host "Stopped PID $processId."
        } catch {
            Write-Host "Failed to stop PID $processId on port ${Port}: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

function Test-PortReleased {
    param([int]$Port)
    $processIds = @(Get-ListeningProcessIds -Port $Port)
    return ($processIds.Count -eq 0)
}

Write-Stage "Check project directory"
$currentRoot = (Resolve-Path -LiteralPath (Get-Location).Path).Path
if (-not [string]::Equals($currentRoot, $ExpectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Host "Current directory is not $ExpectedRoot. Actual: $currentRoot" -ForegroundColor Red
    Write-Host "Advice: run cd /d C:\Users\24607\Desktop\PROJECT\DataSpeak, where PROJECT is the Chinese folder named by char codes 0x9879 0x76EE." -ForegroundColor Yellow
    exit 1
}
Write-Host "Current directory: $currentRoot"

Stop-PortProcess -Port 18501 -ServiceName "Streamlit frontend"
Stop-PortProcess -Port 18088 -ServiceName "FastAPI backend"

Write-Stage "Stop DataSpeak Docker services"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "docker command was not found. Skipping Docker stop." -ForegroundColor Yellow
} else {
    & docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker does not appear to be running. Skipping docker compose stop." -ForegroundColor Yellow
    } else {
        Write-Host "Running: docker compose -p dataspeak stop"
        & docker compose -p dataspeak stop
        if ($LASTEXITCODE -ne 0) {
            Write-Host "docker compose -p dataspeak stop failed with exit code $LASTEXITCODE. Continuing to final status." -ForegroundColor Yellow
        }
    }
}

Write-Stage "Final status"
$port18501Released = Test-PortReleased -Port 18501
$port18088Released = Test-PortReleased -Port 18088
Write-Host "18501 released: $port18501Released"
Write-Host "18088 released: $port18088Released"

Write-Host ""
Write-Host 'docker ps --filter "name=dataspeak" result:'
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "docker command is unavailable."
} else {
    & docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker is not running."
    } else {
        & docker ps --filter "name=dataspeak"
    }
}

Write-Host ""
Write-Host "Stop script finished. Only ports 18501/18088 and docker compose project dataspeak were targeted."
