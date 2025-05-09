import textwrap
import google.generativeai as genai
import re


class LLM:
    def __init__(self, api_key, model_name):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def to_markdown(self, text):
        text = text.replace("•", "  *")
        return textwrap.indent(text, "> ", predicate=lambda _: True)


    def extract_entities(self, text):
        # Gửi yêu cầu sinh nội dung
        # gemini giới hạn đầu vào nên mình ko thể nhúng hoàn toàn bằng gemini mà phải qua một mô hình nhúng bên ngoài.
        prompt = "Thực hiện NER câu sau và đưa từng phần tử S, O vào từng dấu (), chỉ cần trích xuất S và 0 nếu có, giữ nguyên từ, không giải thích hay mô tả. Câu cần NER: "+text
        print("prompt = " + prompt)
        response_text = self.generate_response(prompt)
        markdown_text = self.to_markdown(response_text)
        #Tìm keyword từ () từ yêu cầu của promt
        matches = re.findall(r'\((.*?)\)', markdown_text)
        #Tại đây mình muốn trả về 1 cái list chứa các đôi tượng ner được
        return matches

    #Hàm để có phản hồi thân thiện hơn với người dùng và nhận biết câu trả lời không chính xác
    def get_smooth_answer(self, question, answer):
        # top_answers là list các câu trả lời
        top_answers_text = '; '.join(answer)
        #Nên bổ sung nếu câu trả lời không liên quan đến câu hỏi, phản hồi là trong dataset không có
        prompt = "Tôi có câu hỏi như sau: '" +question+ "' và một nhóm câu trả lời: '" +top_answers_text+ " ', hãy chọn những câu trả lời có ngữ cảnh liên quan đến câu hỏi nhất, sau đó viết lại câu trả lời cho câu hỏi trên một cách dễ hiểu, tự nhiên (chỉ hiển thị câu trả lời này, không giải thích gì thêm và kết thúc). Nếu không có câu trả lời nào phù hợp, hãy hiển thị mà không cần giải thích : 'Câu hỏi này nằm ngoài tập dữ liệu của tôi'"
        print("prompt = "+prompt)
        response_text = self.generate_response(prompt)
        markdown_text = self.to_markdown(response_text)
        print(markdown_text)
        # Tại đây mình muốn trả về 1 cái list chứa các đôi tượng ner được
        return markdown_text

#Test mô hình llm
if __name__ == "__main__":
    GEMINI_API_KEY = "AIzaSyDWeAfquhNPbsNxKAtGFvKDygJj4D5S6TI"
    model_name = "gemini-2.0-flash"

    bot = LLM(GEMINI_API_KEY, model_name)
    text = bot.extract_entities("'Trường đại học Sài Gòn cấp chứng chỉ tiếng anh'")