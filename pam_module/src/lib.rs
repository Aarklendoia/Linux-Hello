// PAM Module for Linux Hello Face Recognition
// Pure Rust implementation with minimal dependencies
// GUI helper is a separate Python process

use std::os::unix::net::UnixStream;
use std::io::{Read, Write};
use std::path::Path;
use std::time::Duration;
use std::ffi::{CStr, CString};
use libc::{c_int, c_char};
use std::process::Command;
use std::fs;

const DAEMON_SOCKET: &str = "/run/linux-hello/daemon.sock";
const CONFIG_DIR: &str = "/run/linux-hello-pam";

// PAM return codes
const PAM_SUCCESS: c_int = 0;
const PAM_OPEN_ERR: c_int = 1;
const PAM_SYMBOL_ERR: c_int = 2;
const PAM_SERVICE_ERR: c_int = 3;
const PAM_SYSTEM_ERR: c_int = 4;
const PAM_BUF_ERR: c_int = 5;
const PAM_PERM_DENIED: c_int = 6;
const PAM_AUTH_ERR: c_int = 7;
const PAM_CRED_INSUFFICIENT: c_int = 8;
const PAM_AUTHINFO_UNAVAIL: c_int = 9;
const PAM_USER_UNKNOWN: c_int = 10;
const PAM_MAXTRIES: c_int = 11;
const PAM_NEW_AUTHTOK_REQD: c_int = 12;
const PAM_ACCT_EXPIRED: c_int = 13;
const PAM_SESSION_ERR: c_int = 14;
const PAM_CRED_EXPIRED: c_int = 15;
const PAM_CRED_UNAVAIL: c_int = 16;
const PAM_CRED_ERR: c_int = 17;
const PAM_NO_MODULE_DATA: c_int = 18;
const PAM_IGNORE: c_int = 25;

/// Send desktop notification via D-Bus (KDE/GNOME compatible)
fn send_notification(title: &str, message: &str) {
    // Try sending notification (non-blocking, best effort)
    let _ = Command::new("bash")
        .arg("-c")
        .arg(format!(
            "dbus-send --session --print-reply \
             --dest=org.freedesktop.Notifications \
             /org/freedesktop/Notifications \
             org.freedesktop.Notifications.Notify \
             string:'linux-hello' uint32:0 string:'face-recognition' \
             string:'{}' string:'{}' array:string: dict:string:variant: int32:5000 2>/dev/null || true",
            title, message
        ))
        .spawn();
}

/// Log to syslog
fn syslog(msg: &str) {
    let _ = Command::new("logger")
        .arg("-t").arg("pam_linux_hello")
        .arg(msg)
        .output();
}

/// Communicate with the Linux Hello daemon via Unix socket
fn authenticate_with_daemon(username: &str) -> Result<String, String> {
    // Wait for daemon socket
    for _ in 0..50 {
        if Path::new(DAEMON_SOCKET).exists() {
            break;
        }
        std::thread::sleep(Duration::from_millis(100));
    }

    if !Path::new(DAEMON_SOCKET).exists() {
        syslog(&format!("Daemon socket not available at {}", DAEMON_SOCKET));
        return Err("Socket not found".to_string());
    }

    // Connect to daemon
    let mut stream = UnixStream::connect(DAEMON_SOCKET)
        .map_err(|e| format!("Failed to connect: {}", e))?;

    stream.set_read_timeout(Some(Duration::from_secs(10)))
        .map_err(|e| format!("Failed to set timeout: {}", e))?;

    // Send auth request
    let request = format!("AUTH:{}", username);
    stream.write_all(request.as_bytes())
        .map_err(|e| format!("Failed to send: {}", e))?;

    // Read response
    let mut response = [0u8; 1024];
    let n = stream.read(&mut response)
        .map_err(|e| format!("Failed to read: {}", e))?;

    let result = String::from_utf8_lossy(&response[..n]).trim().to_string();
    Ok(result)
}

