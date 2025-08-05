# PowerShell script untuk menjalankan test dengan output yang informatif
# run_tests.ps1

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "                          🧪 SAE EBLUP AREA UNIT TESTS                        " -ForegroundColor Yellow
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
try {
    $pytestVersion = python -m pytest --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pytest found: $pytestVersion" -ForegroundColor Green
    } else {
        throw "pytest not found"
    }
} catch {
    Write-Host "❌ pytest not found. Installing..." -ForegroundColor Red
    python -m pip install pytest pytest-cov
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install pytest. Please install manually: pip install pytest" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "📂 Current Directory: $(Get-Location)" -ForegroundColor Blue
Write-Host "📋 Running tests with AAA pattern (Arrange-Act-Assert)..." -ForegroundColor Blue
Write-Host ""

# Run the specific test file
$testFile = "test\modelling\script\test_sae_eblup_area_new.py"

if (Test-Path $testFile) {
    Write-Host "🔍 Running test file: $testFile" -ForegroundColor Yellow
    Write-Host ""
    
    # Run pytest with custom options
    python -m pytest $testFile `
        --verbose `
        --tb=short `
        --color=yes `
        --capture=no `
        --durations=5 `
        --disable-warnings `
        --maxfail=3
    
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    
    if ($exitCode -eq 0) {
        Write-Host "                             ✅ ALL TESTS PASSED!                             " -ForegroundColor Green
        Write-Host "                       🎉 Congratulations! Your code works!                    " -ForegroundColor Green
    } else {
        Write-Host "                             ❌ SOME TESTS FAILED!                            " -ForegroundColor Red
        Write-Host "                        🔧 Please review the failures above                   " -ForegroundColor Yellow
    }
    
    Write-Host "===============================================================================" -ForegroundColor Cyan
    
    # Show test summary
    Write-Host ""
    Write-Host "📊 Test Summary:" -ForegroundColor Blue
    Write-Host "   • Test file: $testFile"
    Write-Host "   • Pattern: AAA (Arrange-Act-Assert)"
    Write-Host "   • Framework: pytest"
    Write-Host "   • Exit code: $exitCode"
    
    exit $exitCode
    
} else {
    Write-Host "❌ Test file not found: $testFile" -ForegroundColor Red
    Write-Host "   Please make sure the test file exists in the correct location." -ForegroundColor Yellow
    exit 1
}
