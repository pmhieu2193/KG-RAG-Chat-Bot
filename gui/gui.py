import re
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import time  # Add this import at the top

from models import LLM
from database import Neo4jConnection, ChatHistory
from models import SimilarityModel, SimilarityFinder
from utils import LogHandler
from visualization import GraphVisualizer
from config import *

class ChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Bot")

        # Khai báo mô hình llm
        self.bot = LLM(GEMINI_API_KEY, model_name)

        # Kết nối Neo4j
        self.conn = Neo4jConnection(uri, user, password)
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

        # Create a frame for buttons in row 2
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Add history and show graph buttons to the frame
        self.history_button = ttk.Button(self.button_frame, text="Xem lịch sử", 
                                       command=self.show_history)
        self.history_button.pack(side=tk.LEFT, padx=5)

        self.show_graph_button = ttk.Button(self.button_frame, text="Hiển thị đồ thị", 
                                          command=self.show_graph, 
                                          state='disabled')
        self.show_graph_button.pack(side=tk.LEFT, padx=5)

        # Add execution time label in its own cell
        self.exec_time_label = ttk.Label(root, text="Thời gian thực thi: 0.00s")
        self.exec_time_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.start_time = 0  # Add this variable to track start time
        self.timer_id = None  # Add this variable to track the timer

        self.chat_history = ChatHistory()  # Add this line

        # Add graph visualizer
        self.graph_visualizer = GraphVisualizer()
        
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

        # Optional: Adjust column widths
        tree.column("Câu hỏi", width=300)  # Make question column wider
        tree.column("Câu trả lời", width=400)  # Make answer column even wider
        tree.column("Thời gian", width=150)  # Keep time column smaller

        tree.pack(fill=tk.BOTH, expand=True)

        # Load history from database
        history_data = self.chat_history.get_all_history()
        for row in history_data:
            question, answer, timestamp = row  # Unpack the tuple correctly
            tree.insert("", tk.END, values=(question, answer, timestamp))

    def send_message(self):
        user_message = self.message_entry.get()
        if user_message:
            self.start_time = time.time()
            self.display_message(f"Bạn: {user_message}")
            self.message_entry.delete(0, tk.END)
            self.last_bot_message_index = self.display_message("> Đang phản hồi...")
            
            # Start the continuous timer update
            self.update_timer()
            
            # Store the original question in an instance variable
            self.current_question = user_message
            
            # Start the response thread
            threading.Thread(target=self.get_bot_response, args=(user_message,)).start()

    def update_timer(self):
        # Cancel any existing timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.exec_time_label.config(text=f"Thời gian thực thi: {elapsed_time:.2f}s")
        
        # Schedule the next update in 100ms
        self.timer_id = self.root.after(100, self.update_timer)

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
            self.update_bot_response("> Xin lỗi tôi không hiểu câu hỏi của bạn \n")
            self.log.write_log("Không tìm thấy keyword để ner")
            self.log.write_log("> Xin lỗi tôi không hiểu câu hỏi của bạn")
            self.log.write_log("END \n")
            return
        print("Kết quả truy vấn: ")
        string_log = "Kết quả truy vấn: +\n";

        #Retriver (tìm kiếm câu trả lời trong neo4j)
        relationships_dict = self.conn.get_relationships(node_names)
        
        if relationships_dict:
            # Store raw relationships for graph visualization
            self.current_relationships_dict = relationships_dict
            # Process relationships for text display
            list_query_result = self.process_relationships(relationships_dict)
            # Enable show graph button
            self.show_graph_button.config(state='normal')
        else:
            self.show_graph_button.config(state='disabled')
            list_query_result = []
        
        list_query_result_string = ', '.join(list_query_result)
        string_log = string_log + list_query_result_string + "\n";
        if not list_query_result:
            print("Key word tìm được nằm ngoài KG")
            self.update_bot_response("> Xin lỗi, câu hỏi này nằm ngoài tập dữ liệu của tôi \n")
            self.log.write_log("Key word tìm được nằm ngoài KG")
            self.log.write_log("> Xin lỗi, câu hỏi này nằm ngoài tập dữ liệu của tôi")
            return
        print("Kết quả truy vấn: ")
        print(list_query_result)

        #Ranker (tìm top k câu trả lời có độ tương đồng cao nhất, các bước nhúng, tính độ tương đồng đều nằm trong này)
        top_matches = self.finder.find_best_match(list_query_result, user_message, TOP_K)
        # Lấy danh sách các câu trả lời thôi (bỏ similarity)
        top_answers = [item for item, sim in top_matches]
        print("TOP 5 câu trả lời có độ tương đồng cao nhất")
        string_log = string_log + "TOP "+ str(TOP_K)+" câu trả lời có độ tương đồng cao nhất: +\n"
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
        # Cancel the timer first
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
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

        matches = re.findall(r'\((.*?)\)', bot_response)
        print(matches)

        # Calculate and display final execution time
        end_time = time.time()
        exec_time = end_time - self.start_time
        self.exec_time_label.config(text=f"Thời gian thực thi: {exec_time:.2f}s")

        # Save conversation to database using the stored question
        self.chat_history.add_conversation(
            self.current_question,  # Use stored question instead of message_entry
            bot_response.strip()
        )
        
    def process_text(self, text):
        self.log.write_date_time()
        # Chuyển đổi thành chữ in hoa
        upper_text = text.upper()
        # Loại bỏ tất cả ký tự không phải là chữ cái, chữ số, dấu chấm và dấu cách
        cleaned_text = re.sub(r'[^A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶĐÊẾỀỂỄỆÔỐỒỔỖỘƠỚỜỞỬỮỪỨĨỊÌÍỈÓÒỌỎÕÈÉẺẸẺÙÚŨỦỤỲÝỶỸỶ0-9. ]', '', upper_text)
        print("Question: " + text)
        self.log.write_log("Question: " + text)
        print("Clean Question: " + cleaned_text)
        self.log.write_log("Clean Question: " + cleaned_text)
        return cleaned_text

    def process_relationships(self, relationships_dict):
        """Convert dictionary relationships to string format and clean underscores"""
        processed = []
        seen = set()  # Keep track of strings we've already seen
        
        for rel in relationships_dict:
            relation_str = f"{rel['node_start'].replace('_', ' ')} {rel['relationship'].replace('_', ' ')} {rel['node_end'].replace('_', ' ')}"
            
            # Only add if we haven't seen this string before
            if relation_str not in seen:
                seen.add(relation_str)
                processed.append(relation_str)
                
        print(f"Processed {len(relationships_dict)} relationships into {len(processed)} unique entries")
        return processed

    def show_graph(self):
        """Display the knowledge graph visualization"""
        print("\n=== Starting Graph Visualization ===")
        if hasattr(self, 'current_relationships_dict'):
            print(f"Found {len(self.current_relationships_dict)} relationships to display:")
            for rel in self.current_relationships_dict:
                print(f"- {rel['node_start']} --[{rel['relationship']}]--> {rel['node_end']}")
            
            self.graph_visualizer.create_graph(self.current_relationships_dict)
            self.graph_visualizer.show_graph()
        else:
            print("No relationships data available")

if __name__ == "__main__":
    root = tk.Tk()
    chat_bot = ChatBot(root)
    root.mainloop()