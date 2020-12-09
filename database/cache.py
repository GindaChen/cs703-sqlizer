import database.configs as configs

class PredCache():
    def __init__(self):
        self.pred_cache = dict()
        self.cache_miss_cnt = 0;
        self.cache_hit_cnt = 0;

    def __getitem__(self, key):
        if configs.enable_pred_cache:
            res = self.pred_cache.get(key)
        else:
            res = None
        if res is None:
            self.cache_miss_cnt += 1
        else:
            self.cache_hit_cnt += 1
        return res

    # query should be a tuple: (tablename, pred_str)
    def addCache(self, query: tuple, result: bool):
        if configs.enable_pred_cache:
            self.pred_cache[query] = result

    def __str__(self):
        return f'PredCache size: {len(self.pred_cache)}\nCache miss: {self.cache_miss_cnt}\nCache hit: {self.cache_hit_cnt}'
