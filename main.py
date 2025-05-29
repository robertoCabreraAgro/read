from agent.dm_agent import DmAgent

def main():
    agent = DmAgent()
    print("Simple DM CLI. Type 'quit' to exit.")
    while True:
        user_input = input("> ")
        if user_input.lower() == "quit":
            break
        response = agent.process_input(user_input)
        print(response)

if __name__ == "__main__":
    main()
