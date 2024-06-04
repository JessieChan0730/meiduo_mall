from haystack import indexes

from goods.models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建⽴索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)
