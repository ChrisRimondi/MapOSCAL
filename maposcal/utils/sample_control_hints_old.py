"""
This file contains sample keywords mapped to NIST 800-53 Control IDs.  These are used to identify which controls are likely applicable
to a certain configuration.  An example of this would be "tls", and it's applicability to the NIST 800-53' SC-8 Control.  This is sample
content only and limited to SC8 as a working example.
"""

global sc8
global sc8_golang
global sc8_python
global sc8_java
global sc8_cpp

# Generic SC8 strings mappings
sc8 = [
    "ssl",
    "tls",
    "https",
    "starttls",
    "openssl",
    "boringssl",
    "libressl",
    "securetransport",
    "schannel",
    "gnutls",
    "ssl_ctx",
    "ssl_new",
    "ssl_connect",
    "dtls",
    "tls.config",
    "sslsocket",
    "grpc.ssl_target_name_override",
    "tm",
    "alg_tcp_aes",
    "cipher_suite",
    "truststore",
    "keystore",
    "ssl_ctx_set_verify",
    "tls_server_prefer_cipher_suites",
    "client_min_tls_version",
    "server_max_tls_version",
]
# Language-specific mappings (Python, Golang, Java, C++)
sc8_python = [
    "sslcontext",
    "ssl.create_default_context",
    "ssl.wrap_socket",
    "ssl.sslcontext.wrap_socket",
    "ssl.protocol_tls_client",
    "ssl.protocol_tls_server",
    "ssl.sslcontext.load_cert_chain",
    "ssl.sslcontextontext.load_verify_locations",
    "ssl.sslcontext.verify_mode",
    "grpc.ssl_channel_credentials",
    "grpc.ssl_server_credentials",
    "ssl.cert_required",
]
sc8_golang = [
    "tls.config",
    " tls.dial",
    "tls.listen",
    "http.transport.tlsclientconfig",
    "crypto/tls",
]
sc8_java = [
    "sslsocket",
    "sslcontext",
    "keystore",
    "truststore",
    "httpsurlconnection",
    "sslserversocket",
    "sslparameters",
    'sslcontext.getinstance("tls")',
    "sslcontext.init",
    "sslengine",
    "keymanagerfactory",
    "trustmanagerfactory",
    "sslcontext.setdefault",
    "sslcontext.getdefault",
    'system.setproperty("https.protocols")',
    'system.setproperty("javax.net.ssl.truststore")',
    'system.setproperty("javax.net.ssl.keystore")',
]
sc8_cpp = [
    "ssl_ctx",
    "ssl_new",
    "ssl_connect",
    "ssl_accept",
    "ssl_write",
    "ssl_load_error_strings",
    "ssl_library_init",
    "openssl_init_ssl",
    "bio_new_ssl_connect",
    "ssl_ctx_new",
    "ssl_ctx_use_certificate_file",
    "ssl_ctx_use_privatekey_file",
    "ssl_ctx_set_verify",
    "ssl_ctx_load_verify_locations",
    "tls_method",
    "bio_s_mem",
]
