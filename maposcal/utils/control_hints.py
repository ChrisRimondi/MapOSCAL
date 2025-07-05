"""
Auto‑generated keyword hints mapping code strings to NIST 800‑53 Rev.5 control IDs.

For each control ID listed in `include-controls`, the generator creates:
  * A generic keyword list:       <controlID without dashes/dots>
  * Four language‑specific lists: <var>_python, <var>_golang, <var>_java, <var>_cpp

Each keyword is followed by an inline comment explaining its relationship to the control.

Generated on: 2025-07-04T20:20:27
"""

# --- ORIGINAL SC‑8 GENERIC AND PER‑LANGUAGE LISTS (from sample) ---
sc8 = [
    "ssl",  # Transport encryption primitives imply SC‑8
    "tls",  # Generic reference to TLS maps to SC‑8
    "https",  # HTTPS is TLS‑protected HTTP ==> SC‑8
    "dtls",  # Datagram TLS keyword points to SC‑8 applicability
    "tls.config",  # Go‑style TLS configuration object
    "sslsocket",  # Java/Python SSL socket wrappers trigger SC‑8
    "grpc.ssl_target_name_override",  # gRPC field altering TLS target
    "tm",  # Likely short for 'trust manager' → TLS → SC‑8
    "alg_tcp_aes",  # Example cipher suite reference
    "cipher_suite",  # Generic cipher‑suite configuration hint
    "truststore",  # Java trust‑store indicates TLS / SC‑8
    "keystore",  # Java key‑store ditto
    "ssl_ctx_set_verify",  # C API setting peer‑cert verification
    "tls_server_prefer_cipher_suites",  # Server‑side TLS hardening flag
    "client_min_tls_version",  # Minimum TLS version setting
    "server_max_tls_version",  # Maximum TLS version setting
]

sc8_python = [
    "ssl.create_default_context",  # Python ssl helper enabling TLS → SC‑8
    "http.client.HTTPSConnection",  # Built‑in HTTPS wrapper
    "requests.Session.verify",  # requests TLS verification flag
]

sc8_golang = [
    "tls.Config",  # Go TLS config struct
    "tls.Handshake",  # Initiates TLS handshake
]

sc8_java = [
    "SSLSocketFactory",  # Java TLS socket factory
    "SSLContext.getInstance",  # Create TLS context
]

sc8_cpp = [
    "SSL_CTX_new",  # OpenSSL API creating TLS context
    "SSL_new",  # Instantiate TLS connection
]

# --- AUTO‑GENERATED HINTS FOR INCLUDE-CONTROLS ---

ac10 = [
    "max_sessions",  # Concurrent Session Control – keyword indicative of control ac-10
    "concurrent_session_limit",  # Concurrent Session Control – keyword indicative of control ac-10
    "session_limit",  # Concurrent Session Control – keyword indicative of control ac-10
]

ac10_python = [
    "MAX_SESSIONS",  # Concurrent Session Control – Python keyword maps to control ac-10
    "CONCURRENT_SESSION_LIMIT",  # Concurrent Session Control – Python keyword maps to control ac-10
    "SESSION_LIMIT",  # Concurrent Session Control – Python keyword maps to control ac-10
]

ac10_golang = [
    "MaxSessions",  # Concurrent Session Control – Golang keyword maps to control ac-10
    "ConcurrentSessionLimit",  # Concurrent Session Control – Golang keyword maps to control ac-10
    "SessionLimit",  # Concurrent Session Control – Golang keyword maps to control ac-10
]

ac10_java = [
    "setMaxSessions",  # Concurrent Session Control – Java keyword maps to control ac-10
    "setConcurrentSessionLimit",  # Concurrent Session Control – Java keyword maps to control ac-10
    "setSessionLimit",  # Concurrent Session Control – Java keyword maps to control ac-10
]

ac10_cpp = [
    "max_sessions_config",  # Concurrent Session Control – Cpp keyword maps to control ac-10
    "concurrent_session_limit_config",  # Concurrent Session Control – Cpp keyword maps to control ac-10
    "session_limit_config",  # Concurrent Session Control – Cpp keyword maps to control ac-10
]

ac12 = [
    "logout",  # Session Termination – keyword indicative of control ac-12
    "session_timeout",  # Session Termination – keyword indicative of control ac-12
    "idle_timeout",  # Session Termination – keyword indicative of control ac-12
]

ac12_python = [
    "LOGOUT",  # Session Termination – Python keyword maps to control ac-12
    "SESSION_TIMEOUT",  # Session Termination – Python keyword maps to control ac-12
    "IDLE_TIMEOUT",  # Session Termination – Python keyword maps to control ac-12
]

ac12_golang = [
    "Logout",  # Session Termination – Golang keyword maps to control ac-12
    "SessionTimeout",  # Session Termination – Golang keyword maps to control ac-12
    "IdleTimeout",  # Session Termination – Golang keyword maps to control ac-12
]

ac12_java = [
    "setLogout",  # Session Termination – Java keyword maps to control ac-12
    "setSessionTimeout",  # Session Termination – Java keyword maps to control ac-12
    "setIdleTimeout",  # Session Termination – Java keyword maps to control ac-12
]

ac12_cpp = [
    "logout_config",  # Session Termination – Cpp keyword maps to control ac-12
    "session_timeout_config",  # Session Termination – Cpp keyword maps to control ac-12
    "idle_timeout_config",  # Session Termination – Cpp keyword maps to control ac-12
]

ac12_1 = [
    "logout",  # Session Termination – keyword indicative of control ac-12.1
    "session_timeout",  # Session Termination – keyword indicative of control ac-12.1
    "idle_timeout",  # Session Termination – keyword indicative of control ac-12.1
]

ac12_1_python = [
    "LOGOUT",  # Session Termination – Python keyword maps to control ac-12.1
    "SESSION_TIMEOUT",  # Session Termination – Python keyword maps to control ac-12.1
    "IDLE_TIMEOUT",  # Session Termination – Python keyword maps to control ac-12.1
]

ac12_1_golang = [
    "Logout",  # Session Termination – Golang keyword maps to control ac-12.1
    "SessionTimeout",  # Session Termination – Golang keyword maps to control ac-12.1
    "IdleTimeout",  # Session Termination – Golang keyword maps to control ac-12.1
]

ac12_1_java = [
    "setLogout",  # Session Termination – Java keyword maps to control ac-12.1
    "setSessionTimeout",  # Session Termination – Java keyword maps to control ac-12.1
    "setIdleTimeout",  # Session Termination – Java keyword maps to control ac-12.1
]

ac12_1_cpp = [
    "logout_config",  # Session Termination – Cpp keyword maps to control ac-12.1
    "session_timeout_config",  # Session Termination – Cpp keyword maps to control ac-12.1
    "idle_timeout_config",  # Session Termination – Cpp keyword maps to control ac-12.1
]

ac12_2 = [
    "logout",  # Session Termination – keyword indicative of control ac-12.2
    "session_timeout",  # Session Termination – keyword indicative of control ac-12.2
    "idle_timeout",  # Session Termination – keyword indicative of control ac-12.2
]

ac12_2_python = [
    "LOGOUT",  # Session Termination – Python keyword maps to control ac-12.2
    "SESSION_TIMEOUT",  # Session Termination – Python keyword maps to control ac-12.2
    "IDLE_TIMEOUT",  # Session Termination – Python keyword maps to control ac-12.2
]

ac12_2_golang = [
    "Logout",  # Session Termination – Golang keyword maps to control ac-12.2
    "SessionTimeout",  # Session Termination – Golang keyword maps to control ac-12.2
    "IdleTimeout",  # Session Termination – Golang keyword maps to control ac-12.2
]

ac12_2_java = [
    "setLogout",  # Session Termination – Java keyword maps to control ac-12.2
    "setSessionTimeout",  # Session Termination – Java keyword maps to control ac-12.2
    "setIdleTimeout",  # Session Termination – Java keyword maps to control ac-12.2
]

ac12_2_cpp = [
    "logout_config",  # Session Termination – Cpp keyword maps to control ac-12.2
    "session_timeout_config",  # Session Termination – Cpp keyword maps to control ac-12.2
    "idle_timeout_config",  # Session Termination – Cpp keyword maps to control ac-12.2
]

ac17_2 = [
    "ssh",  # Remote Access – keyword indicative of control ac-17.2
    "vpn",  # Remote Access – keyword indicative of control ac-17.2
    "remote_desktop",  # Remote Access – keyword indicative of control ac-17.2
]

ac17_2_python = [
    "SSH",  # Remote Access – Python keyword maps to control ac-17.2
    "VPN",  # Remote Access – Python keyword maps to control ac-17.2
    "REMOTE_DESKTOP",  # Remote Access – Python keyword maps to control ac-17.2
]

ac17_2_golang = [
    "Ssh",  # Remote Access – Golang keyword maps to control ac-17.2
    "Vpn",  # Remote Access – Golang keyword maps to control ac-17.2
    "RemoteDesktop",  # Remote Access – Golang keyword maps to control ac-17.2
]

ac17_2_java = [
    "setSsh",  # Remote Access – Java keyword maps to control ac-17.2
    "setVpn",  # Remote Access – Java keyword maps to control ac-17.2
    "setRemoteDesktop",  # Remote Access – Java keyword maps to control ac-17.2
]

ac17_2_cpp = [
    "ssh_config",  # Remote Access – Cpp keyword maps to control ac-17.2
    "vpn_config",  # Remote Access – Cpp keyword maps to control ac-17.2
    "remote_desktop_config",  # Remote Access – Cpp keyword maps to control ac-17.2
]

ac2_10 = [
    "adduser",  # Account Management – keyword indicative of control ac-2.10
    "delete_user",  # Account Management – keyword indicative of control ac-2.10
    "disable_account",  # Account Management – keyword indicative of control ac-2.10
]

ac2_10_python = [
    "ADDUSER",  # Account Management – Python keyword maps to control ac-2.10
    "DELETE_USER",  # Account Management – Python keyword maps to control ac-2.10
    "DISABLE_ACCOUNT",  # Account Management – Python keyword maps to control ac-2.10
]

ac2_10_golang = [
    "Adduser",  # Account Management – Golang keyword maps to control ac-2.10
    "DeleteUser",  # Account Management – Golang keyword maps to control ac-2.10
    "DisableAccount",  # Account Management – Golang keyword maps to control ac-2.10
]

ac2_10_java = [
    "setAdduser",  # Account Management – Java keyword maps to control ac-2.10
    "setDeleteUser",  # Account Management – Java keyword maps to control ac-2.10
    "setDisableAccount",  # Account Management – Java keyword maps to control ac-2.10
]

ac2_10_cpp = [
    "adduser_config",  # Account Management – Cpp keyword maps to control ac-2.10
    "delete_user_config",  # Account Management – Cpp keyword maps to control ac-2.10
    "disable_account_config",  # Account Management – Cpp keyword maps to control ac-2.10
]

ac2_2 = [
    "adduser",  # Account Management – keyword indicative of control ac-2.2
    "delete_user",  # Account Management – keyword indicative of control ac-2.2
    "disable_account",  # Account Management – keyword indicative of control ac-2.2
]

ac2_2_python = [
    "ADDUSER",  # Account Management – Python keyword maps to control ac-2.2
    "DELETE_USER",  # Account Management – Python keyword maps to control ac-2.2
    "DISABLE_ACCOUNT",  # Account Management – Python keyword maps to control ac-2.2
]

ac2_2_golang = [
    "Adduser",  # Account Management – Golang keyword maps to control ac-2.2
    "DeleteUser",  # Account Management – Golang keyword maps to control ac-2.2
    "DisableAccount",  # Account Management – Golang keyword maps to control ac-2.2
]

ac2_2_java = [
    "setAdduser",  # Account Management – Java keyword maps to control ac-2.2
    "setDeleteUser",  # Account Management – Java keyword maps to control ac-2.2
    "setDisableAccount",  # Account Management – Java keyword maps to control ac-2.2
]

ac2_2_cpp = [
    "adduser_config",  # Account Management – Cpp keyword maps to control ac-2.2
    "delete_user_config",  # Account Management – Cpp keyword maps to control ac-2.2
    "disable_account_config",  # Account Management – Cpp keyword maps to control ac-2.2
]

ac2_3 = [
    "adduser",  # Account Management – keyword indicative of control ac-2.3
    "delete_user",  # Account Management – keyword indicative of control ac-2.3
    "disable_account",  # Account Management – keyword indicative of control ac-2.3
]

ac2_3_python = [
    "ADDUSER",  # Account Management – Python keyword maps to control ac-2.3
    "DELETE_USER",  # Account Management – Python keyword maps to control ac-2.3
    "DISABLE_ACCOUNT",  # Account Management – Python keyword maps to control ac-2.3
]

ac2_3_golang = [
    "Adduser",  # Account Management – Golang keyword maps to control ac-2.3
    "DeleteUser",  # Account Management – Golang keyword maps to control ac-2.3
    "DisableAccount",  # Account Management – Golang keyword maps to control ac-2.3
]

ac2_3_java = [
    "setAdduser",  # Account Management – Java keyword maps to control ac-2.3
    "setDeleteUser",  # Account Management – Java keyword maps to control ac-2.3
    "setDisableAccount",  # Account Management – Java keyword maps to control ac-2.3
]

ac2_3_cpp = [
    "adduser_config",  # Account Management – Cpp keyword maps to control ac-2.3
    "delete_user_config",  # Account Management – Cpp keyword maps to control ac-2.3
    "disable_account_config",  # Account Management – Cpp keyword maps to control ac-2.3
]

ac2_3_a = [
    "adduser",  # Account Management – keyword indicative of control ac-2.3.a
    "delete_user",  # Account Management – keyword indicative of control ac-2.3.a
    "disable_account",  # Account Management – keyword indicative of control ac-2.3.a
]

ac2_3_a_python = [
    "ADDUSER",  # Account Management – Python keyword maps to control ac-2.3.a
    "DELETE_USER",  # Account Management – Python keyword maps to control ac-2.3.a
    "DISABLE_ACCOUNT",  # Account Management – Python keyword maps to control ac-2.3.a
]

ac2_3_a_golang = [
    "Adduser",  # Account Management – Golang keyword maps to control ac-2.3.a
    "DeleteUser",  # Account Management – Golang keyword maps to control ac-2.3.a
    "DisableAccount",  # Account Management – Golang keyword maps to control ac-2.3.a
]

ac2_3_a_java = [
    "setAdduser",  # Account Management – Java keyword maps to control ac-2.3.a
    "setDeleteUser",  # Account Management – Java keyword maps to control ac-2.3.a
    "setDisableAccount",  # Account Management – Java keyword maps to control ac-2.3.a
]

ac2_3_a_cpp = [
    "adduser_config",  # Account Management – Cpp keyword maps to control ac-2.3.a
    "delete_user_config",  # Account Management – Cpp keyword maps to control ac-2.3.a
    "disable_account_config",  # Account Management – Cpp keyword maps to control ac-2.3.a
]

ac2_3_d = [
    "adduser",  # Account Management – keyword indicative of control ac-2.3.d
    "delete_user",  # Account Management – keyword indicative of control ac-2.3.d
    "disable_account",  # Account Management – keyword indicative of control ac-2.3.d
]

ac2_3_d_python = [
    "ADDUSER",  # Account Management – Python keyword maps to control ac-2.3.d
    "DELETE_USER",  # Account Management – Python keyword maps to control ac-2.3.d
    "DISABLE_ACCOUNT",  # Account Management – Python keyword maps to control ac-2.3.d
]

ac2_3_d_golang = [
    "Adduser",  # Account Management – Golang keyword maps to control ac-2.3.d
    "DeleteUser",  # Account Management – Golang keyword maps to control ac-2.3.d
    "DisableAccount",  # Account Management – Golang keyword maps to control ac-2.3.d
]

ac2_3_d_java = [
    "setAdduser",  # Account Management – Java keyword maps to control ac-2.3.d
    "setDeleteUser",  # Account Management – Java keyword maps to control ac-2.3.d
    "setDisableAccount",  # Account Management – Java keyword maps to control ac-2.3.d
]

ac2_3_d_cpp = [
    "adduser_config",  # Account Management – Cpp keyword maps to control ac-2.3.d
    "delete_user_config",  # Account Management – Cpp keyword maps to control ac-2.3.d
    "disable_account_config",  # Account Management – Cpp keyword maps to control ac-2.3.d
]

ac2_4 = [
    "adduser",  # Account Management – keyword indicative of control ac-2.4
    "delete_user",  # Account Management – keyword indicative of control ac-2.4
    "disable_account",  # Account Management – keyword indicative of control ac-2.4
]

