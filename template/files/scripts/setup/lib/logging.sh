#!/usr/bin/env bash
# Riso Setup - File Logging with XDG Compliance
# Provides structured logging to files following XDG Base Directory specification

# XDG Base Directory functions
# https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

get_xdg_data_home() {
    echo "${XDG_DATA_HOME:-${HOME}/.local/share}"
}

get_xdg_config_home() {
    echo "${XDG_CONFIG_HOME:-${HOME}/.config}"
}

get_xdg_state_home() {
    echo "${XDG_STATE_HOME:-${HOME}/.local/state}"
}

get_xdg_cache_home() {
    echo "${XDG_CACHE_HOME:-${HOME}/.cache}"
}

# Get Riso log directory (XDG_STATE_HOME/riso)
get_log_dir() {
    local state_home
    state_home="$(get_xdg_state_home)"
    echo "${state_home}/riso"
}

# Get Riso config directory (XDG_CONFIG_HOME/riso)
get_config_dir() {
    local config_home
    config_home="$(get_xdg_config_home)"
    echo "${config_home}/riso"
}

# Get Riso cache directory (XDG_CACHE_HOME/riso)
get_cache_dir() {
    local cache_home
    cache_home="$(get_xdg_cache_home)"
    echo "${cache_home}/riso"
}

# Initialize log file with timestamp
# Args: [log_name] - optional log file name prefix
# Returns: path to log file
init_log_file() {
    local log_name="${1:-setup}"
    local log_dir
    log_dir="$(get_log_dir)"

    # Create log directory if it doesn't exist
    mkdir -p "$log_dir"

    # Generate timestamped log file name
    local timestamp
    timestamp="$(date +%Y%m%d_%H%M%S)"
    local log_file="${log_dir}/${log_name}_${timestamp}.log"

    # Create log file with header
    {
        echo "# Riso Setup Log - ${log_name}"
        echo "# Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        echo "# Platform: $(uname -s) $(uname -r) $(uname -m)"
        echo "# Shell: ${SHELL:-unknown}"
        echo ""
    } > "$log_file"

    echo "$log_file"
}

# Log message to file with ISO 8601 timestamp
# Args: log_file, level, message
log_to_file() {
    local log_file="$1"
    local level="$2"
    shift 2
    local message="$*"

    if [ ! -f "$log_file" ]; then
        # Create parent directory if needed
        mkdir -p "$(dirname "$log_file")"
        touch "$log_file"
    fi

    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    printf "[%s] %-7s %s\n" "$timestamp" "$level" "$message" >> "$log_file"
}

# Log provision result in JSONL format
# Matches the format used in .riso/toolchain_provisioning.jsonl
# Args: tool_name, status, method, version, duration_ms
log_provision_result() {
    local tool_name="$1"
    local status="$2"        # success, failure, skipped
    local method="$3"        # mise, brew, apt, curl, etc.
    local version="$4"       # version string or "unknown"
    local duration_ms="${5:-0}"

    local log_dir
    log_dir="$(get_log_dir)"
    local jsonl_file="${log_dir}/toolchain_provisioning.jsonl"

    # Create log directory if it doesn't exist
    mkdir -p "$log_dir"

    # Get timestamp in ISO 8601 format
    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Build JSON object (using printf for better compatibility)
    local json
    json=$(cat <<EOF
{"timestamp":"${timestamp}","tool":"${tool_name}","status":"${status}","method":"${method}","version":"${version}","duration_ms":${duration_ms}}
EOF
)

    # Append to JSONL file
    echo "$json" >> "$jsonl_file"

    # Also log to standard log file if LOG_FILE is set
    if [ -n "${LOG_FILE:-}" ]; then
        log_to_file "$LOG_FILE" "PROVISION" "${tool_name} → ${status} (${method}, v${version}, ${duration_ms}ms)"
    fi
}

# Get latest log file for a given prefix
# Args: [log_name] - optional log file name prefix
# Returns: path to most recent log file, or empty string if none found
get_latest_log() {
    local log_name="${1:-setup}"
    local log_dir
    log_dir="$(get_log_dir)"

    if [ ! -d "$log_dir" ]; then
        return 1
    fi

    # Find most recent log file matching pattern
    local latest
    latest=$(find "$log_dir" -name "${log_name}_*.log" -type f -print0 2>/dev/null |
             xargs -0 ls -t 2>/dev/null |
             head -n 1)

    if [ -n "$latest" ]; then
        echo "$latest"
        return 0
    fi

    return 1
}

# Clean old log files (keep last N)
# Args: [keep_count] - number of logs to keep (default: 10)
# Args: [log_name] - optional log file name prefix
clean_old_logs() {
    local keep_count="${1:-10}"
    local log_name="${2:-setup}"
    local log_dir
    log_dir="$(get_log_dir)"

    if [ ! -d "$log_dir" ]; then
        return 0
    fi

    # Find log files matching pattern, sorted by modification time
    local log_files
    log_files=$(find "$log_dir" -name "${log_name}_*.log" -type f -print0 2>/dev/null |
                xargs -0 ls -t 2>/dev/null)

    # Count total logs
    local total_logs
    total_logs=$(echo "$log_files" | grep -c '^' 2>/dev/null || echo 0)

    if [ "$total_logs" -le "$keep_count" ]; then
        return 0
    fi

    # Delete old logs (keep most recent N)
    echo "$log_files" | tail -n +$((keep_count + 1)) | while IFS= read -r log_file; do
        rm -f "$log_file"
    done
}

# Display log file summary
# Args: log_file
show_log_summary() {
    local log_file="$1"

    if [ ! -f "$log_file" ]; then
        echo "Log file not found: $log_file"
        return 1
    fi

    echo "=== Log Summary: $log_file ==="
    echo ""
    echo "Errors:"
    grep -c '\[ERROR\]' "$log_file" || echo "0"
    echo ""
    echo "Warnings:"
    grep -c '\[WARN\]' "$log_file" || echo "0"
    echo ""
    echo "Recent entries:"
    tail -n 20 "$log_file"
}
