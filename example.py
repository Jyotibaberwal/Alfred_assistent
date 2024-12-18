import google.generativeai as genai

genai.configure(api_key="AIzaSyAdTjdjdfnAhhI4MxxRDw1jJ1oRMl8v-d0")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)

