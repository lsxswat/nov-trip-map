#!/usr/bin/env python3
"""Fix short tips and desc in trip-data.json"""
import json

with open('/Users/talentclaw/.openclaw/workspace/nov-trip/trip-data.json', 'r') as f:
    td = json.load(f)

# Map of POI name to improved (longer) tips
TIPS_FIXES = {}
DESC_FIXES = {}

# Day 4 - expand tips
TIPS_FIXES["Grand View Point"] = "🥾 1.8 mi 往返，平坦易走，老少皆宜\n📸 傍晚光线最佳，但任何时间都令人震撼，建议广角+长焦各带一支\n🧭 有图标注解说牌帮助理解峡谷地质层次\n🧴 海拔 6000+ 英尺，紫外线强，务必涂防晒霜\n⏰ 建议停留 30-60 分钟，走到最远端约需 20 分钟\n💧 即使是冬天也要带水，干燥环境脱水快"
TIPS_FIXES["Green River Overlook"] = "🚶 从停车场步行不到 5 分钟即达\n📸 全景拍摄的最佳点之一，推荐接片（panorama）\n🌅 日落时分尤为壮观，峡谷壁被染成金色\n⚠️ 悬崖边缘有安全护栏，相对安全\n🅿️ 停车位较充足，通常不需要抢位置\n⏰ 观景点本身 15-20 分钟即可，但建议多待一会感受壮丽"
TIPS_FIXES["Park Avenue (Arches)"] = "🥾 1 mi 往返，注意回程是上坡（从峡谷底部爬回停车场）\n📸 清晨光线从峡谷东侧照入最漂亮\n🧴 峡谷底部上午有阴影，气温可能很低（接近冰点）\n⏰ 约需 30-45 分钟往返\n🚗 停车场就在拱门公园入口处，不要错过\n👟 穿好抓地力的鞋子，部分路面有沙砾"
TIPS_FIXES["Balanced Rock"] = "🥾 0.3 mi 环路，平坦无障碍，轮椅也可到达\n📸 任何角度都好看——日落时岩石会发出金色光芒\n🅿️ 有专用停车场，通常有位置\n⏰ 15-20 分钟即可，是路过必经之站\n🌅 日落前 30 分钟光线最暖\n🧒 全程平路，非常适合家庭游客"
TIPS_FIXES["Windows Section"] = "🥾 1 mi 环路，部分有台阶，总体容易走\n🌅 日出时北窗是完美的天然取景框——太阳从拱门中升起\n🅿️ Windows 停车场容易满员，建议早去（8am前）或傍晚去（3pm后）\n📸 广角镜头拍全景，中长焦拍拱门细节\n⏰ 建议停留 1 小时，三个拱门都要走到\n🚻 停车场有洗手间"
TIPS_FIXES["Double Arch"] = "🥾 0.5 mi 往返，最后一段可爬上岩石基座站在拱门正下方\n📸 超广角或全景模式才能完整拍下巨大开口，手机全景模式很好用\n🎬 夺宝奇兵 3 取景地——站在拱门下感受电影场景\n⏰ 30-45 分钟足矣\n🚗 与 Windows 共用车场，可一并游玩\n🧗 爬上基座需简单攀爬，穿防滑鞋"