ac2_4_python = [
    "ADDUSER",  # Account Management – Python keyword maps to control ac-2.4
    "DELETE_USER",  # Account Management – Python keyword maps to control ac-2.4
    "DISABLE_ACCOUNT",  # Account Management – Python keyword maps to control ac-2.4
]

ac2_4_golang = [
    "Adduser",  # Account Management – Golang keyword maps to control ac-2.4
    "DeleteUser",  # Account Management – Golang keyword maps to control ac-2.4
    "DisableAccount",  # Account Management – Golang keyword maps to control ac-2.4
]

ac2_4_java = [
    "setAdduser",  # Account Management – Java keyword maps to control ac-2.4
    "setDeleteUser",  # Account Management – Java keyword maps to control ac-2.4
    "setDisableAccount",  # Account Management – Java keyword maps to control ac-2.4
]

ac2_4_cpp = [
    "adduser_config",  # Account Management – Cpp keyword maps to control ac-2.4
    "delete_user_config",  # Account Management – Cpp keyword maps to control ac-2.4
    "disable_account_config",  # Account Management – Cpp keyword maps to control ac-2.4
]

ac3 = [
    "rbac",  # Access Enforcement – keyword indicative of control ac-3
    "access_policy",  # Access Enforcement – keyword indicative of control ac-3
    "permission_check",  # Access Enforcement – keyword indicative of control ac-3
]

ac3_python = [
    "RBAC",  # Access Enforcement – Python keyword maps to control ac-3
    "ACCESS_POLICY",  # Access Enforcement – Python keyword maps to control ac-3
    "PERMISSION_CHECK",  # Access Enforcement – Python keyword maps to control ac-3
]

ac3_golang = [
    "Rbac",  # Access Enforcement – Golang keyword maps to control ac-3
    "AccessPolicy",  # Access Enforcement – Golang keyword maps to control ac-3
    "PermissionCheck",  # Access Enforcement – Golang keyword maps to control ac-3
]

ac3_java = [
    "setRbac",  # Access Enforcement – Java keyword maps to control ac-3
    "setAccessPolicy",  # Access Enforcement – Java keyword maps to control ac-3
    "setPermissionCheck",  # Access Enforcement – Java keyword maps to control ac-3
]

ac3_cpp = [
    "rbac_config",  # Access Enforcement – Cpp keyword maps to control ac-3
    "access_policy_config",  # Access Enforcement – Cpp keyword maps to control ac-3
    "permission_check_config",  # Access Enforcement – Cpp keyword maps to control ac-3
]

ac3_4 = [
    "rbac",  # Access Enforcement – keyword indicative of control ac-3.4
    "access_policy",  # Access Enforcement – keyword indicative of control ac-3.4
    "permission_check",  # Access Enforcement – keyword indicative of control ac-3.4
]

ac3_4_python = [
    "RBAC",  # Access Enforcement – Python keyword maps to control ac-3.4
    "ACCESS_POLICY",  # Access Enforcement – Python keyword maps to control ac-3.4
    "PERMISSION_CHECK",  # Access Enforcement – Python keyword maps to control ac-3.4
]

ac3_4_golang = [
    "Rbac",  # Access Enforcement – Golang keyword maps to control ac-3.4
    "AccessPolicy",  # Access Enforcement – Golang keyword maps to control ac-3.4
    "PermissionCheck",  # Access Enforcement – Golang keyword maps to control ac-3.4
]

ac3_4_java = [
    "setRbac",  # Access Enforcement – Java keyword maps to control ac-3.4
    "setAccessPolicy",  # Access Enforcement – Java keyword maps to control ac-3.4
    "setPermissionCheck",  # Access Enforcement – Java keyword maps to control ac-3.4
]

ac3_4_cpp = [
    "rbac_config",  # Access Enforcement – Cpp keyword maps to control ac-3.4
    "access_policy_config",  # Access Enforcement – Cpp keyword maps to control ac-3.4
    "permission_check_config",  # Access Enforcement – Cpp keyword maps to control ac-3.4
]

ac4 = [
    "data_label",  # Information Flow Enforcement – keyword indicative of control ac-4
    "security_tag",  # Information Flow Enforcement – keyword indicative of control ac-4
    "flow_control",  # Information Flow Enforcement – keyword indicative of control ac-4
]

ac4_python = [
    "DATA_LABEL",  # Information Flow Enforcement – Python keyword maps to control ac-4
    "SECURITY_TAG",  # Information Flow Enforcement – Python keyword maps to control ac-4
    "FLOW_CONTROL",  # Information Flow Enforcement – Python keyword maps to control ac-4
]

ac4_golang = [
    "DataLabel",  # Information Flow Enforcement – Golang keyword maps to control ac-4
    "SecurityTag",  # Information Flow Enforcement – Golang keyword maps to control ac-4
    "FlowControl",  # Information Flow Enforcement – Golang keyword maps to control ac-4
]

ac4_java = [
    "setDataLabel",  # Information Flow Enforcement – Java keyword maps to control ac-4
    "setSecurityTag",  # Information Flow Enforcement – Java keyword maps to control ac-4
    "setFlowControl",  # Information Flow Enforcement – Java keyword maps to control ac-4
]

ac4_cpp = [
    "data_label_config",  # Information Flow Enforcement – Cpp keyword maps to control ac-4
    "security_tag_config",  # Information Flow Enforcement – Cpp keyword maps to control ac-4
    "flow_control_config",  # Information Flow Enforcement – Cpp keyword maps to control ac-4
]

ac6_10 = [
    "sudo",  # Least Privilege – keyword indicative of control ac-6.10
    "setuid",  # Least Privilege – keyword indicative of control ac-6.10
    "least_privilege",  # Least Privilege – keyword indicative of control ac-6.10
]

ac6_10_python = [
    "SUDO",  # Least Privilege – Python keyword maps to control ac-6.10
    "SETUID",  # Least Privilege – Python keyword maps to control ac-6.10
    "LEAST_PRIVILEGE",  # Least Privilege – Python keyword maps to control ac-6.10
]

ac6_10_golang = [
    "Sudo",  # Least Privilege – Golang keyword maps to control ac-6.10
    "Setuid",  # Least Privilege – Golang keyword maps to control ac-6.10
    "LeastPrivilege",  # Least Privilege – Golang keyword maps to control ac-6.10
]

ac6_10_java = [
    "setSudo",  # Least Privilege – Java keyword maps to control ac-6.10
    "setSetuid",  # Least Privilege – Java keyword maps to control ac-6.10
    "setLeastPrivilege",  # Least Privilege – Java keyword maps to control ac-6.10
]

ac6_10_cpp = [
    "sudo_config",  # Least Privilege – Cpp keyword maps to control ac-6.10
    "setuid_config",  # Least Privilege – Cpp keyword maps to control ac-6.10
    "least_privilege_config",  # Least Privilege – Cpp keyword maps to control ac-6.10
]

ac6_8 = [
    "sudo",  # Least Privilege – keyword indicative of control ac-6.8
    "setuid",  # Least Privilege – keyword indicative of control ac-6.8
    "least_privilege",  # Least Privilege – keyword indicative of control ac-6.8
]

ac6_8_python = [
    "SUDO",  # Least Privilege – Python keyword maps to control ac-6.8
    "SETUID",  # Least Privilege – Python keyword maps to control ac-6.8
    "LEAST_PRIVILEGE",  # Least Privilege – Python keyword maps to control ac-6.8
]

ac6_8_golang = [
    "Sudo",  # Least Privilege – Golang keyword maps to control ac-6.8
    "Setuid",  # Least Privilege – Golang keyword maps to control ac-6.8
    "LeastPrivilege",  # Least Privilege – Golang keyword maps to control ac-6.8
]

ac6_8_java = [
    "setSudo",  # Least Privilege – Java keyword maps to control ac-6.8
    "setSetuid",  # Least Privilege – Java keyword maps to control ac-6.8
    "setLeastPrivilege",  # Least Privilege – Java keyword maps to control ac-6.8
]

ac6_8_cpp = [
    "sudo_config",  # Least Privilege – Cpp keyword maps to control ac-6.8
    "setuid_config",  # Least Privilege – Cpp keyword maps to control ac-6.8
    "least_privilege_config",  # Least Privilege – Cpp keyword maps to control ac-6.8
]

ac6_9 = [
    "sudo",  # Least Privilege – keyword indicative of control ac-6.9
    "setuid",  # Least Privilege – keyword indicative of control ac-6.9
    "least_privilege",  # Least Privilege – keyword indicative of control ac-6.9
]

ac6_9_python = [
    "SUDO",  # Least Privilege – Python keyword maps to control ac-6.9
    "SETUID",  # Least Privilege – Python keyword maps to control ac-6.9
    "LEAST_PRIVILEGE",  # Least Privilege – Python keyword maps to control ac-6.9
]

ac6_9_golang = [
    "Sudo",  # Least Privilege – Golang keyword maps to control ac-6.9
    "Setuid",  # Least Privilege – Golang keyword maps to control ac-6.9
    "LeastPrivilege",  # Least Privilege – Golang keyword maps to control ac-6.9
]

ac6_9_java = [
    "setSudo",  # Least Privilege – Java keyword maps to control ac-6.9
    "setSetuid",  # Least Privilege – Java keyword maps to control ac-6.9
    "setLeastPrivilege",  # Least Privilege – Java keyword maps to control ac-6.9
]

ac6_9_cpp = [
    "sudo_config",  # Least Privilege – Cpp keyword maps to control ac-6.9
    "setuid_config",  # Least Privilege – Cpp keyword maps to control ac-6.9
    "least_privilege_config",  # Least Privilege – Cpp keyword maps to control ac-6.9
]

ac7a = [
    "login_attempts",  # Unsuccessful Logon Attempts – keyword indicative of control ac-7a
    "lockout_threshold",  # Unsuccessful Logon Attempts – keyword indicative of control ac-7a
    "account_lockout",  # Unsuccessful Logon Attempts – keyword indicative of control ac-7a
]

ac7a_python = [
    "LOGIN_ATTEMPTS",  # Unsuccessful Logon Attempts – Python keyword maps to control ac-7a
    "LOCKOUT_THRESHOLD",  # Unsuccessful Logon Attempts – Python keyword maps to control ac-7a
    "ACCOUNT_LOCKOUT",  # Unsuccessful Logon Attempts – Python keyword maps to control ac-7a
]

ac7a_golang = [
    "LoginAttempts",  # Unsuccessful Logon Attempts – Golang keyword maps to control ac-7a
    "LockoutThreshold",  # Unsuccessful Logon Attempts – Golang keyword maps to control ac-7a
    "AccountLockout",  # Unsuccessful Logon Attempts – Golang keyword maps to control ac-7a
]

ac7a_java = [
    "setLoginAttempts",  # Unsuccessful Logon Attempts – Java keyword maps to control ac-7a
    "setLockoutThreshold",  # Unsuccessful Logon Attempts – Java keyword maps to control ac-7a
    "setAccountLockout",  # Unsuccessful Logon Attempts – Java keyword maps to control ac-7a
]

ac7a_cpp = [
    "login_attempts_config",  # Unsuccessful Logon Attempts – Cpp keyword maps to control ac-7a
    "lockout_threshold_config",  # Unsuccessful Logon Attempts – Cpp keyword maps to control ac-7a
    "account_lockout_config",  # Unsuccessful Logon Attempts – Cpp keyword maps to control ac-7a
]

ac7b = [
    "login_attempts",  # Unsuccessful Logon Attempts – keyword indicative of control ac-7b
    "lockout_threshold",  # Unsuccessful Logon Attempts – keyword indicative of control ac-7b
    "account_lockout",  # Unsuccessful Logon Attempts – keyword indicative of control ac-7b
]

ac7b_python = [
    "LOGIN_ATTEMPTS",  # Unsuccessful Logon Attempts – Python keyword maps to control ac-7b
    "LOCKOUT_THRESHOLD",  # Unsuccessful Logon Attempts – Python keyword maps to control ac-7b
    "ACCOUNT_LOCKOUT",  # Unsuccessful Logon Attempts – Python keyword maps to control ac-7b
]

ac7b_golang = [
    "LoginAttempts",  # Unsuccessful Logon Attempts – Golang keyword maps to control ac-7b
    "LockoutThreshold",  # Unsuccessful Logon Attempts – Golang keyword maps to control ac-7b
    "AccountLockout",  # Unsuccessful Logon Attempts – Golang keyword maps to control ac-7b
]

ac7b_java = [
    "setLoginAttempts",  # Unsuccessful Logon Attempts – Java keyword maps to control ac-7b
    "setLockoutThreshold",  # Unsuccessful Logon Attempts – Java keyword maps to control ac-7b
    "setAccountLockout",  # Unsuccessful Logon Attempts – Java keyword maps to control ac-7b
]

ac7b_cpp = [
    "login_attempts_config",  # Unsuccessful Logon Attempts – Cpp keyword maps to control ac-7b
    "lockout_threshold_config",  # Unsuccessful Logon Attempts – Cpp keyword maps to control ac-7b
    "account_lockout_config",  # Unsuccessful Logon Attempts – Cpp keyword maps to control ac-7b
]

ac9 = [
    "last_login",  # Previous Logon Notification – keyword indicative of control ac-9
    "display_last_login",  # Previous Logon Notification – keyword indicative of control ac-9
    "previous_login_notice",  # Previous Logon Notification – keyword indicative of control ac-9
]

ac9_python = [
    "LAST_LOGIN",  # Previous Logon Notification – Python keyword maps to control ac-9
    "DISPLAY_LAST_LOGIN",  # Previous Logon Notification – Python keyword maps to control ac-9
    "PREVIOUS_LOGIN_NOTICE",  # Previous Logon Notification – Python keyword maps to control ac-9
]

ac9_golang = [
    "LastLogin",  # Previous Logon Notification – Golang keyword maps to control ac-9
    "DisplayLastLogin",  # Previous Logon Notification – Golang keyword maps to control ac-9
    "PreviousLoginNotice",  # Previous Logon Notification – Golang keyword maps to control ac-9
]

ac9_java = [
    "setLastLogin",  # Previous Logon Notification – Java keyword maps to control ac-9
    "setDisplayLastLogin",  # Previous Logon Notification – Java keyword maps to control ac-9
    "setPreviousLoginNotice",  # Previous Logon Notification – Java keyword maps to control ac-9
]

ac9_cpp = [
    "last_login_config",  # Previous Logon Notification – Cpp keyword maps to control ac-9
    "display_last_login_config",  # Previous Logon Notification – Cpp keyword maps to control ac-9
    "previous_login_notice_config",  # Previous Logon Notification – Cpp keyword maps to control ac-9
]

au10 = [
    "signed_logs",  # Non-repudiation – keyword indicative of control au-10
    "log_signature",  # Non-repudiation – keyword indicative of control au-10
    "non_repudiation_log",  # Non-repudiation – keyword indicative of control au-10
]

au10_python = [
    "SIGNED_LOGS",  # Non-repudiation – Python keyword maps to control au-10
    "LOG_SIGNATURE",  # Non-repudiation – Python keyword maps to control au-10
    "NON_REPUDIATION_LOG",  # Non-repudiation – Python keyword maps to control au-10
]

au10_golang = [
    "SignedLogs",  # Non-repudiation – Golang keyword maps to control au-10
    "LogSignature",  # Non-repudiation – Golang keyword maps to control au-10
    "NonRepudiationLog",  # Non-repudiation – Golang keyword maps to control au-10
]

au10_java = [
    "setSignedLogs",  # Non-repudiation – Java keyword maps to control au-10
    "setLogSignature",  # Non-repudiation – Java keyword maps to control au-10
    "setNonRepudiationLog",  # Non-repudiation – Java keyword maps to control au-10
]

au10_cpp = [
    "signed_logs_config",  # Non-repudiation – Cpp keyword maps to control au-10
    "log_signature_config",  # Non-repudiation – Cpp keyword maps to control au-10
    "non_repudiation_log_config",  # Non-repudiation – Cpp keyword maps to control au-10
]

au12_1 = [
    "enable_audit",  # Audit Log Generation – keyword indicative of control au-12.1
    "audit_log",  # Audit Log Generation – keyword indicative of control au-12.1
    "audit_trace",  # Audit Log Generation – keyword indicative of control au-12.1
]

au12_1_python = [
    "ENABLE_AUDIT",  # Audit Log Generation – Python keyword maps to control au-12.1
    "AUDIT_LOG",  # Audit Log Generation – Python keyword maps to control au-12.1
    "AUDIT_TRACE",  # Audit Log Generation – Python keyword maps to control au-12.1
]

