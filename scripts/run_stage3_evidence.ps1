param(
    [Parameter(Mandatory = $true)]
    [switch] $ResetDockerState,

    [Parameter(Mandatory = $true)]
    [Security.SecureString] $Neo4jPassword,

    [string] $GitBash = $env:GIT_BASH
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $ResetDockerState) {
    throw "-ResetDockerState is required for the canonical Stage 3 run."
}

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $repoRoot

$candidates = @()
if ($GitBash) {
    $candidates += $GitBash
}
$candidates += "C:\Program Files\Git\bin\bash.exe"
$candidates += "C:\Program Files\Git\usr\bin\bash.exe"

$bash = $candidates |
    Where-Object { $_ -and (Test-Path -LiteralPath $_) } |
    Select-Object -First 1
if (-not $bash) {
    throw "Git Bash was not found. Set GIT_BASH to Git's bin\\bash.exe path."
}

$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Neo4jPassword)
$previousPassword = $env:NEO4J_PASSWORD
$previousReset = $env:RESET_DOCKER_STATE
try {
    $env:NEO4J_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    $env:RESET_DOCKER_STATE = "1"
    & $bash "scripts/run_stage3_evidence.sh"
    if ($LASTEXITCODE -ne 0) {
        throw "Stage 3 Bash workflow failed with exit code $LASTEXITCODE"
    }
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
    if ($null -eq $previousPassword) {
        Remove-Item Env:NEO4J_PASSWORD -ErrorAction SilentlyContinue
    }
    else {
        $env:NEO4J_PASSWORD = $previousPassword
    }
    if ($null -eq $previousReset) {
        Remove-Item Env:RESET_DOCKER_STATE -ErrorAction SilentlyContinue
    }
    else {
        $env:RESET_DOCKER_STATE = $previousReset
    }
}
