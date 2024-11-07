import json
import os
from datetime import datetime

from making_report.repository.making_report_repository import MakingReportRepository


class MakingReportRepositoryImpl(MakingReportRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def getKeysInDictValues(self, dict):
        return list(dict.values())[0].keys()

    def gatherData(self, corpNameList, *data):
        infoList = [key for info in data for key in self.getKeysInDictValues(info)]
        result = dict.fromkeys(corpNameList, dict.fromkeys(infoList, "-"))

        for corpName in corpNameList:
            print(f"* REPORT - {corpName}")
            infoDict = {}
            for info in data:
                if not info.get(corpName):
                    continue
                infoDict.update(info[corpName])
            result[corpName] = infoDict

        return result