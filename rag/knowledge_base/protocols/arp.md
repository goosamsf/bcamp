# ARP Protocol

## Overview
- **Full Name**: Address Resolution Protocol
- **RFC**: RFC 826
- **OSI Layer**: Layer 2/3 boundary (DataLink/Network)
- **Difficulty**: Beginner

## What is ARP?
ARP translates IP addresses (Layer 3) to MAC addresses (Layer 2). When a device wants to send a packet to an IP address on the local network, it first uses ARP to find the corresponding MAC address.

**Simple Analogy**: ARP is like shouting "Hey! Who has the phone number 192.168.1.5? Tell me your desk number!" in an office. The person at that IP address replies "That's me! I'm at desk B4-23-45-67-89-AB."

## ARP Packet Structure
- **Hardware Type** (2 bytes): 1 = Ethernet
- **Protocol Type** (2 bytes): 0x0800 = IPv4
- **Hardware Address Length** (1 byte): 6 for MAC
- **Protocol Address Length** (1 byte): 4 for IPv4
- **Operation** (2 bytes): 1 = Request, 2 = Reply
- **Sender MAC** (6 bytes): MAC of requester
- **Sender IP** (4 bytes): IP of requester
- **Target MAC** (6 bytes): 00:00:00:00:00:00 in requests (unknown)
- **Target IP** (4 bytes): IP being looked up

## ARP Process
```
Host A (192.168.1.10)              Host B (192.168.1.20)
Broadcast:                                  |
"Who has 192.168.1.20?"     ----------->   |
                                            |
                            <-----------    |
                            "192.168.1.20 is at AA:BB:CC:DD:EE:FF"
```

## Gratuitous ARP
A device sends an ARP reply without a request — announces its own IP-to-MAC mapping.
- Used during IP address assignment
- Used to update ARP caches when MAC changes (e.g., failover)
- Abused in ARP spoofing attacks

## ARP Cache
Every device maintains an ARP cache (table of IP→MAC mappings):
- Entries expire after 60-300 seconds typically
- `arp -n` shows current cache on Linux
- Cache poisoning = attacker inserts false entries

## Red Flags (ARP Attacks)
- **Gratuitous ARPs flooding the network**: Possible ARP spoofing/poisoning
- **Same IP with multiple different MACs**: ARP conflict or spoofing
- **ARP replies without corresponding requests**: Gratuitous ARP, possible poisoning
- **Gateway IP mapped to unexpected MAC**: Classic MITM attack setup
- **High rate of ARP broadcasts**: Network misconfiguration or ARP storm

## ARP Spoofing Attack
```
Attacker tells Host A: "I (Attacker) am the gateway"
Attacker tells Gateway: "I (Attacker) am Host A"
→ All traffic between Host A and Gateway flows through Attacker (MITM)
```

## Why It Matters
ARP operates at the foundation of local network communication. ARP spoofing is one of the most common LAN-level attacks, enabling man-in-the-middle attacks, session hijacking, and traffic interception.

## Related Protocols
IP, Ethernet, IPv6 NDP (replaces ARP in IPv6)
