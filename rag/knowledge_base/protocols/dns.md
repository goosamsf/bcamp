# DNS Protocol

## Overview
- **Full Name**: Domain Name System
- **RFC**: RFC 1034, RFC 1035
- **OSI Layer**: Layer 7 (Application), runs over UDP port 53 (or TCP for large responses)
- **Difficulty**: Beginner to Intermediate

## What is DNS?
DNS translates human-readable domain names (like google.com) into IP addresses (like 142.250.185.78) that computers use to route traffic.

**Simple Analogy**: DNS is the internet's phone book. Just as you look up someone's name to find their phone number, DNS looks up a website name to find its IP address.

## DNS Message Structure
- **Header** (12 bytes): ID, flags, question/answer/authority/additional counts
- **Question Section**: Query name, type (A, AAAA, MX, etc.), class (IN=Internet)
- **Answer Section**: Resource records answering the query
- **Authority Section**: NS records for authoritative servers
- **Additional Section**: Extra helpful records

## DNS Header Flags
- **QR**: 0=Query, 1=Response
- **OPCODE**: 0=Standard query, 1=Inverse query, 2=Status
- **AA**: Authoritative Answer
- **TC**: Truncated (response too large for UDP, use TCP)
- **RD**: Recursion Desired
- **RA**: Recursion Available
- **RCODE**: Response code (0=OK, 3=NXDOMAIN, 2=SERVFAIL)

## DNS Record Types
| Type | Description | Example |
|------|-------------|---------|
| A | IPv4 address | google.com → 142.250.185.78 |
| AAAA | IPv6 address | google.com → 2607:f8b0::200e |
| MX | Mail server | gmail.com → alt1.gmail-smtp-in.l.google.com |
| CNAME | Alias | www.example.com → example.com |
| TXT | Text record | SPF, DKIM verification |
| NS | Name server | example.com NS ns1.example.com |
| PTR | Reverse lookup | 1.1.1.1 → one.one.one.one |
| SOA | Zone authority | Primary NS, serial, refresh times |

## DNS Resolution Process
```
Browser                Resolver              Root NS            TLD NS          Auth NS
  |--"google.com?"-------->|
                            |--"google.com?"-->|
                            |<--"Try .com TLD NS"--|
                            |--"google.com?"------------>|
                            |<--"Try google.com NS"-----------|
                            |--"google.com?"------------------------->|
                            |<--"142.250.185.78"----------------------|
  |<--"142.250.185.78"------|
```

## DNS in PCAP Captures
- **Request**: UDP source port = ephemeral, destination port = 53, QR=0
- **Response**: UDP source port = 53, destination port = client ephemeral, QR=1
- **TTL field**: How long to cache the response (seconds)
- **Transaction ID**: 16-bit value matching request to response

## Red Flags
- **DNS queries to unusual IPs**: May indicate DNS hijacking or rogue resolvers
- **Very long domain names**: Possible DNS tunneling (data encoded in subdomain labels)
- **High query rate**: DNS flood or misconfigured client
- **NXDOMAIN responses**: Client looking for non-existent domains (possible DGA malware)
- **Large TXT record responses**: Possible DNS amplification attack vector
- **DNS over non-standard ports**: Possible tunneling or evasion

## DNS Tunneling Pattern
Attackers encode data in DNS queries to bypass firewalls:
- Long subdomains: `base64encodeddata.c2server.evil.com`
- High query frequency
- Uncommon record types (TXT, NULL)
- Queries to single domain with many variations

## Why It Matters
DNS is fundamental to all internet communication. It's also a common attack vector: DNS spoofing, cache poisoning, tunneling, and amplification attacks all exploit DNS.

## Related Protocols
UDP, TCP, DNSSEC, DoH (DNS over HTTPS), DoT (DNS over TLS)
