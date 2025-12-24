<#
.SYNOPSIS
    Riso Project - Development Environment Setup for Windows

.DESCRIPTION
    Sets up the development environment by checking for and optionally installing required tools.
    Supports check-only mode, interactive installation, and non-interactive installation.

.PARAMETER CheckOnly
    Check for required tools without installing. Returns exit code 0 if all present, 1 otherwise.

.PARAMETER Install
    Install missing tools. Prompts for confirmation unless -Yes is also specified.

.PARAMETER Yes
    Skip confirmation prompts when installing. Must be used with -Install.

.PARAMETER Help
    Show detailed help message.

.EXAMPLE
    .\setup.ps1
    Check and report what tools are missing (default dry-run mode)

.EXAMPLE
    .\setup.ps1 -Install
    Install missing tools with confirmation prompts

.EXAMPLE
    .\setup.ps1 -Install -Yes
    Install missing tools without prompting

.EXAMPLE
    .\setup.ps1 -CheckOnly
    Check for tools and exit with code 0 if all present, 1 if any missing

.NOTES
    Version: 1.0.0
    Requires: PowerShell 5.1 or later
    Platform: Windows (PowerShell Core also supported on macOS/Linux)

.LINK
    https://github.com/yourusername/riso
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Check for required tools without installing")]
    [switch]$CheckOnly,

    [Parameter(HelpMessage = "Install missing tools")]
    [switch]$Install,

    [Parameter(HelpMessage = "Skip confirmation prompts")]
    [switch]$Yes,

    [Parameter(HelpMessage = "Show help message")]
    [switch]$Help
)

# Script metadata
$ScriptName = "Riso Setup"
$ScriptVersion = "1.0.0"
$ErrorActionPreference = "Stop"
$InformationPreference = "Continue"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyInvocation.MyCommand.Path
$LibDir = Join-Path $ScriptDir "lib-ps"

# Version requirements (matches versions.sh)
$script:PYTHON_MIN_VERSION = "3.11"
$script:UV_MIN_VERSION = "0.4"
$script:NODE_MIN_VERSION = "20"
$script:PNPM_MIN_VERSION = "8"
$script:PRECOMMIT_VERSION = "3.0"
$script:ACTIONLINT_VERSION = "1.0"

# Track tool status
$script:ToolStatus = @{}
$script:ToolVersions = @{}
$script:MissingTools = @()
$script:FailedInstalls = @()

#region Helper Functions

