# Detect-Platform.psm1 - Platform detection functions for Riso setup
# Provides cross-platform detection and package manager identification

<#
.SYNOPSIS
    Platform detection and package manager identification for Riso setup scripts.

.DESCRIPTION
    This module provides functions to detect the operating system, architecture,
    available package managers, and execution context (admin, WSL, etc.).
#>

function Get-Platform {
    <#
    .SYNOPSIS
        Detects the current operating system platform.

    .DESCRIPTION
        Returns a standardized platform identifier: windows, linux, or macos.

    .OUTPUTS
        System.String. Returns 'windows', 'linux', or 'macos'.

    .EXAMPLE
        $platform = Get-Platform
        # Returns: windows
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    if ($IsWindows -or ($PSVersionTable.PSVersion.Major -eq 5)) {
        return 'windows'
    }
    elseif ($IsLinux) {
        return 'linux'
    }
    elseif ($IsMacOS) {
        return 'macos'
    }
    else {
        throw "Unable to detect platform"
    }
}

function Get-Architecture {
    <#
    .SYNOPSIS
        Detects the current system architecture.

    .DESCRIPTION
        Returns a standardized architecture identifier: x64 or arm64.

    .OUTPUTS
        System.String. Returns 'x64' or 'arm64'.

    .EXAMPLE
        $arch = Get-Architecture
        # Returns: x64
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    $arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture

    switch ($arch) {
        'X64' { return 'x64' }
        'Arm64' { return 'arm64' }
        'X86' { return 'x86' }
        default { return $arch.ToString().ToLower() }
    }
}

function Get-PackageManager {
    <#
    .SYNOPSIS
        Detects available Windows package managers.

    .DESCRIPTION
        Checks for winget, chocolatey, and scoop in order of preference.
        Returns the first available package manager or 'none' if none found.

    .OUTPUTS
        System.String. Returns 'winget', 'choco', 'scoop', or 'none'.

    .EXAMPLE
        $pkgMgr = Get-PackageManager
        # Returns: winget
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    # Only relevant for Windows
    $platform = Get-Platform
    if ($platform -ne 'windows') {
        return 'none'
    }

    # Check for winget
    try {
        $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCmd) {
            # Verify winget is functional
            $null = winget --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                return 'winget'
            }
        }
    }
    catch {
        # Continue to next package manager
    }

    # Check for chocolatey
    try {
        $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue
        if ($chocoCmd) {
            return 'choco'
        }
    }
    catch {
        # Continue to next package manager
    }

    # Check for scoop
    try {
        $scoopCmd = Get-Command scoop -ErrorAction SilentlyContinue
        if ($scoopCmd) {
            return 'scoop'
        }
    }
    catch {
        # No package manager found
    }

    return 'none'
}

function Test-IsAdmin {
    <#
    .SYNOPSIS
        Checks if the current PowerShell session is running with elevated privileges.

    .DESCRIPTION
        Returns $true if running as Administrator on Windows, or as root on Unix-like systems.

    .OUTPUTS
        System.Boolean. Returns $true if elevated, $false otherwise.

    .EXAMPLE
        if (Test-IsAdmin) {
            Write-Host "Running with elevated privileges"
        }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $platform = Get-Platform

    if ($platform -eq 'windows') {
        # Windows: Check for Administrator role
        $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
        return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    else {
        # Unix-like: Check if running as root (UID 0)
        try {
            $isRoot = (id -u) -eq 0
            return $isRoot
        }
        catch {
            return $false
        }
    }
}

function Test-IsWSL {
    <#
    .SYNOPSIS
        Checks if PowerShell is running inside Windows Subsystem for Linux.

    .DESCRIPTION
        Returns $true if running in WSL, $false otherwise.
        Checks for WSL-specific environment indicators.

    .OUTPUTS
        System.Boolean. Returns $true if in WSL, $false otherwise.

    .EXAMPLE
        if (Test-IsWSL) {
            Write-Host "Running in WSL"
        }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    # WSL only exists on Linux platform
    if (-not $IsLinux) {
        return $false
    }

    # Check for WSL environment variable
    if ($env:WSL_DISTRO_NAME) {
        return $true
    }

    # Check /proc/version for Microsoft/WSL
    try {
        if (Test-Path '/proc/version') {
            $procVersion = Get-Content '/proc/version' -Raw
            if ($procVersion -match '(Microsoft|WSL)') {
                return $true
            }
        }
    }
    catch {
        # Error reading /proc/version, assume not WSL
    }

    # Check /proc/sys/kernel/osrelease for WSL
    try {
        if (Test-Path '/proc/sys/kernel/osrelease') {
            $osRelease = Get-Content '/proc/sys/kernel/osrelease' -Raw
            if ($osRelease -match '(Microsoft|WSL)') {
                return $true
            }
        }
    }
    catch {
        # Error reading osrelease, assume not WSL
    }

    return $false
}

function Get-PlatformInfo {
    <#
    .SYNOPSIS
        Returns comprehensive platform information.

    .DESCRIPTION
        Gathers all platform detection information into a single object.

    .OUTPUTS
        System.Management.Automation.PSCustomObject. Object with platform details.

    .EXAMPLE
        $info = Get-PlatformInfo
        Write-Host "Platform: $($info.Platform) ($($info.Architecture))"
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param()

    [PSCustomObject]@{
        Platform       = Get-Platform
        Architecture   = Get-Architecture
        PackageManager = Get-PackageManager
        IsAdmin        = Test-IsAdmin
        IsWSL          = Test-IsWSL
        PSVersion      = "$($PSVersionTable.PSVersion.Major).$($PSVersionTable.PSVersion.Minor)"
        PSEdition      = $PSVersionTable.PSEdition
    }
}

# Export module members
Export-ModuleMember -Function @(
    'Get-Platform',
    'Get-Architecture',
    'Get-PackageManager',
    'Test-IsAdmin',
    'Test-IsWSL',
    'Get-PlatformInfo'
)
