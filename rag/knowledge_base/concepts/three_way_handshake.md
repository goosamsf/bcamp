# TCP Three-Way Handshake

## Overview
The TCP three-way handshake is the process used to establish a reliable TCP connection between two endpoints before data transfer begins.

**Difficulty**: Beginner

## Why Three Steps?
Both sides must agree on initial sequence numbers and confirm they can send and receive. Three messages achieve this minimum negotiation.

**Simple Analogy**: 
- Person A calls Person B: "Hello, can you hear me?" (SYN)
- Person B responds: "Yes, I hear you. Can you hear me?" (SYN-ACK)
- Person A confirms: "Yes, I hear you too!" (ACK)
- Now both parties know the line works in both directions.

## Detailed Steps

### Step 1: SYN (Synchronize)
```
Client → Server: TCP [SYN] seq=1000
```
- Client chooses a random Initial Sequence Number (ISN): e.g., 1000
- SYN flag set, no ACK flag
- Client enters SYN_SENT state

### Step 2: SYN-ACK (Synchronize-Acknowledge)
```
Server → Client: TCP [SYN, ACK] seq=5000, ack=1001
```
- Server chooses its own ISN: e.g., 5000
- ACK=1001 means "I received up to byte 1000, expecting byte 1001 next"
- Both SYN and ACK flags set
- Server enters SYN_RECEIVED state

### Step 3: ACK (Acknowledge)
```
Client → Server: TCP [ACK] seq=1001, ack=5001
```
- Client acknowledges server's ISN
- ACK=5001 means "I received up to byte 5000, expecting byte 5001 next"
- Only ACK flag set
- Both sides enter ESTABLISHED state

## State Machine
```
Client States:          Server States:
CLOSED                  LISTEN
  ↓ (send SYN)           ↓ (receive SYN, send SYN-ACK)
SYN_SENT               SYN_RECEIVED
  ↓ (receive SYN-ACK,    ↓ (receive ACK)
     send ACK)
ESTABLISHED            ESTABLISHED
```

## What Gets Negotiated
During the handshake, clients and servers also negotiate:
- **MSS (Maximum Segment Size)**: Largest TCP segment each side will accept
- **Window Scale**: Scale factor for window size (for large bandwidth-delay products)
- **SACK (Selective ACK)**: Enable selective retransmission
- **Timestamps**: For RTT measurement and PAWS (Protection Against Wrapped Sequences)

## Detecting Handshakes in PCAP
Look for this pattern in Wireshark/packet captures:
1. Packet with SYN flag only (no ACK) → connection initiation
2. Packet with SYN+ACK flags → server responding
3. Packet with ACK only (no SYN) → handshake complete

## Half-Open Connections
If SYN is sent but no SYN-ACK received:
- Port may be closed (RST received instead)
- Port may be filtered (no response, firewall dropping)
- Server may be unreachable

Many SYNs without corresponding SYN-ACKs = possible SYN scan or SYN flood attack.

## Connection Teardown (Four-Way)
After the three-way handshake establishes connection, closing requires four messages:
```
Client → FIN  (I'm done sending)
Server → ACK  (Got it)
Server → FIN  (I'm done sending too)
Client → ACK  (Got it, connection closed)
```

## Why It Matters
Every TCP connection starts with this handshake. Seeing many half-open handshakes (SYN without SYN-ACK) or unusual patterns reveals scanning, attacks, or connectivity issues.

## Related Concepts
TCP flags, sequence numbers, TCP state machine, SYN flood, port scanning