function Show-Help {
    <#
    .SYNOPSIS
        Display detailed help message
    #>
    $helpText = @"

$ScriptName v$ScriptVersion

USAGE:
    .\setup.ps1 [OPTIONS]

OPTIONS:
    -CheckOnly      Check for required tools without installing
                    Exit 0 if all tools present, 1 if any missing

    -Install        Install missing tools (prompts for confirmation)

    -Install -Yes   Install missing tools without prompting

    -Help           Show this help message

ENVIRONMENT:
    `$env:NO_COLOR       Disable colored output
    `$env:DEBUG          Enable debug logging
    `$env:VERBOSE        Enable verbose logging

EXAMPLES:
    # Check what tools are missing
    .\setup.ps1

    # Check and install missing tools (with prompts)
    .\setup.ps1 -Install

    # Install missing tools without prompts
    .\setup.ps1 -Install -Yes

    # Just check, exit 0 if all present
    .\setup.ps1 -CheckOnly

EXIT CODES:
    0   All required tools present (or successfully installed)
    1   Missing tools (check-only mode) or installation failed
    2   Invalid arguments or script error

For more information, see: docs/development/setup.md

"@
    Write-Host $helpText
}

function Write-ColorOutput {
    <#
    .SYNOPSIS
        Write colored output (respects NO_COLOR)
    #>
    param(
        [string]$Message,
        [string]$ForegroundColor = "White",
        [switch]$NoNewline
    )

    if ($env:NO_COLOR) {
        if ($NoNewline) {
            Write-Host $Message -NoNewline
        } else {
            Write-Host $Message
        }
    } else {
        if ($NoNewline) {
            Write-Host $Message -ForegroundColor $ForegroundColor -NoNewline
        } else {
            Write-Host $Message -ForegroundColor $ForegroundColor
        }
    }
}

function Write-InfoMessage {
    param([string]$Message)
    Write-ColorOutput "ℹ [INFO] $Message" -ForegroundColor Blue
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-ColorOutput "✓ [SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarnMessage {
    param([string]$Message)
    Write-ColorOutput "⚠ [WARN] $Message" -ForegroundColor Yellow
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-ColorOutput "✗ [ERROR] $Message" -ForegroundColor Red
}

function Write-DebugMessage {
    param([string]$Message)
    if ($env:DEBUG -or $env:VERBOSE) {
        Write-ColorOutput "→ [DEBUG] $Message" -ForegroundColor Cyan
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "==> $Title" -ForegroundColor Blue
}

function Test-CommandExists {
    <#
    .SYNOPSIS
        Check if a command exists
    #>
    param([string]$Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Get-ToolVersion {
    <#
    .SYNOPSIS
        Get version of a tool
    #>
    param(
        [string]$ToolName,
        [string]$VersionFlag = "--version"
    )

    if (-not (Test-CommandExists $ToolName)) {
        return "unknown"
    }

    try {
        $output = & $ToolName $VersionFlag 2>&1 | Select-Object -First 1
        if ($output -match '(\d+\.\d+(\.\d+)?)') {
            return $Matches[1]
        }
        return "unknown"
    } catch {
        return "unknown"
    }
}

function Compare-Version {
    <#
    .SYNOPSIS
        Compare two version strings (returns true if $Current >= $Required)
    #>
    param(
        [string]$Current,
        [string]$Required
    )

    try {
        $currentVer = [version]$Current
        $requiredVer = [version]$Required
        return $currentVer -ge $requiredVer
    } catch {
        # If version parsing fails, do string comparison
        return $Current -ge $Required
    }
}

function Test-Tool {
    <#
    .SYNOPSIS
        Check if a tool is installed and meets minimum version
    #>
    param(
        [string]$ToolName,
        [string]$MinVersion,
        [string]$VersionFlag = "--version"
    )

    Write-DebugMessage "Checking $ToolName (min version: $MinVersion)"

    if (-not (Test-CommandExists $ToolName)) {
        $script:ToolStatus[$ToolName] = "missing"
        $script:ToolVersions[$ToolName] = "not installed"
        $script:MissingTools += $ToolName
        return $false
    }

    $currentVersion = Get-ToolVersion -ToolName $ToolName -VersionFlag $VersionFlag
    $script:ToolVersions[$ToolName] = $currentVersion

    if ($currentVersion -eq "unknown") {
        $script:ToolStatus[$ToolName] = "version-unknown"
        Write-DebugMessage "$ToolName`: version detection failed"
        return $true  # Allow unknown versions (tool exists)
    }

    if (Compare-Version -Current $currentVersion -Required $MinVersion) {
        $script:ToolStatus[$ToolName] = "ok"
        Write-DebugMessage "$ToolName`: $currentVersion >= $MinVersion ✓"
        return $true
    } else {
        $script:ToolStatus[$ToolName] = "outdated"
        $script:ToolVersions[$ToolName] = "$currentVersion (need $MinVersion+)"
        $script:MissingTools += $ToolName
        Write-DebugMessage "$ToolName`: $currentVersion < $MinVersion ✗"
        return $false
    }
}

function Test-AllTools {
    <#
    .SYNOPSIS
        Check all required tools
    #>
    Write-Section "Checking required tools"

    # Core tooling
    Test-Tool -ToolName "python" -MinVersion $script:PYTHON_MIN_VERSION | Out-Null
    Test-Tool -ToolName "uv" -MinVersion $script:UV_MIN_VERSION | Out-Null
    Test-Tool -ToolName "node" -MinVersion $script:NODE_MIN_VERSION | Out-Null
    Test-Tool -ToolName "pnpm" -MinVersion $script:PNPM_MIN_VERSION | Out-Null

    # Git and CI tools
    Test-Tool -ToolName "pre-commit" -MinVersion $script:PRECOMMIT_VERSION | Out-Null
    Test-Tool -ToolName "actionlint" -MinVersion $script:ACTIONLINT_VERSION -VersionFlag "-version" | Out-Null

    Write-Host ""
}

function Show-ToolStatus {
    <#
    .SYNOPSIS
        Display tool status table
    #>
    Write-Section "Tool Status"

    $format = "{0,-15} {1,-20} {2,-12}"
    Write-Host ($format -f "Tool", "Version", "Status")
    Write-Host ($format -f "----", "-------", "------")

    $tools = @("python", "uv", "node", "pnpm", "pre-commit", "actionlint")

    foreach ($tool in $tools) {
        $status = $script:ToolStatus[$tool]
        if (-not $status) { $status = "unknown" }

        $version = $script:ToolVersions[$tool]
        if (-not $version) { $version = "unknown" }

        $statusText = switch ($status) {
            "ok" { "✓ OK"; $color = "Green" }
            "missing" { "✗ MISSING"; $color = "Red" }
            "outdated" { "⚠ OUTDATED"; $color = "Yellow" }
            "version-unknown" { "? UNKNOWN"; $color = "Cyan" }
            default { "?"; $color = "White" }
        }

        Write-Host ("{0,-15} {1,-20} " -f $tool, $version) -NoNewline
        Write-ColorOutput $statusText -ForegroundColor $color
    }

    Write-Host ""
}

