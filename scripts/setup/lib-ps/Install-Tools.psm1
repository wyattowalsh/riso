# Install-Tools.psm1 - Tool installation functions for Riso setup
# Provides automated installation with fallback strategies and logging

<#
.SYNOPSIS
    Tool installation functions for Riso setup scripts.

.DESCRIPTION
    This module provides functions to install development tools required by Riso.
    Each function tries multiple installation methods (winget, choco, scoop, direct download)
    and logs results in a structured format.
#>

# Import dependencies
using module ./Detect-Platform.psm1
using module ./Logging.psm1
using module ./Colors.psm1

# Version constants - align with template/copier.yml and existing automation
$script:Versions = @{
    Python     = '3.11'
    Uv         = '0.4'
    Node       = '20'
    Pnpm       = '8'
    Ruff       = '0.14.2'
    Ty         = '0.0.6'
    Pylint     = '4.0.2'
    PreCommit  = 'latest'
    Actionlint = 'latest'
}

# Installation URLs
$script:InstallUrls = @{
    UvWindows = 'https://astral.sh/uv/install.ps1'
    UvUnix    = 'https://astral.sh/uv/install.sh'
}

function Test-CommandExists {
    <#
    .SYNOPSIS
        Checks if a command is available in the current session.

    .PARAMETER Command
        The command name to check.

    .OUTPUTS
        System.Boolean. Returns $true if command exists, $false otherwise.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Invoke-WingetInstall {
    <#
    .SYNOPSIS
        Installs a package using winget.

    .PARAMETER PackageId
        The winget package identifier.

    .PARAMETER PackageName
        Display name for logging.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageId,

        [Parameter(Mandatory = $true)]
        [string]$PackageName
    )

    if (-not (Test-CommandExists 'winget')) {
        return $false
    }

    try {
        Write-Info "Installing $PackageName via winget..."
        $output = winget install --id $PackageId --silent --accept-source-agreements --accept-package-agreements 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Success "$PackageName installed via winget"
            return $true
        }
        else {
            Write-Warn "winget install failed with exit code $LASTEXITCODE"
            return $false
        }
    }
    catch {
        Write-Warn "winget install exception: $_"
        return $false
    }
}

function Invoke-ChocoInstall {
    <#
    .SYNOPSIS
        Installs a package using Chocolatey.

    .PARAMETER PackageName
        The Chocolatey package name.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageName
    )

    if (-not (Test-CommandExists 'choco')) {
        return $false
    }

    try {
        Write-Info "Installing $PackageName via Chocolatey..."
        $output = choco install $PackageName -y 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Success "$PackageName installed via Chocolatey"
            return $true
        }
        else {
            Write-Warn "Chocolatey install failed with exit code $LASTEXITCODE"
            return $false
        }
    }
    catch {
        Write-Warn "Chocolatey install exception: $_"
        return $false
    }
}

function Invoke-ScoopInstall {
    <#
    .SYNOPSIS
        Installs a package using Scoop.

    .PARAMETER PackageName
        The Scoop package name.

    .PARAMETER Bucket
        Optional Scoop bucket name.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageName,

        [Parameter(Mandatory = $false)]
        [string]$Bucket
    )

    if (-not (Test-CommandExists 'scoop')) {
        return $false
    }

    try {
        # Add bucket if specified
        if ($Bucket) {
            scoop bucket add $Bucket 2>&1 | Out-Null
        }

        Write-Info "Installing $PackageName via Scoop..."
        $output = scoop install $PackageName 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Success "$PackageName installed via Scoop"
            return $true
        }
        else {
            Write-Warn "Scoop install failed with exit code $LASTEXITCODE"
            return $false
        }
    }
    catch {
        Write-Warn "Scoop install exception: $_"
        return $false
    }
}

