# Logging.psm1 - Logging functions for Riso setup
# Provides structured logging with Windows-appropriate paths and JSONL format

<#
.SYNOPSIS
    Logging functions for Riso setup scripts.

.DESCRIPTION
    This module provides structured logging capabilities with support for
    Windows-appropriate log directories and JSONL format for tool provisioning.
#>

# Import platform detection for path resolution
using module ./Detect-Platform.psm1

# Script-level variables
$script:CurrentLogFile = $null
$script:SessionId = (New-Guid).ToString().Substring(0, 8)

function Get-LogDirectory {
    <#
    .SYNOPSIS
        Returns the appropriate log directory for the current platform.

    .DESCRIPTION
        On Windows: $env:LOCALAPPDATA\riso\logs
        On macOS: ~/Library/Logs/riso
        On Linux: ~/.local/share/riso/logs

    .OUTPUTS
        System.String. The full path to the log directory.

    .EXAMPLE
        $logDir = Get-LogDirectory
        # Returns: C:\Users\username\AppData\Local\riso\logs (on Windows)
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    $platform = Get-Platform

    switch ($platform) {
        'windows' {
            $baseDir = $env:LOCALAPPDATA
            if (-not $baseDir) {
                $baseDir = Join-Path $env:USERPROFILE 'AppData\Local'
            }
            return Join-Path $baseDir 'riso\logs'
        }
        'macos' {
            return Join-Path $env:HOME 'Library/Logs/riso'
        }
        'linux' {
            $baseDir = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $env:HOME '.local/share' }
            return Join-Path $baseDir 'riso/logs'
        }
        default {
            # Fallback to home directory
            return Join-Path $env:HOME '.riso/logs'
        }
    }
}

function Initialize-LogFile {
    <#
    .SYNOPSIS
        Creates a timestamped log file for the current session.

    .DESCRIPTION
        Creates a new log file with ISO 8601 timestamp in the filename.
        Ensures the log directory exists and returns the log file path.

    .PARAMETER Prefix
        Optional prefix for the log filename (e.g., 'setup', 'provision').

    .OUTPUTS
        System.String. The full path to the created log file.

    .EXAMPLE
        $logFile = Initialize-LogFile -Prefix 'setup'
        # Returns: C:\Users\username\AppData\Local\riso\logs\setup-2025-12-24T10-30-45.log
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Prefix = 'riso'
    )

    $logDir = Get-LogDirectory

    # Ensure log directory exists
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    # Create timestamped filename (Windows-safe format)
    $timestamp = Get-Date -Format 'yyyy-MM-ddTHH-mm-ss'
    $logFileName = "$Prefix-$timestamp.log"
    $logPath = Join-Path $logDir $logFileName

    # Create the log file
    New-Item -ItemType File -Path $logPath -Force | Out-Null

    # Store in script variable for other functions
    $script:CurrentLogFile = $logPath

    # Write initial header
    $header = @"
=== Riso Setup Log ===
Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Session ID: $script:SessionId
Platform: $(Get-Platform)
PowerShell: $($PSVersionTable.PSVersion)
======================

"@
    Add-Content -Path $logPath -Value $header

    return $logPath
}

function Write-LogEntry {
    <#
    .SYNOPSIS
        Writes a structured log entry to the current log file.

    .DESCRIPTION
        Appends a timestamped log entry with the specified level.
        If no log file is initialized, writes to console only.

    .PARAMETER Message
        The log message to write.

    .PARAMETER Level
        The log level (INFO, WARN, ERROR, DEBUG, SUCCESS).

    .EXAMPLE
        Write-LogEntry -Message "Starting installation" -Level INFO
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet('INFO', 'WARN', 'ERROR', 'DEBUG', 'SUCCESS')]
        [string]$Level = 'INFO'
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logLine = "[$timestamp] [$Level] $Message"

    # Write to console with appropriate color
    switch ($Level) {
        'ERROR' { Write-Host $logLine -ForegroundColor Red }
        'WARN' { Write-Host $logLine -ForegroundColor Yellow }
        'SUCCESS' { Write-Host $logLine -ForegroundColor Green }
        'DEBUG' { if ($DebugPreference -ne 'SilentlyContinue') { Write-Host $logLine -ForegroundColor Cyan } }
        default { Write-Host $logLine }
    }

    # Write to log file if initialized
    if ($script:CurrentLogFile) {
        Add-Content -Path $script:CurrentLogFile -Value $logLine
    }
}

