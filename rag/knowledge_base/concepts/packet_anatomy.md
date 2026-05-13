# Packet Anatomy

## Overview
A network packet is the fundamental unit of data transmission. Understanding packet structure is essential for network analysis.

**Difficulty**: Beginner to Intermediate

## What is a Packet?
A packet is a unit of data formatted for transmission over a network. It contains both the payload (actual data) and headers (metadata like addresses and control information).

**Simple Analogy**: A packet is like a letter in an envelope. The envelope has the sender's address, recipient's address, and stamps (headers). Inside is the actual message (payload).

## Ethernet Frame Structure
```
┌──────────────────────────────────────────────────────┐
│ Preamble (7B) │ SFD (1B) │ [Ethernet Frame] │ IFG   │
│               │           │                  │       │
│               │    ┌──────────────────────┐  │       │
│               │    │ Dst MAC (6B)         │  │       │
│               │    │ Src MAC (6B)         │  │       │
│               │    │ EtherType (2B)       │  │       │
│               │    │ [IP Packet]          │  │       │
│               │    │ FCS (4B)             │  │       │
│               │    └──────────────────────┘  │       │
└──────────────────────────────────────────────────────┘
```
- **Preamble**: Synchronization bits
- **SFD**: Start Frame Delimiter
- **Dst/Src MAC**: 48-bit hardware addresses (format: XX:XX:XX:XX:XX:XX)
- **EtherType**: 0x0800 = IPv4, 0x0806 = ARP, 0x86DD = IPv6
- **FCS**: Frame Check Sequence (CRC error detection)

## IPv4 Packet Inside Ethernet
```
┌────────────────────────────────────────┐
│ Version (4b) │ IHL (4b)               │
│ DSCP (6b)    │ ECN (2b)               │
│ Total Length (16b)                     │
│ Identification (16b)                   │
│ Flags (3b)   │ Fragment Offset (13b)  │
│ TTL (8b)     │ Protocol (8b)          │
│ Header Checksum (16b)                  │
│ Source IP Address (32b)               │
│ Destination IP Address (32b)          │
│ [Options if IHL > 5]                   │
│ [TCP/UDP/ICMP Segment]                │
└────────────────────────────────────────┘
```

## TCP Segment Inside IP
```
┌────────────────────────────────────────┐
│ Source Port (16b) │ Dst Port (16b)    │
│ Sequence Number (32b)                  │
│ Acknowledgment Number (32b)           │
│ Data Offset (4b) │ Reserved │ Flags  │
│ Window Size (16b)                      │
│ Checksum (16b)  │ Urgent Ptr (16b)   │
│ [Options]                              │
│ [Application Data / Payload]          │
└────────────────────────────────────────┘
```

## Key Fields at a Glance

### MAC Address
- 48 bits, 6 bytes, written as XX:XX:XX:XX:XX:XX
- First 3 bytes: OUI (manufacturer), last 3 bytes: device-specific
- ff:ff:ff:ff:ff:ff = broadcast (all devices on network)
- Only relevant within local network segment

### IP Address
- IPv4: 32 bits, written as dotted decimal (192.168.1.1)
- IPv6: 128 bits, written as colon-hex (2001:db8::1)
- Routable across the internet (unlike MAC addresses)

### TTL (Time To Live)
- Starts at 64 (Linux), 128 (Windows), 255 (network equipment)
- Decrements by 1 at each router hop
- Packet dropped and ICMP TTL Exceeded sent at TTL=0
- Helps infer OS or number of hops from source

### Sequence and Acknowledgment Numbers
- **Sequence**: Position in the byte stream (not packet number)
- **ACK**: "I've received everything up to this byte, send me byte N next"
- Relative sequence numbers shown in Wireshark by default (0-relative)

## Reading Wireshark Packet Details
```
Frame 42: 1514 bytes on wire, 1514 bytes captured
  → Packet number 42, full frame captured (not truncated)

Ethernet II, Src: Apple_11:22:33 (a4:83:e7:11:22:33), Dst: Cisco_44:55:66
  → Layer 2 info: MAC addresses, manufacturer OUI resolved

Internet Protocol Version 4, Src: 192.168.1.10, Dst: 8.8.8.8
  → Layer 3 info: IP addresses, TTL=64, Protocol=UDP

User Datagram Protocol, Src Port: 52841, Dst Port: 53
  → Layer 4 info: ports, length=30

Domain Name System (query)
  → Layer 7 info: DNS query for "www.google.com"
```

## Common Packet Sizes
- **Minimum Ethernet frame**: 64 bytes (padded if smaller)
- **Maximum Ethernet frame (MTU)**: 1514 bytes payload + 14 bytes header = 1518 bytes
- **Jumbo frames**: Up to 9000 bytes on some networks
- **DNS query**: 40-80 bytes typically
- **HTTP GET**: 200-800 bytes typically
- **Full data packet**: 1514 bytes (max MTU)

## Fragmentation
When a packet is larger than the MTU:
- IP splits it into fragments (each ≤ MTU size)
- Each fragment has same Identification field
- Fragment Offset indicates position in original
- Last fragment has MF (More Fragments) = 0
- Destination reassembles fragments

## Why It Matters
Reading packet fields accurately is the foundation of all network analysis. Every protocol, attack, and anomaly manifests as patterns in packet headers and payloads.

## Related Concepts
OSI layers, TCP/IP, Ethernet, fragmentation, MTU, Wireshark analysis
