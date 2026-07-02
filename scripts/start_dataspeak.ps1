$ErrorActionPreference = "Stop"

$ProjectFolder = [string]([char]0x9879) + [string]([char]0x76EE)
$ExpectedRoot = "C:\Users\24607\Desktop\${ProjectFolder}\DataSpeak"

function Write-Stage {
    param([string]$Title)
    Write-Host ""
    Write-Host "==== $Title ====" -ForegroundColor Cyan
}

function Stop-WithAdvice {
    param(
        [string]$Message,
        [string]$Advice
    )
    Write-Host ""
    Write-Host "START FAILED: $Message" -ForegroundColor Red
    if ($Advice) {
        Write-Host "Advice: $Advice" -ForegroundColor Yellow
    }
    exit 1
}

function Invoke-NativeStep {
    param(
        [string]$Title,
        [string]$Command,
        [string[]]$Arguments,
        [string]$Advice
    )
    Write-Stage $Title
    Write-Host "Running: $Command $($Arguments -join ' ')"
    & $Command @Arguments
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Stop-WithAdvice "Command failed: $Command $($Arguments -join ' '); exit code: $exitCode" $Advice
    }
}

Write-Stage "Check project directory"
$currentRoot = (Resolve-Path -LiteralPath (Get-Location).Path).Path
if (-not [string]::Equals($currentRoot, $ExpectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    Stop-WithAdvice "Current directory is not $ExpectedRoot. Actual: $currentRoot" "Run: cd /d C:\Users\24607\Desktop\PROJECT\DataSpeak, where PROJECT is the Chinese folder named by char codes 0x9879 0x76EE."
}
Write-Host "Current directory: $currentRoot"

Write-Stage "Check conda"
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Stop-WithAdvice "conda command was not found." "Install Anaconda/Miniconda and make sure conda is available in PowerShell."
}

try {
    (& conda "shell.powershell" "hook") | Out-String | Invoke-Expression
} catch {
    Stop-WithAdvice "Failed to initialize conda PowerShell hook: $($_.Exception.Message)" "Run conda init powershell, reopen PowerShell, or activate ds manually before running this script."
}

$beforeEnv = $env:CONDA_DEFAULT_ENV
if ($beforeEnv -eq "em") {
    Write-Host "Current env is em. Switching to ds immediately; DataSpeak commands will not run in em." -ForegroundColor Yellow
}

if ($env:CONDA_DEFAULT_ENV -ne "ds") {
    Write-Stage "Activate conda env ds"
    conda activate ds
    if ($LASTEXITCODE -ne 0) {
        Stop-WithAdvice "conda activate ds failed; exit code: $LASTEXITCODE" "Run scripts\setup_conda_ds.ps1 first to create the ds environment."
    }
}

if ($env:CONDA_DEFAULT_ENV -ne "ds") {
    Stop-WithAdvice "Active conda env is not ds. Actual: '$env:CONDA_DEFAULT_ENV'" "Make sure ds exists and run: conda activate ds. Do not use em for DataSpeak."
}
Write-Host "Current conda env: $env:CONDA_DEFAULT_ENV"

Write-Stage "Check .env"
if (-not (Test-Path -LiteralPath ".env")) {
    if (Test-Path -LiteralPath ".env.example") {
        Copy-Item -LiteralPath ".env.example" -Destination ".env" -ErrorAction Stop
        Write-Host "Created .env from .env.example"
    } else {
        Stop-WithAdvice ".env is missing and .env.example was not found." "Create .env.example or create .env manually."
    }
} else {
    Write-Host ".env already exists. It will not be overwritten."
}

Write-Stage "Start DataSpeak Docker services safely"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Stop-WithAdvice "docker command was not found." "Start Docker Desktop. This script only runs: docker compose -p dataspeak up -d."
}
Invoke-NativeStep `
    -Title "docker compose -p dataspeak up -d" `
    -Command "docker" `
    -Arguments @("compose", "-p", "dataspeak", "up", "-d") `
    -Advice "Check Docker Desktop and port conflicts. Do not run global prune commands or remove EnterpriseMind containers."

Invoke-NativeStep `
    -Title "Initialize demo data" `
    -Command "python" `
    -Arguments @("scripts/init_demo_data.py") `
    -Advice "Check ds dependencies and database settings in .env."

Invoke-NativeStep `
    -Title "Build Schema index" `
    -Command "python" `
    -Arguments @("scripts/build_schema_index.py") `
    -Advice "Make sure demo data was initialized. If Milvus is unavailable, DataSpeak should use local fallback."

Write-Stage "Start FastAPI and Streamlit"
$apiCommand = @"
`$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath '$ExpectedRoot'
(& conda 'shell.powershell' 'hook') | Out-String | Invoke-Expression
conda activate ds
uvicorn dataspeak.app.main:app --host 127.0.0.1 --port 18088
"@

$webCommand = @"
`$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath '$ExpectedRoot'
(& conda 'shell.powershell' 'hook') | Out-String | Invoke-Expression
conda activate ds
streamlit run dataspeak_web/app.py --server.port 18501
"@

Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $apiCommand) -WorkingDirectory $ExpectedRoot
Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $webCommand) -WorkingDirectory $ExpectedRoot

Write-Stage "DataSpeak startup information"
Write-Host "Backend docs: http://127.0.0.1:18088/docs"
Write-Host "Frontend: http://127.0.0.1:18501"
Write-Host "Health check: http://127.0.0.1:18088/api/health"
Write-Host "Docker project name: dataspeak"
Write-Host "Current conda env: $env:CONDA_DEFAULT_ENV"
Write-Host "FastAPI and Streamlit were started in two new PowerShell windows."
