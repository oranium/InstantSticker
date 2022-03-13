from bot import bot

def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    bot.initalize_bot()

if __name__ == '__main__':
    main()
