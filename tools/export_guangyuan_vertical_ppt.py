from __future__ import annotations

import datetime as dt
import os
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "guangyuan-xiaolongbao"
BASE_PPTX = ROOT / "outputs" / "manual-20260607174326-ppt" / "presentations" / "guangyuan-xiaolongbao" / "output" / "test.pptx"
OUT_DIR = ROOT / "exports"
OUT_FILE = OUT_DIR / "guangyuan-xiaolongbao-vertical-proposal.pptx"

EMU_PER_IN = 914400
W_IN = 7.5
H_IN = 13.333333
SLIDE_W = round(W_IN * EMU_PER_IN)
SLIDE_H = round(H_IN * EMU_PER_IN)

INK = "20221C"
SOFT = "596058"
PAPER = "FBF8EF"
PORCELAIN = "FFFEFA"
GREEN = "315C45"
LEAF = "6B8F3D"
TOMATO = "B84332"
BRASS = "B27A2D"
WATER = "266C88"
CREAM = "FFF8E8"
MIST = "EDE8DC"


def emu(v: float) -> int:
    return round(v * EMU_PER_IN)


def safe_text(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def rgb_fill(color: str, alpha: int | None = None) -> str:
    if alpha is None:
        return f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
    return f'<a:solidFill><a:srgbClr val="{color}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>'


def line_xml(color: str | None, width_pt: float = 1.0, alpha: int | None = None) -> str:
    if color is None:
        return '<a:ln><a:noFill/></a:ln>'
    width = round(width_pt * 12700)
    return f'<a:ln w="{width}">{rgb_fill(color, alpha)}</a:ln>'


def crop_rect(path: Path, box_w: float, box_h: float) -> str:
    with Image.open(path) as img:
        img_w, img_h = img.size
    img_aspect = img_w / img_h
    box_aspect = box_w / box_h
    if img_aspect > box_aspect:
        crop = (1 - box_aspect / img_aspect) / 2
        left = right = round(crop * 100000)
        return f'<a:srcRect l="{left}" r="{right}"/>'
    crop = (1 - img_aspect / box_aspect) / 2
    top = bottom = round(crop * 100000)
    return f'<a:srcRect t="{top}" b="{bottom}"/>'


@dataclass
class Rel:
    rid: str
    type: str
    target: str
    target_mode: str | None = None


@dataclass
class Slide:
    parts: list[str] = field(default_factory=list)
    rels: list[Rel] = field(default_factory=list)
    image_counter: int = 1
    link_counter: int = 1
    shape_id: int = 2

    def next_id(self) -> int:
        value = self.shape_id
        self.shape_id += 1
        return value

    def add_rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str | None = None,
        line: str | None = None,
        radius: bool = False,
        alpha: int | None = None,
        line_alpha: int | None = None,
        name: str = "Shape",
    ) -> None:
        sid = self.next_id()
        geom = "roundRect" if radius else "rect"
        fill_part = '<a:noFill/>' if fill is None else rgb_fill(fill, alpha)
        self.parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{safe_text(name)} {sid}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>'
            f'{fill_part}{line_xml(line, 1, line_alpha)}</p:spPr></p:sp>'
        )

    def add_text(
        self,
        text: str,
        x: float,
        y: float,
        w: float,
        h: float,
        size: float = 18,
        color: str = INK,
        bold: bool = False,
        font: str = "Aptos",
        east_asian_font: str = "PingFang SC",
        align: str = "l",
        line_spacing: float | None = None,
        hyperlink: str | None = None,
        name: str = "Text",
    ) -> None:
        sid = self.next_id()
        paragraphs = text.split("\n")
        hlink_xml = ""
        if hyperlink:
            rid = f"rIdLink{self.link_counter}"
            self.link_counter += 1
            self.rels.append(
                Rel(
                    rid=rid,
                    type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                    target=hyperlink,
                    target_mode="External",
                )
            )
            hlink_xml = f'<a:hlinkClick r:id="{rid}"/>'
        p_xml = []
        for paragraph in paragraphs:
            spacing = ""
            if line_spacing:
                spacing = f'<a:lnSpc><a:spcPct val="{round(line_spacing * 100000)}"/></a:lnSpc>'
            p_xml.append(
                f'<a:p><a:pPr algn="{align}">{spacing}</a:pPr><a:r><a:rPr lang="en-US" sz="{round(size * 100)}" '
                f'{"b=\"1\" " if bold else ""}dirty="0">{rgb_fill(color)}'
                f'<a:latin typeface="{safe_text(font)}"/><a:ea typeface="{safe_text(east_asian_font)}"/>{hlink_xml}</a:rPr>'
                f'<a:t>{safe_text(paragraph)}</a:t></a:r></a:p>'
            )
        self.parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{safe_text(name)} {sid}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm>'
            f'<a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>{line_xml(None)}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" anchor="t" lIns="0" tIns="0" rIns="0" bIns="0"/>'
            f'<a:lstStyle/>{"".join(p_xml)}</p:txBody></p:sp>'
        )

    def add_image(
        self,
        image_path: str,
        x: float,
        y: float,
        w: float,
        h: float,
        media_name: str,
        alt: str,
        crop: bool = True,
    ) -> None:
        path = ASSETS / image_path
        rid = f"rIdImg{self.image_counter}"
        self.image_counter += 1
        self.rels.append(
            Rel(
                rid=rid,
                type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                target=f"../media/{media_name}",
            )
        )
        src_rect = crop_rect(path, w, h) if crop else "<a:srcRect/>"
        sid = self.next_id()
        self.parts.append(
            f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="{safe_text(media_name)}" descr="{safe_text(alt)}"/>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/>{src_rect}<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
        )

    def xml(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + "".join(self.parts)
            + '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
        )

    def rels_xml(self) -> str:
        rels = [
            '<Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="/ppt/slideLayouts/slideLayout2.xml"/>'
        ]
        for rel in self.rels:
            mode = f' TargetMode="{rel.target_mode}"' if rel.target_mode else ""
            rels.append(
                f'<Relationship Id="{rel.rid}" Type="{rel.type}" Target="{safe_text(rel.target)}"{mode}/>'
            )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(rels)
            + "</Relationships>"
        )


