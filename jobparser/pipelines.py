# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient("127.0.0.1", 27017)
        self.mongobase = client.scrapy_vacancies

    def process_item(self, item, spider):

        if spider.name == "hhru":
            salary = self.hh_salary(item.get("salary"))

        if spider.name == "sjru":
            salary = self.sjru_salary(item.get("salary"))

        item["salary_min"], item["salary_max"] = salary
        del item["salary"]

        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item

    @staticmethod
    def hh_salary(d_salary):

        if d_salary[0] == "от":
            salary_min = int(d_salary[1].replace("\xa0", ""))
            if d_salary[0] == "до":
                salary_max = int(d_salary[3].replace("\xa0", ""))
            else:
                salary_max = None

        if d_salary[0] == "до":
            salary_max = int(d_salary[3].replace("\xa0", ""))
            salary_min = None

        if "з/п не указана" in d_salary:
            salary_min, salary_max = None, None

        return salary_min, salary_max

    @staticmethod
    def sjru_salary(d_salary):
        min_salary, max_salary = None, None
        if d_salary[0] == "от":
            min_salary = int("".join(filter(str.isdigit, d_salary[2].replace("\xa0", ""))))
        elif d_salary[0] == "до":
            max_salary = int("".join(filter(str.isdigit, d_salary[2].replace("\xa0", ""))))
        elif len(d_salary) > 3:
            min_salary = int("".join(filter(str.isdigit, d_salary[0].replace("\xa0", ""))))
            max_salary = int("".join(filter(str.isdigit, d_salary[4].replace("\xa0", ""))))

        return min_salary, max_salary