function Install-Uv {
    <#
    .SYNOPSIS
        Installs the uv Python package manager.

    .DESCRIPTION
        Tries installation via winget, then PowerShell installer script.
        Logs provisioning results.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-Uv
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $toolName = 'uv'
    $version = $script:Versions.Uv

    # Check if already installed
    if (Test-CommandExists 'uv') {
        Write-Success "uv is already installed"
        $installedVersion = (uv --version 2>&1) -replace '^uv\s+', ''
        Write-Info "Installed version: $installedVersion"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'already_present' -Method 'existing'
        return $true
    }

    Write-Info "Installing uv..."

    # Try winget first (Windows)
    if ((Get-Platform) -eq 'windows') {
        if (Invoke-WingetInstall -PackageId 'astral-sh.uv' -PackageName 'uv') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'winget'
            return $true
        }

        # Try PowerShell installer
        try {
            Write-Info "Trying PowerShell installer for uv..."
            Invoke-RestMethod $script:InstallUrls.UvWindows | Invoke-Expression

            if (Test-CommandExists 'uv') {
                Write-Success "uv installed via PowerShell installer"
                Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'powershell_installer'
                return $true
            }
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-Error "PowerShell installer failed: $errorMsg"
        }

        # Try Chocolatey
        if (Invoke-ChocoInstall -PackageName 'uv') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'choco'
            return $true
        }

        # Try Scoop
        if (Invoke-ScoopInstall -PackageName 'uv') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'scoop'
            return $true
        }
    }

    # Installation failed
    $nextSteps = @"
Manual installation required. Visit: https://docs.astral.sh/uv/getting-started/installation/
Windows: irm https://astral.sh/uv/install.ps1 | iex
"@
    Write-Error "Failed to install uv"
    Write-Info $nextSteps
    Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'failure' -Method 'none' -NextSteps $nextSteps

    return $false
}

function Install-Python {
    <#
    .SYNOPSIS
        Installs Python using the system package manager.

    .DESCRIPTION
        Tries installation via winget, chocolatey, or scoop.
        On Windows, installs Python from python.org distributions.

    .PARAMETER Version
        Python version to install (default: 3.11).

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-Python -Version '3.11'
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Version = $script:Versions.Python
    )

    $toolName = 'python'

    # Check if already installed
    if (Test-CommandExists 'python') {
        Write-Success "Python is already installed"
        $installedVersion = (python --version 2>&1) -replace '^Python\s+', ''
        Write-Info "Installed version: $installedVersion"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'already_present' -Method 'existing'
        return $true
    }

    Write-Info "Installing Python $Version..."

    # Try winget first (Windows)
    if ((Get-Platform) -eq 'windows') {
        $packageId = "Python.Python.$Version"
        if (Invoke-WingetInstall -PackageId $packageId -PackageName "Python $Version") {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'success' -Method 'winget'
            return $true
        }

        # Try Chocolatey
        if (Invoke-ChocoInstall -PackageName 'python') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'success' -Method 'choco'
            return $true
        }

        # Try Scoop
        if (Invoke-ScoopInstall -PackageName 'python' -Bucket 'main') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'success' -Method 'scoop'
            return $true
        }
    }

    # Installation failed
    $nextSteps = "Manual installation required. Visit: https://www.python.org/downloads/"
    Write-Error "Failed to install Python"
    Write-Info $nextSteps
    Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'failure' -Method 'none' -NextSteps $nextSteps

    return $false
}

function Install-Node {
    <#
    .SYNOPSIS
        Installs Node.js using the system package manager.

    .PARAMETER Version
        Node.js major version to install (default: 20).

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-Node -Version '20'
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Version = $script:Versions.Node
    )

    $toolName = 'node'

    # Check if already installed
    if (Test-CommandExists 'node') {
        Write-Success "Node.js is already installed"
        $installedVersion = (node --version 2>&1) -replace '^v', ''
        Write-Info "Installed version: $installedVersion"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'already_present' -Method 'existing'
        return $true
    }

    Write-Info "Installing Node.js $Version..."

    # Try winget first (Windows)
    if ((Get-Platform) -eq 'windows') {
        if (Invoke-WingetInstall -PackageId 'OpenJS.NodeJS.LTS' -PackageName "Node.js $Version LTS") {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'success' -Method 'winget'
            return $true
        }

        # Try Chocolatey
        if (Invoke-ChocoInstall -PackageName 'nodejs-lts') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'success' -Method 'choco'
            return $true
        }

        # Try Scoop
        if (Invoke-ScoopInstall -PackageName 'nodejs-lts' -Bucket 'main') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'success' -Method 'scoop'
            return $true
        }
    }

    # Installation failed
    $nextSteps = "Manual installation required. Visit: https://nodejs.org/"
    Write-Error "Failed to install Node.js"
    Write-Info $nextSteps
    Write-ProvisionResult -ToolName $toolName -VersionRequested $Version -Status 'failure' -Method 'none' -NextSteps $nextSteps

    return $false
}

