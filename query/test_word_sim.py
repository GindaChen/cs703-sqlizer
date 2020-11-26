from query.word_sim import ws_model


def print_ws(w1, w2):
    print(w1, w2, ws_model.similarity(w1, w2))


if __name__ == '__main__':
    print_ws("hi", "hello")
    print_ws("papers", "publication")
    print_ws("papers", "write")
    print_ws("papers", "author")

    while True:
        w1, w2 = input("please type two words:\n").split()
        print_ws(w1, w2)
