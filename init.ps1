<#
.SYNOPSIS
    FrontRow One-Shot Initialization PowerShell Entry Point

.DESCRIPTION
    Launches the cross-platform python init.py runner script for Windows environment setup,
    database migrations, DML data seeding, and multi-service orchestration.

.EXAMPLE
    .\init.ps1
    .\init.ps1 -skip-services
#>

param(
    [switch]$SkipEnv,
    [switch]$SkipMigrations,
    [switch]$SkipSeed,
    [switch]$SkipServices
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$initPy = Join-Path $scriptDir "init.py"

# Build Python CLI arguments
$argsList = @()
if ($SkipEnv) { $argsList += "--skip-env" }
if ($SkipMigrations) { $argsList += "--skip-migrations" }
if ($SkipSeed) { $argsList += "--skip-seed" }
if ($SkipServices) { $argsList += "--skip-services" }

# Execute init.py via Python
Write-Host "Invoking FrontRow One-Shot Initialization Runner via Python..." -ForegroundColor Cyan
python $initPy @argsList
