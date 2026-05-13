param(
    [string]$Python = $env:PARVA_PYTHON
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

function Invoke-PythonCandidate {
    param(
        [string[]]$Candidate,
        [string[]]$Arguments
    )

    $exe = $Candidate[0]
    $prefix = @()
    if ($Candidate.Count -gt 1) {
        $prefix = $Candidate[1..($Candidate.Count - 1)]
    }
    & $exe @prefix @Arguments
}

function Test-Python311 {
    param([string[]]$Candidate)

    try {
        $version = Invoke-PythonCandidate $Candidate @("-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")
        return ($LASTEXITCODE -eq 0 -and $version.Trim() -eq "3.11")
    }
    catch {
        return $false
    }
}

$candidates = @()
if ($Python) {
    $candidates += ,@($Python)
}

$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    $candidates += ,@($pyLauncher.Source, "-3.11")
}

foreach ($name in @("python3.11", "python3", "python")) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command) {
        $candidates += ,@($command.Source)
    }
}

foreach ($candidate in $candidates) {
    if (Test-Python311 $candidate) {
        Set-Location $ProjectRoot
        Invoke-PythonCandidate $candidate @("scripts\release\verify_public.py")
        exit $LASTEXITCODE
    }
}

Write-Error "Unable to find Python 3.11. Set PARVA_PYTHON to a Python 3.11 executable."
exit 1
