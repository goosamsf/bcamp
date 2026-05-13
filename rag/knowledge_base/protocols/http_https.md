# HTTP/HTTPS Protocol

## Overview
- **Full Name**: HyperText Transfer Protocol / HTTP Secure
- **RFC**: HTTP/1.1 - RFC 7230-7235, HTTP/2 - RFC 7540, HTTP/3 - RFC 9114
- **OSI Layer**: Layer 7 (Application), runs over TCP port 80 (HTTP) or 443 (HTTPS)
- **Difficulty**: Beginner

## What is HTTP?
HTTP is the protocol for transmitting web content. HTTPS is HTTP encrypted with TLS, ensuring confidentiality and integrity.

**Simple Analogy**: HTTP is like ordering food at a restaurant — you send a request (I want X), the server responds (here's X). HTTPS is the same but in a sealed, tamper-proof container that only you and the restaurant can read.

## HTTP Request Structure
```
METHOD /path HTTP/version\r\n
Header-Name: Header-Value\r\n
\r\n
[Optional Body]
```

Example:
```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Connection: keep-alive

```

## HTTP Response Structure
```
HTTP/version STATUS_CODE Status-Message\r\n
Header-Name: Header-Value\r\n
\r\n
[Response Body]
```

Example:
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1234
Server: nginx/1.18.0

<html>...</html>
```

## HTTP Methods
| Method | Purpose | Body? | Safe? | Idempotent? |
|--------|---------|-------|-------|-------------|
| GET | Retrieve resource | No | Yes | Yes |
| POST | Create/submit data | Yes | No | No |
| PUT | Replace resource | Yes | No | Yes |
| PATCH | Partial update | Yes | No | No |
| DELETE | Remove resource | No | No | Yes |
| HEAD | GET without body | No | Yes | Yes |
| OPTIONS | Allowed methods | No | Yes | Yes |

## HTTP Status Codes
| Code | Category | Examples |
|------|----------|---------|
| 1xx | Informational | 100 Continue |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirect | 301 Moved Permanently, 302 Found, 304 Not Modified |
| 4xx | Client Error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found |
| 5xx | Server Error | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable |

## Important HTTP Headers
- **Host**: Target server hostname (required in HTTP/1.1)
- **User-Agent**: Client software identification
- **Content-Type**: Format of body (application/json, text/html, etc.)
- **Content-Length**: Body size in bytes
- **Authorization**: Credentials (Bearer token, Basic auth)
- **Cookie/Set-Cookie**: Session state management
- **Cache-Control**: Caching directives
- **Transfer-Encoding**: chunked encoding for streaming

## HTTPS and TLS
HTTPS = HTTP + TLS encryption layer
- **TLS Handshake** establishes encrypted channel before HTTP traffic
- In PCAP: HTTPS traffic appears as opaque TLS Application Data records
- Only metadata visible: IP addresses, ports, SNI (Server Name Indication) in ClientHello
- Cannot see HTTP headers, URLs, or body content in HTTPS captures without decryption key

## HTTP/2 vs HTTP/1.1
| Feature | HTTP/1.1 | HTTP/2 |
|---------|----------|--------|
| Format | Text | Binary |
| Multiplexing | No (pipelining only) | Yes (multiple streams) |
| Header Compression | None | HPACK |
| Server Push | No | Yes |
| Connection | Multiple | Single multiplexed |

## Red Flags in HTTP Traffic
- **Cleartext passwords in GET params**: Credentials in URL visible in logs
- **Unusual User-Agent strings**: Possible scanner or malware
- **HTTP to known HTTPS services**: Downgrade attack
- **Large POST to unexpected URLs**: Possible data exfiltration
- **Many 4xx/5xx responses**: Brute force or broken application
- **HTTP on non-standard ports**: Possible C2 or tunneling

## Why It Matters
HTTP/HTTPS carries the majority of modern internet traffic. Security researchers analyze HTTP captures to detect data exfiltration, command-and-control traffic, and application vulnerabilities.

## Related Protocols
TLS/SSL, TCP, DNS, HTTP/2, WebSocket
