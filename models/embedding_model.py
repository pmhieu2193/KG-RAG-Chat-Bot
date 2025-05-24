import torch
from transformers import AutoModel, AutoTokenizer

class SimilarityModel:
    def __init__(self, model_name="vinai/phobert-base"):
        # Tải mô hình và tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    #ÁP DỤNG MAX POOLING THAY VÌ MEAN BOOLING
    def get_similarity(self, text1, text2):
        # Mã hóa các chuỗi
        inputs = self.tokenizer([text1, text2], return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Lấy vector từ lớp cuối cùng bằng max pooling
        embeddings = torch.max(outputs.last_hidden_state, dim=1).values
        # Tính cosine similarity
        cos_sim = torch.nn.functional.cosine_similarity(embeddings[0], embeddings[1], dim=0)
        return cos_sim.item()

class SimilarityFinder:
    def __init__(self, model):
        self.model = model

    def find_best_match(self, my_list, external_string, top_k):
        similarities = []

        for item in my_list:
            similarity = self.model.get_similarity(item, external_string)
            print(f"Độ tương đồng giữa '{item}' và '{external_string}': {similarity}")
            similarities.append((item, similarity))

        # Sắp xếp theo độ tương đồng giảm dần và lấy top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:top_k]

        return top_matches

#Test mô hình nhúng
if __name__ == "__main__":
    # Danh sách chuỗi tiếng Việt
    my_list = [
        "trường đại học sài gòn trực thuộc ubnd tp hồ chí minh",
        "trường đại học sài gòn chịu sự quản lý bộ giáo dục và đào tạo",
        "trường đại học sài gòn đào tạo kinh tế",
        "trường đại học sài gòn đào tạo kỹ thuật",
        "trường đại học sài gòn đào tạo công nghệ",
        "trường đại học sài gòn đào tạo văn hóa xã hội",
        "trường đại học sài gòn đào tạo chính trị",
        "trường đại học sài gòn đào tạo nghệ thuật",
        "trường đại học sài gòn đào tạo sư phạm",
        "trường đại học sài gòn cấp chứng chỉ bồi dưỡng nghiệp vụ sư phạm",
        "trường đại học sài gòn cấp chứng chỉ công nghệ thông tin",
        "trường đại học sài gòn cấp chứng chỉ tiếng anh",
        "trường đại học sài gòn được phép bộ giáo dục và đào tạo",
        "trường đại học sài gòn đón nhận huân chương lao động hạng ba",
        "trường đại học sài gòn được chứng nhận kiểm định chất lượng giáo dục"
    ]
    external_string = "trường đại học sài gòn trực thuộc cơ quan nào"

    # Khởi tạo mô hình và tìm kiếm
    similarity_model = SimilarityModel()
    finder = SimilarityFinder(similarity_model)
    best_match, highest_similarity = finder.find_best_match(my_list, external_string)

    print("---")
    print(f"Chuỗi tương đồng cao nhất: '{best_match}' với độ tương đồng: {highest_similarity}")