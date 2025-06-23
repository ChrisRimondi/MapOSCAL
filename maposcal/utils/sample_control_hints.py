"""
This file contains sample keywords mapped to NIST 800-53 Control IDs.  These are used to identify which controls are likely applicable
to a certain configuration.  An example of this would be "tls", and it's applicability to the NIST 800-53' SC-8 Control.  This is sample
content only and limited to SC8 as a working example.
"""
# Generic SC8 strings mappings
sc8 = ['ssl', 'tls', 'https', 'starttls', 'openssl', 'boringssl', 'libressl', 'securetransport', 'schannel', 'gnutls', 'ssl_ctx', 'ssl_new', 'ssl_connect', 'dtls', 'tls.config', 'sslsocket', 'grpc.ssl_target_name_override', 'tm', 'alg_tcp_aes', 'cipher_suite', 'truststore', 'keystore', 'ssl_ctx_set_verify', 'tls_server_prefer_cipher_suites', 'client_min_tls_version', 'server_max_tls_version']
# Language-specific mappings
sc8_python = ['sslcontext', 'ssl.create_default_context', 'ssl.wrap_socket', 'ssl.sslcontext.wrap_socket', 'ssl.protocol_tls_client', 'ssl.protocol_tls_server', 'ssl.sslcontext.load_cert_chain', 'ssl.sslcontextontext.load_verify_locations', 'ssl.sslcontext.verify_mode', 'grpc.ssl_channel_credentials', 'grpc.ssl_server_credentials', 'ssl.cert_required']
sc8_golang = ['tls.config', ' tls.dial', 'tls.listen', 'http.transport.tlsclientconfig','crypto/tls']