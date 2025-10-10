import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# This line loads the ANTHROPIC_API_KEY from your .env file
# into the environment, so the library can find it automatically.
load_dotenv()

# When you create this object, it will authenticate using the API key.
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Now you can use the model!
response = llm.invoke("Hello, what is the capital of Utah?")
print(response.content)
# Expected output: Salt Lake City