au12_1_golang = [
    "EnableAudit",  # Audit Log Generation – Golang keyword maps to control au-12.1
    "AuditLog",  # Audit Log Generation – Golang keyword maps to control au-12.1
    "AuditTrace",  # Audit Log Generation – Golang keyword maps to control au-12.1
]

au12_1_java = [
    "setEnableAudit",  # Audit Log Generation – Java keyword maps to control au-12.1
    "setAuditLog",  # Audit Log Generation – Java keyword maps to control au-12.1
    "setAuditTrace",  # Audit Log Generation – Java keyword maps to control au-12.1
]

au12_1_cpp = [
    "enable_audit_config",  # Audit Log Generation – Cpp keyword maps to control au-12.1
    "audit_log_config",  # Audit Log Generation – Cpp keyword maps to control au-12.1
    "audit_trace_config",  # Audit Log Generation – Cpp keyword maps to control au-12.1
]

au12a = [
    "enable_audit",  # Audit Log Generation – keyword indicative of control au-12a
    "audit_log",  # Audit Log Generation – keyword indicative of control au-12a
    "audit_trace",  # Audit Log Generation – keyword indicative of control au-12a
]

au12a_python = [
    "ENABLE_AUDIT",  # Audit Log Generation – Python keyword maps to control au-12a
    "AUDIT_LOG",  # Audit Log Generation – Python keyword maps to control au-12a
    "AUDIT_TRACE",  # Audit Log Generation – Python keyword maps to control au-12a
]

au12a_golang = [
    "EnableAudit",  # Audit Log Generation – Golang keyword maps to control au-12a
    "AuditLog",  # Audit Log Generation – Golang keyword maps to control au-12a
    "AuditTrace",  # Audit Log Generation – Golang keyword maps to control au-12a
]

au12a_java = [
    "setEnableAudit",  # Audit Log Generation – Java keyword maps to control au-12a
    "setAuditLog",  # Audit Log Generation – Java keyword maps to control au-12a
    "setAuditTrace",  # Audit Log Generation – Java keyword maps to control au-12a
]

au12a_cpp = [
    "enable_audit_config",  # Audit Log Generation – Cpp keyword maps to control au-12a
    "audit_log_config",  # Audit Log Generation – Cpp keyword maps to control au-12a
    "audit_trace_config",  # Audit Log Generation – Cpp keyword maps to control au-12a
]

au12c = [
    "enable_audit",  # Audit Log Generation – keyword indicative of control au-12c
    "audit_log",  # Audit Log Generation – keyword indicative of control au-12c
    "audit_trace",  # Audit Log Generation – keyword indicative of control au-12c
]

au12c_python = [
    "ENABLE_AUDIT",  # Audit Log Generation – Python keyword maps to control au-12c
    "AUDIT_LOG",  # Audit Log Generation – Python keyword maps to control au-12c
    "AUDIT_TRACE",  # Audit Log Generation – Python keyword maps to control au-12c
]

au12c_golang = [
    "EnableAudit",  # Audit Log Generation – Golang keyword maps to control au-12c
    "AuditLog",  # Audit Log Generation – Golang keyword maps to control au-12c
    "AuditTrace",  # Audit Log Generation – Golang keyword maps to control au-12c
]

au12c_java = [
    "setEnableAudit",  # Audit Log Generation – Java keyword maps to control au-12c
    "setAuditLog",  # Audit Log Generation – Java keyword maps to control au-12c
    "setAuditTrace",  # Audit Log Generation – Java keyword maps to control au-12c
]

au12c_cpp = [
    "enable_audit_config",  # Audit Log Generation – Cpp keyword maps to control au-12c
    "audit_log_config",  # Audit Log Generation – Cpp keyword maps to control au-12c
    "audit_trace_config",  # Audit Log Generation – Cpp keyword maps to control au-12c
]

au14_1 = [
    "syslog_forward",  # Audit Log Export – keyword indicative of control au-14.1
    "audit_export",  # Audit Log Export – keyword indicative of control au-14.1
    "log_shipping",  # Audit Log Export – keyword indicative of control au-14.1
]

au14_1_python = [
    "SYSLOG_FORWARD",  # Audit Log Export – Python keyword maps to control au-14.1
    "AUDIT_EXPORT",  # Audit Log Export – Python keyword maps to control au-14.1
    "LOG_SHIPPING",  # Audit Log Export – Python keyword maps to control au-14.1
]

au14_1_golang = [
    "SyslogForward",  # Audit Log Export – Golang keyword maps to control au-14.1
    "AuditExport",  # Audit Log Export – Golang keyword maps to control au-14.1
    "LogShipping",  # Audit Log Export – Golang keyword maps to control au-14.1
]

au14_1_java = [
    "setSyslogForward",  # Audit Log Export – Java keyword maps to control au-14.1
    "setAuditExport",  # Audit Log Export – Java keyword maps to control au-14.1
    "setLogShipping",  # Audit Log Export – Java keyword maps to control au-14.1
]

au14_1_cpp = [
    "syslog_forward_config",  # Audit Log Export – Cpp keyword maps to control au-14.1
    "audit_export_config",  # Audit Log Export – Cpp keyword maps to control au-14.1
    "log_shipping_config",  # Audit Log Export – Cpp keyword maps to control au-14.1
]

au3 = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3
    "event_content",  # Content of Audit Records – keyword indicative of control au-3
]

au3_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3
]

au3_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3
]

au3_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3
]

au3_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3
]

au3_1 = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3.1
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3.1
    "event_content",  # Content of Audit Records – keyword indicative of control au-3.1
]

au3_1_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3.1
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3.1
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3.1
]

au3_1_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3.1
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3.1
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3.1
]

au3_1_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3.1
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3.1
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3.1
]

au3_1_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3.1
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3.1
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3.1
]

au3a = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3a
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3a
    "event_content",  # Content of Audit Records – keyword indicative of control au-3a
]

au3a_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3a
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3a
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3a
]

au3a_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3a
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3a
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3a
]

au3a_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3a
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3a
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3a
]

au3a_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3a
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3a
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3a
]

au3b = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3b
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3b
    "event_content",  # Content of Audit Records – keyword indicative of control au-3b
]

au3b_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3b
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3b
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3b
]

au3b_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3b
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3b
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3b
]

au3b_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3b
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3b
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3b
]

au3b_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3b
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3b
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3b
]

au3c = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3c
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3c
    "event_content",  # Content of Audit Records – keyword indicative of control au-3c
]

au3c_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3c
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3c
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3c
]

au3c_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3c
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3c
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3c
]

au3c_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3c
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3c
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3c
]

au3c_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3c
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3c
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3c
]

au3d = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3d
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3d
    "event_content",  # Content of Audit Records – keyword indicative of control au-3d
]

au3d_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3d
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3d
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3d
]

au3d_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3d
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3d
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3d
]

au3d_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3d
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3d
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3d
]

au3d_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3d
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3d
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3d
]

au3e = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3e
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3e
    "event_content",  # Content of Audit Records – keyword indicative of control au-3e
]

au3e_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3e
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3e
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3e
]

au3e_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3e
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3e
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3e
]

au3e_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3e
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3e
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3e
]

au3e_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3e
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3e
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3e
]

au3f = [
    "audit_event",  # Content of Audit Records – keyword indicative of control au-3f
    "log_detail",  # Content of Audit Records – keyword indicative of control au-3f
    "event_content",  # Content of Audit Records – keyword indicative of control au-3f
]

au3f_python = [
    "AUDIT_EVENT",  # Content of Audit Records – Python keyword maps to control au-3f
    "LOG_DETAIL",  # Content of Audit Records – Python keyword maps to control au-3f
    "EVENT_CONTENT",  # Content of Audit Records – Python keyword maps to control au-3f
]

au3f_golang = [
    "AuditEvent",  # Content of Audit Records – Golang keyword maps to control au-3f
    "LogDetail",  # Content of Audit Records – Golang keyword maps to control au-3f
    "EventContent",  # Content of Audit Records – Golang keyword maps to control au-3f
]

au3f_java = [
    "setAuditEvent",  # Content of Audit Records – Java keyword maps to control au-3f
    "setLogDetail",  # Content of Audit Records – Java keyword maps to control au-3f
    "setEventContent",  # Content of Audit Records – Java keyword maps to control au-3f
]

au3f_cpp = [
    "audit_event_config",  # Content of Audit Records – Cpp keyword maps to control au-3f
    "log_detail_config",  # Content of Audit Records – Cpp keyword maps to control au-3f
    "event_content_config",  # Content of Audit Records – Cpp keyword maps to control au-3f
]

au4_1 = [
    "logrotate",  # Audit Storage Capacity – keyword indicative of control au-4.1
    "audit_capacity",  # Audit Storage Capacity – keyword indicative of control au-4.1
    "log_disk_quota",  # Audit Storage Capacity – keyword indicative of control au-4.1
]

au4_1_python = [
    "LOGROTATE",  # Audit Storage Capacity – Python keyword maps to control au-4.1
    "AUDIT_CAPACITY",  # Audit Storage Capacity – Python keyword maps to control au-4.1
    "LOG_DISK_QUOTA",  # Audit Storage Capacity – Python keyword maps to control au-4.1
]

au4_1_golang = [
    "Logrotate",  # Audit Storage Capacity – Golang keyword maps to control au-4.1
    "AuditCapacity",  # Audit Storage Capacity – Golang keyword maps to control au-4.1
    "LogDiskQuota",  # Audit Storage Capacity – Golang keyword maps to control au-4.1
]

au4_1_java = [
    "setLogrotate",  # Audit Storage Capacity – Java keyword maps to control au-4.1
    "setAuditCapacity",  # Audit Storage Capacity – Java keyword maps to control au-4.1
    "setLogDiskQuota",  # Audit Storage Capacity – Java keyword maps to control au-4.1
]

au4_1_cpp = [
    "logrotate_config",  # Audit Storage Capacity – Cpp keyword maps to control au-4.1
    "audit_capacity_config",  # Audit Storage Capacity – Cpp keyword maps to control au-4.1
    "log_disk_quota_config",  # Audit Storage Capacity – Cpp keyword maps to control au-4.1
]

au5b = [
    "alert_on_log_failure",  # Response to Audit Processing Failures – keyword indicative of control au-5b
    "log_failure_notification",  # Response to Audit Processing Failures – keyword indicative of control au-5b
    "audit_processing_error",  # Response to Audit Processing Failures – keyword indicative of control au-5b
]

au5b_python = [
    "ALERT_ON_LOG_FAILURE",  # Response to Audit Processing Failures – Python keyword maps to control au-5b
    "LOG_FAILURE_NOTIFICATION",  # Response to Audit Processing Failures – Python keyword maps to control au-5b
    "AUDIT_PROCESSING_ERROR",  # Response to Audit Processing Failures – Python keyword maps to control au-5b
]

au5b_golang = [
    "AlertOnLogFailure",  # Response to Audit Processing Failures – Golang keyword maps to control au-5b
    "LogFailureNotification",  # Response to Audit Processing Failures – Golang keyword maps to control au-5b
    "AuditProcessingError",  # Response to Audit Processing Failures – Golang keyword maps to control au-5b
]

au5b_java = [
    "setAlertOnLogFailure",  # Response to Audit Processing Failures – Java keyword maps to control au-5b
    "setLogFailureNotification",  # Response to Audit Processing Failures – Java keyword maps to control au-5b
    "setAuditProcessingError",  # Response to Audit Processing Failures – Java keyword maps to control au-5b
]

au5b_cpp = [
    "alert_on_log_failure_config",  # Response to Audit Processing Failures – Cpp keyword maps to control au-5b
    "log_failure_notification_config",  # Response to Audit Processing Failures – Cpp keyword maps to control au-5b
    "audit_processing_error_config",  # Response to Audit Processing Failures – Cpp keyword maps to control au-5b
]

au6_4 = [
    "log_review",  # Audit Review, Analysis, and Reporting – keyword indicative of control au-6.4
    "security_dashboard",  # Audit Review, Analysis, and Reporting – keyword indicative of control au-6.4
    "audit_analysis",  # Audit Review, Analysis, and Reporting – keyword indicative of control au-6.4
]

au6_4_python = [
    "LOG_REVIEW",  # Audit Review, Analysis, and Reporting – Python keyword maps to control au-6.4
    "SECURITY_DASHBOARD",  # Audit Review, Analysis, and Reporting – Python keyword maps to control au-6.4
    "AUDIT_ANALYSIS",  # Audit Review, Analysis, and Reporting – Python keyword maps to control au-6.4
]

au6_4_golang = [
    "LogReview",  # Audit Review, Analysis, and Reporting – Golang keyword maps to control au-6.4
    "SecurityDashboard",  # Audit Review, Analysis, and Reporting – Golang keyword maps to control au-6.4
    "AuditAnalysis",  # Audit Review, Analysis, and Reporting – Golang keyword maps to control au-6.4
]

au6_4_java = [
    "setLogReview",  # Audit Review, Analysis, and Reporting – Java keyword maps to control au-6.4
    "setSecurityDashboard",  # Audit Review, Analysis, and Reporting – Java keyword maps to control au-6.4
    "setAuditAnalysis",  # Audit Review, Analysis, and Reporting – Java keyword maps to control au-6.4
]

au6_4_cpp = [
    "log_review_config",  # Audit Review, Analysis, and Reporting – Cpp keyword maps to control au-6.4
    "security_dashboard_config",  # Audit Review, Analysis, and Reporting – Cpp keyword maps to control au-6.4
    "audit_analysis_config",  # Audit Review, Analysis, and Reporting – Cpp keyword maps to control au-6.4
]

au7a = [
    "log_filter",  # Audit Reduction and Report Generation – keyword indicative of control au-7a
    "report_generation",  # Audit Reduction and Report Generation – keyword indicative of control au-7a
    "audit_reduction",  # Audit Reduction and Report Generation – keyword indicative of control au-7a
]

au7a_python = [
    "LOG_FILTER",  # Audit Reduction and Report Generation – Python keyword maps to control au-7a
    "REPORT_GENERATION",  # Audit Reduction and Report Generation – Python keyword maps to control au-7a
    "AUDIT_REDUCTION",  # Audit Reduction and Report Generation – Python keyword maps to control au-7a
]

au7a_golang = [
    "LogFilter",  # Audit Reduction and Report Generation – Golang keyword maps to control au-7a
    "ReportGeneration",  # Audit Reduction and Report Generation – Golang keyword maps to control au-7a
    "AuditReduction",  # Audit Reduction and Report Generation – Golang keyword maps to control au-7a
]

au7a_java = [
    "setLogFilter",  # Audit Reduction and Report Generation – Java keyword maps to control au-7a
    "setReportGeneration",  # Audit Reduction and Report Generation – Java keyword maps to control au-7a
    "setAuditReduction",  # Audit Reduction and Report Generation – Java keyword maps to control au-7a
]

au7a_cpp = [
    "log_filter_config",  # Audit Reduction and Report Generation – Cpp keyword maps to control au-7a
    "report_generation_config",  # Audit Reduction and Report Generation – Cpp keyword maps to control au-7a
    "audit_reduction_config",  # Audit Reduction and Report Generation – Cpp keyword maps to control au-7a
]

au7b = [
    "log_filter",  # Audit Reduction and Report Generation – keyword indicative of control au-7b
    "report_generation",  # Audit Reduction and Report Generation – keyword indicative of control au-7b
    "audit_reduction",  # Audit Reduction and Report Generation – keyword indicative of control au-7b
]

au7b_python = [
    "LOG_FILTER",  # Audit Reduction and Report Generation – Python keyword maps to control au-7b
    "REPORT_GENERATION",  # Audit Reduction and Report Generation – Python keyword maps to control au-7b
    "AUDIT_REDUCTION",  # Audit Reduction and Report Generation – Python keyword maps to control au-7b
]

au7b_golang = [
    "LogFilter",  # Audit Reduction and Report Generation – Golang keyword maps to control au-7b
    "ReportGeneration",  # Audit Reduction and Report Generation – Golang keyword maps to control au-7b
    "AuditReduction",  # Audit Reduction and Report Generation – Golang keyword maps to control au-7b
]

au7b_java = [
    "setLogFilter",  # Audit Reduction and Report Generation – Java keyword maps to control au-7b
    "setReportGeneration",  # Audit Reduction and Report Generation – Java keyword maps to control au-7b
    "setAuditReduction",  # Audit Reduction and Report Generation – Java keyword maps to control au-7b
]

