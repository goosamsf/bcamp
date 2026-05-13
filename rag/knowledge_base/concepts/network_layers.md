# Network Layers: OSI and TCP/IP Models

## Overview
Network communication is organized into layers, where each layer handles specific functions and communicates only with adjacent layers.

**Difficulty**: Beginner

## OSI Model (7 Layers)

| Layer | Number | Name | Function | Example Protocols |
|-------|--------|------|----------|-------------------|
| Application | 7 | Application | User-facing services | HTTP, DNS, FTP, SMTP |
| Presentation | 6 | Presentation | Encoding, encryption, compression | TLS/SSL, JPEG, ASCII |
| Session | 5 | Session | Session management | NetBIOS, RPC |
| Transport | 4 | Transport | End-to-end communication | TCP, UDP |
| Network | 3 | Network | Logical addressing, routing | IP, ICMP, ARP |
| Data Link | 2 | Data Link | Physical addressing, framing | Ethernet, Wi-Fi, PPP |
| Physical | 1 | Physical | Bit transmission | Cables, radio waves |

## TCP/IP Model (4 Layers)

| Layer | Name | Equivalent OSI Layers | Protocols |
|-------|------|----------------------|-----------|
| 4 | Application | 5, 6, 7 | HTTP, DNS, TLS, FTP, SMTP |
| 3 | Transport | 4 | TCP, UDP |
| 2 | Internet | 3 | IP, ICMP |
| 1 | Network Access | 1, 2 | Ethernet, Wi-Fi |

## Encapsulation: How Layers Work Together

When you send an HTTP request, data is wrapped ("encapsulated") going down, unwrapped ("decapsulated") going up:

```
Application:  [HTTP Data]
Transport:    [TCP Header | HTTP Data]
Network:      [IP Header | TCP Header | HTTP Data]
Data Link:    [Ethernet Header | IP Header | TCP Header | HTTP Data | Ethernet Trailer]
Physical:     01100111 01001100 ... (bits)
```

**Simple Analogy**: Like Russian nesting dolls — your letter (data) goes inside an envelope (TCP), which goes inside a shipping box (IP), which goes into a delivery truck (Ethernet).

## Packet Anatomy in PCAP

When analyzing a PCAP packet, you see headers from each layer:

```
Frame 1: 74 bytes on wire
  Ethernet II: Src=00:11:22:33:44:55, Dst=66:77:88:99:AA:BB
    Internet Protocol: Src=192.168.1.10, Dst=93.184.216.34
      Transmission Control Protocol: Src Port=52341, Dst Port=80
        Hypertext Transfer Protocol: GET / HTTP/1.1
```

## Protocol Data Units (PDUs)
Each layer has its own term for the data it handles:
- Application: Message or Data
- Transport: Segment (TCP) or Datagram (UDP)
- Network: Packet
- Data Link: Frame
- Physical: Bit

## How to Identify Layer from PCAP
- **Ethernet header present**: Layer 2 captured (most PCAP captures)
- **IP header**: Layer 3 data
- **Port numbers**: Layer 4 (TCP or UDP)
- **Application content**: Layer 7 (HTTP, DNS, etc.)

## Why It Matters
Understanding layers helps you:
- Know where to look for specific information (IP addresses in Layer 3, ports in Layer 4)
- Understand encapsulation and decapsulation
- Diagnose problems at the right layer
- Understand how protocols interact and build upon each other

## Related Concepts
TCP/IP protocols, Ethernet, packet anatomy, encapsulation
