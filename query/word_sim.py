import urllib.request
from pathlib import Path

import fasttext
from numpy import dot
from numpy.linalg import norm


class WordSimilarityModel:
    def __init__(
        self,
        model_name="cc.en.50.bin",  # see: http://pages.cs.wisc.edu/~szhong/fasttext
        data_dir=Path(__file__).parent / "word_sim_model",
    ):
        self.data_dir = data_dir
        self.model_name = model_name
        self.filename = data_dir / model_name

        self._download()

        print(f'loading model')
        self.model = fasttext.load_model(self.filename.as_posix())
        print(f'model loaded')

    def _download(self):
        self.data_dir.mkdir(exist_ok=True)

        url = f"http://pages.cs.wisc.edu/~szhong/fasttext/{self.model_name}"

        if self.filename.exists():
            print(f"word similarity model exists at {self.filename}, skip downloading")
            return

        print(f'downloading word similarity model to {self.filename}')
        urllib.request.urlretrieve(url, self.filename)
        print(f'word similarity saved to {self.filename}')

    def similarity(self, w1, w2):
        a = self.model[w1]
        b = self.model[w2]
        cos_sim = dot(a, b) / (norm(a) * norm(b))  # cos similarity is in range (-1, 1)
        return (cos_sim + 1) / 2


ws_model = WordSimilarityModel()


def print_ws(w1, w2):
    print(w1, w2, ws_model.similarity(w1, w2))


def main():
    print_ws("hi", "hello")
    print_ws("papers", "publication")
    print_ws("papers", "write")
    print_ws("papers", "author")
    print_ws("love", "hate")

    while True:
        w1, w2 = input("please type two words:\n").split()
        print_ws(w1, w2)


if __name__ == '__main__':
    main()