au7b_cpp = [
    "log_filter_config",  # Audit Reduction and Report Generation – Cpp keyword maps to control au-7b
    "report_generation_config",  # Audit Reduction and Report Generation – Cpp keyword maps to control au-7b
    "audit_reduction_config",  # Audit Reduction and Report Generation – Cpp keyword maps to control au-7b
]

au8a = [
    "ntp_sync",  # Time Stamps – keyword indicative of control au-8a
    "chrony",  # Time Stamps – keyword indicative of control au-8a
    "time_source",  # Time Stamps – keyword indicative of control au-8a
]

au8a_python = [
    "NTP_SYNC",  # Time Stamps – Python keyword maps to control au-8a
    "CHRONY",  # Time Stamps – Python keyword maps to control au-8a
    "TIME_SOURCE",  # Time Stamps – Python keyword maps to control au-8a
]

au8a_golang = [
    "NtpSync",  # Time Stamps – Golang keyword maps to control au-8a
    "Chrony",  # Time Stamps – Golang keyword maps to control au-8a
    "TimeSource",  # Time Stamps – Golang keyword maps to control au-8a
]

au8a_java = [
    "setNtpSync",  # Time Stamps – Java keyword maps to control au-8a
    "setChrony",  # Time Stamps – Java keyword maps to control au-8a
    "setTimeSource",  # Time Stamps – Java keyword maps to control au-8a
]

au8a_cpp = [
    "ntp_sync_config",  # Time Stamps – Cpp keyword maps to control au-8a
    "chrony_config",  # Time Stamps – Cpp keyword maps to control au-8a
    "time_source_config",  # Time Stamps – Cpp keyword maps to control au-8a
]

au8b = [
    "ntp_sync",  # Time Stamps – keyword indicative of control au-8b
    "chrony",  # Time Stamps – keyword indicative of control au-8b
    "time_source",  # Time Stamps – keyword indicative of control au-8b
]

au8b_python = [
    "NTP_SYNC",  # Time Stamps – Python keyword maps to control au-8b
    "CHRONY",  # Time Stamps – Python keyword maps to control au-8b
    "TIME_SOURCE",  # Time Stamps – Python keyword maps to control au-8b
]

au8b_golang = [
    "NtpSync",  # Time Stamps – Golang keyword maps to control au-8b
    "Chrony",  # Time Stamps – Golang keyword maps to control au-8b
    "TimeSource",  # Time Stamps – Golang keyword maps to control au-8b
]

au8b_java = [
    "setNtpSync",  # Time Stamps – Java keyword maps to control au-8b
    "setChrony",  # Time Stamps – Java keyword maps to control au-8b
    "setTimeSource",  # Time Stamps – Java keyword maps to control au-8b
]

au8b_cpp = [
    "ntp_sync_config",  # Time Stamps – Cpp keyword maps to control au-8b
    "chrony_config",  # Time Stamps – Cpp keyword maps to control au-8b
    "time_source_config",  # Time Stamps – Cpp keyword maps to control au-8b
]

au9 = [
    "log_encryption",  # Protection of Audit Information – keyword indicative of control au-9
    "secure_logging",  # Protection of Audit Information – keyword indicative of control au-9
    "audit_protection",  # Protection of Audit Information – keyword indicative of control au-9
]

au9_python = [
    "LOG_ENCRYPTION",  # Protection of Audit Information – Python keyword maps to control au-9
    "SECURE_LOGGING",  # Protection of Audit Information – Python keyword maps to control au-9
    "AUDIT_PROTECTION",  # Protection of Audit Information – Python keyword maps to control au-9
]

au9_golang = [
    "LogEncryption",  # Protection of Audit Information – Golang keyword maps to control au-9
    "SecureLogging",  # Protection of Audit Information – Golang keyword maps to control au-9
    "AuditProtection",  # Protection of Audit Information – Golang keyword maps to control au-9
]

au9_java = [
    "setLogEncryption",  # Protection of Audit Information – Java keyword maps to control au-9
    "setSecureLogging",  # Protection of Audit Information – Java keyword maps to control au-9
    "setAuditProtection",  # Protection of Audit Information – Java keyword maps to control au-9
]

au9_cpp = [
    "log_encryption_config",  # Protection of Audit Information – Cpp keyword maps to control au-9
    "secure_logging_config",  # Protection of Audit Information – Cpp keyword maps to control au-9
    "audit_protection_config",  # Protection of Audit Information – Cpp keyword maps to control au-9
]

au9_2 = [
    "log_encryption",  # Protection of Audit Information – keyword indicative of control au-9.2
    "secure_logging",  # Protection of Audit Information – keyword indicative of control au-9.2
    "audit_protection",  # Protection of Audit Information – keyword indicative of control au-9.2
]

au9_2_python = [
    "LOG_ENCRYPTION",  # Protection of Audit Information – Python keyword maps to control au-9.2
    "SECURE_LOGGING",  # Protection of Audit Information – Python keyword maps to control au-9.2
    "AUDIT_PROTECTION",  # Protection of Audit Information – Python keyword maps to control au-9.2
]

au9_2_golang = [
    "LogEncryption",  # Protection of Audit Information – Golang keyword maps to control au-9.2
    "SecureLogging",  # Protection of Audit Information – Golang keyword maps to control au-9.2
    "AuditProtection",  # Protection of Audit Information – Golang keyword maps to control au-9.2
]

au9_2_java = [
    "setLogEncryption",  # Protection of Audit Information – Java keyword maps to control au-9.2
    "setSecureLogging",  # Protection of Audit Information – Java keyword maps to control au-9.2
    "setAuditProtection",  # Protection of Audit Information – Java keyword maps to control au-9.2
]

au9_2_cpp = [
    "log_encryption_config",  # Protection of Audit Information – Cpp keyword maps to control au-9.2
    "secure_logging_config",  # Protection of Audit Information – Cpp keyword maps to control au-9.2
    "audit_protection_config",  # Protection of Audit Information – Cpp keyword maps to control au-9.2
]

au9_3 = [
    "log_encryption",  # Protection of Audit Information – keyword indicative of control au-9.3
    "secure_logging",  # Protection of Audit Information – keyword indicative of control au-9.3
    "audit_protection",  # Protection of Audit Information – keyword indicative of control au-9.3
]

au9_3_python = [
    "LOG_ENCRYPTION",  # Protection of Audit Information – Python keyword maps to control au-9.3
    "SECURE_LOGGING",  # Protection of Audit Information – Python keyword maps to control au-9.3
    "AUDIT_PROTECTION",  # Protection of Audit Information – Python keyword maps to control au-9.3
]

au9_3_golang = [
    "LogEncryption",  # Protection of Audit Information – Golang keyword maps to control au-9.3
    "SecureLogging",  # Protection of Audit Information – Golang keyword maps to control au-9.3
    "AuditProtection",  # Protection of Audit Information – Golang keyword maps to control au-9.3
]

au9_3_java = [
    "setLogEncryption",  # Protection of Audit Information – Java keyword maps to control au-9.3
    "setSecureLogging",  # Protection of Audit Information – Java keyword maps to control au-9.3
    "setAuditProtection",  # Protection of Audit Information – Java keyword maps to control au-9.3
]

au9_3_cpp = [
    "log_encryption_config",  # Protection of Audit Information – Cpp keyword maps to control au-9.3
    "secure_logging_config",  # Protection of Audit Information – Cpp keyword maps to control au-9.3
    "audit_protection_config",  # Protection of Audit Information – Cpp keyword maps to control au-9.3
]

au9a = [
    "log_encryption",  # Protection of Audit Information – keyword indicative of control au-9a
    "secure_logging",  # Protection of Audit Information – keyword indicative of control au-9a
    "audit_protection",  # Protection of Audit Information – keyword indicative of control au-9a
]

au9a_python = [
    "LOG_ENCRYPTION",  # Protection of Audit Information – Python keyword maps to control au-9a
    "SECURE_LOGGING",  # Protection of Audit Information – Python keyword maps to control au-9a
    "AUDIT_PROTECTION",  # Protection of Audit Information – Python keyword maps to control au-9a
]

au9a_golang = [
    "LogEncryption",  # Protection of Audit Information – Golang keyword maps to control au-9a
    "SecureLogging",  # Protection of Audit Information – Golang keyword maps to control au-9a
    "AuditProtection",  # Protection of Audit Information – Golang keyword maps to control au-9a
]

au9a_java = [
    "setLogEncryption",  # Protection of Audit Information – Java keyword maps to control au-9a
    "setSecureLogging",  # Protection of Audit Information – Java keyword maps to control au-9a
    "setAuditProtection",  # Protection of Audit Information – Java keyword maps to control au-9a
]

au9a_cpp = [
    "log_encryption_config",  # Protection of Audit Information – Cpp keyword maps to control au-9a
    "secure_logging_config",  # Protection of Audit Information – Cpp keyword maps to control au-9a
    "audit_protection_config",  # Protection of Audit Information – Cpp keyword maps to control au-9a
]

cm11_2 = [
    "baseline_config",  # Configuration Management Plan – keyword indicative of control cm-11.2
    "config_baseline",  # Configuration Management Plan – keyword indicative of control cm-11.2
    "baseline_document",  # Configuration Management Plan – keyword indicative of control cm-11.2
]

cm11_2_python = [
    "BASELINE_CONFIG",  # Configuration Management Plan – Python keyword maps to control cm-11.2
    "CONFIG_BASELINE",  # Configuration Management Plan – Python keyword maps to control cm-11.2
    "BASELINE_DOCUMENT",  # Configuration Management Plan – Python keyword maps to control cm-11.2
]

cm11_2_golang = [
    "BaselineConfig",  # Configuration Management Plan – Golang keyword maps to control cm-11.2
    "ConfigBaseline",  # Configuration Management Plan – Golang keyword maps to control cm-11.2
    "BaselineDocument",  # Configuration Management Plan – Golang keyword maps to control cm-11.2
]

cm11_2_java = [
    "setBaselineConfig",  # Configuration Management Plan – Java keyword maps to control cm-11.2
    "setConfigBaseline",  # Configuration Management Plan – Java keyword maps to control cm-11.2
    "setBaselineDocument",  # Configuration Management Plan – Java keyword maps to control cm-11.2
]

cm11_2_cpp = [
    "baseline_config_config",  # Configuration Management Plan – Cpp keyword maps to control cm-11.2
    "config_baseline_config",  # Configuration Management Plan – Cpp keyword maps to control cm-11.2
    "baseline_document_config",  # Configuration Management Plan – Cpp keyword maps to control cm-11.2
]

cm14 = [
    "code_signing",  # Signed Components – keyword indicative of control cm-14
    "signed_package",  # Signed Components – keyword indicative of control cm-14
    "verify_signature",  # Signed Components – keyword indicative of control cm-14
]

cm14_python = [
    "CODE_SIGNING",  # Signed Components – Python keyword maps to control cm-14
    "SIGNED_PACKAGE",  # Signed Components – Python keyword maps to control cm-14
    "VERIFY_SIGNATURE",  # Signed Components – Python keyword maps to control cm-14
]

cm14_golang = [
    "CodeSigning",  # Signed Components – Golang keyword maps to control cm-14
    "SignedPackage",  # Signed Components – Golang keyword maps to control cm-14
    "VerifySignature",  # Signed Components – Golang keyword maps to control cm-14
]

cm14_java = [
    "setCodeSigning",  # Signed Components – Java keyword maps to control cm-14
    "setSignedPackage",  # Signed Components – Java keyword maps to control cm-14
    "setVerifySignature",  # Signed Components – Java keyword maps to control cm-14
]

cm14_cpp = [
    "code_signing_config",  # Signed Components – Cpp keyword maps to control cm-14
    "signed_package_config",  # Signed Components – Cpp keyword maps to control cm-14
    "verify_signature_config",  # Signed Components – Cpp keyword maps to control cm-14
]

cm5 = [
    "pull_request",  # Access Restrictions for Change – keyword indicative of control cm-5
    "change_control",  # Access Restrictions for Change – keyword indicative of control cm-5
    "code_review",  # Access Restrictions for Change – keyword indicative of control cm-5
]

cm5_python = [
    "PULL_REQUEST",  # Access Restrictions for Change – Python keyword maps to control cm-5
    "CHANGE_CONTROL",  # Access Restrictions for Change – Python keyword maps to control cm-5
    "CODE_REVIEW",  # Access Restrictions for Change – Python keyword maps to control cm-5
]

cm5_golang = [
    "PullRequest",  # Access Restrictions for Change – Golang keyword maps to control cm-5
    "ChangeControl",  # Access Restrictions for Change – Golang keyword maps to control cm-5
    "CodeReview",  # Access Restrictions for Change – Golang keyword maps to control cm-5
]

cm5_java = [
    "setPullRequest",  # Access Restrictions for Change – Java keyword maps to control cm-5
    "setChangeControl",  # Access Restrictions for Change – Java keyword maps to control cm-5
    "setCodeReview",  # Access Restrictions for Change – Java keyword maps to control cm-5
]

cm5_cpp = [
    "pull_request_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5
    "change_control_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5
    "code_review_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5
]

cm5_1 = [
    "pull_request",  # Access Restrictions for Change – keyword indicative of control cm-5.1
    "change_control",  # Access Restrictions for Change – keyword indicative of control cm-5.1
    "code_review",  # Access Restrictions for Change – keyword indicative of control cm-5.1
]

cm5_1_python = [
    "PULL_REQUEST",  # Access Restrictions for Change – Python keyword maps to control cm-5.1
    "CHANGE_CONTROL",  # Access Restrictions for Change – Python keyword maps to control cm-5.1
    "CODE_REVIEW",  # Access Restrictions for Change – Python keyword maps to control cm-5.1
]

cm5_1_golang = [
    "PullRequest",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1
    "ChangeControl",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1
    "CodeReview",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1
]

cm5_1_java = [
    "setPullRequest",  # Access Restrictions for Change – Java keyword maps to control cm-5.1
    "setChangeControl",  # Access Restrictions for Change – Java keyword maps to control cm-5.1
    "setCodeReview",  # Access Restrictions for Change – Java keyword maps to control cm-5.1
]

cm5_1_cpp = [
    "pull_request_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1
    "change_control_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1
    "code_review_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1
]

cm5_1_a = [
    "pull_request",  # Access Restrictions for Change – keyword indicative of control cm-5.1.a
    "change_control",  # Access Restrictions for Change – keyword indicative of control cm-5.1.a
    "code_review",  # Access Restrictions for Change – keyword indicative of control cm-5.1.a
]

cm5_1_a_python = [
    "PULL_REQUEST",  # Access Restrictions for Change – Python keyword maps to control cm-5.1.a
    "CHANGE_CONTROL",  # Access Restrictions for Change – Python keyword maps to control cm-5.1.a
    "CODE_REVIEW",  # Access Restrictions for Change – Python keyword maps to control cm-5.1.a
]

cm5_1_a_golang = [
    "PullRequest",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1.a
    "ChangeControl",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1.a
    "CodeReview",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1.a
]

cm5_1_a_java = [
    "setPullRequest",  # Access Restrictions for Change – Java keyword maps to control cm-5.1.a
    "setChangeControl",  # Access Restrictions for Change – Java keyword maps to control cm-5.1.a
    "setCodeReview",  # Access Restrictions for Change – Java keyword maps to control cm-5.1.a
]

cm5_1_a_cpp = [
    "pull_request_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1.a
    "change_control_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1.a
    "code_review_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1.a
]

cm5_1_b = [
    "pull_request",  # Access Restrictions for Change – keyword indicative of control cm-5.1.b
    "change_control",  # Access Restrictions for Change – keyword indicative of control cm-5.1.b
    "code_review",  # Access Restrictions for Change – keyword indicative of control cm-5.1.b
]

cm5_1_b_python = [
    "PULL_REQUEST",  # Access Restrictions for Change – Python keyword maps to control cm-5.1.b
    "CHANGE_CONTROL",  # Access Restrictions for Change – Python keyword maps to control cm-5.1.b
    "CODE_REVIEW",  # Access Restrictions for Change – Python keyword maps to control cm-5.1.b
]

cm5_1_b_golang = [
    "PullRequest",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1.b
    "ChangeControl",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1.b
    "CodeReview",  # Access Restrictions for Change – Golang keyword maps to control cm-5.1.b
]

cm5_1_b_java = [
    "setPullRequest",  # Access Restrictions for Change – Java keyword maps to control cm-5.1.b
    "setChangeControl",  # Access Restrictions for Change – Java keyword maps to control cm-5.1.b
    "setCodeReview",  # Access Restrictions for Change – Java keyword maps to control cm-5.1.b
]