class Deck:
    def __init__(self) -> None:
        self.slides: list[Slide] = []
        self.media: dict[str, Path] = {}

    def media_name(self, path: str) -> str:
        src = ASSETS / path
        name = f"image{len(self.media) + 1}{src.suffix.lower()}"
        self.media[name] = src
        return name

    def slide(self, bg: str = PAPER) -> Slide:
        s = Slide()
        s.add_rect(0, 0, W_IN, H_IN, fill=bg, line=None)
        self.slides.append(s)
        return s


def add_header(s: Slide, eyebrow: str, title: str, subtitle: str | None = None, bg_dark: bool = False) -> None:
    color = CREAM if bg_dark else TOMATO
    title_color = CREAM if bg_dark else INK
    body_color = "D6E4E4" if bg_dark else SOFT
    s.add_text(eyebrow.upper(), 0.55, 0.56, 6.4, 0.25, size=10.5, bold=True, color=color, font="Aptos")
    s.add_text(title, 0.55, 0.92, 6.4, 1.05, size=27, bold=True, color=title_color, font="Georgia", east_asian_font="Songti SC")
    if subtitle:
        s.add_text(subtitle, 0.55, 1.9, 6.35, 0.9, size=13.5, color=body_color, line_spacing=1.18)


def build_deck() -> Deck:
    d = Deck()

    # 1. Cover
    s = d.slide(bg=INK)
    s.add_image("vegetables-wide.jpg", 0, 0, W_IN, H_IN, d.media_name("vegetables-wide.jpg"), "Guangyuan market vegetables")
    s.add_rect(0, 0, W_IN, H_IN, fill="09110C", line=None, alpha=68000)
    s.add_text("PRIVATE SHANGHAI FOOD CULTURE EXPERIENCE\n私人上海美食文化体验", 0.45, 0.52, 5.35, 0.62, size=10.5, color=CREAM, bold=True)
    s.add_rect(6.07, 0.45, 0.93, 0.93, fill=None, line=CREAM, radius=True, line_alpha=70000)
    s.add_text("Xiao\nLong\nBao", 6.21, 0.62, 0.62, 0.55, size=9.5, color="F8EAD0", align="c", font="Georgia")
    s.add_text("广元菜场\n到家庭厨房", 0.45, 5.65, 6.5, 1.9, size=40, bold=True, color="FFFFFF", font="Georgia", east_asian_font="Songti SC")
    s.add_text(
        "From a neighborhood xiaolongbao shop to a real wet market, then into a Shanghainese home kitchen to fold, steam, and taste soup dumplings together.\n从街坊小笼馆开始，走进菜场，再到上海本地家庭厨房，亲手完成一笼小笼包。",
        0.48,
        8.1,
        6.4,
        1.25,
        size=13.3,
        color="F6F0E2",
        line_spacing=1.12,
    )
    for i, (top, bottom) in enumerate([("June 13", "2026 afternoon"), ("3-4 guests", "Italian travelers"), ("4 hours", "No transfer")]):
        x = 0.48 + i * 2.23
        s.add_rect(x, 10.45, 1.88, 0.01, fill="FFFFFF", line=None, alpha=48000)
        s.add_text(top, x, 10.63, 1.75, 0.28, size=12.5, color="FFFFFF", bold=True)
        s.add_text(bottom, x, 10.98, 1.75, 0.34, size=9.7, color="DFE7DE")

    # 2. Concept
    s = d.slide()
    add_header(
        s,
        "Concept",
        "先看见一只标准小笼包，再去寻找它的来处。",
        "The experience begins with a small tasting at Fuchun Xiaolong. Guests see the finished dumpling first, then walk into Guangyuan Wet Market to decode the ingredients before cooking with a Shanghainese auntie in a private home-style kitchen.",
    )
    s.add_image("xiaolongbao-steamer.jpg", 0.55, 3.05, 6.4, 3.65, d.media_name("xiaolongbao-steamer.jpg"), "Xiaolongbao in bamboo steamer")
    s.add_rect(0.78, 6.15, 5.92, 0.7, fill=INK, line=None, radius=True, alpha=78000)
    s.add_text("Reference bite: thin skin, neat pleats, hot broth, and the local way to taste it.\n标准参照：薄皮、褶子、汤汁和上海本地吃法。", 1.0, 6.28, 5.5, 0.42, size=10.6, color=CREAM)
    s.add_image("market-entrance.jpg", 0.55, 7.28, 3.1, 2.25, d.media_name("market-entrance.jpg"), "Guangyuan market entrance")
    s.add_image("kitchen-wide.jpg", 3.84, 7.28, 3.1, 2.25, d.media_name("kitchen-wide.jpg"), "Private home-style kitchen")
    s.add_text("Finished sample → market ingredients → home kitchen practice\n成品参照 → 菜场原料 → 家庭厨房动手体验", 0.75, 10.0, 6.0, 0.76, size=16, color=GREEN, bold=True, align="c")

    # 3. Fuchun reference bite
    s = d.slide(bg=PORCELAIN)
    add_header(s, "Fuchun Xiaolong", "富春小笼馆：先吃懂，再动手做。")
    s.add_image("xiaolongbao-steamer.jpg", 0.6, 2.08, 6.3, 4.25, d.media_name("xiaolongbao-steamer.jpg"), "Steamed xiaolongbao")
    s.add_rect(0.68, 6.75, 6.12, 3.55, fill=PAPER, line="E4D6C2", radius=True)
    s.add_text("14:30  Light tasting and observation", 0.95, 7.06, 5.6, 0.35, size=15, color=TOMATO, bold=True)
    s.add_text(
        "Guests observe the shape, pleats, broth, and eating rhythm of a standard local xiaolongbao before going to the market.",
        0.95,
        7.58,
        5.55,
        0.72,
        size=13,
        color=SOFT,
        line_spacing=1.15,
    )
    s.add_text("本地吃法 Local way to eat", 0.95, 8.65, 5.4, 0.35, size=14.5, color=GREEN, bold=True)
    s.add_text(
        "Make a small opening first, sip the hot soup carefully, then enjoy the dumpling with vinegar and ginger.\n先轻轻咬开一个小口，慢慢喝汤，再蘸醋和姜丝吃掉整只小笼包。",
        0.95,
        9.12,
        5.65,
        0.9,
        size=12.3,
        color=SOFT,
        line_spacing=1.12,
    )

    # 4. Itinerary
    s = d.slide()
    add_header(
        s,
        "4-hour main experience",
        "主体验行程",
        "Citywalk is kept separate as an optional neighborhood suggestion before or after the experience. The hosted program focuses on xiaolongbao, market life, and the private kitchen.",
    )
    timeline = [
        ("14:30", "富春小笼馆集合与观察", "Light tasting; observe skin, pleats, broth, and local eating method."),
        ("15:00", "广元菜场采购", "Buy pork, scallion, ginger, flour-related ingredients, and seasonal market finds."),
        ("15:45", "前往私人家庭式厨房", "Move to a nearby home-style kitchen opposite the market."),
        ("16:00", "上海阿姨小笼包教学", "Learn filling, wrapping, pleating, and steaming with hands-on guidance."),
        ("17:30", "品尝与家庭餐桌交流", "Taste freshly steamed xiaolongbao and talk about Shanghainese home cooking."),
        ("18:30", "体验结束", "The experience ends on site. Private transfer is not included."),
    ]
    y = 2.96
    s.add_rect(1.18, y + 0.1, 0.025, 7.9, fill="D7D0C2", line=None)
    for time, title, body in timeline:
        s.add_rect(0.58, y, 1.0, 0.38, fill=PORCELAIN, line="D7D0C2", radius=True)
        s.add_text(time, 0.76, y + 0.075, 0.64, 0.16, size=10.5, color=GREEN, bold=True, align="c")
        s.add_text(title, 1.86, y - 0.02, 4.95, 0.28, size=14.5, color=INK, bold=True)
        s.add_text(body, 1.86, y + 0.35, 4.9, 0.56, size=10.6, color=SOFT, line_spacing=1.1)
        y += 1.36

    # 5. Market textures
    s = d.slide(bg=GREEN)
    add_header(
        s,
        "Market textures",
        "菜场不是背景，是这只小笼包的第一间厨房。",
        "The market visit is designed around the logic of the dumpling: meat for texture, aromatics for fragrance, flour for skin, and local stalls for the rhythm of everyday Shanghai.",
        bg_dark=True,
    )
    s.add_image("vegetables-close.jpg", 0.55, 3.0, 3.0, 5.0, d.media_name("vegetables-close.jpg"), "Market vegetables")
    s.add_image("seafood-counter.jpg", 3.75, 3.0, 3.2, 2.38, d.media_name("seafood-counter.jpg"), "Seafood tanks")
    s.add_image("fruit-stand.jpg", 3.75, 5.62, 3.2, 2.38, d.media_name("fruit-stand.jpg"), "Fruit stand")
    s.add_rect(0.7, 8.65, 6.1, 2.15, fill="FFFFFF", line="FFFFFF", radius=True, alpha=10000, line_alpha=18000)
    s.add_text("Shopping is part of the story", 0.98, 8.95, 5.5, 0.3, size=16, color=CREAM, bold=True)
    s.add_text("It lets guests connect the final bite with texture, aroma, seasonality, and the everyday habits of a Shanghai neighborhood market.", 0.98, 9.42, 5.5, 0.7, size=12, color="DFECE5", line_spacing=1.12)

    # 6. Private kitchen
    s = d.slide()
    add_header(s, "Home-style kitchen", "在上海本地家庭厨房里，亲手完成一笼小笼包。")
    s.add_image("kitchen-wide.jpg", 0.55, 2.25, 6.4, 3.55, d.media_name("kitchen-wide.jpg"), "Private kitchen wide view")
    s.add_image("kitchen-stove.jpg", 0.55, 6.05, 3.05, 2.65, d.media_name("kitchen-stove.jpg"), "Kitchen stove")
    s.add_rect(3.85, 6.05, 3.1, 2.65, fill=GREEN, line=None)
    s.add_text("16:00\nAuntie demo + hands-on practice", 4.1, 6.38, 2.55, 0.82, size=18, color=CREAM, bold=True, line_spacing=1.05)
    s.add_text("调馅、包褶、蒸制\nFilling, pleating, steaming", 4.1, 7.52, 2.55, 0.5, size=12.5, color="DAE7DC")
    s.add_text(
        "The private setting keeps the experience warm and personal: guests can ask questions, compare their own folds, and sit down around a family table instead of a classroom counter.",
        0.75,
        9.22,
        6.0,
        1.0,
        size=14,
        color=SOFT,
        line_spacing=1.15,
    )

    # 7. Nearby map guide
    s = d.slide()
    add_header(
        s,
        "Nearby map guide",
        "体验前后，可以顺路感受这一带的上海。",
        "Optional neighborhood strolls for guests to enjoy on their own before or after the hosted experience. They are not part of the 4-hour guided program.",
    )
    walk_cards = [
        ("wukang-road.jpg", "1.1 km | 30-45 min", "武康路 Wukang Road", "Less than 1.2 km long, a compact index of Shanghai's modern history with former residences, plane trees, and old villas."),
        ("huashan-greenland.jpg", "1.2 km | 30-45 min", "华山绿地 & 幸福路", "A romantic green pocket with the pink Xi Bridge. Nearby Xingfu Road adds the meaning of happiness, vows, and a softer side of Shanghai."),
        ("xujiahui-skywalk-cropped.jpg", "1 km | 45-60 min", "徐家汇 Xujiahui", "A nearby commercial hub with malls, cafes, and an elevated pedestrian bridge for evening city lights. Xujiahui Park works as a daytime green alternative."),
    ]
    y = 3.0
    for img, meta, title, body in walk_cards:
        s.add_rect(0.55, y, 6.4, 2.65, fill=PORCELAIN, line="E2DDD2", radius=True)
        s.add_image(img, 0.78, y + 0.22, 2.15, 2.15, d.media_name(img), title)
        s.add_rect(3.18, y + 0.25, 1.75, 0.32, fill="E9EFE7", line=None, radius=True)
        s.add_text(meta, 3.36, y + 0.31, 1.43, 0.12, size=9.5, color=GREEN, bold=True, align="c")
        s.add_text(title, 3.18, y + 0.76, 3.5, 0.32, size=15.5, color=GREEN, bold=True)
        s.add_text(body, 3.18, y + 1.2, 3.45, 0.94, size=10.5, color=SOFT, line_spacing=1.1)
        y += 2.9

    # 8. Budget
    s = d.slide(bg="F5F3EA")
    add_header(
        s,
        "Budget",
        "预算与包含项",
        "A compact private experience for 3-4 guests, designed around real local access rather than a standard cooking classroom.",
    )
    s.add_rect(0.58, 3.05, 6.35, 6.85, fill=PORCELAIN, line="E6C5BB", radius=True)
    s.add_text("RMB 4,000", 1.0, 3.55, 5.55, 0.8, size=36, color=TOMATO, bold=True, font="Georgia")
    s.add_text("Total budget for 3-4 guests | 3-4 位客人总预算", 1.02, 4.42, 5.45, 0.3, size=11, color=SOFT, bold=True)
    included = [
        "Fuchun xiaolongbao light tasting | 富春小笼少量品尝",
        "Guangyuan Wet Market ingredient purchase | 广元菜场食材采购",
        "Private home-style kitchen access | 私人家庭式厨房空间",
        "Shanghainese auntie cooking guidance | 上海阿姨手把手教学",
        "Bilingual guiding, planning, and on-site hosting | 中英双语陪同、策划与现场执行",
    ]
    y = 5.18
    for item in included:
        s.add_text("✓", 1.02, y, 0.25, 0.22, size=15, color=LEAF, bold=True)
        s.add_text(item, 1.38, y, 5.12, 0.46, size=12.7, color=SOFT, line_spacing=1.08)
        y += 0.76

    # 9. Practical notes
    s = d.slide()
    add_header(
        s,
        "Practical notes",
        "天气、排队与确认事项",
        "Shanghai in mid-June can be warm and rainy. The experience keeps walking short and uses indoor spaces as the anchor.",
    )
    notes = [
        ("Fuchun crowd", "If Fuchun is crowded, keep the tasting light, use takeaway if needed, and move quickly into the market section."),
        ("Rain or heat", "If it rains or feels too hot, optional neighborhood walking is reduced. The main experience remains Fuchun, market, kitchen, and tasting."),
        ("Before final confirmation", "Verify the Fuchun branch, Guangyuan market afternoon ingredient condition, and auntie/kitchen availability for June 13."),
    ]
    y = 3.1
    for title, body in notes:
        s.add_rect(0.7, y, 6.1, 1.85, fill="F7EEDB", line=None, radius=True)
        s.add_rect(0.7, y, 0.08, 1.85, fill=BRASS, line=None)
        s.add_text(title, 1.02, y + 0.28, 5.5, 0.28, size=15.5, color=INK, bold=True)
        s.add_text(body, 1.02, y + 0.75, 5.45, 0.7, size=12.3, color=SOFT, line_spacing=1.12)
        y += 2.24
    s.add_image("flower-stand.jpg", 0.7, 10.05, 2.9, 1.65, d.media_name("flower-stand.jpg"), "Market flower stand")
    s.add_image("meat-counter.jpg", 3.9, 10.05, 2.9, 1.65, d.media_name("meat-counter.jpg"), "Market meat counter")

    # 10. Hosted by Lu
    s = d.slide(bg=INK)
    add_header(
        s,
        "Hosted by Lu",
        "把上海真正生活着的一面，带给第一次来到中国的客人。",
        "Lu has lived in Shanghai for 10 years. With a background in brand marketing and years of vlogging, she knows the city's main streets, side lanes, markets, riversides, and everyday food scenes.",
        bg_dark=True,
    )
    s.add_image("lu-portrait.jpg", 0.55, 3.1, 2.75, 4.25, d.media_name("lu-portrait.jpg"), "Lu portrait")
    s.add_image("lu-with-guest.jpg", 3.48, 2.6, 3.45, 4.75, d.media_name("lu-with-guest.jpg"), "Lu with guest")
    s.add_text(
        "Many travelers' first idea of Chinese food comes from Chinese restaurants in their own hometowns. Once they arrive in China, Lu hopes to offer something more local and specific: the way people actually shop, cook, eat, and talk around a table.",
        0.68,
        7.86,
        6.1,
        1.1,
        size=12.6,
        color="E6E1D1",
        line_spacing=1.13,
    )
    s.add_text(
        "常驻上海 10 年，Lu 熟悉上海的大街小巷，也擅长把本地美食和文化特色转译给海外游客。相比只去网红景点，她更希望让客人进入真实的本地生活。",
        0.68,
        9.35,
        6.1,
        0.95,
        size=12.8,
        color="E6E1D1",
        line_spacing=1.13,
    )
    s.add_text("Food first, then family kitchens, neighborhood markets, and the small cultural details that make a city feel personal.", 0.68, 10.82, 6.1, 0.6, size=13.5, color=CREAM, bold=True)

    # 11. Links
    s = d.slide(bg=INK)
    add_header(s, "Links", "视频与地图参考", "Clickable references for guests or the travel planner.", bg_dark=True)
    links = [
        ("Private Shanghai Food Culture Experience Map Guide", "Gaode / Amap route collection", "https://guinness.autonavi.com/activity/2020CommonLanding/index.html?id=default&local=1&logId=&logParams=&gd_from=jinisi&schema=amapuri%3A%2F%2Fajx_favorites%2Ffolder%3Fdata%3D%257B%2522ugcId%2522%253A%252219005740360274004183%2522%252C%2522forceCustom%2522%253Atrue%252C%2522pathId%2522%253A6%252C%2522isCreatorShare%2522%253Atrue%257D&share_from=favorites_FavoriteFolder&share_from_type=AJX&share_type=image&share_lastClickSpm="),
        ("苏州河沿岸 citywalk 体验", "Watch on Xiaohongshu", "http://xhslink.com/o/34tAfhKDAso"),
        ("和法国朋友一起逛菜市场包馄饨", "Watch on Xiaohongshu", "http://xhslink.com/o/5Okh1qGtEAW"),
    ]
    y = 3.25
    for title, meta, url in links:
        s.add_rect(0.7, y, 6.1, 1.35, fill="FFFFFF", line=BRASS, radius=True, alpha=8000, line_alpha=28000)
        s.add_text(title, 1.0, y + 0.3, 5.55, 0.3, size=14.5, color=CREAM, bold=True, hyperlink=url)
        s.add_text(meta, 1.0, y + 0.78, 5.55, 0.22, size=10.5, color="BFC7C1")
        y += 1.75
    s.add_image("wukang-road.jpg", 0.7, 9.1, 2.9, 2.05, d.media_name("wukang-road.jpg"), "Wukang Road")
    s.add_image("xujiahui-park.jpg", 3.9, 9.1, 2.9, 2.05, d.media_name("xujiahui-park.jpg"), "Xujiahui Park")
    s.add_text("Guangyuan Market × Fuchun Xiaolong × Shanghainese Home Kitchen", 0.72, 12.22, 6.05, 0.25, size=10.5, color="AEB4AD", align="c")

    return d


