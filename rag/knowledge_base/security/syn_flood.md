# SYN Flood Attack

## Overview
A SYN flood is a type of Denial-of-Service (DoS) attack that exploits the TCP handshake to exhaust server resources.

**Difficulty**: Intermediate

## How SYN Flood Works

Normal TCP connection uses 3-way handshake:
```
Client → SYN → Server (Server allocates memory, enters SYN_RECEIVED)
Server → SYN-ACK → Client
Client → ACK → Server (Connection established, resource committed)
```

SYN Flood exploits the server's need to maintain state:
```
Attacker → SYN (spoofed src IP) → Server (Server allocates memory)
Server → SYN-ACK → Fake IP (no one there to respond)
Server waits for ACK... (holding memory for 75 seconds default)
Attacker → SYN (another fake IP) → Server (more memory allocated)
...repeat at high rate...
Server: OUT OF MEMORY — cannot accept new connections (DoS)
```

## PCAP Signature of SYN Flood
- Extremely high rate of SYN packets (thousands per second)
- Many different source IPs (spoofed) → all to same destination IP:port
- No SYN-ACK responses ever completed (no ACK received)
- Server's SYN-ACK queue fills up (half-open connections)
- Legitimate connections start failing

## Distinguishing SYN Flood from Port Scan
| Feature | SYN Flood | Port Scan |
|---------|-----------|-----------|
| Destination port | Same port | Many different ports |
| Source IPs | Many (spoofed) | Usually one |
| Intent | Exhaust resources | Discover open ports |
| Rate | Very high | Moderate |

## SYN Cookies (Defense)
The server encodes connection state in the SYN-ACK's sequence number:
- No memory allocated until ACK received
- ACK carries enough info to recreate state
- Immune to basic SYN floods
- Standard on Linux (enabled when backlog queue fills)

## Amplification Variant
- Use third-party servers as amplifiers
- Send SYN with spoofed IP = victim's IP
- Third-party servers → flood victim with SYN-ACK responses
- Victim overwhelmed by unsolicited SYN-ACKs

## Educational Value in PCAP
A SYN flood PCAP demonstrates:
1. High-rate packet injection
2. TCP state machine exploitation
3. IP address spoofing effects
4. The importance of SYN cookies

## Red Flags
- Packet rate far exceeding normal traffic (>1000 SYN/sec to one port)
- Source IPs don't respond to SYN-ACK
- All packets targeting same destination port
- Server resource exhaustion (no new connections succeed)
- IP TTL values inconsistent across "different" sources

## Why It Matters
SYN floods are among the oldest and most common DDoS techniques. Understanding the mechanism helps design defensive countermeasures (SYN cookies, rate limiting, IP reputation filtering).

## Related Concepts
TCP three-way handshake, DoS/DDoS, IP spoofing, SYN cookies, rate limiting
