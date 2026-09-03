"""
Comprehensive Character Catalog for Blue Archive, Wuthering Waves, and Arknights: Endfield.
Contains high-precision Booru tags, Pixiv Japanese keywords, game classification, and aliases.
"""

from typing import Dict, List, Any

CHARACTER_CATALOG: List[Dict[str, Any]] = [
    # =========================================================================
    # 蔚蓝档案 (Blue Archive / ブルアカ)
    # =========================================================================
    {
        "name": "妃咲",
        "slug": "kisaki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kisaki_(blue_archive)", "ryuuge_kisaki", "kisaki"],
        "pixiv_tag": "竜華キサキ",
        "aliases": ["龙华妃咲", "竜华妃咲", "キサキ", "妃咲门", "玄龙门会长"],
        "accent_color": "#0ea5e9"
    },
    {
        "name": "圣园未花",
        "slug": "mika",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["mika_(blue_archive)", "misono_mika"],
        "pixiv_tag": "聖園ミカ",
        "aliases": ["未花", "ミカ", "公主未花"],
        "accent_color": "#f472b6"
    },
    {
        "name": "白洲梓",
        "slug": "azusa",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["shirasu_azusa", "azusa_(blue_archive)"],
        "pixiv_tag": "白洲アズサ",
        "aliases": ["梓", "アズサ", "补习部梓"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "小鸟游星野",
        "slug": "hoshino",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["hoshino_(blue_archive)", "takanashi_hoshino"],
        "pixiv_tag": "小鳥遊ホシノ",
        "aliases": ["星野", "大叔", "临战星野", "ホシノ"],
        "accent_color": "#fb923c"
    },
    {
        "name": "砂狼白子",
        "slug": "shiroko",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["shiroko_(blue_archive)", "sunaookami_shiroko"],
        "pixiv_tag": "砂狼シロコ",
        "aliases": ["白子", "黑化白子", "シロコ", "白子·恐怖"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "早濑优香",
        "slug": "yuuka",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["yuuka_(blue_archive)", "hayase_yuuka"],
        "pixiv_tag": "早瀬ユウカ",
        "aliases": ["优香", "ユウカ", "没关系的优香", "计算器"],
        "accent_color": "#60a5fa"
    },
    {
        "name": "空崎日奈",
        "slug": "hina",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["hina_(blue_archive)", "sorasaki_hina"],
        "pixiv_tag": "空崎ヒナ",
        "aliases": ["日奈", "阳奈", "ヒナ", "礼服日奈", "风纪委员长"],
        "accent_color": "#a855f7"
    },
    {
        "name": "天童爱丽丝",
        "slug": "alice",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["alice_(blue_archive)", "tendou_aris"],
        "pixiv_tag": "天童アリス",
        "aliases": ["爱丽丝", "アリス", "勇者爱丽丝", "邦邦咔邦"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "陆八魔亚露",
        "slug": "aru",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["rikuhachima_aru", "aru_(blue_archive)"],
        "pixiv_tag": "陸八魔アル",
        "aliases": ["亚露", "阿露", "アル", "便利屋68社长"],
        "accent_color": "#ef4444"
    },
    {
        "name": "飞鸟马时",
        "slug": "toki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["toki_(blue_archive)", "asuma_toki"],
        "pixiv_tag": "飛鳥馬トキ",
        "aliases": ["时", "トキ", "兔女郎时", "女仆时"],
        "accent_color": "#0ea5e9"
    },
    {
        "name": "生盐诺亚",
        "slug": "noa",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["ushio_noa", "noa_(blue_archive)"],
        "pixiv_tag": "生塩ノア",
        "aliases": ["诺亚", "ノア", "书记诺亚"],
        "accent_color": "#cbd5e1"
    },
    {
        "name": "霞泽美游",
        "slug": "miyu",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kasumizawa_miyu", "miyu_(blue_archive)"],
        "pixiv_tag": "霞沢ミユ",
        "aliases": ["美游", "ミユ", "垃圾桶美游", "兔子小队美游"],
        "accent_color": "#94a3b8"
    },
    {
        "name": "浦和花子",
        "slug": "hanako",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["urawa_hanako", "hanako_(blue_archive)"],
        "pixiv_tag": "浦和ハナコ",
        "aliases": ["花子", "ハナコ", "泳装花子", "水花子"],
        "accent_color": "#ec4899"
    },
    {
        "name": "杏山和纱",
        "slug": "kazusa",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kyouyama_kazusa", "kazusa_(blue_archive)"],
        "pixiv_tag": "杏山カズサ",
        "aliases": ["和纱", "カズサ", "猫猫和纱", "甜品部和纱"],
        "accent_color": "#f43f5e"
    },
    {
        "name": "一之濑明日奈",
        "slug": "asuna",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["ichinose_asuna", "asuna_(blue_archive)"],
        "pixiv_tag": "一之瀬アスナ",
        "aliases": ["明日奈", "アスナ", "兔女郎明日奈", "金色明日奈"],
        "accent_color": "#fbbf24"
    },
    {
        "name": "角楯花凛",
        "slug": "karin",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kakudate_karin", "karin_(blue_archive)"],
        "pixiv_tag": "角楯カリン",
        "aliases": ["花凛", "カリン", "兔女郎花凛", "黑皮花凛"],
        "accent_color": "#334155"
    },
    {
        "name": "黑见茜香",
        "slug": "serika",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kuromi_serika", "serika_(blue_archive)"],
        "pixiv_tag": "黒見セリカ",
        "aliases": ["茜香", "セリカ", "傲娇黑猫", "打工茜香"],
        "accent_color": "#1e293b"
    },
    {
        "name": "秤亚津子",
        "slug": "atsuko",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["hakari_atsuko", "atsuko_(blue_archive)"],
        "pixiv_tag": "秤アツコ",
        "aliases": ["亚津子", "アツコ", "公主", "阿里乌斯公主"],
        "accent_color": "#a855f7"
    },
    {
        "name": "下江小春",
        "slug": "koharu",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["shimoe_koharu", "koharu_(blue_archive)"],
        "pixiv_tag": "下江コハル",
        "aliases": ["小春", "コハル", "色情死刑", "粉毛小春"],
        "accent_color": "#f472b6"
    },
    {
        "name": "春原心奈",
        "slug": "kokona",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["sunohara_kokona", "kokona_(blue_archive)"],
        "pixiv_tag": "春原ココナ",
        "aliases": ["心奈", "ココナ", "心奈教官", "梅花园教官"],
        "accent_color": "#fb7185"
    },
    {
        "name": "春原瞬",
        "slug": "shun",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["sunohara_shun", "shun_(blue_archive)"],
        "pixiv_tag": "春原シュン",
        "aliases": ["瞬", "シュン", "幼瞬", "瞬教官"],
        "accent_color": "#14b8a6"
    },
    {
        "name": "伊落玛丽",
        "slug": "mari",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["iochi_mari", "mari_(blue_archive)"],
        "pixiv_tag": "伊落マリー",
        "aliases": ["玛丽", "マリー", "修女玛丽", "猫耳修女"],
        "accent_color": "#fb923c"
    },
    {
        "name": "银镜伊织",
        "slug": "iori",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["iori_(blue_archive)", "shiromi_iori"],
        "pixiv_tag": "銀鏡イオリ",
        "aliases": ["伊织", "イオリ", "风纪委员伊织", "舔脚伊织"],
        "accent_color": "#475569"
    },
    {
        "name": "歌住樱子",
        "slug": "sakurako",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["utazumi_sakurako", "sakurako_(blue_archive)"],
        "pixiv_tag": "歌住サクラコ",
        "aliases": ["樱子", "サクラコ", "觉悟樱子", "修女会总会长"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "鬼方佳代子",
        "slug": "kayoko",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["onikata_kayoko", "kayoko_(blue_archive)"],
        "pixiv_tag": "鬼方カヨコ",
        "aliases": ["佳代子", "カヨコ", "礼服佳代子", "便利屋智囊"],
        "accent_color": "#64748b"
    },
    {
        "name": "黑馆晴奈",
        "slug": "haruna",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kurodate_haruna", "haruna_(blue_archive)"],
        "pixiv_tag": "黒舘ハルナ",
        "aliases": ["晴奈", "ハルナ", "美食研究会长"],
        "accent_color": "#475569"
    },
    {
        "name": "锭前纱织",
        "slug": "saori",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["joumae_saori", "saori_(blue_archive)"],
        "pixiv_tag": "錠前サオリ",
        "aliases": ["纱织", "サオリ", "阿里乌斯队长"],
        "accent_color": "#334155"
    },
    {
        "name": "槌永日和",
        "slug": "hiyori",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["tsuchinaga_hiyori", "hiyori_(blue_archive)"],
        "pixiv_tag": "槌永ヒヨリ",
        "aliases": ["日和", "ヒヨリ", "阿里乌斯日和"],
        "accent_color": "#94a3b8"
    },
    {
        "name": "浅黄睦月",
        "slug": "mutsuki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["asagi_mutsuki", "mutsuki_(blue_archive)"],
        "pixiv_tag": "浅黄ムツキ",
        "aliases": ["睦月", "ムツキ", "雌小鬼睦月"],
        "accent_color": "#ef4444"
    },
    {
        "name": "调月莉音",
        "slug": "rio",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["tsukatsuki_rio", "rio_(blue_archive)"],
        "pixiv_tag": "調月リオ",
        "aliases": ["莉音", "リオ", "大黑莉音", "研讨会会长"],
        "accent_color": "#0f172a"
    },

    # =========================================================================
    # 鸣潮 (Wuthering Waves / 鳴潮)
    # =========================================================================
    {
        "name": "今汐",
        "slug": "jinhsi",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["jinhsi_(wuthering_waves)", "jinhsi"],
        "pixiv_tag": "今汐",
        "aliases": ["今州令尹", "今汐令尹", "今汐(鸣潮)"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "长离",
        "slug": "changli",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["changli_(wuthering_waves)", "changli"],
        "pixiv_tag": "長離",
        "aliases": ["长离老师", "长离(鸣潮)", "凤凰长离"],
        "accent_color": "#f97316"
    },
    {
        "name": "守岸人",
        "slug": "shorekeeper",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["shorekeeper_(wuthering_waves)", "shorekeeper"],
        "pixiv_tag": "ショアキーパー",
        "aliases": ["黑海岸守岸人", "守岸人(鸣潮)", "蝴蝶守岸人"],
        "accent_color": "#6366f1"
    },
    {
        "name": "椿",
        "slug": "camellya",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["camellya_(wuthering_waves)", "camellya"],
        "pixiv_tag": "ツバキ(鳴潮)",
        "aliases": ["椿(鸣潮)", "黑海岸椿", "红椿"],
        "accent_color": "#e11d48"
    },
    {
        "name": "吟霖",
        "slug": "yinlin",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["yinlin_(wuthering_waves)", "yinlin"],
        "pixiv_tag": "吟霖",
        "aliases": ["吟霖(鸣潮)", "红发吟霖", "悬丝偶师"],
        "accent_color": "#dc2626"
    },
    {
        "name": "折枝",
        "slug": "zhezhi",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["zhezhi_(wuthering_waves)", "zhezhi"],
        "pixiv_tag": "折枝",
        "aliases": ["折枝画师", "折枝(鸣潮)"],
        "accent_color": "#06b6d4"
    },
    {
        "name": "忌炎",
        "slug": "jiyan",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["jiyan_(wuthering_waves)", "jiyan"],
        "pixiv_tag": "忌炎",
        "aliases": ["夜归将军", "忌炎将军", "青龙忌炎"],
        "accent_color": "#10b981"
    },
    {
        "name": "相里要",
        "slug": "xiangli_yao",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["xiangli_yao_(wuthering_waves)", "xiangli_yao"],
        "pixiv_tag": "相里要",
        "aliases": ["相里要(鸣潮)", "机械相里要"],
        "accent_color": "#8b5cf6"
    },
    {
        "name": "安可",
        "slug": "encore",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["encore_(wuthering_waves)", "encore"],
        "pixiv_tag": "アンコ(鳴潮)",
        "aliases": ["安可(鸣潮)", "黑咩白咩", "黑海岸安可"],
        "accent_color": "#fb7185"
    },
    {
        "name": "维里奈",
        "slug": "verina",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["verina_(wuthering_waves)", "verina"],
        "pixiv_tag": "ヴェリーナ",
        "aliases": ["维里奈(鸣潮)", "小植物学家", "金发维里奈"],
        "accent_color": "#eab308"
    },
    {
        "name": "秧秧",
        "slug": "yangyang",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["yangyang_(wuthering_waves)", "yangyang"],
        "pixiv_tag": "秧秧",
        "aliases": ["秧秧(鸣潮)", "夜归秧秧"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "散华",
        "slug": "sanhua",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["sanhua_(wuthering_waves)", "sanhua"],
        "pixiv_tag": "散華(鳴潮)",
        "aliases": ["散华(鸣潮)", "令尹近卫散华", "白发散华"],
        "accent_color": "#93c5fd"
    },
    {
        "name": "丹瑾",
        "slug": "danjin",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["danjin_(wuthering_waves)", "danjin"],
        "pixiv_tag": "丹瑾",
        "aliases": ["丹瑾(鸣潮)", "红衣丹瑾"],
        "accent_color": "#ef4444"
    },
    {
        "name": "炽霞",
        "slug": "chixia",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["chixia_(wuthering_waves)", "chixia"],
        "pixiv_tag": "熾霞",
        "aliases": ["炽霞(鸣潮)", "天城巡尉炽霞"],
        "accent_color": "#f97316"
    },
    {
        "name": "白芷",
        "slug": "baizhi",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["baizhi_(wuthering_waves)", "baizhi"],
        "pixiv_tag": "白芷(鳴潮)",
        "aliases": ["白芷(鸣潮)", "研究院白芷"],
        "accent_color": "#67e8f9"
    },
    {
        "name": "桃祈",
        "slug": "taoqi",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["taoqi_(wuthering_waves)", "taoqi"],
        "pixiv_tag": "桃祈",
        "aliases": ["桃祈(鸣潮)", "粉发桃祈"],
        "accent_color": "#f472b6"
    },
    {
        "name": "鉴心",
        "slug": "jianxin",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["jianxin_(wuthering_waves)", "jianxin"],
        "pixiv_tag": "鑑心",
        "aliases": ["鉴心道长", "鉴心(鸣潮)", "太极鉴心"],
        "accent_color": "#14b8a6"
    },
    {
        "name": "漂泊者",
        "slug": "rover",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["female_rover_(wuthering_waves)", "rover_(wuthering_waves)"],
        "pixiv_tag": "漂泊者(鳴潮)",
        "aliases": ["女漂泊者", "阿漂", "漂泊者(女)"],
        "accent_color": "#facc15"
    },
    {
        "name": "珂莱塔",
        "slug": "carlotta",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["carlotta_(wuthering_waves)", "carlotta"],
        "pixiv_tag": "カルロッタ",
        "aliases": ["珂莱塔(鸣潮)", "卡洛琳", "黑海岸珂莱塔"],
        "accent_color": "#a855f7"
    },
    {
        "name": "洛可可",
        "slug": "rococo",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["rococo_(wuthering_waves)", "rococo"],
        "pixiv_tag": "ロココ(鳴潮)",
        "aliases": ["洛可可(鸣潮)"],
        "accent_color": "#fb7185"
    },

    # =========================================================================
    # 明日方舟：终末地 (Arknights: Endfield / エンドフィールド)
    # =========================================================================
    {
        "name": "佩丽卡",
        "slug": "perlica",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["perlica_(arknights:_endfield)", "perlica"],
        "pixiv_tag": "ペリカ(エンドフィールド)",
        "aliases": ["佩丽卡监督", "监督", "终末地佩丽卡", "佩利卡"],
        "accent_color": "#eab308"
    },
    {
        "name": "陈千语",
        "slug": "chen_qianyu",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["chen_qianyu_(arknights:_endfield)", "chen_qianyu"],
        "pixiv_tag": "チェン・チエンユー",
        "aliases": ["陈千语特勤", "千语", "终末地陈千语"],
        "accent_color": "#0284c7"
    },
    {
        "name": "庄方宜",
        "slug": "zhuang_fangyi",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["zhuang_fangyi", "zhuang_fang_yi"],
        "pixiv_tag": "庄方宜",
        "aliases": ["庄方宜干员", "终末地庄方宜"],
        "accent_color": "#0d9488"
    },
    {
        "name": "狼卫",
        "slug": "wulfgard",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["wulfgard_(arknights:_endfield)", "wulfgard"],
        "pixiv_tag": "ウルフガード",
        "aliases": ["狼卫(终末地)", "重剑狼卫"],
        "accent_color": "#475569"
    },
    {
        "name": "艾维文娜",
        "slug": "avywenna",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["avywenna_(arknights:_endfield)", "avywenna"],
        "pixiv_tag": "アヴィヴェナ",
        "aliases": ["艾维文娜(终末地)", "电系艾维文娜"],
        "accent_color": "#f59e0b"
    },
    {
        "name": "赛希",
        "slug": "xaihi",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["xaihi_(arknights:_endfield)", "xaihi", "sais"],
        "pixiv_tag": "サイヒ",
        "aliases": ["赛希(终末地)", "术师赛希"],
        "accent_color": "#8b5cf6"
    },
    {
        "name": "别礼",
        "slug": "bieling",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["bieling_(arknights:_endfield)", "bieling", "perlit"],
        "pixiv_tag": "ビエリン",
        "aliases": ["别礼(终末地)"],
        "accent_color": "#10b981"
    },
    {
        "name": "莱万汀",
        "slug": "laevatain",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["laevatain_(arknights:_endfield)", "laevatain"],
        "pixiv_tag": "レーヴァテイン(エンドフィールド)",
        "aliases": ["莱万汀(终末地)", "大剑莱万汀"],
        "accent_color": "#ef4444"
    },
    {
        "name": "余烬",
        "slug": "ember",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["ember_(arknights:_endfield)", "ember"],
        "pixiv_tag": "エンバー(エンドフィールド)",
        "aliases": ["余烬(终末地)", "骑士余烬"],
        "accent_color": "#ca8a04"
    },
    {
        "name": "洁尔佩塔",
        "slug": "jelpeto",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["jelpeto_(arknights:_endfield)", "jelpeto"],
        "pixiv_tag": "ジェルペット",
        "aliases": ["洁尔佩塔(终末地)"],
        "accent_color": "#06b6d4"
    },
    {
        "name": "艾尔黛拉",
        "slug": "eldela",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["eldela_(arknights:_endfield)", "eldela"],
        "pixiv_tag": "エルデラ",
        "aliases": ["艾尔黛拉(终末地)"],
        "accent_color": "#ec4899"
    },
    {
        "name": "伊冯",
        "slug": "yvonne",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["yvonne_(arknights:_endfield)", "yvonne"],
        "pixiv_tag": "イヴォンヌ(エンドフィールド)",
        "aliases": ["伊冯(终末地)"],
        "accent_color": "#6366f1"
    },
    {
        "name": "终末地管理员",
        "slug": "endministrator",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["endministrator_(arknights:_endfield)", "administrator"],
        "pixiv_tag": "管理人(エンドフィールド)",
        "aliases": ["管理员", "终末地主角", "博士"],
        "accent_color": "#eab308"
    },
    {
        "name": "安洁莉娜",
        "slug": "angelina_endfield",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["angelina_(arknights:_endfield)", "angelina_(arknights)"],
        "pixiv_tag": "アンジェリーナ(アークナイツ)",
        "aliases": ["安洁莉娜(终末地)", "洁哥"],
        "accent_color": "#f97316"
    },
    {
        "name": "菲奥娜",
        "slug": "fiona",
        "game": "endfield",
        "game_name": "终末地",
        "booru_tags": ["fiona_(arknights:_endfield)", "fiona"],
        "pixiv_tag": "フィオナ(エンドフィールド)",
        "aliases": ["菲奥娜(终末地)"],
        "accent_color": "#14b8a6"
    },
    # =========================================================================
    # 鸣潮 (Wuthering Waves) 补充角色
    # =========================================================================
    {
        "name": "渊武",
        "slug": "yuanwu",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["yuanwu_(wuthering_waves)", "yuanwu"],
        "pixiv_tag": "淵武",
        "aliases": ["大叔", "拳师"],
        "accent_color": "#a855f7"
    },
    {
        "name": "莫特斐",
        "slug": "mortefi",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["mortefi_(wuthering_waves)", "mortefi"],
        "pixiv_tag": "モルテフィ",
        "aliases": ["火枪", "莫特斐"],
        "accent_color": "#ef4444"
    },
    {
        "name": "釉瑚",
        "slug": "youhu",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["youhu_(wuthering_waves)", "youhu"],
        "pixiv_tag": "釉瑚",
        "aliases": ["釉瑚", "鉴宝萝莉"],
        "accent_color": "#06b6d4"
    },
    {
        "name": "布兰特",
        "slug": "brant",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["brant_(wuthering_waves)", "brant"],
        "pixiv_tag": "ブラント",
        "aliases": ["布兰特"],
        "accent_color": "#f59e0b"
    },
    {
        "name": "菲比",
        "slug": "phoebe",
        "game": "wuthering_waves",
        "game_name": "鸣潮",
        "booru_tags": ["phoebe_(wuthering_waves)", "phoebe"],
        "pixiv_tag": "フィービー",
        "aliases": ["菲比"],
        "accent_color": "#ec4899"
    },
    # =========================================================================
    # 蔚蓝档案 (Blue Archive) 深度补充全量人气角色
    # =========================================================================
    {
        "name": "枣伊吕波",
        "slug": "iroha",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["natsume_iroha", "iroha_(blue_archive)"],
        "pixiv_tag": "棗イロハ",
        "aliases": ["伊吕波", "イロハ", "168", "虎丸车长"],
        "accent_color": "#ef4444"
    },
    {
        "name": "狐坂若藻",
        "slug": "wakamo",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kosaka_wakamo", "wakamo_(blue_archive)"],
        "pixiv_tag": "狐坂ワカモ",
        "aliases": ["若藻", "ワカモ", "狐狸", "灾厄之狐"],
        "accent_color": "#dc2626"
    },
    {
        "name": "才羽桃井",
        "slug": "momoi",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["saiba_momoi", "momoi_(blue_archive)"],
        "pixiv_tag": "才羽モモイ",
        "aliases": ["桃井", "モモイ", "粉毛小春"],
        "accent_color": "#f97316"
    },
    {
        "name": "才羽绿",
        "slug": "midori",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["saiba_midori", "midori_(blue_archive)"],
        "pixiv_tag": "才羽ミドリ",
        "aliases": ["绿", "ミドリ", "小绿"],
        "accent_color": "#22c55e"
    },
    {
        "name": "花冈柚子",
        "slug": "yuzu",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["hanaoka_yuzu", "yuzu_(blue_archive)"],
        "pixiv_tag": "花岡ユズ",
        "aliases": ["柚子", "ユズ", "柜子柚子"],
        "accent_color": "#eab308"
    },
    {
        "name": "美甘宁瑠",
        "slug": "neru",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["mikamo_neru", "neru_(blue_archive)"],
        "pixiv_tag": "美甘ネル",
        "aliases": ["宁瑠", "ネル", "双枪暴躁", "兔女郎宁瑠"],
        "accent_color": "#e11d48"
    },
    {
        "name": "室笠朱音",
        "slug": "akane",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["murokasa_akane", "akane_(blue_archive)"],
        "pixiv_tag": "室笠アカネ",
        "aliases": ["朱音", "アカネ", "扫除女仆"],
        "accent_color": "#eab308"
    },
    {
        "name": "阿慈谷日富美",
        "slug": "hifumi",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["ajitani_hifumi", "hifumi_(blue_archive)"],
        "pixiv_tag": "阿慈谷ヒフミ",
        "aliases": ["日富美", "ヒフミ", "浮士德", "佩洛洛"],
        "accent_color": "#eab308"
    },
    {
        "name": "剑先鹤城",
        "slug": "tsurugi",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kenzaki_tsurugi", "tsurugi_(blue_archive)"],
        "pixiv_tag": "剣先ツルギ",
        "aliases": ["鹤城", "ツルギ", "正义实现委员会会长"],
        "accent_color": "#991b1b"
    },
    {
        "name": "月雪宫子",
        "slug": "miyako",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["tsukiyuki_miyako", "miyako_(blue_archive)"],
        "pixiv_tag": "月雪ミヤコ",
        "aliases": ["宫子", "ミヤコ", "兔小队队长"],
        "accent_color": "#0ea5e9"
    },
    {
        "name": "空井咲",
        "slug": "saki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["sorai_saki", "saki_(blue_archive)"],
        "pixiv_tag": "空井サキ",
        "aliases": ["咲", "サキ", "头盔咲"],
        "accent_color": "#64748b"
    },
    {
        "name": "风仓萌绘",
        "slug": "moe",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kazekura_moe", "moe_(blue_archive)"],
        "pixiv_tag": "風倉モエ",
        "aliases": ["萌绘", "モエ", "迫击炮萌绘"],
        "accent_color": "#f59e0b"
    },
    {
        "name": "近卫美奈",
        "slug": "mina",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["konoe_mina", "mina_(blue_archive)"],
        "pixiv_tag": "近衛ミナ",
        "aliases": ["美奈", "玄龙门执行官"],
        "accent_color": "#0284c7"
    },
    {
        "name": "漆原琉美",
        "slug": "rumi",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["urushibara_rumi", "rumi_(blue_archive)"],
        "pixiv_tag": "漆原ルミ",
        "aliases": ["琉美", "ルミ", "炒饭姐"],
        "accent_color": "#f97316"
    },
    {
        "name": "春日椿",
        "slug": "tsubaki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kasuga_tsubaki", "tsubaki_(blue_archive)"],
        "pixiv_tag": "春日ツバキ",
        "aliases": ["椿", "ツバキ", "睡眠盾"],
        "accent_color": "#e11d48"
    },
    {
        "name": "久田泉奈",
        "slug": "izuna",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kuda_izuna", "izuna_(blue_archive)"],
        "pixiv_tag": "久田イズナ",
        "aliases": ["泉奈", "イズナ", "小狐狸", "忍忍"],
        "accent_color": "#ec4899"
    },
    {
        "name": "苍森美祢",
        "slug": "mine",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["aomori_mine", "mine_(blue_archive)"],
        "pixiv_tag": "蒼森ミネ",
        "aliases": ["美祢", "ミネ", "救护骑士团团长"],
        "accent_color": "#38bdf8"
    },
    {
        "name": "若叶日向",
        "slug": "hinata",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["wakaba_hinata", "hinata_(blue_archive)"],
        "pixiv_tag": "若葉ヒナタ",
        "aliases": ["日向", "ヒナタ", "修女日向"],
        "accent_color": "#60a5fa"
    },
    {
        "name": "黑崎小雪",
        "slug": "koyuki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["kurosaki_koyuki", "koyuki_(blue_archive)"],
        "pixiv_tag": "黒崎コユキ",
        "aliases": ["小雪", "コユキ", "哈哈哈", "恶作剧小雪"],
        "accent_color": "#f472b6"
    },
    {
        "name": "火宫风香",
        "slug": "fuuka",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["aikiyo_fuuka", "fuuka_(blue_archive)"],
        "pixiv_tag": "愛清フウカ",
        "aliases": ["风香", "フウカ", "苦劳人主厨"],
        "accent_color": "#10b981"
    },
    {
        "name": "鳄渊亚伽里",
        "slug": "akari",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["wanibuchi_akari", "akari_(blue_archive)"],
        "pixiv_tag": "鰐渕アカリ",
        "aliases": ["亚伽里", "大胃王"],
        "accent_color": "#ec4899"
    },
    {
        "name": "尾刃神奈",
        "slug": "kanna",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["ogata_kanna", "kanna_(blue_archive)"],
        "pixiv_tag": "尾刃カンナ",
        "aliases": ["神奈", "カンナ", "狂犬神奈", "局长"],
        "accent_color": "#64748b"
    },
    {
        "name": "戒野美咲",
        "slug": "misaki",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["imashino_misaki", "misaki_(blue_archive)"],
        "pixiv_tag": "戒野ミサキ",
        "aliases": ["美咲", "ミサキ", "火箭筒美咲"],
        "accent_color": "#6b7280"
    },
    {
        "name": "狮子堂泉",
        "slug": "izumi",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["shishidou_izumi", "izumi_(blue_archive)"],
        "pixiv_tag": "獅子堂イズミ",
        "aliases": ["泉", "イズミ", "汉堡泉"],
        "accent_color": "#f59e0b"
    },
    {
        "name": "静山真白",
        "slug": "mashiro",
        "game": "blue_archive",
        "game_name": "蔚蓝档案",
        "booru_tags": ["shizuyama_mashiro", "mashiro_(blue_archive)"],
        "pixiv_tag": "静山マシロ",
        "aliases": ["真白", "マシロ", "狙击真白"],
        "accent_color": "#64748b"
    }
]
