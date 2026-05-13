# TLS/SSL Protocol

## Overview
- **Full Name**: Transport Layer Security / Secure Sockets Layer
- **RFC**: TLS 1.3 - RFC 8446, TLS 1.2 - RFC 5246
- **OSI Layer**: Layer 6 (Presentation) / between Transport and Application
- **Difficulty**: Intermediate to Advanced

## What is TLS?
TLS (successor to SSL) provides encrypted communication channels. It ensures three properties: confidentiality (eavesdroppers can't read), integrity (data not modified), and authentication (server identity verified).

**Simple Analogy**: TLS is like a sealed, tamper-evident envelope that only the recipient can open, with a verified return address proving who sent it.

## TLS Handshake (TLS 1.3)
```
Client                              Server
  |---ClientHello------------------>|  Supported ciphers, TLS version, random, key share
  |<--ServerHello-------------------|  Selected cipher, random, key share
  |<--{EncryptedExtensions}---------|  Additional parameters (encrypted)
  |<--{Certificate}-----------------|  Server's X.509 certificate
  |<--{CertificateVerify}-----------|  Proof server holds private key
  |<--{Finished}-------------------|  Handshake complete
  |---{Finished}------------------>|  Client confirms
  |===Application Data (encrypted)===|
```

## TLS Record Types (Visible in PCAP)
| Content Type | Value | Description |
|--------------|-------|-------------|
| Change Cipher Spec | 20 | TLS 1.2 only: signals cipher change |
| Alert | 21 | Error or warning |
| Handshake | 22 | TLS handshake messages |
| Application Data | 23 | Encrypted payload |

## TLS Handshake Message Types
| Type | Value | Description |
|------|-------|-------------|
| ClientHello | 1 | Client's supported ciphers and extensions |
| ServerHello | 2 | Server's selected cipher |
| Certificate | 11 | Server's X.509 certificate chain |
| ServerKeyExchange | 12 | Key exchange parameters (TLS 1.2) |
| ServerHelloDone | 14 | End of server handshake (TLS 1.2) |
| ClientKeyExchange | 16 | Client's key exchange contribution (TLS 1.2) |
| Finished | 20 | Handshake verification |

## What's Visible in PCAP (Without Keys)
- **SNI (Server Name Indication)**: Domain name in ClientHello — reveals which site is accessed even over HTTPS
- **Certificate details**: Subject, issuer, validity period, SANs
- **Cipher suites offered/selected**: Security level of connection
- **TLS version**: 1.0 (deprecated), 1.1 (deprecated), 1.2, 1.3
- **Record sizes and timing**: Can reveal traffic patterns (not content)
- **Alert messages**: Connection errors (certificate invalid, etc.)

## What's Hidden (Encrypted)
- HTTP headers and body
- Actual URLs beyond the hostname
- Cookie values
- All application-layer data

## Cipher Suite Naming (TLS 1.2 example)
`TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
- **TLS**: Protocol
- **ECDHE**: Key exchange (Elliptic Curve Diffie-Hellman Ephemeral)
- **RSA**: Authentication (server cert signature algorithm)
- **AES_256_GCM**: Symmetric encryption algorithm
- **SHA384**: Hash for MAC/integrity

## TLS Versions
| Version | Status | Notes |
|---------|--------|-------|
| SSL 3.0 | Deprecated | POODLE attack |
| TLS 1.0 | Deprecated | BEAST attack |
| TLS 1.1 | Deprecated | No longer secure |
| TLS 1.2 | Current | Still widely used |
| TLS 1.3 | Current | Fastest, most secure, fewer roundtrips |

## Red Flags
- **TLS 1.0/1.1 usage**: Outdated, potentially vulnerable
- **Self-signed certificates**: No CA verification, possible MITM
- **Certificate expired**: Possible oversight or intentional evasion
- **Unusual cipher suites**: Weak encryption (RC4, DES, export ciphers)
- **Certificate mismatch (Alert 42)**: Possible MITM attack
- **Long certificate chains**: Unusual, potential abuse

## Why It Matters
TLS secures virtually all sensitive internet traffic. Understanding TLS handshakes helps detect downgrade attacks, certificate issues, and identify the type of encrypted traffic from metadata alone.

## Related Protocols
HTTP, SMTP, IMAP, TCP, X.509 certificates, OCSP
