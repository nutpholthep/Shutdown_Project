<#
.SYNOPSIS
    Build and Code-Sign Shutdown Scheduler Desktop Application for Windows.
    Solves Windows SmartScreen / Defender Smart Block issues.
#>

param (
    [switch]$NoSign = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Shutdown Scheduler - Build & Anti-SmartBlock Pipeline  " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

# Step 1: Generate Assets (Icon & Version Info)
Write-Host "`n[1/5] Generating Application Assets & Version Info..." -ForegroundColor Green
python generate_assets.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to generate assets."
}

# Step 2: Build with PyInstaller
Write-Host "`n[2/5] Building Executable with PyInstaller (UPX Disabled)..." -ForegroundColor Green
python -m PyInstaller ShutdownScheduler.spec --noconfirm --clean
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed."
}

$ExePath = Join-Path $ScriptDir "dist\ShutdownScheduler.exe"
if (-not (Test-Path $ExePath)) {
    Write-Error "Build output not found at: $ExePath"
}

Write-Host "Build output created: $ExePath" -ForegroundColor Gray

# Step 3: Setup Local Code Signing Certificate
if (-not $NoSign) {
    Write-Host "`n[3/5] Setting up Local Code Signing Certificate..." -ForegroundColor Green
    $CertSubject = "CN=ShutdownScheduler Local Dev, O=Shutdown Project"
    
    # Check if certificate exists in CurrentUser\My
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like "*ShutdownScheduler*" } | Select-Object -First 1

    if (-not $cert) {
        Write-Host "Creating new Self-Signed Code Signing Certificate..." -ForegroundColor Yellow
        $cert = New-SelfSignedCertificate `
            -Type CodeSigningCert `
            -Subject $CertSubject `
            -CertStoreLocation "Cert:\CurrentUser\My" `
            -NotAfter (Get-Date).AddYears(10) `
            -KeyUsage DigitalSignature `
            -FriendlyName "ShutdownScheduler Code Signing"

        # Also trust certificate in CurrentUser Root and TrustedPublisher
        $rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
        $rootStore.Open("ReadWrite")
        $rootStore.Add($cert)
        $rootStore.Close()

        $pubStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("TrustedPublisher", "CurrentUser")
        $pubStore.Open("ReadWrite")
        $pubStore.Add($cert)
        $pubStore.Close()
        Write-Host "Certificate installed to CurrentUser Root & TrustedPublisher stores." -ForegroundColor Green
    } else {
        Write-Host "Found existing certificate: $($cert.Thumbprint)" -ForegroundColor Gray
    }

    # Step 4: Sign the Executable
    Write-Host "`n[4/5] Signing Executable with Authenticode..." -ForegroundColor Green
    try {
        # Try signing with timestamp server first
        $signResult = Set-AuthenticodeSignature `
            -FilePath $ExePath `
            -Certificate $cert `
            -TimestampServer "http://timestamp.digicert.com" `
            -HashAlgorithm SHA256 -ErrorAction SilentlyContinue
    } catch {
        $signResult = $null
    }

    if (-not $signResult -or $signResult.Status -ne "Valid") {
        # Fallback to signing without timestamp if offline
        Write-Host "Timestamp server unavailable or offline, signing without timestamp..." -ForegroundColor Yellow
        $signResult = Set-AuthenticodeSignature `
            -FilePath $ExePath `
            -Certificate $cert `
            -HashAlgorithm SHA256
    }

    Write-Host "Signature Status: $($signResult.Status) ($($signResult.StatusMessage))" -ForegroundColor Cyan
}

# Step 5: Unblock Mark of the Web
Write-Host "`n[5/5] Unblocking Mark-of-the-Web (Zone.Identifier)..." -ForegroundColor Green
Unblock-File -Path $ExePath
Write-Host "File successfully unblocked." -ForegroundColor Green

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "  SUCCESS: Build and Anti-SmartBlock Complete! ✨        " -ForegroundColor Green
Write-Host "  Location: $ExePath                                     " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Green
