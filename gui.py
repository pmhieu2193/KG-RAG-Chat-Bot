import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog

from llm import LLM
from neo4j_connect import Neo4jConnection, RelationshipFinder
from embedding_model import SimilarityModel, SimilarityFinder
from LogHandler import LogHandler
import threading  # Thêm import cho threading
import re
import config
import random
from datetime import datetime

#SỬA LỖI CHÍNH TẢ, LỌC INPUT
#TRƯỜNG HỢP ĐỌC ĐƯỢC NHƯNG KO CÓ TRONG DATASET
#TRƯỜNG HỢP KHÔNG TRÍCH XUẤT ĐƯỢC THỰC THỂ -> HÌNH NHƯ LÀ KHÔNG HIỂU ĐƯỢC CÂU HỎI CỦA BẠN
#Xủ lý khi có chuỗi trống ở so độ tuong dồng
#Lấy rank top 5, hoặc top 3
#KG-RAG

class ChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Bot")

        # Khai báo mô hình llm
        self.bot = LLM(config.GEMINI_API_KEY, config.model_name)

        # Kết nối Neo4j
        self.conn = Neo4jConnection(config.uri, config.user, config.password)
        if self.conn.driver is None:
            self.show_error(self.conn.get_error_message())
            sys.exit()

        # Mô hình nhúng
        self.similarity_model = SimilarityModel()
        self.finder = SimilarityFinder(self.similarity_model)

        # Ghi Log
        self.log = LogHandler()

        # GUI
        self.chat_area = scrolledtext.ScrolledText(root, state='disabled', wrap='word', width=50, height=20)
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.message_entry = ttk.Entry(root, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = ttk.Button(root, text="Gửi", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Nút Update
        self.update_button = ttk.Button(root, text="Update", command=self.show_update_menu)
        self.update_button.grid(row=2, column=0, padx=10, pady=10)

        # Nút Xem lịch sử
        self.history_button = ttk.Button(root, text="Xem lịch sử", command=self.show_history)
        self.history_button.grid(row=2, column=1, padx=10, pady=10)

    def show_history(self):
        # Tạo cửa sổ mới
        history_window = tk.Toplevel(self.root)
        history_window.title("Lịch sử câu hỏi")

        # Tạo Treeview
        columns = ("Câu hỏi", "Câu trả lời", "Thời gian")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        tree.pack(fill=tk.BOTH, expand=True)

        # Dữ liệu mẫu
        sample_data = [
            ("đại học sài gòn có đào tao cntt không ?", "Có"),
            ("đại học sài gòn nhận huân chương nào", "> Đại học Sài Gòn được nhận Huân chương Lao động hạng Ba."),
            ("Đại học Sài Gòn có cơ sở 4 không", "Không có cơ sở 4"),
            ("abc xyz", "Xin lỗi tôi không hiểu câu hỏi của bạn"),
            ("Đại học Sài Gòn có bao nhiêu sinh viên", "Câu hỏi này nằm ngoài tập dữ liệu của tôi"),
        ]

        # Tạo giờ ngẫu nhiên cho cột thời gian
        for question, answer in sample_data:
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            time_str = f"{random_hour:02d}:{random_minute:02d}"
            tree.insert("", tk.END, values=(question, answer, time_str))

    def show_update_menu(self):
        # Tạo cửa sổ popup
        update_window = tk.Toplevel(self.root)
        update_window.title("Chọn chức năng cập nhật")

        # Các nút lựa chọn
        ttk.Button(update_window, text="Thêm Node và quan hệ", command=self.add_node_relation_form).pack(padx=10, pady=5)
        ttk.Button(update_window, text="Cập nhật Node", command=self.update_node_form).pack(padx=10, pady=5)
        ttk.Button(update_window, text="Xóa Node và quan hệ thuộc Node", command=self.delete_node_form).pack(padx=10, pady=5)
        ttk.Button(update_window, text="Xóa quan hệ giữa 2 Node", command=self.delete_relation_form).pack(padx=10, pady=5)

    # ➡️ Form nhập cho từng chức năng:
    def add_node_relation_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Thêm Node và Quan hệ")

        # Label và Entry cho Node 1
        tk.Label(form_window, text="Tên Node 1:").grid(row=0, column=0, padx=5, pady=5)
        node1_entry = ttk.Entry(form_window)
        node1_entry.grid(row=0, column=1, padx=5, pady=5)

        # Label và Entry cho Quan hệ
        tk.Label(form_window, text="Tên Quan hệ:").grid(row=1, column=0, padx=5, pady=5)
        relation_entry = ttk.Entry(form_window)
        relation_entry.grid(row=1, column=1, padx=5, pady=5)

        # Label và Entry cho Node 2
        tk.Label(form_window, text="Tên Node 2:").grid(row=2, column=0, padx=5, pady=5)
        node2_entry = ttk.Entry(form_window)
        node2_entry.grid(row=2, column=1, padx=5, pady=5)

        def submit():
            node1 = node1_entry.get()
            relation = relation_entry.get()
            node2 = node2_entry.get()

            if node1 and relation and node2:
                messagebox.showinfo("Thành công", "Đã thêm node và quan hệ!")
                form_window.destroy()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")

        # Nút Submit
        submit_button = ttk.Button(form_window, text="Thêm", command=submit)
        submit_button.grid(row=3, column=0, columnspan=2, pady=10)

    def update_node_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Cập nhật Node")

        tk.Label(form_window, text="Tên Node cũ:").grid(row=0, column=0, padx=5, pady=5)
        old_name_entry = ttk.Entry(form_window)
        old_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_window, text="Tên Node mới:").grid(row=1, column=0, padx=5, pady=5)
        new_name_entry = ttk.Entry(form_window)
        new_name_entry.grid(row=1, column=1, padx=5, pady=5)

        def submit():
            old_name = old_name_entry.get()
            new_name = new_name_entry.get()

            if old_name and new_name:
                messagebox.showinfo("Thành công", "Đã cập nhật node!")
                form_window.destroy()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")

        submit_button = ttk.Button(form_window, text="Cập nhật", command=submit)
        submit_button.grid(row=2, column=0, columnspan=2, pady=10)

    def delete_node_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Xóa Node")

        tk.Label(form_window, text="Tên Node cần xóa:").grid(row=0, column=0, padx=5, pady=5)
        node_entry = ttk.Entry(form_window)
        node_entry.grid(row=0, column=1, padx=5, pady=5)

        def submit():
            node = node_entry.get()

            if node:
                messagebox.showinfo("Thành công", "Đã xóa node và các quan hệ liên quan!")
                form_window.destroy()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập tên node!")

        submit_button = ttk.Button(form_window, text="Xóa", command=submit)
        submit_button.grid(row=1, column=0, columnspan=2, pady=10)

    def delete_relation_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Xóa Quan hệ giữa 2 Node")

        tk.Label(form_window, text="Tên Node 1:").grid(row=0, column=0, padx=5, pady=5)
        node1_entry = ttk.Entry(form_window)
        node1_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_window, text="Tên Quan hệ:").grid(row=1, column=0, padx=5, pady=5)
        relation_entry = ttk.Entry(form_window)
        relation_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_window, text="Tên Node 2:").grid(row=2, column=0, padx=5, pady=5)
        node2_entry = ttk.Entry(form_window)
        node2_entry.grid(row=2, column=1, padx=5, pady=5)

        #Chưa xử lý cho các hàm submit form
        def submit():
            node1 = node1_entry.get()
            relation = relation_entry.get()
            node2 = node2_entry.get()

            if node1 and relation and node2:
                messagebox.showinfo("Thành công", "Đã xóa quan hệ giữa 2 node!")
                form_window.destroy()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")

        submit_button = ttk.Button(form_window, text="Xóa", command=submit)
        submit_button.grid(row=3, column=0, columnspan=2, pady=10)

    def send_message(self):
        user_message = self.message_entry.get()
        if user_message:
            self.display_message(f"Bạn: {user_message}")
            self.message_entry.delete(0, tk.END)

            # Hiển thị trạng thái "đang phản hồi..."
            self.last_bot_message_index = self.display_message("> Đang phản hồi...")

            # Tạo một luồng mới để gọi bot
            threading.Thread(target=self.get_bot_response, args=(user_message,)).start()

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

        # Trả về chỉ số dòng của tin nhắn vừa được thêm
        return self.chat_area.index(tk.END)

    def show_error(self, message):
        messagebox.showerror("Lỗi", message)

    #Đây nên là hàm final
    #Chưa gọi hàm xử lý đầu vào (mới gọi hàm xử lý kí tự đặc biệt và chuyển thành in hoa)
    def get_bot_response(self, user_message):
        #Gọi hàm log
        # Tiền xử lý đầu vào: loại bỏ ký tự đặc biệt, chuyển câu hỏi thành thành in hoa
        user_message = self.process_text(user_message)
        # Logic phản hồi của bot
        # Gọi LLM để ner câu hỏi
        #node_names là là danh sách key_word được tìm thấy từ câu hỏi
        node_names = self.bot.extract_entities(user_message)
        print("Keyword tìm được sau khi ner: ")
        print(node_names)
        node_names_string = ', '.join(node_names)
        self.log.write_log("Keyword tìm được sau khi ner: \n" + node_names_string)
        if not node_names:
            print("Không tìm thấy keyword để ner")
            self.update_bot_response("> Xin lỗi tôi không hiểu câu hỏi của bạn")
            self.log.write_log("Không tìm thấy keyword để ner")
            self.log.write_log("> Xin lỗi tôi không hiểu câu hỏi của bạn")
            self.log.write_log("END \n")
            return
        print("Kết quả truy vấn: ")
        string_log = "Kết quả truy vấn: +\n";

        #Retriver (tìm kiếm câu trả lời trong neo4j)
        list_query_result = self.conn.get_relationships(node_names)
        list_query_result_string = ', '.join(list_query_result)
        string_log = string_log + list_query_result_string + "\n";
        if not list_query_result:
            print("Key word tìm được nằm ngoài KG")
            self.update_bot_response("> Xin lỗi, câu hỏi này nằm ngoài tập dữ liệu của tôi")
            self.log.write_log("Key word tìm được nằm ngoài KG")
            self.log.write_log("> Xin lỗi, câu hỏi này nằm ngoài tập dữ liệu của tôi")
            return
        print("Kết quả truy vấn: ")
        print(list_query_result)

        #Ranker (tìm top k câu trả lời có độ tương đồng cao nhất, các bước nhúng, tính độ tương đồng đều nằm trong này)
        top_matches = self.finder.find_best_match(list_query_result, user_message, config.TOP_K)
        # Lấy danh sách các câu trả lời thôi (bỏ similarity)
        top_answers = [item for item, sim in top_matches]
        print("TOP 5 câu trả lời có độ tương đồng cao nhất")
        string_log = string_log + "TOP "+ str(config.TOP_K)+" câu trả lời có độ tương đồng cao nhất: +\n"
        string_top = ""
        for item, similarity in top_matches:
            string_top = string_top + f"Mục: {item}, Độ tương đồng: {similarity} \n"
            print(f"Mục: {item}, Độ tương đồng: {similarity}")
        string_log = string_log + string_top
        # Truyền câu hỏi và ngữ cảnh để sinh câu trả lời
        bot_response = self.bot.get_smooth_answer(user_message, top_answers)
        string_log = string_log + bot_response

        # Cập nhật giao diện người dùng từ luồng chính
        self.root.after(0, self.update_bot_response, bot_response)
        #Cập nhật log
        self.log.write_log(string_log)


    def update_bot_response(self, bot_response):
        # Cập nhật phản hồi bot
        self.chat_area.config(state='normal')

        # Xóa dòng "Đang phản hồi..."
        last_line_index = self.chat_area.index(tk.END + "-1c")  # Lấy chỉ số của dòng cuối
        self.chat_area.delete(last_line_index + "-1l", last_line_index)  # Xóa dòng cuối cùng

        #Tu day tro xuong nen tach tham ham rieng
        # Thêm phản hồi thực tế
        self.display_message(bot_response)
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

        #Đưa các thực thể NER được vào list
        #Có nên lưu trữ các câu hỏi và câu trả lời vào database không?
        #1 cuộc trò chuyện sẽ có nhiều câu hỏi và trả lời
        #1 người có nhiều cuộc trò chuyện.
        matches = re.findall(r'\((.*?)\)', bot_response)
        print(matches)

    def process_text(self, text):
        self.log.write_date_time()
        # Chuyển đổi thành chữ in hoa
        upper_text = text.upper()
        # Loại bỏ tất cả ký tự không phải là chữ cái, chữ số, dấu chấm và dấu cách
        cleaned_text = re.sub(r'[^A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶĐÊẾỀỂỄỆÔỐỒỔỖỘƠỚỜỞỠỢÒÓÒỎỌÍÌỊÝỲỶỸUÚÙỦỤŨƯỨỪỬỰỮ0-9. ]', '', upper_text)
        print("Question: " + text)
        self.log.write_log("Question: " + text)
        print("Clean Question: " + cleaned_text)
        self.log.write_log("Clean Question: " + cleaned_text)
        return cleaned_text

if __name__ == "__main__":
    root = tk.Tk()
    chat_bot = ChatBot(root)
    root.mainloop()