function Install-Pnpm {
    <#
    .SYNOPSIS
        Installs pnpm package manager.

    .DESCRIPTION
        Tries installation via corepack (preferred), npm global install, or system package managers.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-Pnpm
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $toolName = 'pnpm'
    $version = $script:Versions.Pnpm

    # Check if already installed
    if (Test-CommandExists 'pnpm') {
        Write-Success "pnpm is already installed"
        $installedVersion = (pnpm --version 2>&1)
        Write-Info "Installed version: $installedVersion"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'already_present' -Method 'existing'
        return $true
    }

    Write-Info "Installing pnpm..."

    # Try corepack enable (requires Node.js)
    if (Test-CommandExists 'node') {
        try {
            Write-Info "Enabling corepack for pnpm..."
            corepack enable 2>&1 | Out-Null

            if ($LASTEXITCODE -eq 0) {
                # Prepare pnpm
                corepack prepare pnpm@latest --activate 2>&1 | Out-Null

                if (Test-CommandExists 'pnpm') {
                    Write-Success "pnpm installed via corepack"
                    Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'corepack'
                    return $true
                }
            }
        }
        catch {
            Write-Warn "Corepack installation failed: $_"
        }

        # Try npm global install
        try {
            Write-Info "Installing pnpm via npm..."
            npm install -g pnpm 2>&1 | Out-Null

            if (Test-CommandExists 'pnpm') {
                Write-Success "pnpm installed via npm"
                Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'npm_global'
                return $true
            }
        }
        catch {
            Write-Warn "npm global install failed: $_"
        }
    }

    # Try system package managers (Windows)
    if ((Get-Platform) -eq 'windows') {
        if (Invoke-WingetInstall -PackageId 'pnpm.pnpm' -PackageName 'pnpm') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'winget'
            return $true
        }

        if (Invoke-ScoopInstall -PackageName 'pnpm' -Bucket 'main') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'scoop'
            return $true
        }
    }

    # Installation failed
    $nextSteps = @"
Manual installation required. Visit: https://pnpm.io/installation
With Node.js installed: corepack enable && corepack prepare pnpm@latest --activate
"@
    Write-Error "Failed to install pnpm"
    Write-Info $nextSteps
    Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'failure' -Method 'none' -NextSteps $nextSteps

    return $false
}

function Install-QualityTools {
    <#
    .SYNOPSIS
        Installs Python quality tools (ruff, ty, pylint) via uv tool install.

    .DESCRIPTION
        Requires uv to be installed first. Installs quality tools globally via uv.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-QualityTools
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    # Check for uv
    if (-not (Test-CommandExists 'uv')) {
        Write-Error "uv is required to install quality tools"
        return $false
    }

    $tools = @(
        @{ Name = 'ruff'; Version = $script:Versions.Ruff }
        @{ Name = 'ty'; Version = $script:Versions.Ty }
        @{ Name = 'pylint'; Version = $script:Versions.Pylint }
    )

    $allSuccess = $true

    foreach ($tool in $tools) {
        $toolName = $tool.Name
        $toolVersion = $tool.Version

        Write-Info "Installing $toolName $toolVersion via uv tool install..."

        try {
            # Install with specific version
            $packageSpec = if ($toolVersion -ne 'latest') { "${toolName}==${toolVersion}" } else { $toolName }
            uv tool install $packageSpec 2>&1 | Out-Null

            if ($LASTEXITCODE -eq 0) {
                Write-Success "$toolName installed successfully"
                Write-ProvisionResult -ToolName $toolName -VersionRequested $toolVersion -Status 'success' -Method 'uv_tool'
            }
            else {
                Write-Error "$toolName installation failed"
                Write-ProvisionResult -ToolName $toolName -VersionRequested $toolVersion -Status 'failure' -Method 'uv_tool'
                $allSuccess = $false
            }
        }
        catch {
            $errorMsg = $_.Exception.Message
            Write-Error "$toolName installation exception: $errorMsg"
            Write-ProvisionResult -ToolName $toolName -VersionRequested $toolVersion -Status 'failure' -Method 'uv_tool' -Stderr $errorMsg
            $allSuccess = $false
        }
    }

    return $allSuccess
}

