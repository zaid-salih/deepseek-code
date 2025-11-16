# deepseek-code/installers/install.ps1
Write-Host "🚀 Installing DeepSeek-Code..." -ForegroundColor Green

# Download and run Python installer
$installerUrl = "https://raw.githubusercontent.com/yourusername/deepseek-code/main/installers/install.py"
$tempFile = "$env:TEMP\deepseek_install.py"

try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $tempFile
    python $tempFile
}
catch {
    Write-Host "❌ Installation failed: $_" -ForegroundColor Red
}
finally {
    if (Test-Path $tempFile) {
        Remove-Item $tempFile
    }
}