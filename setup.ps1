# Check if running with administrative privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as an Administrator" -ForegroundColor Red
    exit
}

# Set variables
$pythonVersion = "3.11.5"  # You can modify this to the desired version
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

# Download Python installer
Write-Host "Downloading Python $pythonVersion..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath

# Install Python silently with pip included
Write-Host "Installing Python..." -ForegroundColor Yellow
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait -NoNewWindow

# Clean up
Remove-Item $installerPath

# Verify installation
Write-Host "Verifying Python installation..." -ForegroundColor Yellow
$pythonCheck = python --version
$pipCheck = pip --version

if ($pythonCheck) {
    Write-Host "Python installed successfully: $pythonCheck" -ForegroundColor Green
} else {
    Write-Host "Python installation failed" -ForegroundColor Red
}

if ($pipCheck) {
    Write-Host "pip installed successfully: $pipCheck" -ForegroundColor Green
} else {
    Write-Host "pip installation failed" -ForegroundColor Red
}

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
Write-Host "Installation complete! You may need to restart your PowerShell session for PATH changes to take effect." -ForegroundColor Green