# Day 5
TIPS_FIXES["Landscape Arch"] = "🥾 1.9 mi 往返，路面硬化平坦，适合各类游客\n📸 超广角或全景模式才能拍下全拱（306英尺跨度）\n⚠️ 拱门下方区域已对游客关闭（1991年落石事件后）\n⏰ 建议清晨前往（8am前），光线好且游客少\n🅿️ Devils Garden 停车场相对较大但旺季仍可能满员\n💧 沿途无水源，自带饮水"
TIPS_FIXES["Sand Dune Arch"] = "🥾 0.4 mi 往返，最后需侧身挤过狭窄岩缝\n🧒 孩子们的最爱！可以在厚厚红沙上玩耍（带个小铲子更好）\n🧣 被高墙包围常年阴凉——即使是夏天也需要薄外套\n📸 正午时分阳光从顶部裂缝洒入，光线最有层次感\n⏰ 15-20 分钟即到，但孩子们可能想多玩一会沙\n👟 沙地行走，穿不介意进沙的鞋子"
TIPS_FIXES["Skyline Arch"] = "🥾 0.4 mi 往返，几乎没有难度\n🧒 家庭友好，适合各种年龄段\n📸 下午光线最柔和，拱门在不同时间呈现不同色彩\n⏰ 15-20 分钟即可，魔鬼花园探索的轻松收尾\n🚗 Devil's Garden 停车场出发\n🌄 日出时拱门被照亮，也是不错的拍摄时机"
TIPS_FIXES["Capitol Reef Petroglyphs"] = "🚶 木栈道平坦易走，从停车场走 5 分钟即到\n🎫 完全免费！在 Hwy 24 路边，无需国家公园门票\n⚠️ 严禁触摸岩画——手上的油脂会破坏千年岩石表面\n📸 上午光线最适合拍照，阴影不能太深\nℹ️ 解说牌有英文详细信息\n⏰ 15-20 分钟即可，路过顺便看"
TIPS_FIXES["Hickman Bridge"] = "🥾 1.8 mi 往返，中等难度（有海拔爬升）\n⏰ 约需 1-1.5 小时，别排太紧\n🧴 步道部分路段无遮荫，涂防晒\n📸 站在桥下仰拍效果最好，用广角镜头\n🌅 上午光线最佳（从东边照入桥下）\n🚻 停车场有洗手间"
TIPS_FIXES["Sunset Point / Goosenecks"] = "🌅 日落前 30 分钟到达最佳，金光照在曲流上\n🚶 5 分钟步行即达，路面平坦\n📸 三脚架拍日落/星空效果惊艳——圆顶礁是国际暗夜公园\n🌌 晚上可以看银河！圆顶礁几乎没有光污染\n⚠️ 悬崖无护栏，带小孩的话要牵好手\n🅿️ 停车位充足，通常不拥挤"

# Day 6
TIPS_FIXES["Sunrise Point (Bryce)"] = "🌅 日出前 30 分钟到达占位置（11 月日出约 7:00-7:10）\n🧣 海拔 8000ft，11 月早间气温 -5°C 到 0°C，穿最厚的衣服！\n🅿️ 观景台旁有大型停车场，日出时段也够用\n📸 渐变滤镜有助于平衡天空和峡谷的曝光\n🏠 Bryce Canyon Lodge 就在附近，可步行过来\n☕ 带热饮！站着等日出时的一杯热咖啡是救命的"
TIPS_FIXES["Sunset Point (Bryce)"] = "🌅 日落前 1 小时到达占好位置（最受欢迎的观景台）\n📸 雷神之锤就在左下方，85mm 以上镜头可拍细节\n🥾 纳瓦霍环路入口在此——可以后续徒步\n🧥 日落前后温差极大，多带衣物\n🅿️ 停车位比 Sunrise Point 少，早点到\n🌄 日落后的暮光也很美，别急着走"
TIPS_FIXES["Inspiration Point"] = "🪜 三层观景台，顶层需要爬 100+ 级楼梯（海拔 8100ft）\n🫁 高海拔空气稀薄，慢走避免高反，喘不过气就休息\n📸 顶层是拍全景的最佳点，360°覆盖整个圆形剧场\n⏰ 任何时间光线都不错，朝南方向上午最好\n🧥 三层之间温差不大但风大，穿防风外套\n🅿️ 停车位中等大小，旺季会满"
TIPS_FIXES["Bryce Point"] = "🌅 此处日出比 Sunrise Point 更有层次感——岩柱层层点亮\n🚗 11 月通往 Bryce Point 的支路可能因雪关闭，去前在游客中心查路况\n🅿️ 停车位较 Sunrise 和 Sunset 少，早到为佳\n📸 长焦压缩岩柱层次感极强，推荐 70-200mm\n⏰ 日出后 1 小时内光线最佳\n🧥 最南端观景台风更大，注意保暖"

