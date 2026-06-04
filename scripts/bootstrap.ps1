param(
    [switch]$InstallPythonDeps = $true,
    [switch]$InstallFrontendDeps = $false
)

$pythonCmd = "python"
try {
    & $pythonCmd --version | Out-Null
} catch {
    $pythonCmd = "py"
}

Write-Host "[1/4] Create virtual env .venv"
& $pythonCmd -m venv .venv

Write-Host "[2/4] Activate virtual env"
& .\.venv\Scripts\Activate.ps1

if ($InstallPythonDeps) {
    Write-Host "[3/4] Install Python deps via Tsinghua mirror"
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
} else {
    Write-Host "[3/4] Skip Python deps"
}

if ($InstallFrontendDeps) {
    Write-Host "[4/4] Install frontend deps"
    Push-Location frontend
    npm install
    Pop-Location
} else {
    Write-Host "[4/4] Skip frontend deps"
}

Write-Host "Bootstrap done."