function Install-MissingTools {
    <#
    .SYNOPSIS
        Install all missing tools
    #>
    Write-Section "Installing missing tools"

    $installCount = 0
    $failCount = 0

    foreach ($tool in $script:MissingTools) {
        Write-InfoMessage "Installing $tool..."

        $installed = switch ($tool) {
            "python" { Install-Python }
            "uv" { Install-Uv }
            "node" { Install-Node }
            "pnpm" { Install-Pnpm }
            "pre-commit" { Install-PreCommit }
            "actionlint" { Install-Actionlint }
            default {
                Write-WarnMessage "Unknown tool: $tool (skipping)"
                $false
            }
        }

        if ($installed) {
            $installCount++
        } else {
            $failCount++
            $script:FailedInstalls += $tool
        }
    }

    Write-Host ""
    Write-InfoMessage "Installation complete: $installCount succeeded, $failCount failed"

    return ($failCount -eq 0)
}

function Confirm-Installation {
    <#
    .SYNOPSIS
        Confirm installation with user
    #>
    if ($Yes) {
        return $true
    }

    Write-WarnMessage "The following tools will be installed:"
    foreach ($tool in $script:MissingTools) {
        Write-Host "  - $tool"
    }
    Write-Host ""

    $response = Read-Host "Proceed with installation? [y/N]"
    return $response -match '^[yY](es)?$'
}

function Show-NextSteps {
    <#
    .SYNOPSIS
        Show next steps to the user
    #>
    Write-Section "Next Steps"

    if ($script:MissingTools.Count -eq 0) {
        Write-Host "✓ All required tools are installed and ready!`n"
        Write-Host "You can now:"
        Write-Host "  1. Render a sample project:"
        Write-ColorOutput "     .\scripts\render-samples.sh" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  2. Navigate to the rendered project:"
        Write-ColorOutput "     cd samples\default\render" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  3. Run the quickstart:"
        Write-ColorOutput "     uv sync" -ForegroundColor Cyan
        Write-ColorOutput "     uv run python -m <package_name>.quickstart" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  4. Run quality checks:"
        Write-ColorOutput "     make quality" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "For more information, see: docs/quickstart.md"
    } elseif (-not $Install) {
        Write-Host "⚠ Missing tools detected. To install them:`n"
        Write-ColorOutput "  .\setup.ps1 -Install" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Or install manually:"
        foreach ($tool in $script:MissingTools) {
            Write-Host "  - $tool"
        }
        Write-Host ""
        Write-Host "For installation instructions, see: docs/development/setup.md"
    } else {
        if ($script:FailedInstalls.Count -gt 0) {
            Write-Host "✗ Some tools failed to install:"
            foreach ($tool in $script:FailedInstalls) {
                Write-Host "  - $tool"
            }
            Write-Host ""
            Write-Host "Please install these tools manually. See: docs/development/setup.md"
        } else {
            Show-NextSteps  # Recursive call after successful install
        }
    }
}

#endregion

#region Installation Functions

function Install-Python {
    <#
    .SYNOPSIS
        Install Python using winget or chocolatey
    #>
    if (Test-CommandExists "winget") {
        try {
            winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements
            Write-SuccessMessage "Python installed via winget"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install Python via winget: $_"
        }
    }

    if (Test-CommandExists "choco") {
        try {
            choco install python311 -y
            Write-SuccessMessage "Python installed via chocolatey"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install Python via chocolatey: $_"
        }
    }

    Write-ErrorMessage "No package manager found. Install Python manually: https://www.python.org/downloads/"
    return $false
}

function Install-Uv {
    <#
    .SYNOPSIS
        Install uv using winget or standalone installer
    #>
    if (Test-CommandExists "winget") {
        try {
            winget install --id astral-sh.uv -e --source winget --accept-package-agreements --accept-source-agreements
            Write-SuccessMessage "uv installed via winget"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install uv via winget: $_"
        }
    }

    # Try PowerShell installer
    try {
        Write-InfoMessage "Installing uv with standalone installer..."
        Invoke-Expression (Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing).Content
        Write-SuccessMessage "uv installed via standalone installer"
        return $true
    } catch {
        Write-ErrorMessage "Failed to install uv: $_"
        return $false
    }
}