# Day 7
TIPS_FIXES["Checkerboard Mesa"] = "🚗 UT-9 公路边即可看到，无需徒步\n📸 下午阳光从西南方向照来，交叉格纹最明显\n🅿️ 路边有小型停车带（仅容 5-6 辆车），不要在行车道上停车\n⏰ 停车拍照 5-10 分钟即可\n🗺️ 位于锡安东入口和隧道之间\n⚠️ 公路弯道处有车辆经过，注意安全"
TIPS_FIXES["Zion-Mount Carmel Tunnel"] = "🚗 SUV/轿车可以直接双向通行\n🚐 RV/大型房车/拖车需购买 $15 护送通行证并在入口处等待管制\n📸 隧道内严禁停车拍照！窗洞只能一扫而过\n🕰️ 建成于 1930 年，1.1 英里长，是国家历史性土木工程里程碑\n⏰ 通行约需 2-3 分钟\n⚠️ 隧道内较暗，开近光灯"
TIPS_FIXES["Canyon Overlook Trail"] = "🥾 1 mi 往返，中等难度（部分路段无护栏）\n📸 下午光线最佳——太阳从西边照亮峡谷西壁\n🚗 停车位极其有限（仅 8-10 个车位）！早去或晚去\n⚠️ 部分路段在天然岩面上行走，无护栏，牵着孩子\n⏰ 往返 30-60 分钟\n🧥 悬崖边风大，注意保暖"
TIPS_FIXES["Scout Lookout (Optional)"] = "🥾 4 mi 往返，艰苦！大量台阶和之字路，海拔爬升约 1500ft\n🚫 Scout Lookout 不需要天使降临许可证——可以放心到这里\n💧 每人至少带 2 升水，爬坡消耗极大\n⏰ 约需 2-3 小时往返\n🧥 峡谷底部和山顶温差可能达 10°C，分层穿着\n🌅 清晨开始徒步避开人流和高温"
TIPS_FIXES["Las Vegas Sphere"] = "🎪 绿野仙踪沉浸秀约 75 分钟，需提前官网购票\n📸 外景完全免费观看，任何角度都震撼——白天和晚上效果不同\n🍕 周边有大量餐饮（Venetian/Palazzo 内）\n🅿️ 停车在 Venetian 或 Palazzo 酒店停车场\n⏰ 内部秀需提前购票并按时入场；外景随时可看\n📱 晚上 Sphere 外部灯光更精彩"
TIPS_FIXES["Downtown LA"] = "🌙 预计抵达 22:00-23:00，建议直接去酒店休息\n🚗 今天是行程中驾驶距离最长的一天（超过 8 小时）\n🍜 韩国城（Koreatown）和市中心有开到凌晨的餐厅\n🏨 提前确认酒店允许深夜入住（late check-in）\n⛽ 在洛杉矶加满油，明天是婚礼日不安排开车\n😴 好好休息！明天是特别的日子"

# Day 9 - fix Los Angeles desc
DESC_FIXES["Los Angeles"] = "今天是大日子——婚礼日！洛杉矶在 11 月天气宜人（约 15-22°C），阳光明媚，是举办婚礼的绝佳时节。这座天使之城既有着好莱坞的星光熠熠，也有圣莫尼卡海滩的悠闲惬意，还有格里菲斯天文台的浪漫夜景。今天没有安排任何观光行程，全身心享受这特别的一天。如果在婚礼前后有空余时间，可以漫步在比弗利山庄、参观盖蒂中心或在威尼斯海滩散步——但最重要的是享受与亲朋好友的欢聚时刻。洛杉矶的秋天碧空如洗，希望你们的婚礼像这座城市一样充满阳光和欢乐。恭喜！💒✨"

# Day 10
TIPS_FIXES["Hidden Valley"] = "🥾 1 mi 环路，平坦易走，家庭友好\n🧗 攀岩者最爱的抱石圣地——可以观赏世界级攀岩者的精彩表演\n📸 约书亚树 + 巨型花岗岩的组合最代表公园特色\n⏰ 约 30-45 分钟走完\n🌅 上午光线最佳——阳光从东边照亮岩石正面\n🚻 停车场有洗手间，旺季停车位紧张"
TIPS_FIXES["Keys View"] = "🚶 从停车场只需步行 5 分钟（铺装坡道）\n🌬️ 山顶风大且冷（5000ft+）！带防风外套，帽子一定要系紧\n🔭 远眺索尔顿湖、圣安德烈亚斯断层和墨西哥边境山脉\n📸 冬季空气最清澈，能见度可达 100+ 英里\n🌅 日落时分俯瞰 Coachella 谷灯光渐亮也很美\n⚠️ 山顶无任何遮风处，大风天慎去"
TIPS_FIXES["Skull Rock"] = "🚗 就在 Park Boulevard 路边，无需徒步即可到达\n🧒 孩子们的最爱——可以爬进眼窝拍照！\n📸 上午或下午侧面光线最能突出骷髅形状\n⏰ 15-20 分钟拍照足够\n🥾 想深入探索可走 Jumbo Rocks 或 1.7 mi 环形步道\n🅿️ 路边随意停车（非正规停车场，注意不要阻碍交通）"
TIPS_FIXES["Cholla Cactus Garden"] = "⚠️ 绝对不要触摸仙人掌！泰迪熊倒刺极难拔除\n🌅 日落前 1 小时是黄金摄影时段——逆光让刺针像在发光\n🥾 0.25 mi 环路，平坦木栈道\n📸 长焦压缩仙人掌密度的效果最佳\n🩹 建议随身携带镊子（以防万一被刺）\n🚗 小停车场，但游客周转快，通常能找到位置"
TIPS_FIXES["Cottonwood Spring"] = "🚗 南出口——不需要折返回西入口，节省至少 1 小时\n🚰 游客中心有饮用水和洗手间\n⏰ 出园后开车约 30 分钟接上 I-10 高速\n🌴 微型绿洲，与公园北部的约书亚树景观截然不同\n🥾 可走短程步道（约 0.5mi）探索泉水和棕榈树\n📸 Cottonwood trees 的秋叶在 11 月可能还挂着"