cm5_1_b_cpp = [
    "pull_request_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1.b
    "change_control_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1.b
    "code_review_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.1.b
]

cm5_3 = [
    "pull_request",  # Access Restrictions for Change – keyword indicative of control cm-5.3
    "change_control",  # Access Restrictions for Change – keyword indicative of control cm-5.3
    "code_review",  # Access Restrictions for Change – keyword indicative of control cm-5.3
]

cm5_3_python = [
    "PULL_REQUEST",  # Access Restrictions for Change – Python keyword maps to control cm-5.3
    "CHANGE_CONTROL",  # Access Restrictions for Change – Python keyword maps to control cm-5.3
    "CODE_REVIEW",  # Access Restrictions for Change – Python keyword maps to control cm-5.3
]

cm5_3_golang = [
    "PullRequest",  # Access Restrictions for Change – Golang keyword maps to control cm-5.3
    "ChangeControl",  # Access Restrictions for Change – Golang keyword maps to control cm-5.3
    "CodeReview",  # Access Restrictions for Change – Golang keyword maps to control cm-5.3
]

cm5_3_java = [
    "setPullRequest",  # Access Restrictions for Change – Java keyword maps to control cm-5.3
    "setChangeControl",  # Access Restrictions for Change – Java keyword maps to control cm-5.3
    "setCodeReview",  # Access Restrictions for Change – Java keyword maps to control cm-5.3
]

cm5_3_cpp = [
    "pull_request_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.3
    "change_control_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.3
    "code_review_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.3
]

cm5_6 = [
    "pull_request",  # Access Restrictions for Change – keyword indicative of control cm-5.6
    "change_control",  # Access Restrictions for Change – keyword indicative of control cm-5.6
    "code_review",  # Access Restrictions for Change – keyword indicative of control cm-5.6
]

cm5_6_python = [
    "PULL_REQUEST",  # Access Restrictions for Change – Python keyword maps to control cm-5.6
    "CHANGE_CONTROL",  # Access Restrictions for Change – Python keyword maps to control cm-5.6
    "CODE_REVIEW",  # Access Restrictions for Change – Python keyword maps to control cm-5.6
]

cm5_6_golang = [
    "PullRequest",  # Access Restrictions for Change – Golang keyword maps to control cm-5.6
    "ChangeControl",  # Access Restrictions for Change – Golang keyword maps to control cm-5.6
    "CodeReview",  # Access Restrictions for Change – Golang keyword maps to control cm-5.6
]

cm5_6_java = [
    "setPullRequest",  # Access Restrictions for Change – Java keyword maps to control cm-5.6
    "setChangeControl",  # Access Restrictions for Change – Java keyword maps to control cm-5.6
    "setCodeReview",  # Access Restrictions for Change – Java keyword maps to control cm-5.6
]

cm5_6_cpp = [
    "pull_request_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.6
    "change_control_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.6
    "code_review_config",  # Access Restrictions for Change – Cpp keyword maps to control cm-5.6
]

cm6b = [
    "sysctl",  # Configuration Settings – keyword indicative of control cm-6b
    "config_setting",  # Configuration Settings – keyword indicative of control cm-6b
    "system_setting",  # Configuration Settings – keyword indicative of control cm-6b
]

cm6b_python = [
    "SYSCTL",  # Configuration Settings – Python keyword maps to control cm-6b
    "CONFIG_SETTING",  # Configuration Settings – Python keyword maps to control cm-6b
    "SYSTEM_SETTING",  # Configuration Settings – Python keyword maps to control cm-6b
]

cm6b_golang = [
    "Sysctl",  # Configuration Settings – Golang keyword maps to control cm-6b
    "ConfigSetting",  # Configuration Settings – Golang keyword maps to control cm-6b
    "SystemSetting",  # Configuration Settings – Golang keyword maps to control cm-6b
]

cm6b_java = [
    "setSysctl",  # Configuration Settings – Java keyword maps to control cm-6b
    "setConfigSetting",  # Configuration Settings – Java keyword maps to control cm-6b
    "setSystemSetting",  # Configuration Settings – Java keyword maps to control cm-6b
]

cm6b_cpp = [
    "sysctl_config",  # Configuration Settings – Cpp keyword maps to control cm-6b
    "config_setting_config",  # Configuration Settings – Cpp keyword maps to control cm-6b
    "system_setting_config",  # Configuration Settings – Cpp keyword maps to control cm-6b
]

cm7_2 = [
    "disable_service",  # Least Functionality – keyword indicative of control cm-7.2
    "remove_package",  # Least Functionality – keyword indicative of control cm-7.2
    "least_functionality",  # Least Functionality – keyword indicative of control cm-7.2
]

cm7_2_python = [
    "DISABLE_SERVICE",  # Least Functionality – Python keyword maps to control cm-7.2
    "REMOVE_PACKAGE",  # Least Functionality – Python keyword maps to control cm-7.2
    "LEAST_FUNCTIONALITY",  # Least Functionality – Python keyword maps to control cm-7.2
]

cm7_2_golang = [
    "DisableService",  # Least Functionality – Golang keyword maps to control cm-7.2
    "RemovePackage",  # Least Functionality – Golang keyword maps to control cm-7.2
    "LeastFunctionality",  # Least Functionality – Golang keyword maps to control cm-7.2
]

cm7_2_java = [
    "setDisableService",  # Least Functionality – Java keyword maps to control cm-7.2
    "setRemovePackage",  # Least Functionality – Java keyword maps to control cm-7.2
    "setLeastFunctionality",  # Least Functionality – Java keyword maps to control cm-7.2
]

cm7_2_cpp = [
    "disable_service_config",  # Least Functionality – Cpp keyword maps to control cm-7.2
    "remove_package_config",  # Least Functionality – Cpp keyword maps to control cm-7.2
    "least_functionality_config",  # Least Functionality – Cpp keyword maps to control cm-7.2
]

cm7_5_b = [
    "disable_service",  # Least Functionality – keyword indicative of control cm-7.5.b
    "remove_package",  # Least Functionality – keyword indicative of control cm-7.5.b
    "least_functionality",  # Least Functionality – keyword indicative of control cm-7.5.b
]

cm7_5_b_python = [
    "DISABLE_SERVICE",  # Least Functionality – Python keyword maps to control cm-7.5.b
    "REMOVE_PACKAGE",  # Least Functionality – Python keyword maps to control cm-7.5.b
    "LEAST_FUNCTIONALITY",  # Least Functionality – Python keyword maps to control cm-7.5.b
]

cm7_5_b_golang = [
    "DisableService",  # Least Functionality – Golang keyword maps to control cm-7.5.b
    "RemovePackage",  # Least Functionality – Golang keyword maps to control cm-7.5.b
    "LeastFunctionality",  # Least Functionality – Golang keyword maps to control cm-7.5.b
]

cm7_5_b_java = [
    "setDisableService",  # Least Functionality – Java keyword maps to control cm-7.5.b
    "setRemovePackage",  # Least Functionality – Java keyword maps to control cm-7.5.b
    "setLeastFunctionality",  # Least Functionality – Java keyword maps to control cm-7.5.b
]

cm7_5_b_cpp = [
    "disable_service_config",  # Least Functionality – Cpp keyword maps to control cm-7.5.b
    "remove_package_config",  # Least Functionality – Cpp keyword maps to control cm-7.5.b
    "least_functionality_config",  # Least Functionality – Cpp keyword maps to control cm-7.5.b
]

cm7a = [
    "disable_service",  # Least Functionality – keyword indicative of control cm-7a
    "remove_package",  # Least Functionality – keyword indicative of control cm-7a
    "least_functionality",  # Least Functionality – keyword indicative of control cm-7a
]

cm7a_python = [
    "DISABLE_SERVICE",  # Least Functionality – Python keyword maps to control cm-7a
    "REMOVE_PACKAGE",  # Least Functionality – Python keyword maps to control cm-7a
    "LEAST_FUNCTIONALITY",  # Least Functionality – Python keyword maps to control cm-7a
]

cm7a_golang = [
    "DisableService",  # Least Functionality – Golang keyword maps to control cm-7a
    "RemovePackage",  # Least Functionality – Golang keyword maps to control cm-7a
    "LeastFunctionality",  # Least Functionality – Golang keyword maps to control cm-7a
]

cm7a_java = [
    "setDisableService",  # Least Functionality – Java keyword maps to control cm-7a
    "setRemovePackage",  # Least Functionality – Java keyword maps to control cm-7a
    "setLeastFunctionality",  # Least Functionality – Java keyword maps to control cm-7a
]

cm7a_cpp = [
    "disable_service_config",  # Least Functionality – Cpp keyword maps to control cm-7a
    "remove_package_config",  # Least Functionality – Cpp keyword maps to control cm-7a
    "least_functionality_config",  # Least Functionality – Cpp keyword maps to control cm-7a
]

ia11 = [
    "reauthenticate",  # Re-authentication – keyword indicative of control ia-11
    "session_reauth",  # Re-authentication – keyword indicative of control ia-11
    "reauth_interval",  # Re-authentication – keyword indicative of control ia-11
]

ia11_python = [
    "REAUTHENTICATE",  # Re-authentication – Python keyword maps to control ia-11
    "SESSION_REAUTH",  # Re-authentication – Python keyword maps to control ia-11
    "REAUTH_INTERVAL",  # Re-authentication – Python keyword maps to control ia-11
]

ia11_golang = [
    "Reauthenticate",  # Re-authentication – Golang keyword maps to control ia-11
    "SessionReauth",  # Re-authentication – Golang keyword maps to control ia-11
    "ReauthInterval",  # Re-authentication – Golang keyword maps to control ia-11
]

ia11_java = [
    "setReauthenticate",  # Re-authentication – Java keyword maps to control ia-11
    "setSessionReauth",  # Re-authentication – Java keyword maps to control ia-11
    "setReauthInterval",  # Re-authentication – Java keyword maps to control ia-11
]

ia11_cpp = [
    "reauthenticate_config",  # Re-authentication – Cpp keyword maps to control ia-11
    "session_reauth_config",  # Re-authentication – Cpp keyword maps to control ia-11
    "reauth_interval_config",  # Re-authentication – Cpp keyword maps to control ia-11
]

ia2 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2
]

ia2_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2
]

ia2_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2
]

ia2_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2
]

ia2_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2
]

ia2_1 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.1
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.1
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.1
]

ia2_1_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.1
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.1
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.1
]

ia2_1_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.1
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.1
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.1
]

ia2_1_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.1
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.1
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.1
]

ia2_1_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.1
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.1
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.1
]

ia2_2 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.2
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.2
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.2
]

ia2_2_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.2
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.2
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.2
]

ia2_2_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.2
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.2
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.2
]

ia2_2_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.2
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.2
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.2
]

ia2_2_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.2
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.2
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.2
]

ia2_3 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.3
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.3
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.3
]

ia2_3_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.3
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.3
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.3
]

ia2_3_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.3
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.3
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.3
]

ia2_3_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.3
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.3
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.3
]

ia2_3_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.3
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.3
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.3
]

ia2_4 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.4
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.4
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.4
]

ia2_4_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.4
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.4
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.4
]

ia2_4_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.4
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.4
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.4
]

ia2_4_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.4
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.4
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.4
]

ia2_4_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.4
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.4
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.4
]

ia2_5 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.5
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.5
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.5
]

ia2_5_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.5
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.5
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.5
]

ia2_5_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.5
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.5
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.5
]

ia2_5_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.5
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.5
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.5
]

ia2_5_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.5
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.5
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.5
]

ia2_8 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.8
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.8
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.8
]

ia2_8_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.8
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.8
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.8
]

ia2_8_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.8
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.8
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.8
]

ia2_8_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.8
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.8
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.8
]

ia2_8_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.8
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.8
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.8
]

ia2_9 = [
    "password_policy",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.9
    "local_login",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.9
    "user_authentication",  # Identification and Authentication (Organizational Users) – keyword indicative of control ia-2.9
]

ia2_9_python = [
    "PASSWORD_POLICY",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.9
    "LOCAL_LOGIN",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.9
    "USER_AUTHENTICATION",  # Identification and Authentication (Organizational Users) – Python keyword maps to control ia-2.9
]

ia2_9_golang = [
    "PasswordPolicy",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.9
    "LocalLogin",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.9
    "UserAuthentication",  # Identification and Authentication (Organizational Users) – Golang keyword maps to control ia-2.9
]

ia2_9_java = [
    "setPasswordPolicy",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.9
    "setLocalLogin",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.9
    "setUserAuthentication",  # Identification and Authentication (Organizational Users) – Java keyword maps to control ia-2.9
]

ia2_9_cpp = [
    "password_policy_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.9
    "local_login_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.9
    "user_authentication_config",  # Identification and Authentication (Organizational Users) – Cpp keyword maps to control ia-2.9
]

ia3_1 = [
    "device_cert",  # Device Identification and Authentication – keyword indicative of control ia-3.1
    "mac_address_auth",  # Device Identification and Authentication – keyword indicative of control ia-3.1
    "device_id",  # Device Identification and Authentication – keyword indicative of control ia-3.1
]

ia3_1_python = [
    "DEVICE_CERT",  # Device Identification and Authentication – Python keyword maps to control ia-3.1
    "MAC_ADDRESS_AUTH",  # Device Identification and Authentication – Python keyword maps to control ia-3.1
    "DEVICE_ID",  # Device Identification and Authentication – Python keyword maps to control ia-3.1
]

ia3_1_golang = [
    "DeviceCert",  # Device Identification and Authentication – Golang keyword maps to control ia-3.1
    "MacAddressAuth",  # Device Identification and Authentication – Golang keyword maps to control ia-3.1
    "DeviceId",  # Device Identification and Authentication – Golang keyword maps to control ia-3.1
]

ia3_1_java = [
    "setDeviceCert",  # Device Identification and Authentication – Java keyword maps to control ia-3.1
    "setMacAddressAuth",  # Device Identification and Authentication – Java keyword maps to control ia-3.1
    "setDeviceId",  # Device Identification and Authentication – Java keyword maps to control ia-3.1
]

ia3_1_cpp = [
    "device_cert_config",  # Device Identification and Authentication – Cpp keyword maps to control ia-3.1
    "mac_address_auth_config",  # Device Identification and Authentication – Cpp keyword maps to control ia-3.1
    "device_id_config",  # Device Identification and Authentication – Cpp keyword maps to control ia-3.1
]

ia4e = [
    "user_id",  # Identifier Management – keyword indicative of control ia-4e
    "identifier_format",  # Identifier Management – keyword indicative of control ia-4e
    "id_management",  # Identifier Management – keyword indicative of control ia-4e
]

ia4e_python = [
    "USER_ID",  # Identifier Management – Python keyword maps to control ia-4e
    "IDENTIFIER_FORMAT",  # Identifier Management – Python keyword maps to control ia-4e
    "ID_MANAGEMENT",  # Identifier Management – Python keyword maps to control ia-4e
]

ia4e_golang = [
    "UserId",  # Identifier Management – Golang keyword maps to control ia-4e
    "IdentifierFormat",  # Identifier Management – Golang keyword maps to control ia-4e
    "IdManagement",  # Identifier Management – Golang keyword maps to control ia-4e
]

ia4e_java = [
    "setUserId",  # Identifier Management – Java keyword maps to control ia-4e
    "setIdentifierFormat",  # Identifier Management – Java keyword maps to control ia-4e
    "setIdManagement",  # Identifier Management – Java keyword maps to control ia-4e
]

ia4e_cpp = [
    "user_id_config",  # Identifier Management – Cpp keyword maps to control ia-4e
    "identifier_format_config",  # Identifier Management – Cpp keyword maps to control ia-4e
    "id_management_config",  # Identifier Management – Cpp keyword maps to control ia-4e
]

ia5_1_a = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.1.a
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.1.a
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.1.a
]

ia5_1_a_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.1.a
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.1.a
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.1.a
]

ia5_1_a_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.1.a
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.1.a
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.1.a
]

ia5_1_a_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.1.a
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.1.a
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.1.a
]

ia5_1_a_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.a
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.a
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.a
]

ia5_1_b = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.1.b
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.1.b
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.1.b
]

ia5_1_b_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.1.b
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.1.b
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.1.b
]

ia5_1_b_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.1.b
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.1.b
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.1.b
]

ia5_1_b_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.1.b
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.1.b
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.1.b
]

ia5_1_b_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.b
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.b
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.b
]

