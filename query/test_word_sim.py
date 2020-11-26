def test_word_sim():
    from query.word_sim import ws_model

    def print_ws(w1, w2):
        print(w1, w2, ws_model.similarity(w1, w2))

    print_ws("hi", "hello")
    print_ws("papers", "publication")
    print_ws("papers", "write")
    print_ws("papers", "author")


if __name__ == '__main__':
    test_word_sim()