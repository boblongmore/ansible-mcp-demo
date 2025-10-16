from ollama import chat
from ollama import ChatResponse


def granite_chat(input_content):
  response: ChatResponse = chat(model='granite3.3:latest', messages=[
    {
      'role': 'assistant',
      'content': input_content,
    },
  ])
  print(response['message']['content'])
  return(response['message']['content'])
# or access fields directly from the response object
# print(response.message.content)