ia5_1_c = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.1.c
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.1.c
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.1.c
]

ia5_1_c_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.1.c
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.1.c
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.1.c
]

ia5_1_c_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.1.c
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.1.c
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.1.c
]

ia5_1_c_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.1.c
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.1.c
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.1.c
]

ia5_1_c_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.c
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.c
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.c
]

ia5_1_d = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.1.d
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.1.d
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.1.d
]

ia5_1_d_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.1.d
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.1.d
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.1.d
]

ia5_1_d_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.1.d
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.1.d
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.1.d
]

ia5_1_d_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.1.d
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.1.d
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.1.d
]

ia5_1_d_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.d
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.d
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.d
]

ia5_1_h = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.1.h
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.1.h
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.1.h
]

ia5_1_h_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.1.h
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.1.h
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.1.h
]

ia5_1_h_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.1.h
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.1.h
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.1.h
]

ia5_1_h_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.1.h
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.1.h
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.1.h
]

ia5_1_h_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.h
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.h
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.1.h
]

ia5_13 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.13
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.13
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.13
]

ia5_13_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.13
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.13
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.13
]

ia5_13_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.13
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.13
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.13
]

ia5_13_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.13
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.13
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.13
]

ia5_13_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.13
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.13
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.13
]

ia5_2_a = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.a
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.a
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.a
]

ia5_2_a_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.a
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.a
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.a
]

ia5_2_a_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.a
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.a
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.a
]

ia5_2_a_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.a
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.a
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.a
]

ia5_2_a_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a
]

ia5_2_a_1 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.a.1
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.a.1
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.a.1
]

ia5_2_a_1_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.a.1
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.a.1
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.a.1
]

ia5_2_a_1_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.a.1
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.a.1
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.a.1
]

ia5_2_a_1_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.a.1
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.a.1
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.a.1
]

ia5_2_a_1_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a.1
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a.1
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a.1
]

ia5_2_a_2 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.a.2
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.a.2
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.a.2
]

ia5_2_a_2_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.a.2
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.a.2
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.a.2
]

ia5_2_a_2_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.a.2
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.a.2
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.a.2
]

ia5_2_a_2_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.a.2
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.a.2
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.a.2
]

ia5_2_a_2_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a.2
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a.2
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.a.2
]

ia5_2_b = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.b
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.b
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.b
]

ia5_2_b_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.b
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.b
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.b
]

ia5_2_b_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.b
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.b
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.b
]

ia5_2_b_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.b
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.b
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.b
]

ia5_2_b_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b
]

ia5_2_b_1 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.b.1
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.b.1
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.b.1
]

ia5_2_b_1_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.b.1
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.b.1
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.b.1
]

ia5_2_b_1_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.b.1
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.b.1
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.b.1
]

ia5_2_b_1_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.b.1
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.b.1
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.b.1
]

ia5_2_b_1_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b.1
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b.1
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b.1
]

ia5_2_b_2 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.b.2
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.b.2
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.b.2
]

ia5_2_b_2_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.b.2
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.b.2
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.b.2
]

ia5_2_b_2_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.b.2
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.b.2
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.b.2
]

ia5_2_b_2_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.b.2
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.b.2
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.b.2
]

ia5_2_b_2_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b.2
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b.2
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.b.2
]

ia5_2_c = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.c
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.c
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.c
]

ia5_2_c_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.c
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.c
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.c
]

ia5_2_c_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.c
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.c
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.c
]

ia5_2_c_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.c
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.c
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.c
]

ia5_2_c_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.c
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.c
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.c
]

ia5_2_d = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.2.d
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.2.d
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.2.d
]

ia5_2_d_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.2.d
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.2.d
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.2.d
]

ia5_2_d_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.2.d
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.2.d
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.2.d
]

ia5_2_d_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.2.d
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.2.d
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.2.d
]

ia5_2_d_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.d
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.d
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.2.d
]

ia5_6 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.6
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.6
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.6
]

ia5_6_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.6
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.6
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.6
]

ia5_6_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.6
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.6
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.6
]

ia5_6_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.6
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.6
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.6
]

ia5_6_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.6
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.6
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.6
]

ia5_7 = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5.7
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5.7
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5.7
]

ia5_7_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5.7
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5.7
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5.7
]

ia5_7_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5.7
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5.7
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5.7
]

ia5_7_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5.7
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5.7
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5.7
]

ia5_7_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5.7
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5.7
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5.7
]

ia5h = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5h
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5h
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5h
]

ia5h_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5h
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5h
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5h
]

ia5h_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5h
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5h
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5h
]

ia5h_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5h
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5h
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5h
]

ia5h_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5h
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5h
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5h
]

ia5i = [
    "password_expiration",  # Authenticator Management – keyword indicative of control ia-5i
    "key_rotation",  # Authenticator Management – keyword indicative of control ia-5i
    "token_lifetime",  # Authenticator Management – keyword indicative of control ia-5i
]

ia5i_python = [
    "PASSWORD_EXPIRATION",  # Authenticator Management – Python keyword maps to control ia-5i
    "KEY_ROTATION",  # Authenticator Management – Python keyword maps to control ia-5i
    "TOKEN_LIFETIME",  # Authenticator Management – Python keyword maps to control ia-5i
]

ia5i_golang = [
    "PasswordExpiration",  # Authenticator Management – Golang keyword maps to control ia-5i
    "KeyRotation",  # Authenticator Management – Golang keyword maps to control ia-5i
    "TokenLifetime",  # Authenticator Management – Golang keyword maps to control ia-5i
]

ia5i_java = [
    "setPasswordExpiration",  # Authenticator Management – Java keyword maps to control ia-5i
    "setKeyRotation",  # Authenticator Management – Java keyword maps to control ia-5i
    "setTokenLifetime",  # Authenticator Management – Java keyword maps to control ia-5i
]

ia5i_cpp = [
    "password_expiration_config",  # Authenticator Management – Cpp keyword maps to control ia-5i
    "key_rotation_config",  # Authenticator Management – Cpp keyword maps to control ia-5i
    "token_lifetime_config",  # Authenticator Management – Cpp keyword maps to control ia-5i
]

ia6 = [
    "password_feedback",  # Authenticator Feedback – keyword indicative of control ia-6
    "masked_input",  # Authenticator Feedback – keyword indicative of control ia-6
    "auth_feedback",  # Authenticator Feedback – keyword indicative of control ia-6
]

ia6_python = [
    "PASSWORD_FEEDBACK",  # Authenticator Feedback – Python keyword maps to control ia-6
    "MASKED_INPUT",  # Authenticator Feedback – Python keyword maps to control ia-6
    "AUTH_FEEDBACK",  # Authenticator Feedback – Python keyword maps to control ia-6
]

ia6_golang = [
    "PasswordFeedback",  # Authenticator Feedback – Golang keyword maps to control ia-6
    "MaskedInput",  # Authenticator Feedback – Golang keyword maps to control ia-6
    "AuthFeedback",  # Authenticator Feedback – Golang keyword maps to control ia-6
]

ia6_java = [
    "setPasswordFeedback",  # Authenticator Feedback – Java keyword maps to control ia-6
    "setMaskedInput",  # Authenticator Feedback – Java keyword maps to control ia-6
    "setAuthFeedback",  # Authenticator Feedback – Java keyword maps to control ia-6
]

ia6_cpp = [
    "password_feedback_config",  # Authenticator Feedback – Cpp keyword maps to control ia-6
    "masked_input_config",  # Authenticator Feedback – Cpp keyword maps to control ia-6
    "auth_feedback_config",  # Authenticator Feedback – Cpp keyword maps to control ia-6
]

ia7 = [
    "hsm_login",  # Cryptographic Module Authentication – keyword indicative of control ia-7
    "crypto_module_auth",  # Cryptographic Module Authentication – keyword indicative of control ia-7
    "pkcs11_login",  # Cryptographic Module Authentication – keyword indicative of control ia-7
]

ia7_python = [
    "HSM_LOGIN",  # Cryptographic Module Authentication – Python keyword maps to control ia-7
    "CRYPTO_MODULE_AUTH",  # Cryptographic Module Authentication – Python keyword maps to control ia-7
    "PKCS11_LOGIN",  # Cryptographic Module Authentication – Python keyword maps to control ia-7
]

ia7_golang = [
    "HsmLogin",  # Cryptographic Module Authentication – Golang keyword maps to control ia-7
    "CryptoModuleAuth",  # Cryptographic Module Authentication – Golang keyword maps to control ia-7
    "Pkcs11Login",  # Cryptographic Module Authentication – Golang keyword maps to control ia-7
]

ia7_java = [
    "setHsmLogin",  # Cryptographic Module Authentication – Java keyword maps to control ia-7
    "setCryptoModuleAuth",  # Cryptographic Module Authentication – Java keyword maps to control ia-7
    "setPkcs11Login",  # Cryptographic Module Authentication – Java keyword maps to control ia-7
]

ia7_cpp = [
    "hsm_login_config",  # Cryptographic Module Authentication – Cpp keyword maps to control ia-7
    "crypto_module_auth_config",  # Cryptographic Module Authentication – Cpp keyword maps to control ia-7
    "pkcs11_login_config",  # Cryptographic Module Authentication – Cpp keyword maps to control ia-7
]

ia8 = [
    "fingerprint_scan",  # Biometric Authentication – keyword indicative of control ia-8
    "biometric_auth",  # Biometric Authentication – keyword indicative of control ia-8
    "facial_recognition",  # Biometric Authentication – keyword indicative of control ia-8
]

ia8_python = [
    "FINGERPRINT_SCAN",  # Biometric Authentication – Python keyword maps to control ia-8
    "BIOMETRIC_AUTH",  # Biometric Authentication – Python keyword maps to control ia-8
    "FACIAL_RECOGNITION",  # Biometric Authentication – Python keyword maps to control ia-8
]

ia8_golang = [
    "FingerprintScan",  # Biometric Authentication – Golang keyword maps to control ia-8
    "BiometricAuth",  # Biometric Authentication – Golang keyword maps to control ia-8
    "FacialRecognition",  # Biometric Authentication – Golang keyword maps to control ia-8
]

ia8_java = [
    "setFingerprintScan",  # Biometric Authentication – Java keyword maps to control ia-8
    "setBiometricAuth",  # Biometric Authentication – Java keyword maps to control ia-8
    "setFacialRecognition",  # Biometric Authentication – Java keyword maps to control ia-8
]

ia8_cpp = [
    "fingerprint_scan_config",  # Biometric Authentication – Cpp keyword maps to control ia-8
    "biometric_auth_config",  # Biometric Authentication – Cpp keyword maps to control ia-8
    "facial_recognition_config",  # Biometric Authentication – Cpp keyword maps to control ia-8
]

sa15_5 = [
    "sbom",  # Development Process, Standards, and Tools – keyword indicative of control sa-15.5
    "secure_build",  # Development Process, Standards, and Tools – keyword indicative of control sa-15.5
    "code_analysis",  # Development Process, Standards, and Tools – keyword indicative of control sa-15.5
]

sa15_5_python = [
    "SBOM",  # Development Process, Standards, and Tools – Python keyword maps to control sa-15.5
    "SECURE_BUILD",  # Development Process, Standards, and Tools – Python keyword maps to control sa-15.5
    "CODE_ANALYSIS",  # Development Process, Standards, and Tools – Python keyword maps to control sa-15.5
]

sa15_5_golang = [
    "Sbom",  # Development Process, Standards, and Tools – Golang keyword maps to control sa-15.5
    "SecureBuild",  # Development Process, Standards, and Tools – Golang keyword maps to control sa-15.5
    "CodeAnalysis",  # Development Process, Standards, and Tools – Golang keyword maps to control sa-15.5
]

sa15_5_java = [
    "setSbom",  # Development Process, Standards, and Tools – Java keyword maps to control sa-15.5
    "setSecureBuild",  # Development Process, Standards, and Tools – Java keyword maps to control sa-15.5
    "setCodeAnalysis",  # Development Process, Standards, and Tools – Java keyword maps to control sa-15.5
]

sa15_5_cpp = [
    "sbom_config",  # Development Process, Standards, and Tools – Cpp keyword maps to control sa-15.5
    "secure_build_config",  # Development Process, Standards, and Tools – Cpp keyword maps to control sa-15.5
    "code_analysis_config",  # Development Process, Standards, and Tools – Cpp keyword maps to control sa-15.5
]

sa4_5_a = [
    "security_requirements",  # Acquisition Process – keyword indicative of control sa-4.5.a
    "contract_clause",  # Acquisition Process – keyword indicative of control sa-4.5.a
    "acquisition_doc",  # Acquisition Process – keyword indicative of control sa-4.5.a
]

sa4_5_a_python = [
    "SECURITY_REQUIREMENTS",  # Acquisition Process – Python keyword maps to control sa-4.5.a
    "CONTRACT_CLAUSE",  # Acquisition Process – Python keyword maps to control sa-4.5.a
    "ACQUISITION_DOC",  # Acquisition Process – Python keyword maps to control sa-4.5.a
]

sa4_5_a_golang = [
    "SecurityRequirements",  # Acquisition Process – Golang keyword maps to control sa-4.5.a
    "ContractClause",  # Acquisition Process – Golang keyword maps to control sa-4.5.a
    "AcquisitionDoc",  # Acquisition Process – Golang keyword maps to control sa-4.5.a
]

sa4_5_a_java = [
    "setSecurityRequirements",  # Acquisition Process – Java keyword maps to control sa-4.5.a
    "setContractClause",  # Acquisition Process – Java keyword maps to control sa-4.5.a
    "setAcquisitionDoc",  # Acquisition Process – Java keyword maps to control sa-4.5.a
]

sa4_5_a_cpp = [
    "security_requirements_config",  # Acquisition Process – Cpp keyword maps to control sa-4.5.a
    "contract_clause_config",  # Acquisition Process – Cpp keyword maps to control sa-4.5.a
    "acquisition_doc_config",  # Acquisition Process – Cpp keyword maps to control sa-4.5.a
]

sc10 = [
    "network_disconnect",  # Network Disconnect – keyword indicative of control sc-10
    "auto_disconnect",  # Network Disconnect – keyword indicative of control sc-10
    "idle_disconnect",  # Network Disconnect – keyword indicative of control sc-10
]

sc10_python = [
    "NETWORK_DISCONNECT",  # Network Disconnect – Python keyword maps to control sc-10
    "AUTO_DISCONNECT",  # Network Disconnect – Python keyword maps to control sc-10
    "IDLE_DISCONNECT",  # Network Disconnect – Python keyword maps to control sc-10
]

sc10_golang = [
    "NetworkDisconnect",  # Network Disconnect – Golang keyword maps to control sc-10
    "AutoDisconnect",  # Network Disconnect – Golang keyword maps to control sc-10
    "IdleDisconnect",  # Network Disconnect – Golang keyword maps to control sc-10
]

sc10_java = [
    "setNetworkDisconnect",  # Network Disconnect – Java keyword maps to control sc-10
    "setAutoDisconnect",  # Network Disconnect – Java keyword maps to control sc-10
    "setIdleDisconnect",  # Network Disconnect – Java keyword maps to control sc-10
]

sc10_cpp = [
    "network_disconnect_config",  # Network Disconnect – Cpp keyword maps to control sc-10
    "auto_disconnect_config",  # Network Disconnect – Cpp keyword maps to control sc-10
    "idle_disconnect_config",  # Network Disconnect – Cpp keyword maps to control sc-10
]

sc11b = [
    "trusted_path",  # Trusted Path – keyword indicative of control sc-11b
    "secure_console",  # Trusted Path – keyword indicative of control sc-11b
    "secure_shell",  # Trusted Path – keyword indicative of control sc-11b
]

sc11b_python = [
    "TRUSTED_PATH",  # Trusted Path – Python keyword maps to control sc-11b
    "SECURE_CONSOLE",  # Trusted Path – Python keyword maps to control sc-11b
    "SECURE_SHELL",  # Trusted Path – Python keyword maps to control sc-11b
]

sc11b_golang = [
    "TrustedPath",  # Trusted Path – Golang keyword maps to control sc-11b
    "SecureConsole",  # Trusted Path – Golang keyword maps to control sc-11b
    "SecureShell",  # Trusted Path – Golang keyword maps to control sc-11b
]

sc11b_java = [
    "setTrustedPath",  # Trusted Path – Java keyword maps to control sc-11b
    "setSecureConsole",  # Trusted Path – Java keyword maps to control sc-11b
    "setSecureShell",  # Trusted Path – Java keyword maps to control sc-11b
]

