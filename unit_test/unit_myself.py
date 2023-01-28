from anime_module import Myself, MyselfAnimeTable, MyselfAnime

from unittest import TestCase, IsolatedAsyncioTestCase


class MyselfTestCase(TestCase):
    def test_MyselfAnime(self):
        result = MyselfAnime(**{"animate-name": "HELLO WORLD【全 1 集】",
                             "episode-name": "第 01 話", "tid": "46195", "vid": "001"})

        expected = {
            "ANI_NAME": "HELLO WORLD【全 1 集】",
            "EPS_NAME": "第 01 話",
            "TID": "46195",
            "VID": "001",
        }
        self.assertDictEqual(result.dict(), expected)

    def test_MyselfAnimeTable(self):
        result = MyselfAnimeTable(
            **{"url": "https://myself-bbs.com/thread-46195-1-1.html"})

        expected = expected = {
            "URL": "https://myself-bbs.com/thread-46195-1-1.html",
            "TID": "46195",
            "NAME": None,
            "ANI_TYPE": None,
            "PRE_DATE": None,
            "EPS_NUM": None,
            "AUTHOR": None,
            "OFFICIAL_WEB": None,
            "REMARKS": None,
            "INTRO": None,
            "IMAGE_URL": None,
            "VIDEO_LIST": [],
            "updated": False
        }
        self.assertDictEqual(result.dict(), expected)


class MyselfTestCase_Async(IsolatedAsyncioTestCase):
    async def test_MyselfAnime_get_m3u8_url(self):
        result = await MyselfAnime(**{"animate-name": "HELLO WORLD【全 1 集】", "episode-name": "第 01 話", "tid": "46195", "vid": "001"}).get_m3u8_url()
        m3u8_server, m3u8_file = result

        self.assertEqual(type(result), tuple)
        self.assertEqual(type(m3u8_server), str)
        self.assertEqual(type(m3u8_file), str)

    async def test_MyselfAnimeTable_update(self):
        result = MyselfAnimeTable(
            **{"url": "https://myself-bbs.com/thread-46195-1-1.html"})
        await result.update()

        expected = {
            "URL": "https://myself-bbs.com/thread-46195-1-1.html",
            "TID": "46195",
            "NAME": "HELLO WORLD【全 1 集】",
            "ANI_TYPE": "科幻 / 冒險 / 戀愛",
            "PRE_DATE": "2019年09月20日",
            "EPS_NUM": "全 1 話",
            "AUTHOR": "",
            "OFFICIAL_WEB": "https://hello-world-movie.com/",
            "REMARKS": "",
            "INTRO": "動畫電影《HELLO WORLD》是以 2027 年的京都為舞臺，描述一名高中生的面前，突然出現一位自稱是來自 10 年後自己的人，希望和他一起改變未來，只為了拯救在 3 個月後會開始交往的同學一行瑠璃……。",
            "IMAGE_URL": "https://myself-bbs.com/data/attachment/forum/202010/11/1314529sq2sy7gzmqqd7m2.jpg",
            "VIDEO_LIST": [
                {
                    "ANI_NAME": "HELLO WORLD【全 1 集】",
                    "EPS_NAME": "第 01 話",
                    "TID": "46195",
                    "VID": "001"
                }
            ],
            "updated": True
        }
        self.assertDictEqual(result.dict(), expected)

    async def test_Myself_weekly_update(self):
        result: list[list[tuple[MyselfAnimeTable, str]]]
        result = await Myself.weekly_update()

        week_list = result
        daily_list = week_list[0]
        anime_tuple = daily_list[0]
        anime, name = anime_tuple
        self.assertEqual(type(result), list)
        self.assertEqual(type(daily_list), list)
        self.assertEqual(type(anime_tuple), tuple)
        self.assertEqual(type(anime), MyselfAnimeTable)
        self.assertEqual(type(name), str)

    async def test_Myself_year_list(self):
        result: dict[str, list[MyselfAnimeTable]]
        result = await Myself.year_list()

        all_year_dict = result
        year_key, yearresult = list(all_year_dict.items())[0]
        anime = yearresult[0]
        self.assertEqual(type(all_year_dict), dict)
        self.assertEqual(type(year_key), str)
        self.assertEqual(type(yearresult), list)
        self.assertEqual(type(anime), MyselfAnimeTable)

    async def test_Myself_finish_list(self):
        result = await Myself.finish_list(1, 5)

        result_list = result
        anime = result_list[0]
        self.assertEqual(type(result_list), list)
        self.assertEqual(type(anime), MyselfAnimeTable)
        self.assertEqual(100, len(result_list))

    async def test_Myself_search(self):
        result = await Myself.search("Hello World")

        result_list = result
        anime = result_list[0]
        self.assertEqual(type(result_list), list)
        self.assertEqual(type(anime), MyselfAnimeTable)
