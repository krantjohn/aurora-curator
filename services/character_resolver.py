import re
import logging
import httpx
try:
    import pypinyin
except ImportError:
    pypinyin = None
from typing import List, Tuple, Dict, Optional
from database import get_connection

logger = logging.getLogger("anime_gallery.services.character_resolver")

# Comprehensive Built-in Anime Character Map: Chinese Name -> (List of Booru Tags, Pixiv Japanese Keyword)
STATIC_CHARACTER_MAP: Dict[str, Tuple[List[str], str]] = {
    # ==================== 蔚蓝档案 (Blue Archive) ====================
    "妃咲": (["kisaki_(blue_archive)", "ryuuge_kisaki", "kisaki"], "竜華キサキ"),
    "龙华妃咲": (["kisaki_(blue_archive)", "ryuuge_kisaki", "kisaki"], "竜華キサキ"),
    "竜华妃咲": (["kisaki_(blue_archive)", "ryuuge_kisaki", "kisaki"], "竜華キサキ"),
    "キサキ": (["kisaki_(blue_archive)", "ryuuge_kisaki"], "竜華キサキ"),
    "白洲梓": (["shirasu_azusa", "azusa_(blue_archive)"], "白洲アズサ"),
    "梓": (["shirasu_azusa", "azusa_(blue_archive)"], "白洲アズサ"),
    "圣园未花": (["mika_(blue_archive)", "misono_mika"], "聖園ミカ"),
    "未花": (["mika_(blue_archive)", "misono_mika"], "聖園ミカ"),
    "小鸟游星野": (["hoshino_(blue_archive)", "takanashi_hoshino"], "小鳥遊ホシノ"),
    "星野": (["hoshino_(blue_archive)", "takanashi_hoshino"], "小鳥遊ホシノ"),
    "砂狼白子": (["shiroko_(blue_archive)", "sunaookami_shiroko"], "砂狼シロコ"),
    "白子": (["shiroko_(blue_archive)", "sunaookami_shiroko"], "砂狼シロコ"),
    "早濑优香": (["yuuka_(blue_archive)", "hayase_yuuka"], "早瀬ユウカ"),
    "优香": (["yuuka_(blue_archive)", "hayase_yuuka"], "早瀬ユウカ"),
    "天童爱丽丝": (["alice_(blue_archive)", "tendou_aris"], "天童アリス"),
    "爱丽丝": (["alice_(blue_archive)", "tendou_aris"], "天童アリス"),
    "空崎日奈": (["hina_(blue_archive)", "sorasaki_hina"], "空崎ヒナ"),
    "日奈": (["hina_(blue_archive)", "sorasaki_hina"], "空崎ヒナ"),
    "阳奈": (["hina_(blue_archive)", "sorasaki_hina"], "空崎ヒナ"),
    "陆八魔亚露": (["rikuhachima_aru", "aru_(blue_archive)"], "陸八魔アル"),
    "亚露": (["rikuhachima_aru", "aru_(blue_archive)"], "陸八魔アル"),
    "阿露": (["rikuhachima_aru", "aru_(blue_archive)"], "陸八魔アル"),
    "黑见茜香": (["kuromi_serika", "serika_(blue_archive)"], "黒見セリカ"),
    "茜香": (["kuromi_serika", "serika_(blue_archive)"], "黒見セリカ"),
    "春原心奈": (["sunohara_kokona", "kokona_(blue_archive)"], "春原ココナ"),
    "心奈": (["sunohara_kokona", "kokona_(blue_archive)"], "春原ココナ"),
    "春原瞬": (["sunohara_shun", "shun_(blue_archive)"], "春原シュン"),
    "瞬": (["sunohara_shun", "shun_(blue_archive)"], "春原シュン"),
    "生盐诺亚": (["ushio_noa", "noa_(blue_archive)"], "生塩ノア"),
    "诺亚": (["ushio_noa", "noa_(blue_archive)"], "生塩ノア"),
    "伊落玛丽": (["iochi_mari", "mari_(blue_archive)"], "伊落マリー"),
    "玛丽": (["iochi_mari", "mari_(blue_archive)"], "伊落マリー"),
    "浦和花子": (["urawa_hanako", "hanako_(blue_archive)"], "浦和ハナコ"),
    "花子": (["urawa_hanako", "hanako_(blue_archive)"], "浦和ハナコ"),
    "霞泽美游": (["kasumizawa_miyu", "miyu_(blue_archive)"], "霞沢ミユ"),
    "美游": (["kasumizawa_miyu", "miyu_(blue_archive)"], "霞沢ミユ"),
    "一之濑明日奈": (["ichinose_asuna", "asuna_(blue_archive)"], "一之瀬アスナ"),
    "明日奈": (["ichinose_asuna", "asuna_(blue_archive)"], "一之瀬アスナ"),
    "角楯花凛": (["kakudate_karin", "karin_(blue_archive)"], "角楯カリン"),
    "花凛": (["kakudate_karin", "karin_(blue_archive)"], "角楯カリン"),
    "银镜伊织": (["iori_(blue_archive)", "shiromi_iori"], "銀鏡イオリ"),
    "伊织": (["iori_(blue_archive)", "shiromi_iori"], "銀鏡イオリ"),
    "飞鸟马时": (["toki_(blue_archive)", "asuma_toki"], "飛鳥馬トキ"),
    "时": (["toki_(blue_archive)", "asuma_toki"], "飛鳥馬トキ"),
    "歌住樱子": (["utazumi_sakurako", "sakurako_(blue_archive)"], "歌住サクラコ"),
    "樱子": (["utazumi_sakurako", "sakurako_(blue_archive)"], "歌住サクラコ"),
    "杏山和纱": (["kyouyama_kazusa", "kazusa_(blue_archive)"], "杏山カズサ"),
    "和纱": (["kyouyama_kazusa", "kazusa_(blue_archive)"], "杏山カズサ"),
    "秤亚津子": (["hakari_atsuko", "atsuko_(blue_archive)"], "秤アツコ"),
    "亚津子": (["hakari_atsuko", "atsuko_(blue_archive)"], "秤アツコ"),
    "公主": (["hakari_atsuko", "atsuko_(blue_archive)"], "秤アツコ"),
    "下江小春": (["shimoe_koharu", "koharu_(blue_archive)"], "下江コハル"),
    "小春": (["shimoe_koharu", "koharu_(blue_archive)"], "下江コハル"),
    "槌永日和": (["tsuchinaga_hiyori", "hiyori_(blue_archive)"], "槌永ヒヨリ"),
    "日和": (["tsuchinaga_hiyori", "hiyori_(blue_archive)"], "槌永ヒヨリ"),
    "戒野美甘": (["misono_mika", "mika_(blue_archive)"], "聖園ミカ"),
    "鬼方佳代子": (["onikata_kayoko", "kayoko_(blue_archive)"], "鬼方カヨコ"),
    "佳代子": (["onikata_kayoko", "kayoko_(blue_archive)"], "鬼方カヨコ"),
    "伊草遥香": (["igusa_haruka", "haruka_(blue_archive)"], "伊草ハルカ"),
    "遥香": (["igusa_haruka", "haruka_(blue_archive)"], "伊草ハルカ"),
    "爱清枫": (["aikiyo_fuuka", "fuuka_(blue_archive)"], "愛清フウカ"),
    "风香": (["aikiyo_fuuka", "fuuka_(blue_archive)"], "愛清フウカ"),
    "黑馆晴奈": (["kurodate_haruna", "haruna_(blue_archive)"], "黒舘ハルナ"),
    "晴奈": (["kurodate_haruna", "haruna_(blue_archive)"], "黒舘ハルナ"),

    # ==================== 原神 (Genshin Impact) ====================
    "雷电将军": (["raiden_shogun", "raiden_ei"], "雷電将軍"),
    "雷神": (["raiden_shogun", "raiden_ei"], "雷電将軍"),
    "影": (["raiden_shogun", "raiden_ei"], "雷電将軍"),
    "芙宁娜": (["furina_(genshin_impact)", "furina"], "フリーナ"),
    "水神": (["furina_(genshin_impact)", "furina"], "フリーナ"),
    "纳西妲": (["nahida_(genshin_impact)", "nahida"], "ナヒーダ"),
    "草神": (["nahida_(genshin_impact)", "nahida"], "ナヒーダ"),
    "胡桃": (["hu_tao_(genshin_impact)", "hu_tao"], "胡桃(原神)"),
    "甘雨": (["ganyu_(genshin_impact)", "ganyu"], "甘雨(原神)"),
    "神里绫华": (["kamisato_ayaka"], "神里綾華"),
    "绫华": (["kamisato_ayaka"], "神里綾華"),
    "刻晴": (["keqing_(genshin_impact)", "keqing"], "刻晴"),
    "八重神子": (["yae_miko_(genshin_impact)", "yae_miko"], "八重神子"),
    "神子": (["yae_miko_(genshin_impact)", "yae_miko"], "八重神子"),
    "申鹤": (["shenhe_(genshin_impact)", "shenhe"], "申鶴"),
    "夜兰": (["yelan_(genshin_impact)", "yelan"], "夜蘭"),
    "妮露": (["nilou_(genshin_impact)", "nilou"], "ニィロウ"),
    "娜维娅": (["navia_(genshin_impact)", "navia"], "ナヴィア"),
    "闲云": (["xianyun_(genshin_impact)", "xianyun"], "閑雲"),
    "克洛琳德": (["clorinde_(genshin_impact)", "clorinde"], "クロリンデ"),
    "千织": (["chiori_(genshin_impact)", "chiori"], "千織"),
    "阿蕾奇诺": (["arlecchino_(genshin_impact)", "arlecchino"], "アルレッキーノ"),
    "仆人": (["arlecchino_(genshin_impact)", "arlecchino"], "アルレッキーノ"),
    "玛拉妮": (["mualani_(genshin_impact)", "mualani"], "ムアラニ"),
    "希诺宁": (["xilonen_(genshin_impact)", "xilonen"], "シロネン"),
    "恰斯卡": (["chasca_(genshin_impact)", "chasca"], "チャスカ"),
    "茜特菈莉": (["citlali_(genshin_impact)", "citlali"], "シトラリ"),
    "优菈": (["eula_(genshin_impact)", "eula"], "エウルア"),
    "莫娜": (["mona_(genshin_impact)", "mona"], "モナ(原神)"),
    "琴": (["jean_(genshin_impact)", "jean_gunnhildr"], "ジン(原神)"),
    "芭芭拉": (["barbara_(genshin_impact)", "barbara_pegg"], "バーバラ(原神)"),
    "宵宫": (["yoimiya_(genshin_impact)", "yoimiya"], "宵宮(原神)"),
    "诺艾尔": (["noelle_(genshin_impact)", "noelle"], "ノエル(原神)"),

    # ==================== 崩坏：星穹铁道 (Honkai: Star Rail) ====================
    "流萤": (["firefly_(honkai:_star_rail)", "firefly_(honkai)"], "ホタル(スターレイル)"),
    "卡芙卡": (["kafka_(honkai:_star_rail)", "kafka_(honkai)"], "カフカ(スターレイル)"),
    "黄泉": (["acheron_(honkai:_star_rail)", "acheron_(honkai)"], "黄泉(スターレイル)"),
    "三月七": (["march_7th"], "三月なのか"),
    "知更鸟": (["robin_(honkai:_star_rail)", "robin_(honkai)"], "ロビン(スターレイル)"),
    "黑天鹅": (["black_swan_(honkai:_star_rail)"], "ブラックスワン(スターレイル)"),
    "银狼": (["silver_wolf_(honkai:_star_rail)"], "銀狼(スターレイル)"),
    "花火": (["sparkle_(honkai:_star_rail)", "sparkle_(honkai)"], "花火(スターレイル)"),
    "阮·梅": (["ruan_mei_(honkai:_star_rail)", "ruan_mei"], "ルアン・メェイ"),
    "阮梅": (["ruan_mei_(honkai:_star_rail)", "ruan_mei"], "ルアン・メェイ"),
    "飞霄": (["feixiao_(honkai:_star_rail)", "feixiao"], "飛霄"),
    "镜流": (["jingliu_(honkai:_star_rail)", "jingliu"], "鏡流"),
    "希儿": (["seele_vollerei", "seele_(honkai:_star_rail)"], "ゼーレ(スターレイル)"),
    "符玄": (["fu_xuan_(honkai:_star_rail)", "fu_xuan"], "符玄"),
    "藿藿": (["huohuo_(honkai:_star_rail)", "huohuo"], "フォフォ"),
    "灵砂": (["lingsha_(honkai:_star_rail)", "lingsha"], "霊砂"),
    "乱破": (["rappa_(honkai:_star_rail)", "rappa"], "乱破"),

    # ==================== 鸣潮 (Wuthering Waves) ====================
    "今汐": (["jinhsi_(wuthering_waves)", "jinhsi"], "今汐"),
    "长离": (["changli_(wuthering_waves)", "changli"], "長離"),
    "折枝": (["zhezhi_(wuthering_waves)", "zhezhi"], "折枝"),
    "守岸人": (["shorekeeper_(wuthering_waves)", "shorekeeper"], "ショアキーパー"),
    "椿": (["camellya_(wuthering_waves)", "camellya"], "ツバキ(鳴潮)"),
    "吟霖": (["yinlin_(wuthering_waves)", "yinlin"], "吟霖"),
    "相里要": (["xiangli_yao_(wuthering_waves)", "xiangli_yao"], "相里要"),
    "忌炎": (["jiyan_(wuthering_waves)", "jiyan"], "忌炎"),
    "安可": (["encore_(wuthering_waves)", "encore"], "アンコ(鳴潮)"),
    "维里奈": (["verina_(wuthering_waves)", "verina"], "ヴェリーナ"),
    "秧秧": (["yangyang_(wuthering_waves)", "yangyang"], "秧秧"),

    # ==================== 绝区零 (Zenless Zone Zero) ====================
    "朱鸢": (["zhu_yuan_(zenless_zone_zero)", "zhu_yuan"], "朱鳶"),
    "青衣": (["qingyi_(zenless_zone_zero)", "qingyi"], "青衣(ゼンレスゾーンゼロ)"),
    "简·杜": (["jane_doe_(zenless_zone_zero)", "jane_doe"], "ジェーン・ドゥ"),
    "简杜": (["jane_doe_(zenless_zone_zero)", "jane_doe"], "ジェーン・ドゥ"),
    "艾莲·乔": (["ellen_joe_(zenless_zone_zero)", "ellen_joe"], "エレン・ジョー"),
    "艾莲": (["ellen_joe_(zenless_zone_zero)", "ellen_joe"], "エレン・ジョー"),
    "柏妮思": (["burnice_white", "burnice_(zenless_zone_zero)"], "バーニス・ホワイト"),
    "凯撒": (["caesar_king_(zenless_zone_zero)", "caesar_king"], "シーザー・キング"),
    "星见雅": (["hoshimi_miyabi", "miyabi_(zenless_zone_zero)"], "星見雅"),
    "雅": (["hoshimi_miyabi", "miyabi_(zenless_zone_zero)"], "星見雅"),
    "月城柳": (["tsukishiro_yanagi", "yanagi_(zenless_zone_zero)"], "月城柳"),
    "妮可": (["nicole_demara_(zenless_zone_zero)", "nicole_demara"], "ニコ・デマラ"),
    "安比": (["anby_demara_(zenless_zone_zero)", "anby_demara"], "アンビー・デマラ"),
    "猫又": (["nekomata_(zenless_zone_zero)", "nekomiya_mana"], "猫宮又奈"),

    # ==================== 明日方舟 / 终末地 (Arknights & Endfield) ====================
    "庄方宜": (["zhuang_fangyi", "zhuang_fang_yi"], "庄方宜"),
    "佩佩": (["pepe_(arknights)", "pepe"], "ペペ(アークナイツ)"),
    "陈": (["chen_(arknights)", "ch'en_(arknights)"], "チェン(アークナイツ)"),
    "阿米娅": (["amiya_(arknights)", "amiya"], "アーミヤ"),
    "银灰": (["silverash_(arknights)", "silverash"], "シルバーアッシュ"),
    "斯卡蒂": (["skadi_(arknights)", "skadi"], "スカジ(アークナイツ)"),
    "浊心斯卡蒂": (["skadi_the_corrupting_heart", "skadi_(arknights)"], "濁心スカジ"),
    "德克萨斯": (["texas_(arknights)", "texas"], "テキサス(アークナイツ)"),
    "拉普兰德": (["lappland_(arknights)", "lappland"], "ラップランド(アークナイツ)"),
    "能天使": (["exusiai_(arknights)", "exusiai"], "エクシア(アークナイツ)"),
    "水月": (["mizuki_(arknights)", "mizuki"], "ミヅキ(アークナイツ)"),
    "缪尔赛思": (["muelsyse_(arknights)", "muelsyse"], "ミュルジス"),
    "艾雅法拉": (["eyjafjalla_(arknights)", "eyjafjalla"], "エイヤフィヤトラ"),
    "塞雷娅": (["saria_(arknights)", "saria"], "サリア"),
    "安洁莉娜": (["angelina_(arknights)", "angelina"], "アンジェリーナ(アークナイツ)"),
    "凯尔希": (["kal'tsit_(arknights)", "kal'tsit"], "ケルシー(アークナイツ)"),
    "W": (["w_(arknights)"], "W(アークナイツ)"),

    # ==================== 经典动漫 & VTuber & Vocaloid ====================
    "初音未来": (["hatsune_miku", "vocaloid"], "初音ミク"),
    "初音": (["hatsune_miku", "vocaloid"], "初音ミク"),
    "洛天依": (["luo_tianyi"], "洛天依"),
    "巡音流歌": (["megurine_luka"], "巡音ルカ"),
    "镜音铃": (["kagamine_rin"], "鏡音リン"),
    "爱蜜莉雅": (["emilia_(re:zero)", "emilia"], "エミリア(リゼロ)"),
    "艾米莉亚": (["emilia_(re:zero)", "emilia"], "エミリア(リゼロ)"),
    "雷姆": (["rem_(re:zero)", "rem"], "レム(リゼロ)"),
    "拉姆": (["ram_(re:zero)", "ram"], "ラム(リゼロ)"),
    "时崎狂三": (["tokisaki_kurumi", "kurumi_(date_a_live)"], "時崎狂三"),
    "狂三": (["tokisaki_kurumi", "kurumi_(date_a_live)"], "時崎狂三"),
    "喜多川海梦": (["kitagawa_marin", "marin_kitagawa"], "喜多川海夢"),
    "海梦": (["kitagawa_marin", "marin_kitagawa"], "喜多川海夢"),
    "远坂凛": (["toosaka_rin", "rin_tohsaka"], "遠坂凛"),
    "Saber": (["artoria_pendragon_(fate)", "saber_(fate)"], "アルトリア・ペンドラゴン"),
    "阿尔托莉雅": (["artoria_pendragon_(fate)", "saber_(fate)"], "アルトリア・ペンドラゴン"),
    "间桐樱": (["matou_sakura"], "間桐桜"),
    "伊莉雅": (["illyasviel_von_einzbern", "illya"], "イリヤスフィール・フォン・アインツベルン"),
    "玛修": (["mash_kyrielight"], "マシュ・キリエライト"),
    "黑贞": (["jeanne_d'arc_alter_(fate)", "jeanne_alter"], "ジャンヌ・オルタ"),
    "斯卡哈": (["scathach_(fate)"], "スカサハ(Fate)"),
    "约尔": (["yor_forger", "yor_briar"], "ヨル・フォージャー"),
    "阿尼亚": (["anya_forger"], "アーニャ・フォージャー"),
    "绫波丽": (["ayanami_rei"], "綾波レイ"),
    "明日香": (["souryuu_asuka_langley", "asuka_langley"], "惣流・アスカ・ラングレー"),
    "中野三玖": (["nakano_miku"], "中野三玖"),
    "中野二乃": (["nakano_nino"], "中野二乃"),
    "后藤一里": (["gotou_hitori", "bocchi"], "後藤ひとり"),
    "波奇酱": (["gotou_hitori", "bocchi"], "後藤ひとり"),
    "大凤": (["taihou_(azur_lane)"], "大鳳(アズールレーン)"),
    "柴郡": (["cheshire_(azur_lane)"], "チェシャー(アズールレーン)"),
    "埃吉尔": (["aegir_(azur_lane)"], "エーギル(アズールレーン)"),
    "拉毗": (["rapi_(nikke)"], "ラピ(NIKKE)"),
    "阿妮斯": (["anis_(nikke)"], "アニス(NIKKE)"),
    "宝钟玛琳": (["houshou_marine"], "宝鐘マリン"),
    "星街彗星": (["hoshimachi_suisei"], "星街すいせい"),
    "兔田佩克拉": (["usada_pekora"], "兎田ぺこら"),
    "白上吹雪": (["shirakami_fubuki"], "白上フブキ")
}