function Install-Node {
    <#
    .SYNOPSIS
        Install Node.js using winget or chocolatey
    #>
    if (Test-CommandExists "winget") {
        try {
            winget install --id OpenJS.NodeJS.LTS -e --source winget --accept-package-agreements --accept-source-agreements
            Write-SuccessMessage "Node.js installed via winget"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install Node.js via winget: $_"
        }
    }

    if (Test-CommandExists "choco") {
        try {
            choco install nodejs-lts -y
            Write-SuccessMessage "Node.js installed via chocolatey"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install Node.js via chocolatey: $_"
        }
    }

    Write-ErrorMessage "No package manager found. Install Node.js manually: https://nodejs.org/"
    return $false
}

function Install-Pnpm {
    <#
    .SYNOPSIS
        Install pnpm using npm or standalone installer
    #>
    if (Test-CommandExists "npm") {
        try {
            npm install -g pnpm
            Write-SuccessMessage "pnpm installed via npm"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install pnpm via npm: $_"
        }
    }

    if (Test-CommandExists "winget") {
        try {
            winget install --id pnpm.pnpm -e --source winget --accept-package-agreements --accept-source-agreements
            Write-SuccessMessage "pnpm installed via winget"
            return $true
        } catch {
            Write-ErrorMessage "Failed to install pnpm via winget: $_"
        }
    }

    Write-ErrorMessage "No package manager found. Install pnpm manually: https://pnpm.io/installation"
    return $false
}

function Install-PreCommit {
    <#
    .SYNOPSIS
        Install pre-commit using uv
    #>
    if (-not (Test-CommandExists "uv")) {
        Write-ErrorMessage "uv is required to install pre-commit"
        return $false
    }

    try {
        uv tool install pre-commit
        Write-SuccessMessage "pre-commit installed via uv tool"
        return $true
    } catch {
        Write-ErrorMessage "Failed to install pre-commit: $_"
        return $false
    }
}

function Install-Actionlint {
    <#
    .SYNOPSIS
        Install actionlint via download
    #>
    try {
        $installDir = "$env:USERPROFILE\.local\bin"
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        }

        # Download latest release
        $latestUrl = "https://api.github.com/repos/rhysd/actionlint/releases/latest"
        $release = Invoke-RestMethod -Uri $latestUrl
        $version = $release.tag_name -replace '^v', ''

        $assetUrl = $release.assets | Where-Object { $_.name -match "actionlint_.*_windows_amd64.zip" } | Select-Object -First 1 -ExpandProperty browser_download_url

        if (-not $assetUrl) {
            Write-ErrorMessage "Could not find Windows asset in GitHub release"
            return $false
        }

        $zipPath = Join-Path $env:TEMP "actionlint.zip"
        Invoke-WebRequest -Uri $assetUrl -OutFile $zipPath

        Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
        Remove-Item $zipPath

        Write-SuccessMessage "actionlint $version installed to $installDir"
        Write-InfoMessage "Add $installDir to your PATH to use actionlint"
        return $true
    } catch {
        Write-ErrorMessage "Failed to install actionlint: $_"
        return $false
    }
}

#endregion

#region Main

function Main {
    # Validate parameters
    if ($CheckOnly -and $Install) {
        Write-ErrorMessage "Cannot use -CheckOnly and -Install together"
        exit 2
    }

    if ($Yes -and -not $Install) {
        Write-ErrorMessage "-Yes can only be used with -Install"
        exit 2
    }

    if ($Help) {
        Show-Help
        exit 0
    }

    # Show header
    Write-Host ""
    Write-ColorOutput "$ScriptName v$ScriptVersion" -ForegroundColor Blue
    Write-Host ""

    # Check all tools
    Test-AllTools

    # Show status
    Show-ToolStatus

    # Determine action
    if ($script:MissingTools.Count -eq 0) {
        Write-SuccessMessage "All required tools are present!"
        Show-NextSteps
        exit 0
    }

    # Missing tools detected
    if ($CheckOnly) {
        Write-WarnMessage "$($script:MissingTools.Count) tool(s) missing or outdated"
        exit 1
    }

    if (-not $Install) {
        # Default dry-run mode
        Write-WarnMessage "$($script:MissingTools.Count) tool(s) missing or outdated"
        Show-NextSteps
        exit 1
    }

    # Install mode
    if (-not (Confirm-Installation)) {
        Write-InfoMessage "Installation cancelled by user"
        exit 1
    }

    # Install missing tools
    if (Install-MissingTools) {
        Write-SuccessMessage "All tools installed successfully!"

        # Re-check tools after installation
        Write-Host ""
        $script:ToolStatus = @{}
        $script:ToolVersions = @{}
        $script:MissingTools = @()
        Test-AllTools
        Show-ToolStatus
        Show-NextSteps

        exit 0
    } else {
        Write-ErrorMessage "Installation completed with failures"
        Show-NextSteps
        exit 1
    }
}

# Run main function
Main

#endregion
