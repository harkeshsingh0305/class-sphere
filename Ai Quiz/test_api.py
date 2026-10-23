import requests

url = "http://localhost:5001/generate-quiz"
data = {"topic": "Photosynthesis", "num_questions": 3, "difficulty": "mixed"}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())