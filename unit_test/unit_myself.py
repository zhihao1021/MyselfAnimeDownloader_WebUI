from unittest import TestCase, IsolatedAsyncioTestCase
from myself import Myself, MyselfAnimeTable, MyselfAnime, retouch_name

class MyselfTestCase(TestCase):
    def test_retouch_name(self):
        _arg = "\n\\T/e:s*t?N\"a<m>e|\r"
        _expected = "T e s t N a m e"
        
        _result = retouch_name(_arg)
        self.assertEqual(_expected, _result)
    
    def test_MyselfAnime(self):
        _result = MyselfAnime("第 01 話", "46195", "001")

        _expected = {
            "EPS_NAME": "第 01 話",
            "TID": "46195",
            "VID": "001",
        }
        self.assertDictEqual(_result.__dict__, _expected)
    
    def test_MyselfAnimeTable(self):
        _result = MyselfAnimeTable("https://myself-bbs.com/thread-46195-1-1.html")
        
        _expected = {
            "URL": "https://myself-bbs.com/thread-46195-1-1.html",
            "TID": "46195",
        }
        self.assertDictEqual(_result.__dict__, _expected)

class MyselfTestCase_Async(IsolatedAsyncioTestCase):
    async def test_MyselfAnime_get_m3u8_url(self):
        _result = await MyselfAnime("第 01 話", "46195", "001").get_m3u8_url()
        _m3u8_server, _m3u8_file = _result

        self.assertEqual(type(_result), tuple)
        self.assertEqual(type(_m3u8_server), str)
        self.assertEqual(type(_m3u8_file), str)

    async def test_MyselfAnimeTable_update(self):
        _result = MyselfAnimeTable("https://myself-bbs.com/thread-46195-1-1.html")
        await _result.update()

        _expected = {
            "URL": "https://myself-bbs.com/thread-46195-1-1.html",
            "TID": "46195",
            "NAME": "HELLO WORLD【全 1 集】",
            "ANI_TYPE": "科幻 / 冒險 / 戀愛",
            "PRE_DATE": "2019年09月20日",
            "EPS_NUM": "全 1 話",
            "AUTHOR": "",
            "OFFICIAL_WEB": "https://hello-world-movie.com/",
            "REMARKS": "",
            "IMAGE_URL": "https://myself-bbs.com/data/attachment/forum/202010/11/1314529sq2sy7gzmqqd7m2.jpg",
            "INTRO": "動畫電影《HELLO WORLD》是以 2027 年的京都為舞臺，描述一名高中生的面前，突然出現一位自稱是來自 10 年後自己的人，希望和他一起改變未來，只為了拯救在 3 個月後會開始交往的同學一行瑠璃……。",
            "VIDEO_LIST": [
                MyselfAnime("第 01 話", "46195", "001"),
            ],
            "updated": True
        }
        self.assertDictEqual(_result.__dict__, _expected)

    async def test_Myself_weekly_update(self):
        _result: list[list[tuple[MyselfAnimeTable, str]]]
        _result = await Myself.weekly_update()

        _week_list = _result
        _daily_list = _week_list[0]
        _anime_tuple = _daily_list[0]
        _anime, _name = _anime_tuple
        self.assertEqual(type(_result), list)
        self.assertEqual(type(_daily_list), list)
        self.assertEqual(type(_anime_tuple), tuple)
        self.assertEqual(type(_anime), MyselfAnimeTable)
        self.assertEqual(type(_name), str)
    
    async def test_Myself_finish_list(self):
        _result: dict[str, list[MyselfAnimeTable]]
        _result = await Myself.finish_list()

        _all_year_dict = _result
        _year_key, _year_result = list(_all_year_dict.items())[0]
        _anime = _year_result[0]
        self.assertEqual(type(_all_year_dict), dict)
        self.assertEqual(type(_year_key), str)
        self.assertEqual(type(_year_result), list)
        self.assertEqual(type(_anime), MyselfAnimeTable)
    
    async def test_Myself_search(self):
        _result: list[MyselfAnimeTable]
        _result = await Myself.search("Hello World")

        _result_list = _result
        _anime = _result_list[0]
        self.assertEqual(type(_result_list), list)
        self.assertEqual(type(_anime), MyselfAnimeTable)


        