sc11b_cpp = [
    "trusted_path_config",  # Trusted Path – Cpp keyword maps to control sc-11b
    "secure_console_config",  # Trusted Path – Cpp keyword maps to control sc-11b
    "secure_shell_config",  # Trusted Path – Cpp keyword maps to control sc-11b
]

sc2 = [
    "namespace_isolation",  # Application Partitioning – keyword indicative of control sc-2
    "chroot",  # Application Partitioning – keyword indicative of control sc-2
    "container_partition",  # Application Partitioning – keyword indicative of control sc-2
]

sc2_python = [
    "NAMESPACE_ISOLATION",  # Application Partitioning – Python keyword maps to control sc-2
    "CHROOT",  # Application Partitioning – Python keyword maps to control sc-2
    "CONTAINER_PARTITION",  # Application Partitioning – Python keyword maps to control sc-2
]

sc2_golang = [
    "NamespaceIsolation",  # Application Partitioning – Golang keyword maps to control sc-2
    "Chroot",  # Application Partitioning – Golang keyword maps to control sc-2
    "ContainerPartition",  # Application Partitioning – Golang keyword maps to control sc-2
]

sc2_java = [
    "setNamespaceIsolation",  # Application Partitioning – Java keyword maps to control sc-2
    "setChroot",  # Application Partitioning – Java keyword maps to control sc-2
    "setContainerPartition",  # Application Partitioning – Java keyword maps to control sc-2
]

sc2_cpp = [
    "namespace_isolation_config",  # Application Partitioning – Cpp keyword maps to control sc-2
    "chroot_config",  # Application Partitioning – Cpp keyword maps to control sc-2
    "container_partition_config",  # Application Partitioning – Cpp keyword maps to control sc-2
]

sc23 = [
    "csrf_token",  # Session Authenticity – keyword indicative of control sc-23
    "session_cookie",  # Session Authenticity – keyword indicative of control sc-23
    "session_binding",  # Session Authenticity – keyword indicative of control sc-23
]

sc23_python = [
    "CSRF_TOKEN",  # Session Authenticity – Python keyword maps to control sc-23
    "SESSION_COOKIE",  # Session Authenticity – Python keyword maps to control sc-23
    "SESSION_BINDING",  # Session Authenticity – Python keyword maps to control sc-23
]

sc23_golang = [
    "CsrfToken",  # Session Authenticity – Golang keyword maps to control sc-23
    "SessionCookie",  # Session Authenticity – Golang keyword maps to control sc-23
    "SessionBinding",  # Session Authenticity – Golang keyword maps to control sc-23
]

sc23_java = [
    "setCsrfToken",  # Session Authenticity – Java keyword maps to control sc-23
    "setSessionCookie",  # Session Authenticity – Java keyword maps to control sc-23
    "setSessionBinding",  # Session Authenticity – Java keyword maps to control sc-23
]

sc23_cpp = [
    "csrf_token_config",  # Session Authenticity – Cpp keyword maps to control sc-23
    "session_cookie_config",  # Session Authenticity – Cpp keyword maps to control sc-23
    "session_binding_config",  # Session Authenticity – Cpp keyword maps to control sc-23
]

sc23_1 = [
    "csrf_token",  # Session Authenticity – keyword indicative of control sc-23.1
    "session_cookie",  # Session Authenticity – keyword indicative of control sc-23.1
    "session_binding",  # Session Authenticity – keyword indicative of control sc-23.1
]

sc23_1_python = [
    "CSRF_TOKEN",  # Session Authenticity – Python keyword maps to control sc-23.1
    "SESSION_COOKIE",  # Session Authenticity – Python keyword maps to control sc-23.1
    "SESSION_BINDING",  # Session Authenticity – Python keyword maps to control sc-23.1
]

sc23_1_golang = [
    "CsrfToken",  # Session Authenticity – Golang keyword maps to control sc-23.1
    "SessionCookie",  # Session Authenticity – Golang keyword maps to control sc-23.1
    "SessionBinding",  # Session Authenticity – Golang keyword maps to control sc-23.1
]

sc23_1_java = [
    "setCsrfToken",  # Session Authenticity – Java keyword maps to control sc-23.1
    "setSessionCookie",  # Session Authenticity – Java keyword maps to control sc-23.1
    "setSessionBinding",  # Session Authenticity – Java keyword maps to control sc-23.1
]

sc23_1_cpp = [
    "csrf_token_config",  # Session Authenticity – Cpp keyword maps to control sc-23.1
    "session_cookie_config",  # Session Authenticity – Cpp keyword maps to control sc-23.1
    "session_binding_config",  # Session Authenticity – Cpp keyword maps to control sc-23.1
]

sc23_3 = [
    "csrf_token",  # Session Authenticity – keyword indicative of control sc-23.3
    "session_cookie",  # Session Authenticity – keyword indicative of control sc-23.3
    "session_binding",  # Session Authenticity – keyword indicative of control sc-23.3
]

sc23_3_python = [
    "CSRF_TOKEN",  # Session Authenticity – Python keyword maps to control sc-23.3
    "SESSION_COOKIE",  # Session Authenticity – Python keyword maps to control sc-23.3
    "SESSION_BINDING",  # Session Authenticity – Python keyword maps to control sc-23.3
]

sc23_3_golang = [
    "CsrfToken",  # Session Authenticity – Golang keyword maps to control sc-23.3
    "SessionCookie",  # Session Authenticity – Golang keyword maps to control sc-23.3
    "SessionBinding",  # Session Authenticity – Golang keyword maps to control sc-23.3
]

sc23_3_java = [
    "setCsrfToken",  # Session Authenticity – Java keyword maps to control sc-23.3
    "setSessionCookie",  # Session Authenticity – Java keyword maps to control sc-23.3
    "setSessionBinding",  # Session Authenticity – Java keyword maps to control sc-23.3
]

sc23_3_cpp = [
    "csrf_token_config",  # Session Authenticity – Cpp keyword maps to control sc-23.3
    "session_cookie_config",  # Session Authenticity – Cpp keyword maps to control sc-23.3
    "session_binding_config",  # Session Authenticity – Cpp keyword maps to control sc-23.3
]

sc23_5 = [
    "csrf_token",  # Session Authenticity – keyword indicative of control sc-23.5
    "session_cookie",  # Session Authenticity – keyword indicative of control sc-23.5
    "session_binding",  # Session Authenticity – keyword indicative of control sc-23.5
]

sc23_5_python = [
    "CSRF_TOKEN",  # Session Authenticity – Python keyword maps to control sc-23.5
    "SESSION_COOKIE",  # Session Authenticity – Python keyword maps to control sc-23.5
    "SESSION_BINDING",  # Session Authenticity – Python keyword maps to control sc-23.5
]

sc23_5_golang = [
    "CsrfToken",  # Session Authenticity – Golang keyword maps to control sc-23.5
    "SessionCookie",  # Session Authenticity – Golang keyword maps to control sc-23.5
    "SessionBinding",  # Session Authenticity – Golang keyword maps to control sc-23.5
]

sc23_5_java = [
    "setCsrfToken",  # Session Authenticity – Java keyword maps to control sc-23.5
    "setSessionCookie",  # Session Authenticity – Java keyword maps to control sc-23.5
    "setSessionBinding",  # Session Authenticity – Java keyword maps to control sc-23.5
]

sc23_5_cpp = [
    "csrf_token_config",  # Session Authenticity – Cpp keyword maps to control sc-23.5
    "session_cookie_config",  # Session Authenticity – Cpp keyword maps to control sc-23.5
    "session_binding_config",  # Session Authenticity – Cpp keyword maps to control sc-23.5
]

sc24 = [
    "fail_closed",  # Fail in Known State – keyword indicative of control sc-24
    "fail_secure",  # Fail in Known State – keyword indicative of control sc-24
    "safe_state",  # Fail in Known State – keyword indicative of control sc-24
]

sc24_python = [
    "FAIL_CLOSED",  # Fail in Known State – Python keyword maps to control sc-24
    "FAIL_SECURE",  # Fail in Known State – Python keyword maps to control sc-24
    "SAFE_STATE",  # Fail in Known State – Python keyword maps to control sc-24
]

sc24_golang = [
    "FailClosed",  # Fail in Known State – Golang keyword maps to control sc-24
    "FailSecure",  # Fail in Known State – Golang keyword maps to control sc-24
    "SafeState",  # Fail in Known State – Golang keyword maps to control sc-24
]

sc24_java = [
    "setFailClosed",  # Fail in Known State – Java keyword maps to control sc-24
    "setFailSecure",  # Fail in Known State – Java keyword maps to control sc-24
    "setSafeState",  # Fail in Known State – Java keyword maps to control sc-24
]

sc24_cpp = [
    "fail_closed_config",  # Fail in Known State – Cpp keyword maps to control sc-24
    "fail_secure_config",  # Fail in Known State – Cpp keyword maps to control sc-24
    "safe_state_config",  # Fail in Known State – Cpp keyword maps to control sc-24
]

sc28 = [
    "luks",  # Protection of Information at Rest – keyword indicative of control sc-28
    "disk_encryption",  # Protection of Information at Rest – keyword indicative of control sc-28
    "data_at_rest_encryption",  # Protection of Information at Rest – keyword indicative of control sc-28
]

sc28_python = [
    "LUKS",  # Protection of Information at Rest – Python keyword maps to control sc-28
    "DISK_ENCRYPTION",  # Protection of Information at Rest – Python keyword maps to control sc-28
    "DATA_AT_REST_ENCRYPTION",  # Protection of Information at Rest – Python keyword maps to control sc-28
]

sc28_golang = [
    "Luks",  # Protection of Information at Rest – Golang keyword maps to control sc-28
    "DiskEncryption",  # Protection of Information at Rest – Golang keyword maps to control sc-28
    "DataAtRestEncryption",  # Protection of Information at Rest – Golang keyword maps to control sc-28
]

sc28_java = [
    "setLuks",  # Protection of Information at Rest – Java keyword maps to control sc-28
    "setDiskEncryption",  # Protection of Information at Rest – Java keyword maps to control sc-28
    "setDataAtRestEncryption",  # Protection of Information at Rest – Java keyword maps to control sc-28
]

sc28_cpp = [
    "luks_config",  # Protection of Information at Rest – Cpp keyword maps to control sc-28
    "disk_encryption_config",  # Protection of Information at Rest – Cpp keyword maps to control sc-28
    "data_at_rest_encryption_config",  # Protection of Information at Rest – Cpp keyword maps to control sc-28
]

sc28_1 = [
    "luks",  # Protection of Information at Rest – keyword indicative of control sc-28.1
    "disk_encryption",  # Protection of Information at Rest – keyword indicative of control sc-28.1
    "data_at_rest_encryption",  # Protection of Information at Rest – keyword indicative of control sc-28.1
]

sc28_1_python = [
    "LUKS",  # Protection of Information at Rest – Python keyword maps to control sc-28.1
    "DISK_ENCRYPTION",  # Protection of Information at Rest – Python keyword maps to control sc-28.1
    "DATA_AT_REST_ENCRYPTION",  # Protection of Information at Rest – Python keyword maps to control sc-28.1
]

sc28_1_golang = [
    "Luks",  # Protection of Information at Rest – Golang keyword maps to control sc-28.1
    "DiskEncryption",  # Protection of Information at Rest – Golang keyword maps to control sc-28.1
    "DataAtRestEncryption",  # Protection of Information at Rest – Golang keyword maps to control sc-28.1
]

sc28_1_java = [
    "setLuks",  # Protection of Information at Rest – Java keyword maps to control sc-28.1
    "setDiskEncryption",  # Protection of Information at Rest – Java keyword maps to control sc-28.1
    "setDataAtRestEncryption",  # Protection of Information at Rest – Java keyword maps to control sc-28.1
]

sc28_1_cpp = [
    "luks_config",  # Protection of Information at Rest – Cpp keyword maps to control sc-28.1
    "disk_encryption_config",  # Protection of Information at Rest – Cpp keyword maps to control sc-28.1
    "data_at_rest_encryption_config",  # Protection of Information at Rest – Cpp keyword maps to control sc-28.1
]

sc3 = [
    "seccomp",  # Security Function Isolation – keyword indicative of control sc-3
    "selinux_domain",  # Security Function Isolation – keyword indicative of control sc-3
    "security_isolation",  # Security Function Isolation – keyword indicative of control sc-3
]

sc3_python = [
    "SECCOMP",  # Security Function Isolation – Python keyword maps to control sc-3
    "SELINUX_DOMAIN",  # Security Function Isolation – Python keyword maps to control sc-3
    "SECURITY_ISOLATION",  # Security Function Isolation – Python keyword maps to control sc-3
]

sc3_golang = [
    "Seccomp",  # Security Function Isolation – Golang keyword maps to control sc-3
    "SelinuxDomain",  # Security Function Isolation – Golang keyword maps to control sc-3
    "SecurityIsolation",  # Security Function Isolation – Golang keyword maps to control sc-3
]

sc3_java = [
    "setSeccomp",  # Security Function Isolation – Java keyword maps to control sc-3
    "setSelinuxDomain",  # Security Function Isolation – Java keyword maps to control sc-3
    "setSecurityIsolation",  # Security Function Isolation – Java keyword maps to control sc-3
]

sc3_cpp = [
    "seccomp_config",  # Security Function Isolation – Cpp keyword maps to control sc-3
    "selinux_domain_config",  # Security Function Isolation – Cpp keyword maps to control sc-3
    "security_isolation_config",  # Security Function Isolation – Cpp keyword maps to control sc-3
]

sc39 = [
    "docker_container",  # Process Isolation – keyword indicative of control sc-39
    "pod_sandbox",  # Process Isolation – keyword indicative of control sc-39
    "process_namespace",  # Process Isolation – keyword indicative of control sc-39
]

sc39_python = [
    "DOCKER_CONTAINER",  # Process Isolation – Python keyword maps to control sc-39
    "POD_SANDBOX",  # Process Isolation – Python keyword maps to control sc-39
    "PROCESS_NAMESPACE",  # Process Isolation – Python keyword maps to control sc-39
]

sc39_golang = [
    "DockerContainer",  # Process Isolation – Golang keyword maps to control sc-39
    "PodSandbox",  # Process Isolation – Golang keyword maps to control sc-39
    "ProcessNamespace",  # Process Isolation – Golang keyword maps to control sc-39
]

sc39_java = [
    "setDockerContainer",  # Process Isolation – Java keyword maps to control sc-39
    "setPodSandbox",  # Process Isolation – Java keyword maps to control sc-39
    "setProcessNamespace",  # Process Isolation – Java keyword maps to control sc-39
]

sc39_cpp = [
    "docker_container_config",  # Process Isolation – Cpp keyword maps to control sc-39
    "pod_sandbox_config",  # Process Isolation – Cpp keyword maps to control sc-39
    "process_namespace_config",  # Process Isolation – Cpp keyword maps to control sc-39
]

sc4 = [
    "shared_memory_protection",  # Information in Shared Resources – keyword indicative of control sc-4
    "object_reuse",  # Information in Shared Resources – keyword indicative of control sc-4
    "clear_memory",  # Information in Shared Resources – keyword indicative of control sc-4
]

sc4_python = [
    "SHARED_MEMORY_PROTECTION",  # Information in Shared Resources – Python keyword maps to control sc-4
    "OBJECT_REUSE",  # Information in Shared Resources – Python keyword maps to control sc-4
    "CLEAR_MEMORY",  # Information in Shared Resources – Python keyword maps to control sc-4
]

sc4_golang = [
    "SharedMemoryProtection",  # Information in Shared Resources – Golang keyword maps to control sc-4
    "ObjectReuse",  # Information in Shared Resources – Golang keyword maps to control sc-4
    "ClearMemory",  # Information in Shared Resources – Golang keyword maps to control sc-4
]

sc4_java = [
    "setSharedMemoryProtection",  # Information in Shared Resources – Java keyword maps to control sc-4
    "setObjectReuse",  # Information in Shared Resources – Java keyword maps to control sc-4
    "setClearMemory",  # Information in Shared Resources – Java keyword maps to control sc-4
]

sc4_cpp = [
    "shared_memory_protection_config",  # Information in Shared Resources – Cpp keyword maps to control sc-4
    "object_reuse_config",  # Information in Shared Resources – Cpp keyword maps to control sc-4
    "clear_memory_config",  # Information in Shared Resources – Cpp keyword maps to control sc-4
]

sc5 = [
    "rate_limit",  # Denial of Service Protection – keyword indicative of control sc-5
    "dos_protection",  # Denial of Service Protection – keyword indicative of control sc-5
    "throttle",  # Denial of Service Protection – keyword indicative of control sc-5
]

