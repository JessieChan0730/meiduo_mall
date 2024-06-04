from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name']


class SubsSerializer(serializers.ModelSerializer):
    # 获取省下所有的数据
    subs = AreaSerializer(many=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