def presentation_xml(slide_count: int) -> str:
    slide_ids = "".join(
        f'<p:sldId id="{256 + idx}" r:id="rIdSlide{idx + 1}"/>' for idx in range(slide_count)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster1"/></p:sldMasterIdLst>'
        '<p:notesMasterIdLst><p:notesMasterId r:id="rIdNotesMaster1"/></p:notesMasterIdLst>'
        f'<p:sldIdLst>{slide_ids}</p:sldIdLst>'
        f'<p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="custom"/><p:notesSz cx="{SLIDE_W}" cy="9144000"/>'
        '<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle>'
        '</p:presentation>'
    )


def presentation_rels(slide_count: int) -> str:
    rels = [
        '<Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="/ppt/slideMasters/slideMaster1.xml"/>',
        '<Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="/ppt/theme/theme1.xml"/>',
        '<Relationship Id="rIdNotesMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="/ppt/notesMasters/notesMaster1.xml"/>',
        '<Relationship Id="rIdPresProps" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="/ppt/presProps.xml"/>',
        '<Relationship Id="rIdViewProps" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="/ppt/viewProps.xml"/>',
        '<Relationship Id="rIdTableStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="/ppt/tableStyles.xml"/>',
    ]
    rels.extend(
        f'<Relationship Id="rIdSlide{idx + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="/ppt/slides/slide{idx + 1}.xml"/>'
        for idx in range(slide_count)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )


