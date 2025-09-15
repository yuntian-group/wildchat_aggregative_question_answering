from modeling.rag_model import RetrieverBase


class NoRetriever(RetrieverBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.topk = 0

    def build_context(self, full_data):
        return full_data
