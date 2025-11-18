# P2PMSG Guide (RunIT CLI v1.3.2)

This guide explains how to use the `p2pmsg` command for encrypted peer-to-peer messaging, and how to troubleshoot connectivity across local networks and the internet.

## What p2pmsg does
- Encrypted chat using AES‑256‑CBC; the symmetric key is derived from a 16‑digit session code.
- Direct UDP communication with a simple handshake and NAT hole‑punch keepalives.
- No messages are stored; a small `data/p2p_sessions.json` cache only tracks session metadata.

## Quick Start

### Same PC (one device, two terminals)
1. Open two terminals in the project directory.
2. Terminal A (Host): run `python main.py`, type `p2pmsg`, choose `h`.
   - Copy the session code and the listening port.
3. Terminal B (Guest): run `python main.py`, type `p2pmsg`, choose `g`.
   - Enter the same session code.
   - Enter `localhost` (or leave empty) for Host IP — it defaults to `127.0.0.1`.
   - Enter the Host’s printed listening port.
4. You should see handshake confirmations on both sides, then you can chat. Type `/exit` to close.

### Same LAN (two devices on same Wi‑Fi/router)
1. On the Host device: run `python main.py` → `p2pmsg` → `h` and note the port.
2. Find the Host’s LAN IPv4 (on Windows: `ipconfig` → look for `IPv4 Address`, e.g., `192.168.1.23`).
3. On the Guest device: run `python main.py` → `p2pmsg` → `g`.
   - Enter the Host’s session code.
   - Enter the Host’s LAN IP (e.g., `192.168.1.23`).
   - Enter the Host’s port.
4. If it doesn’t connect, check Windows Firewall on the Host: allow inbound UDP for the given port or allow Python.

### Across the Internet (different networks)
Direct UDP P2P over the internet depends on NAT and firewall policies. Follow these steps:
1. Host runs `p2pmsg` in Host mode and notes the port.
2. Determine Host’s public IP (shown by the tool or via https://www.ipify.org).
3. Configure the Host’s router to forward the chosen UDP port to the Host PC’s LAN IP (port forwarding). Steps vary by router:
   - Log into the router admin page.
   - Find Port Forwarding / NAT / Virtual Server.
   - Add a rule: Protocol `UDP`; External Port = Host port; Internal IP = Host PC LAN IP; Internal Port = same Host port.
   - Save and apply.
4. On Windows Firewall (Host):
   - Open Windows Defender Firewall → Advanced Settings → Inbound Rules.
   - Add a New Rule → Port → UDP → Specific local ports = Host port → Allow → apply to Private/Public as needed → Name it (e.g., RunIT p2pmsg UDP).
5. Guest runs `p2pmsg` in Guest mode:
   - Enter the session code.
   - Enter the Host’s public IP.
   - Enter the Host’s forwarded UDP port.
6. After port forwarding and firewall allow, the handshake should complete and chat starts.

## Common Issues and Fixes
- No handshake / timeout
  - Same PC: ensure Guest uses `127.0.0.1` and the exact Host port.
  - Same LAN: use the Host’s LAN IP, not the public IP; verify both devices can ping each other.
  - Internet: confirm router UDP port forwarding and Windows Firewall inbound rule for the port. Double‑check the Host’s LAN IP in the router rule.
- Using the wrong IP
  - Public IP is only for internet peers; LAN peers need the Host’s LAN IP (`192.168.x.x`, `10.x.x.x`, or `172.16‑31.x.x`).
- CGNAT or strict NAT
  - Some ISPs place you behind CGNAT; inbound connections won’t reach you even with router rules. Solutions:
    - Ask ISP for a public IPv4 or use IPv6 if both ends support it.
    - Use a VPN that provides a public port (e.g., Zerotier/Tailscale with subnet routers or services that offer UDP hole‑punch relay).
- Firewall blocks
  - Temporarily test with Windows Firewall off to confirm the diagnosis. Then add a specific inbound UDP rule for the Host port instead of leaving the firewall off.
- Unstable ports
  - The Host currently binds to a random UDP port per session. For stable forwarding, you can edit `commands/p2pmsg.py` to bind a fixed port: change `self.sock.bind(('0.0.0.0', 0))` to a specific port like `self.sock.bind(('0.0.0.0', 45000))` and forward that port in your router.

## Best Practices
- Share only the session code and port with your peer; never share logs or cache files.
- Prefer LAN IPs for same‑network peers and `127.0.0.1` for same‑device tests.
- For internet peers, verify port forwarding and firewall rules before testing.
- Keep `deps/dependencies.txt` installed so cryptography works (`install_deps.bat`).

## Security Notes
- AES‑256‑CBC with a per‑message random IV; key is derived from the session code via SHA‑256.
- Messages are not stored; only minimal session metadata is cached.
- Anyone who knows your session code during the session could attempt to connect; treat codes as sensitive and end sessions with `/exit`.

## Quick Checklist (Internet)
- Host port forwarding: UDP external→internal to Host PC.
- Host Windows Firewall: allow inbound UDP for that port.
- Guest uses Host public IP and that exact port.
- If still failing, suspect CGNAT or strict NAT; try VPN or request public IPv4 from ISP.