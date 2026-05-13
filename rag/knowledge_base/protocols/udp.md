# UDP Protocol

## Overview
- **Full Name**: User Datagram Protocol
- **RFC**: RFC 768
- **OSI Layer**: Layer 4 (Transport)
- **Difficulty**: Beginner

## What is UDP?
UDP is a connectionless, unreliable transport protocol. It sends data without establishing a connection, without guaranteeing delivery, and without ordering.

**Simple Analogy**: UDP is like dropping a postcard in a mailbox — you send it and hope it arrives, but you don't get a delivery confirmation. It's fast but unreliable.

## UDP Header Fields
- **Source Port** (16 bits): Sending application port
- **Destination Port** (16 bits): Target service port
- **Length** (16 bits): Header + data length in bytes (minimum 8)
- **Checksum** (16 bits): Optional error detection (mandatory in IPv6)

Total header size: only 8 bytes (vs TCP's 20+ bytes)

## When to Use UDP vs TCP
| Feature | UDP | TCP |
|---------|-----|-----|
| Connection | None | Established (3-way handshake) |
| Reliability | None | Guaranteed delivery |
| Ordering | None | In-order delivery |
| Speed | Faster | Slower (overhead) |
| Use case | Streaming, games, DNS | Web, email, file transfer |

## Common UDP Port Numbers
| Port | Service |
|------|---------|
| 53 | DNS queries |
| 67/68 | DHCP server/client |
| 69 | TFTP |
| 123 | NTP (time sync) |
| 161/162 | SNMP |
| 500 | IKE (VPN) |
| 514 | Syslog |
| 1194 | OpenVPN |
| 5353 | mDNS |

## Real-World Uses
- **DNS**: Quick queries don't need connection overhead
- **Video streaming**: Lost frames acceptable, retransmission would cause stuttering
- **Online gaming**: Low latency critical, some packet loss acceptable
- **VoIP**: Real-time voice cannot afford TCP's retransmission delays
- **NTP**: Simple time sync request-response

## Red Flags
- **Large UDP packets (>1500 bytes)**: May indicate DNS amplification attack
- **Many small UDP packets from one source**: Possible UDP flood
- **UDP on unusual ports**: May indicate tunneling or C2 communication
- **UDP with no established flow**: Unsolicited inbound UDP

## Why It Matters
UDP's simplicity and low overhead make it essential for real-time applications. Modern protocols like QUIC (HTTP/3) build reliability on top of UDP to avoid TCP's head-of-line blocking.

## Related Protocols
TCP, DNS, DHCP, NTP, QUIC
