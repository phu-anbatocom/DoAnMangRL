# DoAnMangRL
# Đồ Án Mạng Máy Tính: Tối Ưu Định Tuyến Bằng Học Tăng Cường (Reinforcement Learning)

Đây là mã nguồn cho đồ án môn học Mạng Máy Tính, tập trung vào việc áp dụng các thuật toán Học tăng cường để tìm ra đường đi tối ưu trong một mạng giả lập, so sánh hiệu quả với các giao thức định tuyến truyền thống.

## Mục Tiêu Của Đồ Án

*   **Xây dựng mô hình mạng giả lập:** Tạo ra một topo mạng có thể tùy chỉnh (10-20 router) bằng công cụ Mininet.
*   **Áp dụng Học tăng cường:** Triển khai các thuật toán như Q-learning và Deep Q-Network (DQN) để "dạy" cho các router cách chọn đường đi tối ưu.
*   **Tối ưu hóa các chỉ số mạng:** Mục tiêu của mô hình RL là giảm thiểu độ trễ (latency) và tỉ lệ mất gói (packet loss), đồng thời tối đa hóa thông lượng (throughput).
*   **So sánh hiệu năng:** Đối chiếu kết quả của phương pháp RL với giao thức định tuyến OSPF trong các kịch bản mạng khác nhau (bình thường, có sự cố đứt link).
*   **Định tuyến động:** Hệ thống phải có khả năng tự động cập nhật bảng định tuyến khi trạng thái mạng thay đổi.

## Công Nghệ Sử Dụng

*   **Giả lập mạng:** Mininet
*   **Ngôn ngữ lập trình:** Python 3.x
*   **Thư viện Học sâu:** PyTorch
*   **Môi trường phát triển:** Windows Subsystem for Linux (WSL2) - Ubuntu

## Cài Đặt & Thiết Lập Môi Trường

Để chạy được dự án này, bạn cần thiết lập môi trường trên WSL2.

### 1. Yêu cầu tiên quyết

*   Đã cài đặt WSL2 trên Windows.
*   Đã cài đặt bản phân phối Ubuntu từ Microsoft Store.

### 2. Cài đặt các gói hệ thống cần thiết

Mở terminal WSL/Ubuntu và chạy các lệnh sau để cài đặt Mininet và các công cụ mạng cần thiết mà chúng ta đã gỡ lỗi:

# Cập nhật danh sách gói
sudo apt update

# Cài đặt Mininet và các công cụ đi kèm
sudo apt install mininet

# Cài đặt Open vSwitch để quản lý switch
sudo apt install openvswitch-switch

# Cài đặt các công cụ đồ họa và chẩn đoán mạng
sudo apt install xterm traceroute

### 3. Cài đặt các thư viện Python

Dự án này sử dụng các thư viện được liệt kê trong file `requirements.txt`.

# Cài đặt pip nếu chưa có
sudo apt install python3-pip

# Cài đặt các thư viện từ file requirements.txt
pip3 install -r requirements.txt
*(Ghi chú: Bạn có thể tạo file `requirements.txt` bằng lệnh `pip3 freeze > requirements.txt` sau khi đã cài đặt torch, numpy...)*

## Cách Sử Dụng

Tất cả các lệnh sau đều được chạy từ thư mục gốc của dự án trong terminal WSL.

### 1. Chạy các kịch bản Demo

Luôn chạy lệnh `reset` và `sudo mn -c` trước khi chuyển đổi giữa các kịch bản để đảm bảo môi trường sạch.

*   **Thí nghiệm đo băng thông và nút cổ chai:**
    # Dọn dẹp môi trường
    sudo mn -c
    
    # Chạy kịch bản (sử dụng -E nếu cần xterm)
    sudo -E python3 bandwidth_test.py

*   **Thí nghiệm định tuyến tĩnh và sự cố đứt link:**
    # Dọn dẹp môi trường
    sudo mn -c
    
    # Chạy kịch bản
    sudo -E python3 static_routing.py

### 2. Huấn luyện mô hình RL (Sau khi hoàn thành)

# Chạy file huấn luyện chính
sudo python3 main.py


## Cấu Trúc Thư Mục

.
├── main.py                # File chính để huấn luyện mô hình DQN
├── topology.py            # Định nghĩa các topo mạng Mininet
├── bandwidth_test.py      # Kịch bản demo đo băng thông
├── static_routing.py      # Kịch bản demo định tuyến tĩnh
├── trained_models/        # Thư mục để lưu các mô hình đã huấn luyện
└── README.md              # File tài liệu này```

## Tác Giả
Hà Minh Phú - 2312646
Nguyễn Mai Huy Phát - 2312589