sc5_python = [
    "RATE_LIMIT",  # Denial of Service Protection – Python keyword maps to control sc-5
    "DOS_PROTECTION",  # Denial of Service Protection – Python keyword maps to control sc-5
    "THROTTLE",  # Denial of Service Protection – Python keyword maps to control sc-5
]

sc5_golang = [
    "RateLimit",  # Denial of Service Protection – Golang keyword maps to control sc-5
    "DosProtection",  # Denial of Service Protection – Golang keyword maps to control sc-5
    "Throttle",  # Denial of Service Protection – Golang keyword maps to control sc-5
]

sc5_java = [
    "setRateLimit",  # Denial of Service Protection – Java keyword maps to control sc-5
    "setDosProtection",  # Denial of Service Protection – Java keyword maps to control sc-5
    "setThrottle",  # Denial of Service Protection – Java keyword maps to control sc-5
]

sc5_cpp = [
    "rate_limit_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5
    "dos_protection_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5
    "throttle_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5
]

sc5_1 = [
    "rate_limit",  # Denial of Service Protection – keyword indicative of control sc-5.1
    "dos_protection",  # Denial of Service Protection – keyword indicative of control sc-5.1
    "throttle",  # Denial of Service Protection – keyword indicative of control sc-5.1
]

sc5_1_python = [
    "RATE_LIMIT",  # Denial of Service Protection – Python keyword maps to control sc-5.1
    "DOS_PROTECTION",  # Denial of Service Protection – Python keyword maps to control sc-5.1
    "THROTTLE",  # Denial of Service Protection – Python keyword maps to control sc-5.1
]

sc5_1_golang = [
    "RateLimit",  # Denial of Service Protection – Golang keyword maps to control sc-5.1
    "DosProtection",  # Denial of Service Protection – Golang keyword maps to control sc-5.1
    "Throttle",  # Denial of Service Protection – Golang keyword maps to control sc-5.1
]

sc5_1_java = [
    "setRateLimit",  # Denial of Service Protection – Java keyword maps to control sc-5.1
    "setDosProtection",  # Denial of Service Protection – Java keyword maps to control sc-5.1
    "setThrottle",  # Denial of Service Protection – Java keyword maps to control sc-5.1
]

sc5_1_cpp = [
    "rate_limit_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5.1
    "dos_protection_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5.1
    "throttle_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5.1
]

sc5_2 = [
    "rate_limit",  # Denial of Service Protection – keyword indicative of control sc-5.2
    "dos_protection",  # Denial of Service Protection – keyword indicative of control sc-5.2
    "throttle",  # Denial of Service Protection – keyword indicative of control sc-5.2
]

sc5_2_python = [
    "RATE_LIMIT",  # Denial of Service Protection – Python keyword maps to control sc-5.2
    "DOS_PROTECTION",  # Denial of Service Protection – Python keyword maps to control sc-5.2
    "THROTTLE",  # Denial of Service Protection – Python keyword maps to control sc-5.2
]

sc5_2_golang = [
    "RateLimit",  # Denial of Service Protection – Golang keyword maps to control sc-5.2
    "DosProtection",  # Denial of Service Protection – Golang keyword maps to control sc-5.2
    "Throttle",  # Denial of Service Protection – Golang keyword maps to control sc-5.2
]

sc5_2_java = [
    "setRateLimit",  # Denial of Service Protection – Java keyword maps to control sc-5.2
    "setDosProtection",  # Denial of Service Protection – Java keyword maps to control sc-5.2
    "setThrottle",  # Denial of Service Protection – Java keyword maps to control sc-5.2
]

sc5_2_cpp = [
    "rate_limit_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5.2
    "dos_protection_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5.2
    "throttle_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5.2
]

sc5a = [
    "rate_limit",  # Denial of Service Protection – keyword indicative of control sc-5a
    "dos_protection",  # Denial of Service Protection – keyword indicative of control sc-5a
    "throttle",  # Denial of Service Protection – keyword indicative of control sc-5a
]

sc5a_python = [
    "RATE_LIMIT",  # Denial of Service Protection – Python keyword maps to control sc-5a
    "DOS_PROTECTION",  # Denial of Service Protection – Python keyword maps to control sc-5a
    "THROTTLE",  # Denial of Service Protection – Python keyword maps to control sc-5a
]

sc5a_golang = [
    "RateLimit",  # Denial of Service Protection – Golang keyword maps to control sc-5a
    "DosProtection",  # Denial of Service Protection – Golang keyword maps to control sc-5a
    "Throttle",  # Denial of Service Protection – Golang keyword maps to control sc-5a
]

sc5a_java = [
    "setRateLimit",  # Denial of Service Protection – Java keyword maps to control sc-5a
    "setDosProtection",  # Denial of Service Protection – Java keyword maps to control sc-5a
    "setThrottle",  # Denial of Service Protection – Java keyword maps to control sc-5a
]

sc5a_cpp = [
    "rate_limit_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5a
    "dos_protection_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5a
    "throttle_config",  # Denial of Service Protection – Cpp keyword maps to control sc-5a
]

sc8 = [
    "tls",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8
    "ssl",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8
    "https",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8
]

sc8_python = [
    "TLS",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8
    "SSL",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8
    "HTTPS",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8
]

sc8_golang = [
    "Tls",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8
    "Ssl",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8
    "Https",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8
]

sc8_java = [
    "setTls",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8
    "setSsl",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8
    "setHttps",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8
]

sc8_cpp = [
    "tls_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8
    "ssl_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8
    "https_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8
]

sc8_1 = [
    "tls",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8.1
    "ssl",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8.1
    "https",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8.1
]

sc8_1_python = [
    "TLS",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8.1
    "SSL",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8.1
    "HTTPS",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8.1
]

sc8_1_golang = [
    "Tls",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8.1
    "Ssl",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8.1
    "Https",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8.1
]

sc8_1_java = [
    "setTls",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8.1
    "setSsl",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8.1
    "setHttps",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8.1
]

sc8_1_cpp = [
    "tls_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8.1
    "ssl_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8.1
    "https_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8.1
]

sc8_2 = [
    "tls",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8.2
    "ssl",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8.2
    "https",  # Transmission Confidentiality and Integrity – keyword indicative of control sc-8.2
]

sc8_2_python = [
    "TLS",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8.2
    "SSL",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8.2
    "HTTPS",  # Transmission Confidentiality and Integrity – Python keyword maps to control sc-8.2
]

sc8_2_golang = [
    "Tls",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8.2
    "Ssl",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8.2
    "Https",  # Transmission Confidentiality and Integrity – Golang keyword maps to control sc-8.2
]

sc8_2_java = [
    "setTls",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8.2
    "setSsl",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8.2
    "setHttps",  # Transmission Confidentiality and Integrity – Java keyword maps to control sc-8.2
]

sc8_2_cpp = [
    "tls_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8.2
    "ssl_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8.2
    "https_config",  # Transmission Confidentiality and Integrity – Cpp keyword maps to control sc-8.2
]

si10 = [
    "input_validation",  # Information Input Validation – keyword indicative of control si-10
    "sanitize_input",  # Information Input Validation – keyword indicative of control si-10
    "validate_payload",  # Information Input Validation – keyword indicative of control si-10
]

si10_python = [
    "INPUT_VALIDATION",  # Information Input Validation – Python keyword maps to control si-10
    "SANITIZE_INPUT",  # Information Input Validation – Python keyword maps to control si-10
    "VALIDATE_PAYLOAD",  # Information Input Validation – Python keyword maps to control si-10
]

si10_golang = [
    "InputValidation",  # Information Input Validation – Golang keyword maps to control si-10
    "SanitizeInput",  # Information Input Validation – Golang keyword maps to control si-10
    "ValidatePayload",  # Information Input Validation – Golang keyword maps to control si-10
]

si10_java = [
    "setInputValidation",  # Information Input Validation – Java keyword maps to control si-10
    "setSanitizeInput",  # Information Input Validation – Java keyword maps to control si-10
    "setValidatePayload",  # Information Input Validation – Java keyword maps to control si-10
]

si10_cpp = [
    "input_validation_config",  # Information Input Validation – Cpp keyword maps to control si-10
    "sanitize_input_config",  # Information Input Validation – Cpp keyword maps to control si-10
    "validate_payload_config",  # Information Input Validation – Cpp keyword maps to control si-10
]

si10_3 = [
    "input_validation",  # Information Input Validation – keyword indicative of control si-10.3
    "sanitize_input",  # Information Input Validation – keyword indicative of control si-10.3
    "validate_payload",  # Information Input Validation – keyword indicative of control si-10.3
]

si10_3_python = [
    "INPUT_VALIDATION",  # Information Input Validation – Python keyword maps to control si-10.3
    "SANITIZE_INPUT",  # Information Input Validation – Python keyword maps to control si-10.3
    "VALIDATE_PAYLOAD",  # Information Input Validation – Python keyword maps to control si-10.3
]

si10_3_golang = [
    "InputValidation",  # Information Input Validation – Golang keyword maps to control si-10.3
    "SanitizeInput",  # Information Input Validation – Golang keyword maps to control si-10.3
    "ValidatePayload",  # Information Input Validation – Golang keyword maps to control si-10.3
]

si10_3_java = [
    "setInputValidation",  # Information Input Validation – Java keyword maps to control si-10.3
    "setSanitizeInput",  # Information Input Validation – Java keyword maps to control si-10.3
    "setValidatePayload",  # Information Input Validation – Java keyword maps to control si-10.3
]

si10_3_cpp = [
    "input_validation_config",  # Information Input Validation – Cpp keyword maps to control si-10.3
    "sanitize_input_config",  # Information Input Validation – Cpp keyword maps to control si-10.3
    "validate_payload_config",  # Information Input Validation – Cpp keyword maps to control si-10.3
]

si11a = [
    "error_masking",  # Error Handling – keyword indicative of control si-11a
    "generic_error",  # Error Handling – keyword indicative of control si-11a
    "exception_handling",  # Error Handling – keyword indicative of control si-11a
]

si11a_python = [
    "ERROR_MASKING",  # Error Handling – Python keyword maps to control si-11a
    "GENERIC_ERROR",  # Error Handling – Python keyword maps to control si-11a
    "EXCEPTION_HANDLING",  # Error Handling – Python keyword maps to control si-11a
]

si11a_golang = [
    "ErrorMasking",  # Error Handling – Golang keyword maps to control si-11a
    "GenericError",  # Error Handling – Golang keyword maps to control si-11a
    "ExceptionHandling",  # Error Handling – Golang keyword maps to control si-11a
]

si11a_java = [
    "setErrorMasking",  # Error Handling – Java keyword maps to control si-11a
    "setGenericError",  # Error Handling – Java keyword maps to control si-11a
    "setExceptionHandling",  # Error Handling – Java keyword maps to control si-11a
]

si11a_cpp = [
    "error_masking_config",  # Error Handling – Cpp keyword maps to control si-11a
    "generic_error_config",  # Error Handling – Cpp keyword maps to control si-11a
    "exception_handling_config",  # Error Handling – Cpp keyword maps to control si-11a
]

si11b = [
    "error_masking",  # Error Handling – keyword indicative of control si-11b
    "generic_error",  # Error Handling – keyword indicative of control si-11b
    "exception_handling",  # Error Handling – keyword indicative of control si-11b
]

si11b_python = [
    "ERROR_MASKING",  # Error Handling – Python keyword maps to control si-11b
    "GENERIC_ERROR",  # Error Handling – Python keyword maps to control si-11b
    "EXCEPTION_HANDLING",  # Error Handling – Python keyword maps to control si-11b
]

si11b_golang = [
    "ErrorMasking",  # Error Handling – Golang keyword maps to control si-11b
    "GenericError",  # Error Handling – Golang keyword maps to control si-11b
    "ExceptionHandling",  # Error Handling – Golang keyword maps to control si-11b
]

si11b_java = [
    "setErrorMasking",  # Error Handling – Java keyword maps to control si-11b
    "setGenericError",  # Error Handling – Java keyword maps to control si-11b
    "setExceptionHandling",  # Error Handling – Java keyword maps to control si-11b
]

si11b_cpp = [
    "error_masking_config",  # Error Handling – Cpp keyword maps to control si-11b
    "generic_error_config",  # Error Handling – Cpp keyword maps to control si-11b
    "exception_handling_config",  # Error Handling – Cpp keyword maps to control si-11b
]

si16 = [
    "aslr",  # Memory Protection – keyword indicative of control si-16
    "nx_bit",  # Memory Protection – keyword indicative of control si-16
    "stack_protector",  # Memory Protection – keyword indicative of control si-16
]

si16_python = [
    "ASLR",  # Memory Protection – Python keyword maps to control si-16
    "NX_BIT",  # Memory Protection – Python keyword maps to control si-16
    "STACK_PROTECTOR",  # Memory Protection – Python keyword maps to control si-16
]

si16_golang = [
    "Aslr",  # Memory Protection – Golang keyword maps to control si-16
    "NxBit",  # Memory Protection – Golang keyword maps to control si-16
    "StackProtector",  # Memory Protection – Golang keyword maps to control si-16
]

si16_java = [
    "setAslr",  # Memory Protection – Java keyword maps to control si-16
    "setNxBit",  # Memory Protection – Java keyword maps to control si-16
    "setStackProtector",  # Memory Protection – Java keyword maps to control si-16
]

si16_cpp = [
    "aslr_config",  # Memory Protection – Cpp keyword maps to control si-16
    "nx_bit_config",  # Memory Protection – Cpp keyword maps to control si-16
    "stack_protector_config",  # Memory Protection – Cpp keyword maps to control si-16
]

si4_12 = [
    "ids_alert",  # System Monitoring – keyword indicative of control si-4.12
    "siem_event",  # System Monitoring – keyword indicative of control si-4.12
    "intrusion_detection",  # System Monitoring – keyword indicative of control si-4.12
]

si4_12_python = [
    "IDS_ALERT",  # System Monitoring – Python keyword maps to control si-4.12
    "SIEM_EVENT",  # System Monitoring – Python keyword maps to control si-4.12
    "INTRUSION_DETECTION",  # System Monitoring – Python keyword maps to control si-4.12
]

si4_12_golang = [
    "IdsAlert",  # System Monitoring – Golang keyword maps to control si-4.12
    "SiemEvent",  # System Monitoring – Golang keyword maps to control si-4.12
    "IntrusionDetection",  # System Monitoring – Golang keyword maps to control si-4.12
]

si4_12_java = [
    "setIdsAlert",  # System Monitoring – Java keyword maps to control si-4.12
    "setSiemEvent",  # System Monitoring – Java keyword maps to control si-4.12
    "setIntrusionDetection",  # System Monitoring – Java keyword maps to control si-4.12
]

si4_12_cpp = [
    "ids_alert_config",  # System Monitoring – Cpp keyword maps to control si-4.12
    "siem_event_config",  # System Monitoring – Cpp keyword maps to control si-4.12
    "intrusion_detection_config",  # System Monitoring – Cpp keyword maps to control si-4.12
]

si5b = [
    "antivirus",  # Malicious Code Protection – keyword indicative of control si-5b
    "malware_scan",  # Malicious Code Protection – keyword indicative of control si-5b
    "malware_def",  # Malicious Code Protection – keyword indicative of control si-5b
]

si5b_python = [
    "ANTIVIRUS",  # Malicious Code Protection – Python keyword maps to control si-5b
    "MALWARE_SCAN",  # Malicious Code Protection – Python keyword maps to control si-5b
    "MALWARE_DEF",  # Malicious Code Protection – Python keyword maps to control si-5b
]

si5b_golang = [
    "Antivirus",  # Malicious Code Protection – Golang keyword maps to control si-5b
    "MalwareScan",  # Malicious Code Protection – Golang keyword maps to control si-5b
    "MalwareDef",  # Malicious Code Protection – Golang keyword maps to control si-5b
]

si5b_java = [
    "setAntivirus",  # Malicious Code Protection – Java keyword maps to control si-5b
    "setMalwareScan",  # Malicious Code Protection – Java keyword maps to control si-5b
    "setMalwareDef",  # Malicious Code Protection – Java keyword maps to control si-5b
]

si5b_cpp = [
    "antivirus_config",  # Malicious Code Protection – Cpp keyword maps to control si-5b
    "malware_scan_config",  # Malicious Code Protection – Cpp keyword maps to control si-5b
    "malware_def_config",  # Malicious Code Protection – Cpp keyword maps to control si-5b
]
