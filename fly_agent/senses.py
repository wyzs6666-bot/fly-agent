from __future__ import annotations

import re
from dataclasses import dataclass

from .types import SenseSignal


SENSES: dict[str, tuple[list[str], str]] = {
    "threat": (["LC4", "LPLC2"], "一个巨大的东西正在逼近（逼近检测神经元）"),
    "taste": (["claw_tpGRN", "dorsal_tpGRN", "BM_Taste"], "嘴边有甜的东西（味觉神经元）"),
    "mate": (["LC10a"], "附近有其他果蝇在动（运动目标检测）"),
    "wind": (
        ["JO-CL", "JO-CM", "JO-CA2", "JO-EV1", "JO-EV2", "JO-EV3", "JO-EV5", "JO-EV6", "JO-ED1",
         "JO-ED2_a", "JO-ED2_b", "JO-ED2_c"],
        "有风吹到触角（Johnston器）",
    ),
    "touch": (["BM_InOm"], "有东西碰到眼睛或身体（触觉）"),
    "smell": (["ORN_DA1"], "闻到特殊气味（信息素受体）"),
    "nothing": ([], "没有特别强烈的刺激"),
}


KEYWORDS: dict[str, str] = {
    "threat": (
        r"swat|slap|kill|\bhit\b|attack|danger|scary|monster|boss|deadline|\bbugs?\b|crash|error|fail|"
        r"angry|shout|spider|bird|\bhands?\b|\brun\b|urgent|panic|police|tax|"
        r"拍|打|杀|攻击|危险|吓人|怪物|手|逼近|靠近|威胁|害怕|崩溃|失败|生气|喊|蜘蛛|鸟|快跑|紧急|恐慌|巨大"
    ),
    "taste": (
        r"pizza|food|eat|hungry|sugar|sweet|cake|fruit|banana|apple|wine|beer|coffee|juice|lunch|dinner|"
        r"snack|honey|candy|trash|garbage|rotten|burger|"
        r"甜|吃|食物|饿|糖|蛋糕|水果|香蕉|苹果|酒|咖啡|果汁|午餐|晚餐|零食|蜂蜜|糖果|垃圾|汉堡|好吃|美味"
    ),
    "mate": (
        r"\bhi\b|hello|hey|cute|love|date|kiss|crush|friend|party|meet|dance|flirt|beautiful|handsome|single|"
        r"tinder|gm\b|"
        r"你好|嗨|哈喽|可爱|喜欢|爱|约会|亲|朋友|派对|见面|跳舞|帅哥|美女|单身"
    ),
    "wind": (
        r"wind|fan|blow|breeze|air|storm|cold|ac\b|window|fly away|fast|"
        r"风|风扇|吹|空气|风暴|冷|空调|窗户|飞走|快点"
    ),
    "touch": (
        r"touch|poke|tickle|pet|hug|scratch|brush|rub|itch|face|eye|"
        r"碰|摸|戳|挠|抱|抓|刷|擦|痒|脸|眼睛|触碰"
    ),
    "smell": (
        r"smell|perfume|cologne|stink|scent|odou?r|fart|sweat|deodorant|"
        r"闻|味道|香水|臭|气味|香|汗"
    ),
}


@dataclass(frozen=True)
class LexiconSenseEncoder:
    case_sensitive: bool = False

    def encode(self, text: str) -> SenseSignal:
        source = text if self.case_sensitive else text.lower()
        scores = {name: len(re.findall(pattern, source)) for name, pattern in KEYWORDS.items()}
        best = max(scores, key=scores.get)
        sense = best if scores[best] > 0 else "nothing"
        cells, felt = SENSES[sense]
        return SenseSignal(
            sense=sense,
            stimulated=tuple(cells),
            felt=felt,
            score=float(scores[best]),
            notes={"scores": scores},
        )
