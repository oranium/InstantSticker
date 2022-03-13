try:
    while True:
        s = input("Smiley: ")
        ascii_code = s.encode('unicode-escape').decode('ASCII')
        print("u'"+ascii_code+"'")
except KeyboardInterrupt:
    print("\nbye " + u'\U0001f44b' + "\n")