def content_types(slide_count: int) -> str:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"/>',
        '<Override PartName="/ppt/notesMasters/theme/theme2.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>',
        '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>',
        '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    overrides.extend(
        f'<Override PartName="/ppt/slides/slide{idx + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for idx in range(slide_count)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="jpg" ContentType="image/jpeg"/>'
        '<Default Extension="jpeg" ContentType="image/jpeg"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        + "".join(overrides)
        + "</Types>"
    )


def root_rels() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )


def core_xml() -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Guangyuan Market x Fuchun Xiaolong x Shanghainese Home Kitchen</dc:title>'
        '<dc:creator>Lu</dc:creator>'
        '<cp:lastModifiedBy>Codex</cp:lastModifiedBy>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>'
        '</cp:coreProperties>'
    )


def app_xml(slide_count: int) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>Microsoft PowerPoint</Application><PresentationFormat>On-screen Show (9:16)</PresentationFormat>'
        f'<Slides>{slide_count}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides><MMClips>0</MMClips>'
        '<ScaleCrop>false</ScaleCrop><Company></Company><LinksUpToDate>false</LinksUpToDate>'
        '<SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion>'
        '</Properties>'
    )


def write_deck(deck: Deck) -> None:
    if not BASE_PPTX.exists():
        raise FileNotFoundError(f"Base PPTX not found: {BASE_PPTX}")
    OUT_DIR.mkdir(exist_ok=True)
    static_parts = [
        "ppt/slideMasters/slideMaster1.xml",
        "ppt/theme/theme1.xml",
        "ppt/notesMasters/notesMaster1.xml",
        "ppt/notesMasters/theme/theme2.xml",
        "ppt/presProps.xml",
        "ppt/viewProps.xml",
        "ppt/tableStyles.xml",
        "ppt/slideLayouts/slideLayout2.xml",
        "ppt/notesMasters/_rels/notesMaster1.xml.rels",
        "ppt/slideLayouts/_rels/slideLayout2.xml.rels",
        "ppt/slideMasters/_rels/slideMaster1.xml.rels",
    ]
    with zipfile.ZipFile(OUT_FILE, "w", compression=zipfile.ZIP_DEFLATED) as out:
        out.writestr("[Content_Types].xml", content_types(len(deck.slides)))
        out.writestr("_rels/.rels", root_rels())
        out.writestr("docProps/core.xml", core_xml())
        out.writestr("docProps/app.xml", app_xml(len(deck.slides)))
        out.writestr("ppt/presentation.xml", presentation_xml(len(deck.slides)))
        out.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(deck.slides)))
        with zipfile.ZipFile(BASE_PPTX) as base:
            for part in static_parts:
                out.writestr(part, base.read(part))
        for idx, slide in enumerate(deck.slides, start=1):
            out.writestr(f"ppt/slides/slide{idx}.xml", slide.xml())
            out.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide.rels_xml())
        for name, src in deck.media.items():
            out.write(src, f"ppt/media/{name}")


def main() -> None:
    deck = build_deck()
    write_deck(deck)
    print(OUT_FILE)
    print(f"slides={len(deck.slides)} media={len(deck.media)}")


if __name__ == "__main__":
    main()
