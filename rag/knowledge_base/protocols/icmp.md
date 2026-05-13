# ICMP Protocol

## Overview
- **Full Name**: Internet Control Message Protocol
- **RFC**: RFC 792 (ICMPv4), RFC 4443 (ICMPv6)
- **OSI Layer**: Layer 3 (Network), encapsulated in IP
- **Difficulty**: Beginner

## What is ICMP?
ICMP is used by network devices to send error messages and operational information. It's the protocol behind the `ping` and `traceroute` utilities.

**Simple Analogy**: ICMP is like the postal service's return-to-sender notices. When a packet can't be delivered, ICMP sends back a message explaining why.

## ICMP Header
- **Type** (1 byte): Category of message
- **Code** (1 byte): Subcategory
- **Checksum** (2 bytes): Error detection
- **Rest of Header** (4 bytes): Type-specific data
- **Data**: Variable, often includes original IP header + first 8 bytes of offending packet

## Common ICMP Types
| Type | Code | Name | Description |
|------|------|------|-------------|
| 0 | 0 | Echo Reply | Response to ping |
| 3 | 0-15 | Dest Unreachable | Cannot deliver packet |
| 3 | 0 | Net Unreachable | No route to network |
| 3 | 1 | Host Unreachable | Host not responding |
| 3 | 3 | Port Unreachable | UDP port closed |
| 3 | 4 | Fragmentation Needed | Packet too large, DF set |
| 4 | 0 | Source Quench | Slow down (deprecated) |
| 5 | 0-3 | Redirect | Better route exists |
| 8 | 0 | Echo Request | Ping request |
| 11 | 0 | TTL Exceeded | Traceroute hop reply |
| 12 | 0 | Parameter Problem | Bad IP header |

## Ping Operation
```
Host A sends: Type=8 (Echo Request), identifier=X, sequence=1
Host B responds: Type=0 (Echo Reply), identifier=X, sequence=1
RTT = time from request to reply
```

## Traceroute Operation
```
Probe TTL=1: Router 1 sends ICMP TTL Exceeded → we know Router 1's IP
Probe TTL=2: Router 2 sends ICMP TTL Exceeded → we know Router 2's IP
...
Probe TTL=N: Destination sends ICMP Port Unreachable → path complete
```

## Red Flags
- **ICMP flood (ping flood)**: Many echo requests — DDoS attempt
- **ICMP from many sources to one host**: Smurf attack or reflection DDoS
- **Large ICMP payloads**: Ping of death (historical) or data exfiltration via ICMP tunnel
- **ICMP redirect messages**: May indicate routing manipulation
- **High rate of ICMP unreachable**: Network misconfiguration or active scanning
- **ICMP tunneling**: Data encoded in ICMP echo request/reply payload for covert channel

## ICMP Tunneling
Attackers can use ICMP to create covert channels:
- Encode data in echo request/reply payload
- Bypass firewalls that allow ICMP
- Detection: unusual payload content, high frequency, non-standard payload sizes

## Why It Matters
ICMP is essential for network diagnostics but is also used in various attacks. Understanding ICMP behavior helps distinguish legitimate diagnostics from attack traffic.

## Related Protocols
IP, UDP, IPv6 (ICMPv6 adds NDP, MLD), TCP
