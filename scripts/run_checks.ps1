Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Lightweight checks for scaffold and local Python logic on Windows.

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        [scriptblock] $Script
    )

    Write-Host "==> $Name"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Script
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    $exitCode = $LASTEXITCODE
    if ($null -ne $exitCode -and $exitCode -ne 0) {
        throw "$Name failed with exit code $exitCode"
    }
    Write-Host ""
}

function Get-PythonCommand {
    $venvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return (Resolve-Path -LiteralPath $venvPython).Path
    }

    return "python"
}

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $repoRoot

$python = Get-PythonCommand
$env:PYTHONUTF8 = "1"
$pytestBaseTemp = Join-Path ([System.IO.Path]::GetTempPath()) "lab04-pytest-$PID"

Write-Host "==> Codex config"
$doctorScript = Join-Path $repoRoot ".codex\scripts\doctor.sh"
if (Test-Path -LiteralPath $doctorScript) {
    $bash = Get-Command bash -ErrorAction SilentlyContinue
    if ($null -eq $bash) {
        Write-Host "Skipping .codex doctor; bash is not available on this Windows environment."
    }
    else {
        & $bash.Source ".codex/scripts/doctor.sh"
        if ($LASTEXITCODE -ne 0) {
            throw "Codex doctor failed with exit code $LASTEXITCODE"
        }
    }
}
else {
    Write-Host "Skipping .codex doctor; agent-local files are not required in public clones."
}
Write-Host ""

Invoke-Step "Python tests" {
    & $python -m pytest --basetemp $pytestBaseTemp -p no:cacheprovider
}

Invoke-Step "Docker Compose syntax" {
    $standaloneCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if ($null -ne $standaloneCompose) {
        & $standaloneCompose.Source config *> $null
    }
    else {
        & docker compose config *> $null
    }
}

Invoke-Step "JSON connector config" {
    & $python -m json.tool "neo4j\sink_connector.json" *> $null
}

Write-Host "Scaffold checks passed."