# Day 11
TIPS_FIXES["La Jolla Cove"] = "🦭 海狮和海豹全年可见，保持 15 米以上距离（联邦法律要求）\n🅿️ 街边停车极其困难，建议使用 Coastal Blvd 沿线付费停车场\n🌊 低潮时潮汐池最精彩——提前查潮汐表\n🚶 海岸步行道（Coast Walk Trail）免费，可以走到 Children's Pool\n🧥 海风很大，即使晴天也要带外套\n⏰ 上午人少，海狮最活跃；下午阳光好但人也多"
TIPS_FIXES["Hotel del Coronado"] = "🏖️ 酒店后方沙滩对公众开放——从旁边公共入口进\n📸 最佳拍照点：在沙滩上以低角度仰拍酒店全貌\n🍹 Sun Deck 酒吧鸡尾酒 $15-20，价格偏高但景色值回票价\n🚗 科罗纳多大桥免费过桥\n🅿️ 酒店停车场收费 $20+，街边也有限时免费停车\n🏛️ 大堂可以自由参观（华丽的木质内饰和百年历史照片）"
TIPS_FIXES["Coronado Beach"] = "🌅 日落时分沙滩金光闪闪——云母矿物在余晖中闪烁\n🚶 从 Hotel del Coronado 可以沿着沙滩直接走过来（约 10 分钟）\n🐚 沙滩因云母矿物而带有独特的金色光芒\n🅿️ Ocean Blvd 沿线有免费街边停车（限时 2-3 小时）\n🧥 傍晚海风较大，多穿衣物\n🏄 北端有指定冲浪区域，南端更适合游泳和散步"

# Day 12
TIPS_FIXES["Cabrillo National Monument"] = "🌊 圣地亚哥湾最佳全景——能看到市中心、Coronado 和北岛海军基地\n🐋 11 月是灰鲸南迁季节！带望远镜在 Whale Overlook 守候\n💲 约 $20/车（NPS 门票）\n🏠 Old Point Loma Lighthouse 免费参观，内部还原 1855 年样貌\n⏰ 建议上午去——午后 Point Loma 常被海雾笼罩\n🅿️ 山顶停车场免费"
TIPS_FIXES["USS Midway Museum"] = "⏰ 至少预留 2-3 小时——展区庞大，内容极其丰富\n💲 成人约 $34，儿童优惠（建议网上提前购票免排队）\n🎧 语音导览含在门票中，有中文选项\n🛩️ 飞行甲板上停放着 F-14、F/A-18 等著名战机，可以进入部分驾驶舱\n👴 志愿者讲解员很多是退役海军老兵——和他们聊聊天，故事极其精彩\n📸 甲板上向西拍科罗纳多大桥，向北拍市中心天际线"
TIPS_FIXES["LAX Airport"] = "🚗 18:00 前还车（租车合同截止时间）\n✈️ 19:30 前完成托运和安检\n🛫 航班 23:00，国际航班建议提前 3 小时到达\n🧳 确认所有行李符合航空公司重量限制\n📱 登机前最后确认所有照片已备份到云端\n🌟 行程终点！12 天 5 个国家公园，2,000+ 英里——完美的旅程"

# Apply fixes
for day in td:
    for poi in day['pois']:
        n = poi['name']
        if n in TIPS_FIXES:
            poi['tips'] = TIPS_FIXES[n]
        if n in DESC_FIXES:
            poi['desc'] = DESC_FIXES[n]

# Verify
total = 0
desc_ok = 0
tips_ok = 0
for day in td:
    for poi in day['pois']:
        total += 1
        dl = len(poi.get('desc',''))
        tl = len(poi.get('tips',''))
        if dl >= 200: desc_ok += 1
        else: print(f"  STILL SHORT desc: {poi['name']} = {dl} chars")
        if tl >= 100: tips_ok += 1
        else: print(f"  STILL SHORT tips: {poi['name']} = {tl} chars")

print(f"\nAfter fixes:")
print(f"desc >= 200: {desc_ok}/{total}")
print(f"tips >= 100: {tips_ok}/{total}")

with open('/Users/talentclaw/.openclaw/workspace/nov-trip/trip-data.json', 'w') as f:
    json.dump(td, f, ensure_ascii=False, indent=2)

print("trip-data.json updated!")
