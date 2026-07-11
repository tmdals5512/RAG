from rag import ask

print("="*50)
print("오징어게임 전문가 챗봇")
print("="*50)

while True:
    question = input("\n질문: ")

    if question == "exit":
        break

    answer = ask(question)
    print()
    print(answer)