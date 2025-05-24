import os
from config import LOG_FILE_NAME
from datetime import datetime

class LogHandler:
    def __init__(self):
        self.log_file = LOG_FILE_NAME
        # Kiểm tra file, nếu chưa có thì tạo rỗng
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('')  # Tạo file rỗng
            print(f"Đã tạo file log mới: {self.log_file}")
        else:
            print(f"File log đã tồn tại: {self.log_file}")

    def write_log(self, message):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')  # Ghi thêm vào cuối file

    def write_date_time(self):
        # Lấy thời gian hiện tại
        now = datetime.now()
        # Định dạng thành chuỗi: Năm-Tháng-Ngày Giờ:Phút:Giây
        time_string = now.strftime("%Y-%m-%d %H:%M:%S")
        self.write_log("############### NEW LOG ##############")
        self.write_log(time_string)
