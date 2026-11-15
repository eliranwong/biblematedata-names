import os
import re
import sqlite3
from collections import Counter, defaultdict

def build_bl_mapping():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    indexes2_path = os.path.join(repo_root, "indexes2.sqlite")
    names_path = os.path.join(repo_root, "scripts", "names_english_chinese.py")
    people_data_path = os.path.join(repo_root, "biblePeople.data")
    exlb3_path = os.path.join(repo_root, "exlb3.data")
    
    # Path to CUV Bible
    cuv_bible_path = os.path.expanduser("~/biblemate/data/bibles/CUV.bible")
    if not os.path.exists(cuv_bible_path):
        cuv_bible_path = "/home/eliran/UniqueBible/marvelData/bibles/CUV.bible"

    # 1. Build Traditional -> Simplified character map
    tc2sc = {}
    line_regex_sub = re.compile(r'\"(\d+)\.(\d+)\.(\d+)\":\s*\[\"([^\"]*)\",\s*\"([^\"]*)\"')
    with open(names_path, "r", encoding="utf-8") as f:
        for line in f:
            m = line_regex_sub.search(line)
            if m:
                sc, tc = m.group(4), m.group(5)
                if len(sc) == len(tc):
                    for c1, c2 in zip(tc, sc):
                        if c1 != c2:
                            tc2sc[c1] = c2

    if os.path.exists(people_data_path):
        bconn = sqlite3.connect(people_data_path)
        for table in ["PEOPLE", "PEOPLERELATIONSHIP"]:
            tc_names = [r[0] for r in bconn.execute(f"SELECT Name FROM {table}_TC").fetchall()]
            sc_names = [r[0] for r in bconn.execute(f"SELECT Name FROM {table}_SC").fetchall()]
            for tc, sc in zip(tc_names, sc_names):
                if len(tc) == len(sc):
                    for c1, c2 in zip(tc, sc):
                        if c1 != c2:
                            tc2sc[c1] = c2
        bconn.close()

    try:
        from name_meanings_tc import name_meanings_tc
        from name_meanings_sc import name_meanings_sc
        for k, tc_val in name_meanings_tc.items():
            sc_val = name_meanings_sc.get(k, "")
            if len(tc_val) == len(sc_val):
                for c1, c2 in zip(tc_val, sc_val):
                    if c1 != c2:
                        tc2sc[c1] = c2
    except ImportError:
        pass

    # Ensure additional traditional characters are mapped accurately
    tc2sc.update({
        '臺': '台', '並': '并', '慾': '欲', '阬': '坑', '窪': '洼', '舖': '铺',
        '繫': '系', '迴': '回', '裏': '里', '嶽': '岳', '巖': '岩', '滙': '汇',
        '蹟': '迹', '歷': '历', '鬥': '斗', '恆': '恒', '迺': '乃', '祕': '秘'
    })

    def to_sc(s):
        return "".join(tc2sc.get(c, c) if c != "雅" else "雅" for c in s)

    # 2. Parse names_english_chinese.py preserving all verses and aliases
    line_regex_full = re.compile(r'\"(\d+)\.(\d+)\.(\d+)\":\s*\[\"([^\"]*)\",\s*\"([^\"]*)\",\s*\(([^)]*)\)\]')
    verse_names = defaultdict(list)
    global_eng = defaultdict(Counter)

    with open(names_path, "r", encoding="utf-8") as f:
        for line in f:
            m = line_regex_full.search(line)
            if m:
                b, c, v, sc, tc, eng_tuple_str = m.groups()
                engs = tuple(re.findall(r'\"([^\"]*)\"|\x27([^\x27]*)\x27', eng_tuple_str))
                eng_list = [e[0] or e[1] for e in engs]
                tc_clean = tc.replace(" ", "")
                sc_clean = sc.replace(" ", "")
                verse_names[(int(b), int(c), int(v))].append((sc_clean, tc_clean, eng_list))
                for e in eng_list:
                    if e:
                        global_eng[e.lower()][(tc_clean, sc_clean)] += 1

    # 3. Load exlbli canonical location names from exlb3.data
    exlb3 = sqlite3.connect(exlb3_path)
    bl_canon = dict(exlb3.execute("SELECT path, location FROM exlbli").fetchall())
    exlb3.close()

    # 4. Load CUV verses
    cuv_conn = sqlite3.connect(cuv_bible_path)
    cuv_dict = dict(cuv_conn.execute("SELECT Book*1000000 + Chapter*1000 + Verse, Scripture FROM Verses").fetchall())
    cuv_conn.close()

    # 5. Load exlbl rows
    iconn = sqlite3.connect(indexes2_path)
    rows = iconn.execute("SELECT Book, Chapter, Verse, Information FROM exlbl").fetchall()

    ref_regex = re.compile(r'<ref onclick=\"exlbl\(\x27([^\x27]+)\x27\)\">(.*?)(?:</exlbp>)?</ref>')

    bl_to_refs = defaultdict(list)
    for b, c, v, info in rows:
        for bl_id, name in ref_regex.findall(info):
            bl_to_refs[bl_id].append((b, c, v, name.strip()))

    # 6. Build base BL mappings (Level 1: verse match, Level 2: CUV-verified global match)
    bl_map = {}
    for bl_id, refs in bl_to_refs.items():
        counts = Counter()
        for b, c, v, name in refs:
            for sc, tc, engs in verse_names.get((b, c, v), []):
                if any(e and (e.lower() == name.lower() or name.lower() in [p.lower() for p in re.split(r'[/,-]', e)]) for e in engs):
                    if tc and sc:
                        counts[(tc, sc)] += 1
        if counts:
            bl_map[bl_id] = counts.most_common(1)[0][0]

    for bl_id, refs in bl_to_refs.items():
        if bl_id in bl_map:
            continue
        counts = Counter()
        canon = bl_canon.get(bl_id, "")
        for b, c, v, name in refs:
            cuv = re.sub(r'<[^>]+>', '', cuv_dict.get(b*1000000 + c*1000 + v, '')).strip()
            for cand, count in global_eng.get(name.lower(), {}).items():
                tc, sc = cand
                if tc and tc in cuv:
                    counts[cand] += count
            for part in re.split(r'[/,-]', canon):
                part = part.strip()
                for cand, count in global_eng.get(part.lower(), {}).items():
                    tc, sc = cand
                    if tc and tc in cuv:
                        counts[cand] += count
        if counts:
            bl_map[bl_id] = counts.most_common(1)[0][0]

    # Level 3: Verified CUV place names for remaining BL entries
    extra_bl_map = {
        'BL951': '比遜', 'BL1048': '西發', 'BL817': '摩利', 'BL202': '伯特利', 'BL1021': '鹽海',
        'BL393': '安‧密巴', 'BL697': '基列‧亞巴', 'BL167': '庇耳‧拉海‧萊', 'BL1075': '示巴',
        'BL631': '伊迦爾‧撒哈杜他', 'BL367': '伊勒‧伯特利', 'BL48': '亞倫‧巴古', 'BL355': '以得臺',
        'BL915': '巴旦', 'BL112': '亞達', 'BL986': '紅海', 'BL948': '比‧哈希錄', 'BL685': '基博羅‧哈他瓦',
        'BL117': '亞他林', 'BL1224': '撒烈', 'BL1228': '紅海', 'BL164': '比珥', 'BL700': '基列‧胡瑣',
        'BL1274': '瑣腓', 'BL707': '基提', 'BL1038': '示班', 'BL119': '亞他錄‧朔反', 'BL506': '比‧哈希錄',
        'BL854': '沙斐', 'BL1151': '他拉', 'BL807': '密加', 'BL174': '比尼‧亞干', 'BL579': '曷‧哈及甲',
        'BL13': '阿博拿', 'BL423': '以旬‧迦別', 'BL607': '以耶‧亞巴琳', 'BL50': '亞門‧低比拉太音',
        'BL215': '伯‧耶施末', 'BL44': '亞克拉濱', 'BL536': '哈薩‧亞達', 'BL1246': '西達達',
        'BL1268': '西斐崙', 'BL537': '哈薩‧以難', 'BL339': '底撒哈', 'BL1017': '撒迦', 'BL856': '西雲',
        'BL169': '比羅', 'BL823': '摩西拉', 'BL496': '谷歌大', 'BL1243': '撒拉但', 'BL191': '伯‧亞文',
        'BL1196': '亞割', 'BL214': '伯‧和崙', 'BL1197': '亞雅崙', 'BL494': '西頓',
        'BL806': '米斯利弗‧瑪音', 'BL203': '伯特利', 'BL1076': '西曷', 'BL1257': '細列‧哈沙轄',
        'BL668': '甲加', 'BL188': '伯‧亞拉巴', 'BL32': '亞都冥', 'BL396': '隱‧示麥', 'BL395': '隱‧羅結',
        'BL234': '伯‧示麥', 'BL1078': '施基崙', 'BL703': '基列‧西弗', 'BL550': '哈大他',
        'BL538': '哈薩‧迦大', 'BL227': '伯‧帕列', 'BL251': '比斯約他', 'BL387': '隱‧干寧',
        'BL298': '基提利', 'BL598': '益弗他', 'BL702': '基列‧薩拿', 'BL410': '以珊', 'BL620': '雅農',
        'BL242': '伯‧夙', 'BL185': '伯‧亞諾', 'BL302': '鹽城', 'BL389': '隱‧基底', 'BL733': '伯‧和崙',
        'BL115': '亞他綠‧亞達', 'BL1188': '伯‧和崙', 'BL794': '密米他', 'BL621': '雅挪哈',
        'BL867': '拿拉', 'BL233': '伯‧善', 'BL124': '亞文', 'BL505': '以利弗', 'BL222': '伯‧瑪加博',
        'BL540': '哈薩‧蘇撒', 'BL318': '大巴設', 'BL420': '以特‧加汛', 'BL1208': '伊弗他‧伊勒',
        'BL351': '亞別', 'BL388': '隱‧干寧', 'BL390': '隱‧哈大', 'BL226': '伯‧帕薛',
        'BL1057': '沙哈洗瑪', 'BL235': '伯‧示麥', 'BL47': '亞拉米勒', 'BL1077': '希曷‧立納',
        'BL204': '伯‧以墨', 'BL352': '義伯崙', 'BL1094': '西頓', 'BL23': '亞大米‧尼吉',
        'BL715': '拉共', 'BL586': '戶割', 'BL797': '密大‧伊勒', 'BL184': '伯‧亞納', 'BL236': '伯‧示麥',
        'BL600': '伊珥‧示麥', 'BL602': '伊提拉', 'BL173': '比尼‧比拉', 'BL778': '美‧耶昆',
        'BL15': '亞柯', 'BL840': '希烈', 'BL1166': '亭拿‧希烈', 'BL1043': '西伊拉', 'BL530': '夏羅設',
        'BL529': '哈律', 'BL818': '摩利', 'BL237': '伯‧哈示他', 'BL1256': '西利拉', 'BL194': '伯‧巴拉',
        'BL165': '比珥', 'BL338': '米惡尼尼', 'BL665': '加們', 'BL391': '隱‧哈歌利', 'BL404': '以法他',
        'BL977': '拉瑪‧瑣非', 'BL196': '伯‧甲', 'BL1058': '沙利沙', 'BL1054': '沙琳',
        'BL1222': '洗波音', 'BL399': '以弗‧大憫', 'BL1041': '西沽', 'BL563': '哈列', 'BL500': '哈基拉',
        'BL639': '曠野', 'BL968': '拉哈勒', 'BL253': '歌拉珊', 'BL232': '伯‧珊',
        'BL559': '希利甲‧哈素林', 'BL57': '亞瑪', 'BL1100': '西拉', 'BL139': '巴拉‧猶大',
        'BL791': '京城的權柄', 'BL1215': '鹽谷', 'BL732': '羅‧底巴', 'BL861': '橄欖山',
        'BL221': '伯‧瑪迦', 'BL662': '他停‧合示', 'BL1051': '瑣希列', 'BL97': '亞魯泊',
        'BL1254': '洗利達', 'BL1171': '提斯比', 'BL1': '亞罷拿', 'BL1236': '撒益', 'BL497': '姑珥',
        'BL315': '古他', 'BL123': '亞瓦', 'BL605': '以瓦', 'BL1040': '第二區', 'BL1226': '欣嫩子谷',
        'BL309': '哥西巴', 'BL725': '雅叔比利恆', 'BL541': '哈薩‧蘇撒', 'BL195': '伯‧比利',
        'BL876': '拿非施', 'BL525': '哈拉', 'BL696': '基列亭', 'BL1006': '臨摩挪', 'BL618': '雅哈撒',
        'BL734': '伯‧和崙', 'BL1193': '烏羨‧舍伊拉', 'BL923': '巴斯‧達閔', 'BL153': '巴路米',
        'BL311': '均', 'BL1255': '撒利但', 'BL1104': '梭哥', 'BL406': '以法拉音', 'BL1200': '比拉迦',
        'BL498': '姑珥‧巴力', 'BL698': '基列‧耶琳', 'BL1148': '特‧米拉', 'BL1147': '特‧哈薩',
        'BL1118': '書珊', 'BL353': '亞馬他', 'BL1177': '哈楠業', 'BL209': '伯‧哈基琳',
        'BL863': '哈米弗甲', 'BL847': '米薩', 'BL84': '亞蘭‧拿哈蓮', 'BL85': '亞蘭‧瑣巴',
        'BL1237': '撒們', 'BL1199': '流淚谷', 'BL160': '巴特‧拉併', 'BL714': '萊煞',
        'BL301': '滅亡城', 'BL482': '歌亞', 'BL557': '伯‧示麥', 'BL1156': '挪',
        'BL199': '伯‧低比拉太音', 'BL223': '伯‧米恩', 'BL1143': '提勒‧亞畢', 'BL435': '勇士',
        'BL929': '訓', 'BL947': '比伯實', 'BL386': '隱‧以革蓮', 'BL543': '哈撒‧哈提干',
        'BL121': '亞文', 'BL189': '伯‧亞比勒', 'BL1198': '亞文', 'BL216': '伯‧亞弗拉',
        'BL1062': '沙斐', 'BL206': '伯‧以薛', 'BL371': '伊勒歌斯', 'BL822': '瑪革提施',
        'BL501': '哈達臨門', 'BL753': '馬加丹', 'BL90': '亞利馬太', 'BL592': '以土買',
        'BL604': '以土利亞', 'BL1181': '特拉可尼', 'BL1154': '髑髏地', 'BL187': '伯大巴喇',
        'BL658': '猶太', 'BL205': '畢士大', 'BL1155': '鋪華石處', 'BL43': '亞革大馬',
        'BL944': '腓尼基', 'BL1025': '撒摩特喇', 'BL880': '尼亞坡里', 'BL308': '哥士',
        'BL29': '亞大米田', 'BL864': '每拉', 'BL424': '佳澳', 'BL945': '菲尼基', 'BL280': '高大',
        'BL1123': '賽耳底沙灘', 'BL30': '亞得里亞海', 'BL761': '馬耳他', 'BL427': '亞比烏',
        'BL1159': '三館', 'BL305': '歌羅西', 'BL937': '別迦摩',
        'BL5': '亞伯‧伯‧瑪迦', 'BL7': '亞伯‧瑪音', 'BL8': '亞伯‧米何拉', 'BL10': '亞伯‧什亭',
        'BL83': '亞蘭‧瑪迦', 'BL131': '亞斯納‧他泊', 'BL138': '巴拉‧比珥', 'BL140': '巴力‧迦得',
        'BL141': '巴力‧哈們', 'BL142': '巴力‧夏瑣', 'BL143': '巴力‧黑們', 'BL144': '巴力‧免',
        'BL146': '巴力‧毗拉心', 'BL147': '巴力‧沙利沙', 'BL148': '巴力‧他瑪', 'BL149': '巴力‧洗分',
        'BL158': '巴末‧巴力', 'BL166': '比珥‧以琳', 'BL193': '伯‧巴力‧勉', 'BL197': '伯‧大袞',
        'BL198': '伯‧大袞', 'BL207': '伯‧迦末', 'BL211': '伯‧亞蘭', 'BL212': '伯‧哈蘭',
        'BL213': '伯‧曷拉', 'BL224': '伯米羅', 'BL225': '伯‧寧拉', 'BL228': '伯‧毗珥',
        'BL230': '伯‧利合', 'BL267': '凱撒利亞腓立比', 'BL297': '吉斯綠‧他泊', 'BL323': '但‧雅安',
        'BL333': '底本‧迦得', 'BL350': '以便以謝', 'BL374': '以倫‧伯‧哈南', 'BL376': '伊勒‧巴蘭',
        'BL385': '隱‧多珥', 'BL392': '隱‧夏瑣', 'BL394': '音‧臨門', 'BL443': '迦特‧希弗',
        'BL444': '迦特‧臨門', 'BL445': '迦特‧臨門', 'BL517': '哈馬瑣巴', 'BL520': '哈末‧多珥',
        'BL539': '哈薩‧書亞', 'BL542': '哈洗遜‧他瑪', 'BL611': '基列‧雅比', 'BL684': '加略希斯崙',
        'BL694': '吉珥‧哈列設', 'BL699': '基列‧巴力', 'BL701': '基列‧耶琳', 'BL757': '瑪哈尼‧但',
        'BL798': '麥大‧迦得', 'BL820': '摩利設‧迦特', 'BL829': '巴力‧黑們', 'BL916': '巴旦‧亞蘭',
        'BL934': '毗列斯‧烏撒', 'BL935': '毗列斯‧烏撒', 'BL978': '拉末‧利希', 'BL1007': '臨門‧帕烈',
        'BL1083': '伸崙‧米崙', 'BL1125': '他納‧示羅', 'BL1167': '亭拿‧西拉', 'BL1205': '哈們‧歌革',
        'BL175': '便雅憫', 'BL220': '以法他', 'BL239': '陀迦瑪', 'BL398': '以法',
        'BL401': '以法蓮', 'BL402': '以法蓮', 'BL408': '以掃', 'BL436': '迦立',
        'BL438': '以法蓮', 'BL460': '基暗', 'BL484': '歌革', 'BL515': '含',
        'BL524': '哈弗連', 'BL527': '哈蘭', 'BL627': '雅完', 'BL674': '基達',
        'BL754': '瑪各', 'BL788': '米設', 'BL789': '米設／土巴', 'BL833': '以法蓮',
        'BL835': '以掃', 'BL881': '尼拜約', 'BL898': '寧錄', 'BL985': '利迦',
        'BL1183': '土巴', 'BL1192': '烏撒', 'BL1209': '約沙法',
    }
    for bl, tc in extra_bl_map.items():
        bl_map[bl] = (tc, to_sc(tc))

    # Demonym and specific surface-form overrides
    pair_overrides = {
        ('BL362', 'egyptians'): ('埃及人', '埃及人'),
        ('BL362', 'egyptian'): ('埃及人', '埃及人'),
        ('BL796', 'midianites'): ('米甸人', '米甸人'),
        ('BL796', 'midianitish'): ('米甸女子', '米甸女子'),
        ('BL272', 'canaanite'): ('迦南人', '迦南人'),
        ('BL272', 'canaanitish'): ('迦南女子', '迦南女子'),
        ('BL475', 'gileadite'): ('基列人', '基列人'),
        ('BL475', 'gileadites'): ('基列人', '基列人'),
        ('BL815', 'moabites'): ('摩押人', '摩押人'),
        ('BL815', 'moabitish'): ('摩押女子', '摩押女子'),
        ('BL357', 'edomite'): ('以東人', '以东人'),
        ('BL357', 'edomites'): ('以東人', '以东人'),
        ('BL111', 'assyrian'): ('亞述人', '亚述人'),
        ('BL111', 'assyrians'): ('亞述人', '亚述人'),
        ('BL899', 'ninevites'): ('尼尼微人', '尼尼微人'),
        ('BL1118', 'susanchites'): ('書珊迦人', '书珊迦人'),
        ('BL407', 'archevites'): ('亞基衛人', '亚基卫人'),
        ('BL1084', 'babylonish'): ('示拿的', '示拿的'),
        ('BL470', 'gibeonite'): ('基遍人', '基遍人'),
        ('BL278', 'carmelite'): ('迦密人', '迦密人'),
        ('BL442', 'gittites'): ('迦特人', '迦特人'),
        ('BL1050', 'sepharvites'): ('西法瓦音人', '西法瓦音人'),
        ('BL234', 'bethshemite'): ('伯‧示麥人', '伯‧示麦人'),
        ('BL53', 'amalekites'): ('亞瑪力人', '亚玛力人'),
        ('BL735', 'lydians'): ('路德人', '路德人'),
        ('BL643', 'jezreelite'): ('耶斯列人', '耶斯列人'),
        ('BL154', 'barhumite'): ('巴路米人', '巴路米人'),
        ('BL153', 'baharumite'): ('巴路米人', '巴路米人'),
        ('BL529', 'harodite'): ('哈律人', '哈律人'),
        ('BL371', 'elkoshite'): ('伊勒歌斯人', '伊勒歌斯人'),
        ('BL168', 'beerothite'): ('比錄人', '比录人'),
        ('BL101', 'ashdothites'): ('亞實突人', '亚实突人'),
        ('BL452', 'gederathite'): ('基低拉人', '基低拉人'),
        ('BL1122', 'syrians'): ('亞蘭人', '亚兰人'),
        ('BL461', 'geshurites'): ('基述人', '基述人'),
        ('BL63', 'anetothite'): ('亞拿突人', '亚拿突人'),
        ('BL58', 'ammonites'): ('亞捫人', '亚扪人'),
        ('BL564', 'hermonites'): ('黑門人', '黑门人'),
        ('BL317', 'cyrenian'): ('古利奈人', '古利奈人'),
        ('BL743', 'maachathite'): ('瑪迦人', '玛迦人'),
        ('BL1171', 'tishbite'): ('提斯比人', '提斯比人'),
        ('BL949', 'pirathonite'): ('比拉頓人', '比拉顿人'),
        ('BL87', 'areopagite'): ('亞略‧巴古的官', '亚略‧巴古的官'),
        ('BL421', 'river'): ('大河', '大河'),
        ('BL902', 'city'): ('城', '城'),
        ('BL272', 'city'): ('城', '城'),
        ('BL1044', 'rock'): ('山頂', '山顶'),
        ('BL1040', 'college'): ('第二區', '第二区'),
        ('BL1123', 'quicksands'): ('賽耳底沙灘', '赛耳底沙滩'),
        ('BL1159', 'taverns'): ('三館', '三馆'),
        ('BL424', 'havens'): ('佳澳', '佳澳'),
        ('BL117', 'spies'): ('亞他林', '亚他林'),
        ('BL87', 'hill'): ('亞略‧巴古', '亚略‧巴古'),
        ('BL1032', 'sea of galilee'): ('加利利海', '加利利海'),
        ('BL799', 'tower'): ('色弗尼塔', '色弗尼塔'),
        ('BL301', 'destruction'): ('滅亡城', '灭亡城'),
        ('BL782', 'waters'): ('米利巴水', '米利巴水'),
        ('BL259', 'waters'): ('米利巴‧加低斯的水', '米利巴‧加低斯的水'),
        ('BL2', 'passages'): ('亞巴琳', '亚巴琳'),
        ('BL986', 'red'): ('紅海', '红海'),
        ('BL986', 'sea'): ('紅海', '红海'),
        ('BL1021', 'salt'): ('鹽海', '盐海'),
        ('BL1021', 'sea'): ('鹽海', '盐海'),
        ('BL1215', 'salt'): ('鹽谷', '盐谷'),
        ('BL1228', 'red'): ('紅海', '红海'),
        ('BL1228', 'sea'): ('紅海', '红海'),
        ('BL202', 'house'): ('伯特利', '伯特利'),
        ('BL962', 'put'): ('挪弗', '挪弗'),
        ('BL783', 'wilderness'): ('曠野', '旷野'),
        ('BL452', 'hedges'): ('基低拉', '基低拉'),
        ('BL1241', 'northward'): ('北方', '北方'),
        ('BL1101', 'field'): ('田野', '田野'),
    }

    return bl_map, verse_names, pair_overrides, rows, ref_regex, iconn