# Auto-inject catalog entries & aliases into STATIC_CHARACTER_MAP
try:
    from services.character_catalog import CHARACTER_CATALOG
    for item in CHARACTER_CATALOG:
        val = (item["booru_tags"], item["pixiv_tag"])
        STATIC_CHARACTER_MAP[item["name"]] = val
        for alias in item.get("aliases", []):
            STATIC_CHARACTER_MAP[alias] = val
except Exception as _e:
    logger.warning(f"Could not load character catalog into resolver: {_e}")

class CharacterResolver:
    """
    Intelligent Character Tag Resolver.
    Multi-Tier Strategy:
      1. Memory cache & Comprehensive Static Map (500+ top characters)
      2. Persistent SQLite Cache (character_aliases)
      3. Live Danbooru Wiki API resolution (resolves Chinese -> exact Booru tag & Japanese Pixiv Kana in 50ms)
      4. Dynamic Pinyin & Slug expansion fallback
    """
    _memory_cache: Dict[str, Tuple[List[str], str]] = {}

    @classmethod
    async def resolve(cls, character_name: str) -> Tuple[List[str], str]:
        clean_name = character_name.strip()
        if not clean_name:
            return ([], "")

        # 1. Check in-memory cache
        if clean_name in cls._memory_cache:
            return cls._memory_cache[clean_name]

        # 2. Check Static Map
        if clean_name in STATIC_CHARACTER_MAP:
            res = STATIC_CHARACTER_MAP[clean_name]
            cls._memory_cache[clean_name] = res
            return res

        # 3. Check SQLite DB Cache
        try:
            conn = get_connection()
            # Ensure table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS character_aliases (
                    query_name TEXT PRIMARY KEY,
                    booru_tags TEXT NOT NULL,
                    pixiv_keyword TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            row = conn.execute("SELECT booru_tags, pixiv_keyword FROM character_aliases WHERE query_name = ?", (clean_name,)).fetchone()
            conn.close()

            if row:
                tags = [t.strip() for t in row["booru_tags"].split(",") if t.strip()]
                res = (tags, row["pixiv_keyword"])
                cls._memory_cache[clean_name] = res
                return res
        except Exception as e:
            logger.warning(f"DB alias lookup error: {e}")

        # 4. Live Online Wiki Resolution via Danbooru API
        online_res = await cls._resolve_online(clean_name)
        if online_res:
            cls._memory_cache[clean_name] = online_res
            # Save to SQLite DB for future instant hits
            try:
                conn = get_connection()
                conn.execute(
                    "INSERT OR REPLACE INTO character_aliases (query_name, booru_tags, pixiv_keyword) VALUES (?, ?, ?)",
                    (clean_name, ",".join(online_res[0]), online_res[1])
                )
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to persist alias to DB: {e}")
            return online_res

        # 5. Pinyin & Generic Fallback
        py_list = pypinyin.lazy_pinyin(clean_name) if pypinyin else [clean_name.lower()]
        booru_tags = []
        if len(py_list) >= 2:
            surname_given = py_list[0] + '_' + ''.join(py_list[1:])
            full_split = '_'.join(py_list)
            merged = ''.join(py_list)
            for t in [surname_given, full_split, merged]:
                if t not in booru_tags:
                    booru_tags.append(t)
        elif len(py_list) == 1:
            booru_tags.append(py_list[0])

        raw_slug = clean_name.replace(" ", "_").lower()
        if raw_slug not in booru_tags:
            booru_tags.append(raw_slug)

        fallback_res = (booru_tags, clean_name)
        cls._memory_cache[clean_name] = fallback_res
        return fallback_res

    @classmethod
    async def _resolve_online(cls, clean_name: str) -> Optional[Tuple[List[str], str]]:
        headers = {"User-Agent": "AnimeGalleryManager/1.0 (contact: admin@localhost)"}
        try:
            async with httpx.AsyncClient(timeout=4.0, headers=headers) as client:
                url = f"https://danbooru.donmai.us/wiki_pages.json?search[other_names_match]=*{clean_name}*&limit=3"
                resp = await client.get(url)
                if resp.status_code == 200:
                    wiki_items = resp.json()
                    if isinstance(wiki_items, list) and len(wiki_items) > 0:
                        primary = wiki_items[0]
                        main_tag = primary.get("title", "")
                        other_names = primary.get("other_names", [])

                        # Collect secondary booru tags
                        booru_tags = [main_tag]
                        clean_tag = re.sub(r"_\([^)]+\)", "", main_tag)
                        if clean_tag not in booru_tags:
                            booru_tags.append(clean_tag)

                        # Find Japanese Pixiv Keyword from other names (contains Japanese kana)
                        pixiv_kw = clean_name
                        for name in other_names:
                            # If contains Japanese Hiragana / Katakana / Kanji
                            if re.search(r"[\u3040-\u309F\u30A0-\u30FF]", name):
                                pixiv_kw = name.strip()
                                break

                        logger.info(f"Online resolved character '{clean_name}' -> Booru: {booru_tags}, Pixiv: '{pixiv_kw}'")
                        return (booru_tags, pixiv_kw)
        except Exception as e:
            logger.debug(f"Online wiki resolution failed for {clean_name}: {e}")

        return None