function Install-PreCommit {
    <#
    .SYNOPSIS
        Installs pre-commit via uv tool install.

    .DESCRIPTION
        Requires uv to be installed first.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-PreCommit
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $toolName = 'pre-commit'
    $version = $script:Versions.PreCommit

    # Check for uv
    if (-not (Test-CommandExists 'uv')) {
        Write-Error "uv is required to install pre-commit"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'failure' -Method 'none' -NextSteps 'Install uv first'
        return $false
    }

    # Check if already installed
    if (Test-CommandExists 'pre-commit') {
        Write-Success "pre-commit is already installed"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'already_present' -Method 'existing'
        return $true
    }

    Write-Info "Installing pre-commit via uv tool install..."

    try {
        uv tool install pre-commit 2>&1 | Out-Null

        if ($LASTEXITCODE -eq 0) {
            Write-Success "pre-commit installed successfully"
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'uv_tool'
            return $true
        }
        else {
            Write-Error "pre-commit installation failed"
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'failure' -Method 'uv_tool'
            return $false
        }
    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-Error "pre-commit installation exception: $errorMsg"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'failure' -Method 'uv_tool' -Stderr $errorMsg
        return $false
    }
}

function Install-Actionlint {
    <#
    .SYNOPSIS
        Installs actionlint for GitHub Actions workflow validation.

    .DESCRIPTION
        Tries installation via system package managers or direct download from GitHub releases.

    .OUTPUTS
        System.Boolean. Returns $true on success, $false otherwise.

    .EXAMPLE
        Install-Actionlint
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $toolName = 'actionlint'
    $version = $script:Versions.Actionlint

    # Check if already installed
    if (Test-CommandExists 'actionlint') {
        Write-Success "actionlint is already installed"
        $installedVersion = (actionlint --version 2>&1)
        Write-Info "Installed version: $installedVersion"
        Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'already_present' -Method 'existing'
        return $true
    }

    Write-Info "Installing actionlint..."

    # Try package managers (Windows)
    if ((Get-Platform) -eq 'windows') {
        if (Invoke-ScoopInstall -PackageName 'actionlint' -Bucket 'main') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'scoop'
            return $true
        }

        if (Invoke-ChocoInstall -PackageName 'actionlint') {
            Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'success' -Method 'choco'
            return $true
        }
    }

    # Installation failed - provide manual steps
    $nextSteps = @"
Manual installation required. Visit: https://github.com/rhysd/actionlint/releases
Scoop: scoop install actionlint
Chocolatey: choco install actionlint
"@
    Write-Error "Failed to install actionlint"
    Write-Info $nextSteps
    Write-ProvisionResult -ToolName $toolName -VersionRequested $version -Status 'failure' -Method 'none' -NextSteps $nextSteps

    return $false
}

function Install-AllTools {
    <#
    .SYNOPSIS
        Installs all required Riso tools in the correct order.

    .DESCRIPTION
        Orchestrates installation of all tools with proper dependency ordering.

    .OUTPUTS
        System.Boolean. Returns $true if all installations succeeded.

    .EXAMPLE
        Install-AllTools
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    Write-Info "Starting installation of all Riso tools..."
    Write-Info ""

    $results = @{}

    # Install in dependency order
    Write-Info "=== Phase 1: Core Tools ==="
    $results['python'] = Install-Python
    $results['uv'] = Install-Uv
    $results['node'] = Install-Node
    $results['pnpm'] = Install-Pnpm

    Write-Info ""
    Write-Info "=== Phase 2: Quality Tools ==="
    $results['quality_tools'] = Install-QualityTools
    $results['pre-commit'] = Install-PreCommit
    $results['actionlint'] = Install-Actionlint

    Write-Info ""
    Write-Info "=== Installation Summary ==="

    $successCount = ($results.Values | Where-Object { $_ -eq $true }).Count
    $totalCount = $results.Count

    foreach ($tool in $results.Keys) {
        $status = if ($results[$tool]) { '[SUCCESS]' } else { '[FAILED]' }
        $color = if ($results[$tool]) { 'Green' } else { 'Red' }
        Write-Host "$status $tool" -ForegroundColor $color
    }

    Write-Info ""
    Write-Info "Installed: $successCount / $totalCount tools"

    $allSuccess = $successCount -eq $totalCount
    if ($allSuccess) {
        Write-Success "All tools installed successfully!"
    }
    else {
        Write-Warn "Some tools failed to install. Check logs for details."
    }

    return $allSuccess
}

# Export module members
Export-ModuleMember -Function @(
    'Install-Uv',
    'Install-Python',
    'Install-Node',
    'Install-Pnpm',
    'Install-QualityTools',
    'Install-PreCommit',
    'Install-Actionlint',
    'Install-AllTools'
)

Export-ModuleMember -Variable 'Versions'
