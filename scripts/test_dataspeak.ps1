$ErrorActionPreference = "Stop"

$ProjectFolder = [string]([char]0x9879) + [string]([char]0x76EE)
$ExpectedRoot = "C:\Users\24607\Desktop\${ProjectFolder}\DataSpeak"
$pytestPassed = $false
$smokePassed = $false
$benchmarkPassed = $false
$benchmarkSkipped = $false
$notUsingEm = $false

function Write-Stage {
    param([string]$Title)
    Write-Host ""
    Write-Host "==== $Title ====" -ForegroundColor Cyan
}

function Stop-WithFailure {
    param(
        [string]$CommandText,
        [int]$ExitCode,
        [string]$Advice
    )
    Write-Host ""
    Write-Host "FAILED COMMAND: $CommandText" -ForegroundColor Red
    Write-Host "EXIT CODE: $ExitCode" -ForegroundColor Red
    if ($Advice) {
        Write-Host "Advice: $Advice" -ForegroundColor Yellow
    }
    exit $ExitCode
}

function Invoke-TestStep {
    param(
        [string]$Title,
        [string]$Command,
        [string[]]$Arguments,
        [string]$Advice
    )
    Write-Stage $Title
    $commandText = "$Command $($Arguments -join ' ')"
    Write-Host "Running: $commandText"
    & $Command @Arguments
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Stop-WithFailure $commandText $exitCode $Advice
    }
}

Write-Stage "Check project directory"
$currentRoot = (Resolve-Path -LiteralPath (Get-Location).Path).Path
if (-not [string]::Equals($currentRoot, $ExpectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Host "Current directory is not $ExpectedRoot. Actual: $currentRoot" -ForegroundColor Red
    Write-Host "Advice: run cd /d C:\Users\24607\Desktop\PROJECT\DataSpeak, where PROJECT is the Chinese folder named by char codes 0x9879 0x76EE." -ForegroundColor Yellow
    exit 1
}
Write-Host "Current directory: $currentRoot"

Write-Stage "Check conda env"
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "conda command was not found." -ForegroundColor Red
    Write-Host "Advice: install Anaconda/Miniconda and make sure conda is available in PowerShell." -ForegroundColor Yellow
    exit 1
}

try {
    (& conda "shell.powershell" "hook") | Out-String | Invoke-Expression
} catch {
    Write-Host "Failed to initialize conda PowerShell hook: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Advice: run conda init powershell, reopen PowerShell, or activate ds manually before running this script." -ForegroundColor Yellow
    exit 1
}

$currentEnv = $env:CONDA_DEFAULT_ENV
if ($currentEnv -eq "em") {
    Write-Host "Current env is em. Stopping to avoid EnterpriseMind impact." -ForegroundColor Red
    Write-Host "Advice: open a new PowerShell and run conda activate ds." -ForegroundColor Yellow
    exit 1
}

if ($currentEnv -ne "ds") {
    Write-Host "Active conda env is '$currentEnv'. Activating ds before tests." -ForegroundColor Yellow
    conda activate ds
    if ($LASTEXITCODE -ne 0) {
        Write-Host "conda activate ds failed; exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Advice: run scripts\setup_conda_ds.ps1 first to create the ds environment." -ForegroundColor Yellow
        exit 1
    }
    $currentEnv = $env:CONDA_DEFAULT_ENV
}

if ($currentEnv -ne "ds") {
    Write-Host "Active conda env is still not ds. Actual: '$currentEnv'." -ForegroundColor Red
    Write-Host "Advice: confirm ds exists and do not run this script from em." -ForegroundColor Yellow
    exit 1
}

$notUsingEm = $true
Write-Host "Current conda env: $currentEnv"

Invoke-TestStep `
    -Title "Run pytest" `
    -Command "pytest" `
    -Arguments @("-q") `
    -Advice "Check failed tests. If dependencies are missing, run pip install -r requirements.txt in ds."
$pytestPassed = $true

Invoke-TestStep `
    -Title "Run smoke test" `
    -Command "python" `
    -Arguments @("scripts/smoke_test.py") `
    -Advice "Make sure demo data and Schema index are initialized with python scripts/init_demo_data.py and python scripts/build_schema_index.py."
$smokePassed = $true

Write-Stage "Run benchmark"
if (Test-Path -LiteralPath "dataspeak/evaluation/benchmark.py") {
    Invoke-TestStep `
        -Title "Execute benchmark" `
        -Command "python" `
        -Arguments @("-m", "dataspeak.evaluation.benchmark") `
        -Advice "Check evaluation/sample_queries.json, demo data, and index files."
    $benchmarkPassed = $true
} else {
    $benchmarkSkipped = $true
    Write-Host "dataspeak/evaluation/benchmark.py was not found. Benchmark skipped."
}

Write-Stage "Test summary"
Write-Host "pytest passed: $pytestPassed"
Write-Host "smoke_test passed: $smokePassed"
if ($benchmarkSkipped) {
    Write-Host "benchmark passed or skipped: skipped"
} else {
    Write-Host "benchmark passed or skipped: $benchmarkPassed"
}
Write-Host "confirmed not using em env: $notUsingEm"
Write-Host "This test script did not start, stop, or delete Docker containers and does not affect EnterpriseMind."
