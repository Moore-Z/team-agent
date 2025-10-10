from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen3:4b")
response = llm.invoke("The first man on the moon was ...")
print(response)