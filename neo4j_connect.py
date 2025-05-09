from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError
import sys

class Neo4jConnection:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Kiểm tra kết nối
            self.test_connection()
        except (AuthError, ServiceUnavailable) as e:
            self.error_message = f"Lỗi kết nối đến Neo4j: {str(e)}"
            print(f"Lỗi kết nối đến Neo4j: {e}")
            self.driver = None
        except Exception as e:
            self.error_message = f"Đã xảy ra lỗi không xác định: {str(e)}"
            print(f"Đã xảy ra lỗi không xác định: {e}")
            self.driver = None

    def get_error_message(self):
        return self.error_message

    def test_connection(self):
        with self.driver.session() as session:
            session.run("RETURN 1")  # Truy vấn đơn giản để kiểm tra kết nối

    def close(self):
        self.driver.close()

    def run_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [record for record in result]

    def get_relationships(self, node_names):
        relationships = []
        print("da vao ham tim quan he")
        print(node_names)

        for node_name in node_names:
            query = """
            MATCH (n)
            WHERE n.name CONTAINS $name
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n.name as node_name, type(r) as relationship, m.name as related_node
            """
            with self.driver.session() as session:
                result = session.run(query, name=node_name)
                node_relationships = [
                    f"{record['node_name']} {record['relationship']} {record['related_node']}"
                    for record in result
                    if record['related_node'] is not None and record['relationship'] is not None
                ]
                cleaned_list = [item.replace("_", " ") for item in node_relationships]
                relationships.extend(cleaned_list)  # Thay vì append, sử dụng extend để thêm vào danh sách

        return relationships

class RelationshipFinder:
    def __init__(self, conn):
        self.conn = conn

    #Hàm này chỉ để in các nút và quan hệ tìm đc -> có thể bỏ class này
    def find_relationships(self, node_names):
        relationships = self.conn.get_relationships(node_names)
        for node_name, rels in relationships:
            if rels:
                print(f"Tất cả các quan hệ với nút '{node_name}':")
                for rel in rels:
                    print(rel)
            else:
                print(f"Không tìm thấy nút '{node_name}' hoặc không có quan hệ nào.")