function Write-ProvisionResult {
    <#
    .SYNOPSIS
        Logs tool provisioning results in JSONL format.

    .DESCRIPTION
        Appends a JSON-formatted provisioning record to the toolchain_provisioning.jsonl file.
        Matches the format used by existing Riso automation scripts.

    .PARAMETER ToolName
        Name of the tool being provisioned.

    .PARAMETER VersionRequested
        The version that was requested (e.g., '3.11', '0.4', 'latest').

    .PARAMETER Status
        Provisioning status: 'success', 'failure', 'skipped', 'already_present'.

    .PARAMETER Method
        Installation method used: 'winget', 'choco', 'scoop', 'direct_download', 'uv_tool', 'npm', etc.

    .PARAMETER Stderr
        Any error output from the installation process.

    .PARAMETER NextSteps
        Recommended next steps or manual installation instructions.

    .EXAMPLE
        Write-ProvisionResult -ToolName 'uv' -VersionRequested '0.4' -Status 'success' -Method 'winget'
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ToolName,

        [Parameter(Mandatory = $true)]
        [string]$VersionRequested,

        [Parameter(Mandatory = $true)]
        [ValidateSet('success', 'failure', 'skipped', 'already_present')]
        [string]$Status,

        [Parameter(Mandatory = $true)]
        [string]$Method,

        [Parameter(Mandatory = $false)]
        [string]$Stderr = '',

        [Parameter(Mandatory = $false)]
        [string]$NextSteps = ''
    )

    # Determine log file location
    $logDir = Get-LogDirectory
    $provisionLogPath = Join-Path $logDir 'toolchain_provisioning.jsonl'

    # Ensure log directory exists
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    # Build JSON object matching existing format
    $record = [ordered]@{
        timestamp         = (Get-Date -Format 'o')
        session_id        = $script:SessionId
        tool              = $ToolName
        version_requested = $VersionRequested
        status            = $Status
        method            = $Method
        platform          = Get-Platform
        architecture      = Get-Architecture
        stderr            = $Stderr
        next_steps        = $NextSteps
    }

    # Convert to JSON (single line for JSONL)
    $jsonLine = $record | ConvertTo-Json -Compress -Depth 10

    # Append to JSONL file
    Add-Content -Path $provisionLogPath -Value $jsonLine

    # Also write to standard log if available
    if ($script:CurrentLogFile) {
        $logMessage = "Provisioned $ToolName ($VersionRequested) - Status: $Status, Method: $Method"
        Write-LogEntry -Message $logMessage -Level $(if ($Status -eq 'success') { 'SUCCESS' } elseif ($Status -eq 'failure') { 'ERROR' } else { 'INFO' })
    }
}

function Get-CurrentLogFile {
    <#
    .SYNOPSIS
        Returns the path to the current log file.

    .DESCRIPTION
        Returns the log file path initialized by Initialize-LogFile, or $null if not initialized.

    .OUTPUTS
        System.String. The current log file path or $null.

    .EXAMPLE
        $logFile = Get-CurrentLogFile
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    return $script:CurrentLogFile
}

function Get-ProvisioningHistory {
    <#
    .SYNOPSIS
        Reads and parses the toolchain provisioning history.

    .DESCRIPTION
        Reads the toolchain_provisioning.jsonl file and returns parsed records.

    .PARAMETER ToolName
        Optional filter for specific tool name.

    .PARAMETER Status
        Optional filter for specific status.

    .OUTPUTS
        System.Array. Array of provisioning record objects.

    .EXAMPLE
        $history = Get-ProvisioningHistory -ToolName 'uv'
    #>
    [CmdletBinding()]
    [OutputType([array])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$ToolName,

        [Parameter(Mandatory = $false)]
        [ValidateSet('success', 'failure', 'skipped', 'already_present')]
        [string]$Status
    )

    $logDir = Get-LogDirectory
    $provisionLogPath = Join-Path $logDir 'toolchain_provisioning.jsonl'

    if (-not (Test-Path $provisionLogPath)) {
        return @()
    }

    $records = Get-Content $provisionLogPath | ForEach-Object {
        $_ | ConvertFrom-Json
    }

    # Apply filters
    if ($ToolName) {
        $records = $records | Where-Object { $_.tool -eq $ToolName }
    }

    if ($Status) {
        $records = $records | Where-Object { $_.status -eq $Status }
    }

    return $records
}

# Export module members
Export-ModuleMember -Function @(
    'Get-LogDirectory',
    'Initialize-LogFile',
    'Write-LogEntry',
    'Write-ProvisionResult',
    'Get-CurrentLogFile',
    'Get-ProvisioningHistory'
)
