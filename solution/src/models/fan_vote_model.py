class FanVoteModel: #粉丝投票估算模型
    def fit(self, panel):
        raise NotImplementedError

    def predict(self, panel):
        raise NotImplementedError
