# TCP/IP Protocol

## Overview
- **Full Name**: Transmission Control Protocol / Internet Protocol
- **RFC**: TCP - RFC 793, IP - RFC 791
- **OSI Layer**: TCP = Layer 4 (Transport), IP = Layer 3 (Network)
- **Difficulty**: Beginner to Intermediate

## What is TCP/IP?
TCP/IP is the foundational communication protocol suite of the internet. IP handles addressing and routing of packets, while TCP ensures reliable, ordered, and error-checked delivery.

**Simple Analogy**: IP is like the postal address system — it knows where to send things. TCP is like a certified mail service — it confirms every package arrived and asks for resend if something is lost.

## IP Header Fields
- **Version** (4 bits): IPv4 or IPv6
- **IHL** (4 bits): Header length in 32-bit words
- **DSCP/ECN** (8 bits): Quality of service and congestion notification
- **Total Length** (16 bits): Total packet length in bytes
- **Identification** (16 bits): Fragment grouping identifier
- **Flags** (3 bits): Don't Fragment (DF), More Fragments (MF)
- **Fragment Offset** (13 bits): Position within original datagram
- **TTL** (8 bits): Time To Live — decrements at each router hop, packet dropped at 0
- **Protocol** (8 bits): Encapsulated protocol (6=TCP, 17=UDP, 1=ICMP)
- **Header Checksum** (16 bits): Error detection for header
- **Source IP** (32 bits): Sender's IP address
- **Destination IP** (32 bits): Recipient's IP address

## TCP Header Fields
- **Source Port** (16 bits): Sending application port (1024-65535 for ephemeral)
- **Destination Port** (16 bits): Target service port (e.g., 80=HTTP, 443=HTTPS)
- **Sequence Number** (32 bits): Byte position of first data byte in segment
- **Acknowledgment Number** (32 bits): Next expected sequence number from peer
- **Data Offset** (4 bits): Header length in 32-bit words
- **Flags** (9 bits): SYN, ACK, FIN, RST, PSH, URG, ECE, CWR, NS
- **Window Size** (16 bits): Receive buffer size (flow control)
- **Checksum** (16 bits): Error detection for header + data
- **Urgent Pointer** (16 bits): Offset to urgent data if URG flag set

## TCP Flags Explained
- **SYN**: Synchronize — initiates connection, carries initial sequence number
- **ACK**: Acknowledge — confirms receipt of data, carries acknowledgment number
- **FIN**: Finish — initiates graceful connection termination
- **RST**: Reset — abruptly terminates connection (error condition)
- **PSH**: Push — deliver data to application immediately without buffering
- **URG**: Urgent — urgent data present, check urgent pointer

## TCP Three-Way Handshake
```
Client                    Server
  |----SYN (seq=x)-------->|   Step 1: Client initiates
  |<---SYN+ACK (seq=y, ack=x+1)---|   Step 2: Server responds
  |----ACK (ack=y+1)------->|   Step 3: Client confirms
  |====== DATA TRANSFER =====|
```

## TCP Four-Way Termination
```
Client                    Server
  |----FIN---------------->|   Step 1: Client done sending
  |<---ACK-----------------|   Step 2: Server acknowledges
  |<---FIN-----------------|   Step 3: Server done sending
  |----ACK---------------->|   Step 4: Client acknowledges
```

## Common TCP Port Numbers
| Port | Service | Protocol |
|------|---------|----------|
| 20/21 | FTP Data/Control | FTP |
| 22 | SSH | SSH |
| 23 | Telnet | Telnet |
| 25 | Email sending | SMTP |
| 80 | Web HTTP | HTTP |
| 143 | Email receiving | IMAP |
| 443 | Web HTTPS | HTTPS |
| 3306 | MySQL | MySQL |
| 5432 | PostgreSQL | PostgreSQL |
| 6379 | Redis | Redis |
| 8080 | Alternative HTTP | HTTP |

## Red Flags (Anomalous Behaviors)
- **SYN without ACK response**: Possible port scan or firewall drop
- **RST after SYN**: Port closed or connection rejected
- **Many SYN from one source**: Possible SYN flood DDoS attack
- **TTL=1 or very low TTL**: Possible traceroute or TTL manipulation
- **Window size = 0**: Flow control pause, receiver buffer full
- **Retransmissions**: Network congestion or packet loss
- **Out-of-order sequence numbers**: Network reordering or replay attack

## Why It Matters
TCP/IP is responsible for virtually all internet traffic. Understanding it helps diagnose connectivity issues, understand security vulnerabilities, and design robust network applications.

## Related Protocols
UDP, HTTP, HTTPS, TLS, DNS, ICMP
