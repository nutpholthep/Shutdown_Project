<#
.SYNOPSIS
    Smart Block & SmartScreen Fix Tool for Shutdown Scheduler
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Shutdown Scheduler - Fix Smart Block & SmartScreen   " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

# Find exe
$exePaths = @(
    (Join-Path $ScriptDir "dist\ShutdownScheduler.exe"),
    (Join-Path $ScriptDir "ShutdownScheduler.exe")
)

$targetExe = $null
foreach ($p in $exePaths) {
    if (Test-Path $p) {
        $targetExe = $p
        break
    }
}

if (-not $targetExe) {
    Write-Warning "Could not find ShutdownScheduler.exe in ./dist or current folder."
    Write-Host "Please build the app first or place this script next to ShutdownScheduler.exe" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nTarget Executable: $targetExe" -ForegroundColor Gray

# Step 1: Unblock Mark of the Web
Write-Host "`n[1/2] Removing Mark-of-the-Web (Zone.Identifier)..." -ForegroundColor Green
try {
    Unblock-File -Path $targetExe -ErrorAction Stop
    Write-Host "✓ File unblocked successfully." -ForegroundColor Green
} catch {
    Write-Host "! Unblock warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 2: Trust Signature / Certificate
Write-Host "`n[2/2] Checking & Trusting Digital Signature..." -ForegroundColor Green
try {
    $sig = Get-AuthenticodeSignature -FilePath $targetExe
    if ($sig.SignerCertificate) {
        $cert = $sig.SignerCertificate
        
        # Add to CurrentUser TrustedPublisher and Root
        $pubStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("TrustedPublisher", "CurrentUser")
        $pubStore.Open("ReadWrite")
        $pubStore.Add($cert)
        $pubStore.Close()

        $rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
        $rootStore.Open("ReadWrite")
        $rootStore.Add($cert)
        $rootStore.Close()

        Write-Host "✓ Certificate added to Trusted Root & Trusted Publisher stores." -ForegroundColor Green
        Write-Host "  Signer: $($cert.Subject)" -ForegroundColor Gray
    } else {
        Write-Host "- Executable has no embedded digital signature." -ForegroundColor Yellow
    }
} catch {
    Write-Host "! Certificate trust warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Smart Block fix applied.                     " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "`n💡 คำแนะนำเพิ่มเติมสำหรับ Windows SmartScreen:" -ForegroundColor Cyan
Write-Host "หากเปิดโปรแกรมแล้วยังมีหน้าต่างสีฟ้า 'Windows protected your PC':" -ForegroundColor White
Write-Host "1. คลิกที่ลิงก์ 'More info' (ข้อมูลเพิ่มเติม)" -ForegroundColor Yellow
Write-Host "2. คลิกปุ่ม 'Run anyway' (เรียกใช้ต่อไป)" -ForegroundColor Yellow
Write-Host "หลังจากกดครั้งแรกแล้ว ระบบจะไม่แสดงการแจ้งเตือนนี้อีกต่อไป ✨`n" -ForegroundColor Gray