/// Show confirmation dialog via Python helper with notification
fn show_confirmation_dialog(username: &str) -> Result<bool, String> {
    // Send "processing" notification
    send_notification(
        "Linux Hello",
        &format!("Face recognition in progress for '{}'...", username)
    );

    // Create config directory
    fs::create_dir_all(CONFIG_DIR)
        .map_err(|e| format!("Failed to create dir: {}", e))?;

    let pipe_file = format!("{}/{}.fifo", CONFIG_DIR, username);

    // Clean up old pipe
    let _ = fs::remove_file(&pipe_file);

    // Create FIFO
    unsafe {
        let c_path = CString::new(pipe_file.as_str())
            .map_err(|_| "Invalid path".to_string())?;
        if libc::mkfifo(c_path.as_ptr(), 0o600) != 0 {
            return Err("Failed to create FIFO".to_string());
        }
    }

    // Launch helper via systemd-run with display from user session
    let display = std::env::var("DISPLAY").unwrap_or_else(|_| ":0".to_string());
    let output = Command::new("systemd-run")
        .arg("--user")
        .arg("--scope")
        .arg("--quiet")
        .env("DISPLAY", display)
        .arg(format!("linux-hello-pam-confirm --username={} --pipe={}", username, pipe_file))
        .output()
        .map_err(|e| format!("Failed to launch GUI: {}", e))?;

    if !output.status.success() {
        let _ = fs::remove_file(&pipe_file);
        return Err("GUI helper failed".to_string());
    }

    // Read response from FIFO with timeout
    let start = std::time::Instant::now();
    let timeout = Duration::from_secs(30);

    loop {
        if start.elapsed() > timeout {
            let _ = fs::remove_file(&pipe_file);
            send_notification("Linux Hello", "Confirmation timed out - authentication cancelled");
            return Err("Timeout waiting for user".to_string());
        }

        match fs::read_to_string(&pipe_file) {
            Ok(response) => {
                let _ = fs::remove_file(&pipe_file);
                let confirmed = response.trim() == "CONFIRM";
                
                // Send result notification
                if confirmed {
                    send_notification("Linux Hello", "✓ Confirmation accepted");
                } else {
                    send_notification("Linux Hello", "✗ Confirmation cancelled");
                }
                
                return Ok(confirmed);
            }
            Err(_) => {
                std::thread::sleep(Duration::from_millis(100));
            }
        }
    }
}

/// PAM authentication function
#[no_mangle]
pub extern "C" fn pam_sm_authenticate(
    _pamh: *const libc::c_void,
    _flags: c_int,
    argc: c_int,
    argv: *const *const c_char,
) -> c_int {
    // Parse arguments
    let mut required = false;
    let mut show_gui = true;

    unsafe {
        for i in 0..argc as usize {
            if let Ok(arg) = CStr::from_ptr(*argv.add(i)).to_str() {
                match arg {
                    "required" => required = true,
                    "optional" => required = false,
                    "no-gui" => show_gui = false,
                    _ => {}
                }
            }
        }
    }

    // Get username from environment
    let username = std::env::var("USER").unwrap_or_else(|_| "unknown".to_string());

    // Try to authenticate with daemon
    match authenticate_with_daemon(&username) {
        Ok(response) => {
            match response.as_str() {
                "OK" => {
                    // Face recognized
                    if show_gui {
                        match show_confirmation_dialog(&username) {
                            Ok(confirmed) => {
                                if confirmed {
                                    syslog(&format!("Authentication successful for {}", username));
                                    return PAM_SUCCESS;
                                } else {
                                    syslog(&format!("User cancelled for {}", username));
                                    return PAM_AUTH_ERR;
                                }
                            }
                            Err(e) => {
                                syslog(&format!("GUI error for {}: {}, auto-confirming", username, e));
                                return PAM_SUCCESS;
                            }
                        }
                    } else {
                        syslog(&format!("Authentication successful for {} (no GUI)", username));
                        return PAM_SUCCESS;
                    }
                }
                "NO_CAMERA" | "NO_FACE" | "FAIL" => {
                    syslog(&format!("Face recognition failed for {}: {}", username, response));
                    if required {
                        return PAM_AUTH_ERR;
                    } else {
                        return PAM_IGNORE;
                    }
                }
                _ => {
                    syslog(&format!("Daemon error for {}: {}", username, response));
                    if required {
                        return PAM_AUTH_ERR;
                    } else {
                        return PAM_IGNORE;
                    }
                }
            }
        }
        Err(e) => {
            syslog(&format!("Daemon communication error for {}: {}", username, e));
            if required {
                return PAM_AUTH_ERR;
            } else {
                return PAM_IGNORE;
            }
        }
    }
}

#[no_mangle]
pub extern "C" fn pam_sm_setcred(
    _pamh: *const libc::c_void,
    _flags: c_int,
    _argc: c_int,
    _argv: *const *const c_char,
) -> c_int {
    PAM_SUCCESS
}

#[no_mangle]
pub extern "C" fn pam_sm_acct_mgmt(
    _pamh: *const libc::c_void,
    _flags: c_int,
    _argc: c_int,
    _argv: *const *const c_char,
) -> c_int {
    PAM_SUCCESS
}

#[no_mangle]
pub extern "C" fn pam_sm_open_session(
    _pamh: *const libc::c_void,
    _flags: c_int,
    _argc: c_int,
    _argv: *const *const c_char,
) -> c_int {
    PAM_SUCCESS
}

#[no_mangle]
pub extern "C" fn pam_sm_close_session(
    _pamh: *const libc::c_void,
    _flags: c_int,
    _argc: c_int,
    _argv: *const *const c_char,
) -> c_int {
    PAM_SUCCESS
}

#[no_mangle]
pub extern "C" fn pam_sm_chauthtok(
    _pamh: *const libc::c_void,
    _flags: c_int,
    _argc: c_int,
    _argv: *const *const c_char,
) -> c_int {
    PAM_SERVICE_ERR
}
