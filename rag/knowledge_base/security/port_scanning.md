# Port Scanning

## Overview
Port scanning is a technique to discover which network ports on a host are open, closed, or filtered. It's used legitimately by network administrators and maliciously by attackers for reconnaissance.

**Difficulty**: Intermediate

## Types of Port Scans

### SYN Scan (Half-Open Scan) — Most Common
```
Scanner → SYN → Target
Target → SYN-ACK → Scanner (port OPEN)
Scanner → RST → Target (cancels connection, "half-open")

Target → RST → Scanner (port CLOSED)
No response (port FILTERED/FIREWALL)
```
- Never completes three-way handshake
- Stealthy — older firewalls may not log incomplete connections
- Requires root/admin privileges

### TCP Connect Scan
- Completes full three-way handshake
- More detectable (connection logged by target)
- Doesn't require privileges

### UDP Scan
```
Scanner → UDP packet → Target
Target → ICMP Port Unreachable → Scanner (port CLOSED)
No response (port OPEN or FILTERED)
```
- Slower and less reliable than TCP scans
- Important for services like DNS (53), SNMP (161)

### FIN/NULL/Xmas Scans
- Send packets with unusual flag combinations
- Designed to evade certain firewalls and IDS
- Open port: no response; Closed port: RST

## PCAP Signatures of Port Scans

### SYN Scan Pattern
- Same source IP → many different destination ports
- SYN flag only (no ACK)
- Rapid sequence of connections (milliseconds apart)
- Mix of RST responses (closed) and SYN-ACK (open)
- No data transfer after SYN-ACK

### Detection Metrics
- Port scan threshold: typically 15+ different ports in under 1 second
- Connection rate anomaly: much faster than human browsing
- Geographic anomaly: source IP in unusual location

## Tools That Produce Scan Traffic
- **Nmap**: Most common port scanner
  - `-sS`: SYN scan
  - `-sU`: UDP scan
  - `-sV`: Version detection
- **Masscan**: High-speed scanner
- **Zmap**: Internet-scale scanner

## Nmap in PCAP
Nmap SYN scan signature:
- IP TTL often 64 or 128
- IP ID = 0 (with OS detection probes)
- Window size = 1024
- TCP options: mss only (no timestamps, window scaling)

## Educational Significance
Port scans appear in PCAP captures when:
- Security team is doing authorized penetration testing
- Attacker is doing reconnaissance
- Automated vulnerability scanner is running
- Worm/malware is spreading laterally

## Red Flags
- SYN packets to many different ports from one source
- No corresponding connection completion
- Sequential port progression (1, 2, 3... or 21, 22, 23...)
- Rapid-fire timing (much faster than human interaction)
- Source IP with no prior legitimate traffic

## Why It Matters
Port scanning is usually the first step in an attack — attackers scan to find open services, then exploit vulnerabilities in those services.

## Related Concepts
TCP flags, SYN flood, firewall, IDS/IPS, network reconnaissance
