import urllib.request
from pathlib import Path

from gensim.models.fasttext import load_facebook_vectors


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
        self.model = load_facebook_vectors(self.filename)
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

    def similarity(self, a, b):
        return self.model.similarity(a, b)


ws_model = WordSimilarityModel()
