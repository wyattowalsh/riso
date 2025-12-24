# Colors.psm1 - Colored output functions for Riso setup
# Provides cross-platform colored console output with NO_COLOR support

<#
.SYNOPSIS
    Colored output functions for Riso setup scripts.

.DESCRIPTION
    This module provides standardized colored output functions that respect
    the NO_COLOR environment variable and work across PowerShell platforms.
#>

# Status symbols
$script:Symbols = @{
    Success = if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) { '[+]' } else { '✓' }
    Error   = if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) { '[X]' } else { '✗' }
    Warning = if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) { '[!]' } else { '⚠' }
    Info    = if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) { '[i]' } else { 'ℹ' }
    Debug   = if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) { '[D]' } else { '🐛' }
}

function Test-ColorSupport {
    <#
    .SYNOPSIS
        Checks if colored output is supported and allowed.

    .DESCRIPTION
        Returns $false if NO_COLOR environment variable is set (any value).
        Otherwise returns $true for interactive sessions with color support.
    #>
    if ($env:NO_COLOR) {
        return $false
    }

    # Check if we're in an interactive session
    if ($Host.UI -and $Host.UI.SupportsVirtualTerminal) {
        return $true
    }

    # PowerShell 5.1 fallback
    if ($PSVersionTable.PSVersion.Major -eq 5) {
        return $true
    }

    return $false
}

function Write-ColorText {
    <#
    .SYNOPSIS
        Internal helper to write colored text.

    .PARAMETER Message
        The message to display.

    .PARAMETER Color
        The color to use (ignored if NO_COLOR is set).

    .PARAMETER Symbol
        Optional symbol prefix.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [string]$Color,

        [Parameter(Mandatory = $false)]
        [string]$Symbol
    )

    $prefix = if ($Symbol) { "$Symbol " } else { "" }
    $fullMessage = "$prefix$Message"

    if (-not (Test-ColorSupport)) {
        Write-Host $fullMessage
        return
    }

    # ANSI color codes
    $colors = @{
        'Blue'   = "`e[34m"
        'Yellow' = "`e[33m"
        'Red'    = "`e[31m"
        'Green'  = "`e[32m"
        'Cyan'   = "`e[36m"
        'Reset'  = "`e[0m"
    }

    if ($Color -and $colors.ContainsKey($Color)) {
        Write-Host "$($colors[$Color])$fullMessage$($colors['Reset'])"
    }
    else {
        Write-Host $fullMessage
    }
}

function Write-Info {
    <#
    .SYNOPSIS
        Writes an informational message in blue.

    .DESCRIPTION
        Displays an informational message with an info symbol prefix.
        Respects the NO_COLOR environment variable.

    .PARAMETER Message
        The informational message to display.

    .EXAMPLE
        Write-Info "Starting setup process"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message
    )

    Write-ColorText -Message $Message -Color 'Blue' -Symbol $script:Symbols.Info
}

function Write-Warn {
    <#
    .SYNOPSIS
        Writes a warning message in yellow.

    .DESCRIPTION
        Displays a warning message with a warning symbol prefix.
        Respects the NO_COLOR environment variable.

    .PARAMETER Message
        The warning message to display.

    .EXAMPLE
        Write-Warn "Tool not found, will install"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message
    )

    Write-ColorText -Message $Message -Color 'Yellow' -Symbol $script:Symbols.Warning
}

function Write-Error {
    <#
    .SYNOPSIS
        Writes an error message in red.

    .DESCRIPTION
        Displays an error message with an error symbol prefix.
        Respects the NO_COLOR environment variable.

    .PARAMETER Message
        The error message to display.

    .EXAMPLE
        Write-Error "Installation failed"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message
    )

    Write-ColorText -Message $Message -Color 'Red' -Symbol $script:Symbols.Error
}

function Write-Success {
    <#
    .SYNOPSIS
        Writes a success message in green.

    .DESCRIPTION
        Displays a success message with a checkmark symbol prefix.
        Respects the NO_COLOR environment variable.

    .PARAMETER Message
        The success message to display.

    .EXAMPLE
        Write-Success "Installation completed"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message
    )

    Write-ColorText -Message $Message -Color 'Green' -Symbol $script:Symbols.Success
}

function Write-Debug {
    <#
    .SYNOPSIS
        Writes a debug message in cyan.

    .DESCRIPTION
        Displays a debug message with a debug symbol prefix.
        Only shown when $DebugPreference is not 'SilentlyContinue'.
        Respects the NO_COLOR environment variable.

    .PARAMETER Message
        The debug message to display.

    .EXAMPLE
        Write-Debug "Checking tool version"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message
    )

    if ($DebugPreference -ne 'SilentlyContinue') {
        Write-ColorText -Message $Message -Color 'Cyan' -Symbol $script:Symbols.Debug
    }
}

# Export module members
Export-ModuleMember -Function @(
    'Write-Info',
    'Write-Warn',
    'Write-Error',
    'Write-Success',
    'Write-Debug'
)