def main():
    print("Loading datasets...")
    bl_map, verse_names, pair_overrides, rows, ref_regex, iconn = build_bl_mapping()

    def make_replacer(b, c, v, is_tc=True):
        def _repl(m):
            bl_id = m.group(1)
            name = m.group(2).strip()
            key = (bl_id, name.lower())
            if key in pair_overrides:
                rep = pair_overrides[key][0 if is_tc else 1]
                return f'<ref onclick=\"exlbl(\x27{bl_id}\x27)\">{rep}</ref>'
            for sc, tc, engs in verse_names.get((b, c, v), []):
                if any(e and (e.lower() == name.lower() or name.lower() in [p.lower() for p in re.split(r'[/,-]', e)]) for e in engs):
                    if tc and sc:
                        rep = tc if is_tc else sc
                        return f'<ref onclick=\"exlbl(\x27{bl_id}\x27)\">{rep}</ref>'
            if bl_id in bl_map:
                rep = bl_map[bl_id][0 if is_tc else 1]
                return f'<ref onclick=\"exlbl(\x27{bl_id}\x27)\">{rep}</ref>'
            return f'<ref onclick=\"exlbl(\x27{bl_id}\x27)\">{name}</ref>'
        return _repl

    print("Generating Traditional Chinese and Simplified Chinese data...")
    tc_data = []
    sc_data = []
    for b, c, v, info in rows:
        tc_info = ref_regex.sub(make_replacer(b, c, v, is_tc=True), info)
        sc_info = ref_regex.sub(make_replacer(b, c, v, is_tc=False), info)
        tc_data.append((b, c, v, tc_info))
        sc_data.append((b, c, v, sc_info))

    # Verify no untranslated English remains
    inner_ref = re.compile(r'<ref onclick=\"exlbl\(\x27[^\x27]+\x27\)\">(.*?)</ref>')
    for b, c, v, info in tc_data:
        for text in inner_ref.findall(info):
            if re.search(r'[A-Za-z]', text):
                raise ValueError(f"Untranslated English in TC: {b}.{c}.{v} -> {text}")

    for b, c, v, info in sc_data:
        for text in inner_ref.findall(info):
            if re.search(r'[A-Za-z]', text):
                raise ValueError(f"Untranslated English in SC: {b}.{c}.{v} -> {text}")

    print("Writing to indexes2.sqlite...")
    cursor = iconn.cursor()
    cursor.execute("BEGIN TRANSACTION;")
    cursor.execute("DROP TABLE IF EXISTS exlbl_tc;")
    cursor.execute("CREATE TABLE exlbl_tc (Book INT, Chapter INT, Verse INT, Information TEXT);")
    cursor.executemany("INSERT INTO exlbl_tc (Book, Chapter, Verse, Information) VALUES (?, ?, ?, ?);", tc_data)

    cursor.execute("DROP TABLE IF EXISTS exlbl_sc;")
    cursor.execute("CREATE TABLE exlbl_sc (Book INT, Chapter INT, Verse INT, Information TEXT);")
    cursor.executemany("INSERT INTO exlbl_sc (Book, Chapter, Verse, Information) VALUES (?, ?, ?, ?);", sc_data)

    iconn.commit()

    count_tc = iconn.execute("SELECT COUNT(*) FROM exlbl_tc;").fetchone()[0]
    count_sc = iconn.execute("SELECT COUNT(*) FROM exlbl_sc;").fetchone()[0]
    count_orig = iconn.execute("SELECT COUNT(*) FROM exlbl;").fetchone()[0]
    iconn.close()

    print(f"Original exlbl rows: {count_orig}")
    print(f"Created exlbl_tc rows: {count_tc}")
    print(f"Created exlbl_sc rows: {count_sc}")

if __name__ == "__main__":
    main()

