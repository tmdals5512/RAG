from rag import ask

print("="*50)
print("지브리 가이드")
print("="*50)

while True:
    question = input("\n질문: ")

    if question == "exit":
        break

    answer = ask(question)
    print()
    print(answer)