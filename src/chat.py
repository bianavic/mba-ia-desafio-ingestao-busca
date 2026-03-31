from search import search_prompt


def main():
    print("-" * 50)
    print("Faça sua pergunta (exit/sair/quit para sair):")
    print("-" * 50)
    try:
        while True:
            print("\nPERGUNTA: ", end="", flush=True)
            pergunta = ""
            while not pergunta:
                pergunta = input().strip()
            if pergunta.lower() in ("exit", "sair", "quit"):
                break
            resposta = search_prompt(pergunta)
            print(f"\nRESPOSTA: {resposta}\n")
            print("-" * 50)
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrando chat.")


if __name__ == "__main__":
    main()