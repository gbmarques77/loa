
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import Flowable
from reportlab.pdfgen import canvas as rl_canvas
import os

OUTPUT = "/mnt/user-data/outputs/Garou_PF2e_Remaster.pdf"

# ─── PALETTE ─────────────────────────────────────────────────────────────────
C_BG        = colors.HexColor("#0f172a")
C_SURFACE   = colors.HexColor("#1e293b")
C_BORDER    = colors.HexColor("#334155")
C_TEXT      = colors.HexColor("#e2e8f0")
C_MUTED     = colors.HexColor("#94a3b8")
C_ACCENT    = colors.HexColor("#7c3aed")
C_ACCENT2   = colors.HexColor("#a78bfa")
C_GREEN     = colors.HexColor("#10b981")
C_RED       = colors.HexColor("#ef4444")
C_AMBER     = colors.HexColor("#f59e0b")
C_BLUE      = colors.HexColor("#3b82f6")
C_PINK      = colors.HexColor("#f472b6")
C_WHITE     = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm

# ─── STYLES ──────────────────────────────────────────────────────────────────
def make_styles():
    s = {}

    base = ParagraphStyle("base",
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=C_TEXT, backColor=None,
        spaceAfter=4, spaceBefore=0)

    s["h_chapter"] = ParagraphStyle("h_chapter",
        fontName="Helvetica-Bold", fontSize=22, leading=28,
        textColor=C_WHITE, spaceAfter=4, spaceBefore=0, alignment=TA_LEFT)

    s["h_sub"] = ParagraphStyle("h_sub",
        fontName="Helvetica-Bold", fontSize=13, leading=18,
        textColor=C_ACCENT2, spaceAfter=6, spaceBefore=14, alignment=TA_LEFT)

    s["h3"] = ParagraphStyle("h3",
        fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=C_AMBER, spaceAfter=4, spaceBefore=10)

    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=9.5, leading=15,
        textColor=C_TEXT, spaceAfter=6, alignment=TA_JUSTIFY)

    s["body_muted"] = ParagraphStyle("body_muted",
        fontName="Helvetica", fontSize=9, leading=14,
        textColor=C_MUTED, spaceAfter=4, alignment=TA_LEFT)

    s["label"] = ParagraphStyle("label",
        fontName="Helvetica-Bold", fontSize=8, leading=11,
        textColor=C_MUTED, spaceAfter=2, spaceBefore=0)

    s["callout"] = ParagraphStyle("callout",
        fontName="Helvetica", fontSize=9, leading=14,
        textColor=C_TEXT, spaceAfter=0, leftIndent=8)

    s["callout_title"] = ParagraphStyle("callout_title",
        fontName="Helvetica-Bold", fontSize=9.5, leading=14,
        textColor=C_RED, spaceAfter=4, leftIndent=8)

    s["tag"] = ParagraphStyle("tag",
        fontName="Helvetica-Bold", fontSize=8, leading=11,
        textColor=C_ACCENT2, spaceAfter=0)

    s["toc"] = ParagraphStyle("toc",
        fontName="Helvetica", fontSize=10, leading=18,
        textColor=C_TEXT, spaceAfter=0)

    s["toc_num"] = ParagraphStyle("toc_num",
        fontName="Helvetica-Bold", fontSize=10, leading=18,
        textColor=C_ACCENT, spaceAfter=0)

    s["center"] = ParagraphStyle("center",
        fontName="Helvetica", fontSize=9.5, leading=14,
        textColor=C_MUTED, alignment=TA_CENTER)

    s["table_header"] = ParagraphStyle("table_header",
        fontName="Helvetica-Bold", fontSize=8.5, leading=12,
        textColor=C_WHITE, alignment=TA_CENTER)

    s["table_cell"] = ParagraphStyle("table_cell",
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=C_TEXT, alignment=TA_LEFT)

    s["table_cell_c"] = ParagraphStyle("table_cell_c",
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=C_TEXT, alignment=TA_CENTER)

    return s

ST = make_styles()

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def HR(color=C_BORDER, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=8, spaceBefore=4)

def SP(h=6):
    return Spacer(1, h)

def chapter_header(title, subtitle="", color=C_ACCENT):
    """Returns a styled chapter block as a Table (colored left bar)."""
    inner = []
    inner.append(Paragraph(title, ST["h_chapter"]))
    if subtitle:
        inner.append(Paragraph(subtitle, ST["body_muted"]))
    bar_col = Table([[""]], colWidths=[4], rowHeights=[50 if subtitle else 36])
    bar_col.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,-1), color),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    content_col = Table([[p] for p in inner], colWidths=[PAGE_W - MARGIN*2 - 14])
    content_col.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    t = Table([[bar_col, content_col]], colWidths=[4, PAGE_W - MARGIN*2 - 4])
    t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def section_title(text):
    return [SP(10), Paragraph(text, ST["h_sub"]), HR(C_ACCENT, 0.4)]

def callout_box(title, body, color=C_RED):
    rows = []
    if title:
        rows.append([Paragraph(title, ParagraphStyle("ct", fontName="Helvetica-Bold",
            fontSize=9.5, leading=14, textColor=color, spaceAfter=4))])
    rows.append([Paragraph(body, ST["callout"])])
    t = Table(rows, colWidths=[PAGE_W - MARGIN*2 - 24])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), colors.HexColor("#1e293b")),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LINEAFTER",(0,0),(0,-1), 3, color),
        ("ROUNDEDCORNERS",[4,4,4,4]),
    ]))
    return [SP(4), t, SP(4)]

def info_grid(items, cols=2):
    """items = list of (label, value, color)"""
    col_w = (PAGE_W - MARGIN*2) / cols
    rows_data = []
    row = []
    for i, (label, value, color) in enumerate(items):
        cell_inner = Table([
            [Paragraph(label, ParagraphStyle("il", fontName="Helvetica-Bold",
                fontSize=7.5, leading=10, textColor=C_MUTED))],
            [Paragraph(str(value), ParagraphStyle("iv", fontName="Helvetica-Bold",
                fontSize=13, leading=16, textColor=color))],
        ], colWidths=[col_w - 20])
        cell_inner.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),0), ("BOTTOMPADDING",(0,0),(-1,-1),0),
            ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
        ]))
        cell = Table([[cell_inner]], colWidths=[col_w - 12])
        cell.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), colors.HexColor("#1e293b")),
            ("LEFTPADDING",(0,0),(-1,-1),10),
            ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("ROUNDEDCORNERS",[4,4,4,4]),
        ]))
        row.append(cell)
        if len(row) == cols:
            rows_data.append(row)
            row = []
    if row:
        while len(row) < cols:
            row.append("")
        rows_data.append(row)
    t = Table(rows_data, colWidths=[col_w]*cols)
    t.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),4),
        ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    return t

def styled_table(headers, rows, col_widths, row_colors=None):
    header_row = [Paragraph(h, ST["table_header"]) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), ST["table_cell"]) for c in row])
    t = Table(data, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0,0), (-1,0), C_ACCENT),
        ("TEXTCOLOR", (0,0), (-1,0), C_WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#1a2744"), colors.HexColor("#1e293b")]),
        ("GRID", (0,0), (-1,-1), 0.3, C_BORDER),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]
    t.setStyle(TableStyle(style))
    return t

def tribe_card(name, ability, desc, boost, flaw, color_hex):
    color = colors.HexColor(color_hex)
    content = [
        [Paragraph(name, ParagraphStyle("tn", fontName="Helvetica-Bold",
            fontSize=12, leading=16, textColor=color))],
        [Paragraph(f"Dom Gratuito: {ability}", ParagraphStyle("ta", fontName="Helvetica-Bold",
            fontSize=8.5, leading=12, textColor=C_AMBER))],
        [SP(4)],
        [Paragraph(desc, ST["body"])],
        [SP(4)],
        [Paragraph(f"Bônus: {', '.join(boost)}", ParagraphStyle("tb", fontName="Helvetica",
            fontSize=9, leading=13, textColor=C_GREEN))],
        [SP(2)],
        [Paragraph(f"Falha: {flaw}", ParagraphStyle("tf", fontName="Helvetica-Oblique",
            fontSize=9, leading=13, textColor=C_RED))],
    ]
    inner = Table(content, colWidths=[PAGE_W - MARGIN*2 - 26])
    inner.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1), ("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    bar = Table([[""]], colWidths=[4], rowHeights=[170])
    bar.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),color),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    outer = Table([[bar, inner]], colWidths=[4, PAGE_W - MARGIN*2 - 4])
    outer.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), colors.HexColor("#1e293b")),
        ("LEFTPADDING",(1,0),(1,-1),12),
        ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    return [SP(6), outer]

# ─── PAGE TEMPLATE ───────────────────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    # Dark background
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Header bar
    canvas.setFillColor(colors.HexColor("#1e293b"))
    canvas.rect(0, PAGE_H - 20*mm, PAGE_W, 20*mm, fill=1, stroke=0)
    # Header text
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(C_ACCENT2)
    canvas.drawString(MARGIN, PAGE_H - 13*mm, "GAROU: THE APOCALYPSE — CONVERSÃO PF2E REMASTER")
    canvas.setFillColor(C_MUTED)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 13*mm, f"p. {doc.page}")
    # Footer
    canvas.setFillColor(colors.HexColor("#1e293b"))
    canvas.rect(0, 0, PAGE_W, 12*mm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MUTED)
    canvas.drawCentredString(PAGE_W/2, 4*mm, "Documento de Regras — Uso em Mesa — Não Oficial")
    canvas.restoreState()

def on_cover(canvas, doc):
    canvas.saveState()
    # Full dark bg
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Accent band top
    canvas.setFillColor(C_ACCENT)
    canvas.rect(0, PAGE_H - 8*mm, PAGE_W, 8*mm, fill=1, stroke=0)
    # Bottom band
    canvas.setFillColor(colors.HexColor("#1e293b"))
    canvas.rect(0, 0, PAGE_W, 50*mm, fill=1, stroke=0)
    canvas.restoreState()

# ─── CONTENT BUILDERS ────────────────────────────────────────────────────────

def build_cover():
    story = []
    story.append(SP(60))
    # Small label
    story.append(Paragraph("DOCUMENTO DE REGRAS", ParagraphStyle("cl",
        fontName="Helvetica-Bold", fontSize=9, leading=14, textColor=C_ACCENT2,
        alignment=TA_CENTER, spaceAfter=8, letterSpacing=3)))
    story.append(Paragraph("Garou: The Apocalypse", ParagraphStyle("ctitle",
        fontName="Helvetica-Bold", fontSize=36, leading=44, textColor=C_WHITE,
        alignment=TA_CENTER, spaceAfter=8)))
    story.append(Paragraph("Conversão para Pathfinder 2e Remaster", ParagraphStyle("csub",
        fontName="Helvetica", fontSize=16, leading=22, textColor=C_ACCENT2,
        alignment=TA_CENTER, spaceAfter=30)))
    story.append(HR(C_ACCENT, 1))
    story.append(SP(12))
    story.append(Paragraph(
        "Este documento apresenta uma conversão completa e equilibrada do universo de "
        "Werewolf: The Apocalypse para o sistema Pathfinder 2e Remaster. "
        "Preserva o sabor narrativo e a tensão mecânica do WtA — Raiva, Gnose, Frenesi, "
        "Umbra e o sistema de Renome — sobre a estrutura sólida do d20, proficiências "
        "e sistema de 3 ações do PF2e.",
        ParagraphStyle("cdesc", fontName="Helvetica", fontSize=11, leading=18,
            textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=20)))
    story.append(SP(20))
    # Stats grid on cover
    grid_items = [
        ("Sistema Base", "Pathfinder 2e Remaster", C_ACCENT2),
        ("Dado Central", "d20 + Modificador vs CD", C_GREEN),
        ("Tribos", "8 Ancestralidades", C_AMBER),
        ("Auspícios", "5 Backgrounds", C_BLUE),
        ("Recursos", "Raiva, Gnose, Vontade", C_RED),
        ("Progressão", "Nível + Rank de Renome", C_PINK),
    ]
    story.append(info_grid(grid_items, cols=3))
    story.append(SP(30))
    story.append(Paragraph("Não oficial. Para uso pessoal em mesa.", ParagraphStyle("disc",
        fontName="Helvetica-Oblique", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)))
    return story

def build_toc():
    story = []
    story.append(chapter_header("Sumário", color=C_MUTED))
    story.append(SP(16))
    chapters = [
        ("1", "Filosofia e Visão Geral da Conversão", "3"),
        ("2", "O Sistema d20 — Base Mecânica", "5"),
        ("3", "Tribos como Ancestralidades", "7"),
        ("4", "Auspícios como Backgrounds", "11"),
        ("5", "A Classe Garou — Progressão e Habilidades", "13"),
        ("6", "As 5 Formas Garou", "16"),
        ("7", "Os Três Recursos: Raiva, Gnose e Vontade", "19"),
        ("8", "Dons (Gifts) como Feitos de Classe", "22"),
        ("9", "Renome e Progressão de Rank", "26"),
        ("10", "O Frenesi — Mecânica Completa", "29"),
        ("11", "A Umbra — O Mundo Espiritual", "31"),
        ("12", "Dano Agravado e Cura", "34"),
        ("Apêndice", "Tabelas de Referência Rápida", "36"),
    ]
    for num, title, page in chapters:
        row = Table([
            [Paragraph(num, ParagraphStyle("tn2", fontName="Helvetica-Bold", fontSize=10,
                textColor=C_ACCENT, leading=16)),
             Paragraph(title, ST["toc"]),
             Paragraph(f"...{page}", ParagraphStyle("tp", fontName="Helvetica",
                fontSize=10, textColor=C_MUTED, alignment=TA_LEFT, leading=16))
            ]
        ], colWidths=[20, PAGE_W - MARGIN*2 - 60, 40])
        row.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),2), ("BOTTOMPADDING",(0,0),(-1,-1),2),
            ("LINEBELOW",(0,0),(-1,-1),0.3,C_BORDER),
        ]))
        story.append(row)
    return story

def build_ch1():
    story = []
    story.append(chapter_header("Cap. 1 — Filosofia e Visão Geral", "Por que converter para PF2e Remaster?", C_ACCENT))
    story.append(SP(12))

    story.append(Paragraph(
        "Werewolf: The Apocalypse é um dos jogos de RPG mais ricos tematicamente já criados. "
        "Sua proposta — guerreiros espirituais lutando contra a destruição do mundo — carrega "
        "tensão narrativa intrínseca que muitos sistemas modernos simplesmente não conseguem "
        "replicar. O sistema Storyteller original, com suas pools de d10, captura essa essência "
        "com elegância, mas possui limitações práticas: inconsistência matemática em pools muito "
        "grandes, combate mortal em excesso e dificuldade de escalar campanhas longas.",
        ST["body"]))

    story.append(Paragraph(
        "O Pathfinder 2e Remaster, por outro lado, é um dos sistemas d20 mais bem construídos "
        "da atualidade. Seu sistema de 3 ações, 4 graus de sucesso, proficiências progressivas "
        "e arquitetura modular de feitos oferecem uma espinha dorsal robusta e matematicamente "
        "sólida. A proposta desta conversão é usar o PF2e como motor e enxertar sobre ele "
        "os elementos que fazem o WtA único.",
        ST["body"]))

    story.extend(section_title("Princípios da Conversão"))
    principles = [
        ("Sabor antes de simetria",
         "Quando uma escolha mecânica preserva melhor o sabor do WtA à custa de elegância "
         "matemática perfeita, o sabor vence. O sistema deve sentir como Garou."),
        ("Recursos paralelos, não substituídos",
         "Raiva, Gnose e Força de Vontade existem como pools independentes. Eles não "
         "substituem pontos de magia ou outros recursos do PF2e — coexistem com eles, "
         "criando uma camada extra de decisão em cada turno."),
        ("Identidade tribal obrigatória",
         "Cada Tribo funciona como Ancestralidade no PF2e, com bônus, Dom gratuito e uma "
         "Falha narrativa. A Falha não é opcional — ela é o que dá vida à tribo."),
        ("Rank separado do Nível",
         "O Rank Garou (Cliath → Elder) não é o mesmo que o nível do personagem. É uma "
         "camada social conquistada por Renome, que pode ou não acompanhar o nível."),
        ("Dano Agravado preservado",
         "O tipo de dano Agravado do WtA é mantido. Ele não cura naturalmente e requer "
         "Gnose ou rituais para ser removido — preservando seu peso narrativo."),
    ]
    for title, body in principles:
        story.append(KeepTogether([
            Paragraph(f"● {title}", ST["h3"]),
            Paragraph(body, ST["body"]),
        ]))

    story.extend(section_title("Mapa da Conversão"))
    map_data = [
        ["Elemento WtA", "Equivalente PF2e Remaster", "Observação"],
        ["Tribo", "Ancestralidade", "Com Dom gratuito e Falha narrativa"],
        ["Auspício", "Background", "Bônus de atributo e perícias únicas"],
        ["Garou (geral)", "Classe única", "Uma só classe; diversidade via feitos"],
        ["Dons (Gifts)", "Feitos de Classe", "Custo em Raiva ou Gnose"],
        ["Rank (Cliath→Elder)", "Rank separado do nível", "Baseado em Renome acumulado"],
        ["Raiva / Gnose", "Recursos de Classe independentes", "Pools gerenciados separadamente"],
        ["Força de Vontade", "Pool de Vontade (novo recurso)", "Proteção contra Frenesi"],
        ["Frenesi", "Save de Resistência ao Frenesi", "Save novo derivado de Sab + Rank"],
        ["Umbra / Gauntlet", "Plano espiritual com CD variável", "Teste de Ocultismo ou Sobrevivência"],
        ["Dano Agravado", "Tipo de dano novo", "Não cura com descanso comum"],
        ["Litanias", "Restrições narrativas obrigatórias", "Violação gera perda de Renome"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.28, 0.35, 0.37]]
    story.append(SP(6))
    story.append(styled_table(map_data[0], map_data[1:], col_w))
    return story

def build_ch2():
    story = []
    story.append(chapter_header("Cap. 2 — O Sistema d20", "Base mecânica do Pathfinder 2e Remaster", C_BLUE))
    story.append(SP(12))

    story.append(Paragraph(
        "Toda rolagem no PF2e Garou segue a mesma estrutura: role 1d20, adicione o modificador "
        "relevante (geralmente Atributo + Proficiência + bônus de item) e compare com a "
        "Classe de Dificuldade (CD) estabelecida pelo Narrador. O resultado cai em um dos "
        "quatro graus de sucesso.",
        ST["body"]))

    story.extend(section_title("Os 4 Graus de Sucesso"))
    degrees = [
        ("Sucesso Crítico", "d20 + mod ≥ CD + 10 (ou resultado natural 20 com sucesso)",
         "A ação supera todas as expectativas. Dano dobrado em ataques, efeito extra em Dons, "
         "vantagem narrativa. Em testes de Gnose, pode revelar informações espirituais extras.", C_GREEN),
        ("Sucesso", "d20 + mod ≥ CD",
         "A ação é realizada normalmente. Resultado esperado sem complicações.", C_BLUE),
        ("Falha", "d20 + mod < CD",
         "A ação falha. Em combate, o ataque não causa dano. Em Dons, o recurso gasto é perdido.", C_AMBER),
        ("Falha Crítica", "d20 + mod ≤ CD − 10 (ou resultado natural 1 com falha)",
         "Catástrofe. Em combate, pode causar dano a si mesmo. Em testes de Frenesi, "
         "automaticamente entra em Frenesi por 1d4 minutos.", C_RED),
    ]
    for name, condition, desc, color in degrees:
        inner = Table([
            [Paragraph(name, ParagraphStyle("dn", fontName="Helvetica-Bold",
                fontSize=11, leading=14, textColor=color))],
            [Paragraph(f"Condição: {condition}", ParagraphStyle("dc",
                fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=C_MUTED))],
            [SP(4)],
            [Paragraph(desc, ST["body"])],
        ], colWidths=[PAGE_W - MARGIN*2 - 24])
        inner.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ]))
        bar = Table([[""]], colWidths=[4], rowHeights=[90])
        bar.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),color),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        card = Table([[bar, inner]], colWidths=[4, PAGE_W - MARGIN*2 - 4])
        card.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e293b")),
            ("LEFTPADDING",(1,0),(1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        story.append(SP(6))
        story.append(card)

    story.extend(section_title("O Sistema de 3 Ações"))
    story.append(Paragraph(
        "Cada turno em combate, o personagem possui 3 ações para gastar livremente. "
        "Ações são marcadas com o símbolo [A]. Algumas atividades custam 2 ações [AA] "
        "ou 3 ações [AAA]. Além disso, cada personagem possui 1 Reação por rodada, "
        "que pode ser gasta fora do seu turno em resposta a um gatilho específico.",
        ST["body"]))

    actions_data = [
        ["Atividade", "Custo", "Exemplo Garou"],
        ["Stride (Mover)", "[A]", "Mover até a Velocidade em metros"],
        ["Strike (Atacar)", "[A]", "Atacar com garras; −5/−10 em ataques extras"],
        ["Mudar de Forma (Homid/Glabro/Lupus)", "[A]", "Transformar-se em formas menores"],
        ["Mudar de Forma (Crinos/Hispo)", "[AA]", "Transformar-se em formas maiores"],
        ["Ativar Dom de Rank 1", "[A]", "Garra da Fúria, Pele de Aço"],
        ["Ativar Dom de Rank 2+", "[AA]", "Uivo da Matilha, Passo na Umbra"],
        ["Cruzar o Gauntlet", "[AA]", "Gastar 2 Gnose + teste de Ocultismo"],
        ["Recuperar (usar Vontade)", "[A]", "Suprimir Frenesi por 1 rodada"],
        ["Entrar em Crinos (Reação)", "[R]", "Gastar 2 Raiva quando atacado"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.38, 0.15, 0.47]]
    story.append(SP(8))
    story.append(styled_table(actions_data[0], actions_data[1:], col_w))

    story.extend(section_title("Saves e Proficiências"))
    story.append(Paragraph(
        "O PF2e utiliza um sistema de proficiências com 5 graus: Sem Treinamento (−4 ao bônus), "
        "Treinado (+2), Especialista (+4), Mestre (+6) e Lendário (+8). Esses bônus somam-se "
        "ao nível do personagem e ao modificador de atributo para formar a rolagem final.",
        ST["body"]))
    story.append(Paragraph(
        "Garou possuem 4 saves: <b>Fortitude</b> (Constituição — resistência física e venenos), "
        "<b>Reflexo</b> (Destreza — ataques em área e armadilhas), <b>Vontade</b> (Sabedoria — "
        "efeitos mentais e medo) e o novo save exclusivo <b>Resistência ao Frenesi</b> "
        "(Sabedoria + Rank — resistência à perda de controle).",
        ST["body"]))
    return story

def build_ch3():
    story = []
    story.append(chapter_header("Cap. 3 — Tribos como Ancestralidades",
        "8 tribos convertidas para o sistema de Ancestralidades do PF2e", C_ACCENT))
    story.append(SP(8))
    story.append(Paragraph(
        "No PF2e Remaster, a Ancestralidade define a origem do personagem: bônus de atributos, "
        "habilidade inata, velocidade base e traços especiais. As Tribos Garou funcionam exatamente "
        "assim. Cada tribo fornece dois bônus de atributo (+2 cada), um Dom gratuito de Rank 1, "
        "uma habilidade passiva de tribo e uma Falha narrativa obrigatória. A Falha não é uma "
        "penalidade mecânica isolada — é uma restrição que cria drama e identidade.",
        ST["body"]))

    tribes = [
        ("Black Furies", "Fúria Sagrada",
         "Guerreiras dedicadas a Gaia e à proteção da natureza feminina. Sua cultura é matriarcal "
         "e suas batalhas são travadas com intensidade ritualística. Possuem um elo especial com "
         "espíritos da terra e com a lua em sua fase cheia. São temidas em combate e respeitadas "
         "como guardiãs dos lugares sagrados.",
         ["Força +2", "Sabedoria +2"],
         "Desconfiança masculina: NPCs do gênero masculino começam com atitude Hostil. "
         "Pode ser melhorada com testes de Diplomacia (CD 18), mas nunca abaixo de Indiferente "
         "sem razão extraordinária.",
         "#7c3aed"),
        ("Bone Gnawers", "Sobrevivência Urbana",
         "Garou das ruas e guetos, frequentemente desprezados pelas tribos nobres. Sua força está "
         "na adaptabilidade e no conhecimento das redes sociais humanas mais baixas. São espiões, "
         "batedores e sobreviventes natos, com acesso a informações que outras tribos jamais "
         "conseguiriam obter por meios convencionais.",
         ["Constituição +2", "Carisma +2"],
         "Sem lar fixo: não pode manter propriedades ou recursos de Riqueza acima do nível Parco. "
         "Perde acesso a itens caros entre sessões a menos que os esconda fisicamente.",
         "#92400e"),
        ("Children of Gaia", "Toque Curativo",
         "Os pacificadores do mundo Garou. Onde outras tribos veem guerra, os Filhos de Gaia "
         "buscam harmonia — não por fraqueza, mas pela convicção de que a cura é mais poderosa "
         "que a destruição. São mediadores em conclaves, curandeiros no campo de batalha e "
         "diplomatas entre Garou e espíritos.",
         ["Sabedoria +2", "Carisma +2"],
         "Abomina violência desnecessária: deve fazer um save de Vontade (CD 15) para atacar "
         "qualquer ser que não tenha iniciado hostilidade direta nessa cena.",
         "#065f46"),
        ("Get of Fenris", "Berserker Nórdico",
         "Guerreiros inspirados nas tradições nórdicas, que abraçam a violência como caminho "
         "espiritual. Para os Get, a batalha é sagrada e a coragem é a mais alta virtude. "
         "São a linha de frente em qualquer confronto contra o Wyrm, e sua reputação de "
         "implacabilidade precede qualquer negociação.",
         ["Força +2", "Constituição +2"],
         "Orgulho extremo: não pode recuar voluntariamente de um combate sem fazer um save "
         "de Vontade (CD 18). Falha significa que continua lutando independentemente das "
         "consequências táticas.",
         "#1e3a8a"),
        ("Glass Walkers", "Interface Tecnológica",
         "Os Garou do mundo moderno, integrados ao ambiente urbano e à tecnologia. Onde outras "
         "tribos veem a cidade como inimiga de Gaia, os Glass Walkers a veem como um campo "
         "de batalha a ser dominado de dentro. Trabalham em finanças, tecnologia e política "
         "para combater o Wyrm nos corredores do poder.",
         ["Inteligência +2", "Destreza +2"],
         "Desconexão espiritual: recebe −2 em todos os testes de Gnose para cruzar o Gauntlet "
         "e em interações com espíritos de natureza selvagem.",
         "#0f766e"),
        ("Shadow Lords", "Dominância Sombria",
         "Manipuladores frios e calculistas que acreditam que o poder justifica os meios. "
         "Vislumbram um futuro onde os Garou governam abertamente — sob sua liderança. "
         "São políticos implacáveis, estrategistas brilhantes e aliados perigosos. "
         "Toda aliança com um Shadow Lord tem um preço.",
         ["Carisma +2", "Inteligência +2"],
         "Paranoia política: deve fazer um teste de Vontade (CD 14) para compartilhar "
         "informações estratégicas com qualquer pessoa fora de sua tribo, mesmo que confie nela.",
         "#1f2937"),
        ("Silent Striders", "Passo sem Rastro",
         "Nômades amaldiçoados que não podem permanecer em um lugar por muito tempo. "
         "Carregam mensagens entre matilhas, exploram territórios desconhecidos e "
         "são os primeiros a descobrir ameaças do Wyrm em movimento. Sua maldição "
         "os priva do descanso, mas os torna os melhores batedores do mundo Garou.",
         ["Destreza +2", "Sabedoria +2"],
         "Banidos dos mortos: não podem se comunicar com espíritos de ancestrais ou usar "
         "rituais que invoquem espíritos de Garou falecidos. Os mortos não respondem.",
         "#44403c"),
        ("Silver Fangs", "Liderança Real",
         "A nobreza do mundo Garou, descendentes diretos da linhagem de Lúcifer — o anjo "
         "que se tornou o primeiro Garou. Carregam o peso da liderança hereditária e a "
         "corrupção genética que vem com ela. São belos, carismáticos e instáveis, "
         "equilibrando grandeza e loucura em medidas iguais.",
         ["Carisma +2", "Força +2"],
         "Linhagem instável: a cada avanço de Rank, deve ser feito um teste de Sanidade "
         "(CD 10 + Rank × 3). Falha resulta em uma compulsão narrativa temporária "
         "determinada pelo Narrador.",
         "#94a3b8"),
    ]

    for name, ability, desc, boost, flaw, color in tribes:
        story.extend(tribe_card(name, ability, desc, boost, flaw, color))

    return story

def build_ch4():
    story = []
    story.append(chapter_header("Cap. 4 — Auspícios como Backgrounds",
        "O signo lunar que define vocação e bônus secundários", C_AMBER))
    story.append(SP(8))
    story.append(Paragraph(
        "O Auspício é a fase da lua sob a qual o Garou nasceu. No PF2e Remaster, "
        "funciona como Background: fornece bônus de atributos, perícias treinadas exclusivas "
        "e uma habilidade passiva de auspício. Diferente da Tribo, o Auspício não tem Falha — "
        "é uma vocação, não uma limitação.",
        ST["body"]))

    auspices = [
        ("Ahroun", "Lua Cheia — O Guerreiro",
         "O Ahroun é nascido para a batalha. Sua conexão com Gaia é a mais direta e violenta: "
         "ele é a arma. Ahroun lideram cargas, terminam lutas e raramente recuam. Sua Raiva "
         "queima mais intensa que a de qualquer outro auspício, o que os torna letais — e perigosos.",
         ["+2 Força", "+1 Raiva Máxima"],
         ["Atletismo", "Intimidação"],
         "Fúria Inata: uma vez por combate, pode gastar 1 Raiva como ação livre (não conta como ação). "
         "Quando em Frenesi, o Ahroun não ataca aliados a menos que estes tentem fisicamente impedi-lo.",
         C_RED),
        ("Galliard", "Quarto Crescente — O Cantor",
         "Historiadores, contadores de histórias e comunicadores do mundo Garou. Os Galliard "
         "preservam as memórias da tribo, compõem uivos de guerra e mantêm viva a cultura Garou. "
         "Em combate, usam sua voz e presença para inspirar aliados e confundir inimigos.",
         ["+2 Carisma", "+1 Gnose"],
         ["Performance", "História (Garou)"],
         "Memória Vívida: pode gastar 1 Gnose para recordar perfeitamente qualquer evento que "
         "testemunhou. Também pode usar Performance no lugar de Intimidação para demoralizações.",
         C_PINK),
        ("Philodox", "Meia Lua — O Juiz",
         "Os legisladores e árbitros do mundo Garou. Conhecem as Litanias de cor e as "
         "aplicam com sabedoria. São chamados para resolver disputas, julgar violações "
         "e negociar paz. Seu senso de justiça é legendário — e às vezes inflexível.",
         ["+2 Sabedoria", "+1 Força de Vontade Máxima"],
         ["Diplomacia", "Leis (Garou)"],
         "Senso de Verdade: pode detectar mentiras com um teste de Percepção (CD igual ao "
         "resultado do teste de Enganação do alvo). Automaticamente bem-sucedido contra "
         "espíritos menores.",
         C_BLUE),
        ("Theurge", "Lua Crescente — O Mago",
         "Os xamãs e comunicadores espirituais do mundo Garou. Onde outros Garou veem o mundo "
         "físico, os Theurge veem também a Umbra sobreposta. São os especialistas em rituais, "
         "invocação de espíritos e interpretação de presságios. Sua Gnose é naturalmente superior.",
         ["+2 Sabedoria", "+3 Gnose Máxima"],
         ["Ocultismo", "Percepção (Espiritual)"],
         "Visão Dupla: pode perceber espíritos na Penumbra sem cruzar o Gauntlet, como ação "
         "livre. Recebe +2 em todos os testes de interação com espíritos.",
         C_ACCENT2),
        ("Ragabash", "Lua Nova — O Trapaceiro",
         "Os questionadores, espiões e desafiadores do status quo Garou. O Ragabash "
         "questiona regras que não fazem sentido e encontra caminhos que outros não veem. "
         "São os infiltradores, batedores e sabotadores — e frequentemente os mais "
         "criativos membros de qualquer matilha.",
         ["+2 Destreza", "+1 Dom adicional"],
         ["Furtividade", "Enganação"],
         "Lua Oculta: pode mover-se furtivamente como ação livre (sem custo de ação) uma "
         "vez por turno. Recebe +2 em iniciativa quando não foi detectado antes do combate.",
         C_GREEN),
    ]

    for name, subtitle, desc, boosts, skills, ability, color in auspices:
        inner = [
            Paragraph(name, ParagraphStyle("an", fontName="Helvetica-Bold",
                fontSize=13, leading=17, textColor=color)),
            Paragraph(subtitle, ParagraphStyle("as", fontName="Helvetica-Oblique",
                fontSize=9, leading=13, textColor=C_MUTED)),
            SP(6),
            Paragraph(desc, ST["body"]),
            SP(4),
            Paragraph("Bônus de Atributo: " + " | ".join(boosts), ParagraphStyle("ab",
                fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=C_GREEN)),
            Paragraph("Perícias Treinadas: " + ", ".join(skills), ParagraphStyle("ab2",
                fontName="Helvetica", fontSize=9, leading=13, textColor=C_MUTED)),
            SP(4),
            Paragraph(f"Habilidade de Auspício: {ability}", ParagraphStyle("aa",
                fontName="Helvetica", fontSize=9, leading=14, textColor=C_AMBER)),
        ]
        card_inner = Table([[p] for p in inner], colWidths=[PAGE_W - MARGIN*2 - 24])
        card_inner.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ]))
        bar = Table([[""]], colWidths=[4], rowHeights=[200])
        bar.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),color),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        card = Table([[bar, card_inner]], colWidths=[4, PAGE_W - MARGIN*2 - 4])
        card.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e293b")),
            ("LEFTPADDING",(1,0),(1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        story.append(SP(8))
        story.append(card)

    return story

def build_ch5():
    story = []
    story.append(chapter_header("Cap. 5 — A Classe Garou",
        "Progressão de nível, habilidades de classe e feitos disponíveis", C_GREEN))
    story.append(SP(8))
    story.append(Paragraph(
        "Todos os personagens jogadores são Garou — uma única classe base. Não existe "
        "subclasse no sentido tradicional do PF2e. A diversidade vem da combinação "
        "Tribo + Auspício + escolha de Dons ao longo dos níveis. Isso garante que "
        "dois Garou da mesma tribo e auspício possam ser radicalmente diferentes dependendo "
        "dos Dons escolhidos.",
        ST["body"]))

    story.extend(section_title("Habilidades de Classe Iniciais (Nível 1)"))
    abilities = [
        ("Forma Garou", "O personagem pode assumir qualquer uma das 5 formas Garou. "
         "Mudar para Crinos ou Hispo custa 2 ações; as demais formas custam 1 ação. "
         "As formas conferem modificadores de atributo e habilidades especiais detalhadas "
         "no Capítulo 6."),
        ("Sentidos de Predador", "O Garou possui olfato sobrenatural. Automaticamente "
         "Treinado em Percepção. Pode rastrear criaturas por cheiro com um teste de "
         "Sobrevivência (CD estabelecida pelo Narrador com base no tempo e condições)."),
        ("Resistência ao Frenesi", "O Garou possui o save especial de Resistência ao "
         "Frenesi, calculado como: d20 + mod Sabedoria + bônus de Rank + bônus de "
         "proficiência em Vontade. A CD varia com o gatilho do Frenesi."),
        ("Pool de Recursos", "O personagem começa com Raiva 5 (máximo 6), Gnose 4 "
         "(máximo 4) e Força de Vontade 7 (máximo 7). Esses valores crescem conforme "
         "o nível e o Auspício escolhido."),
    ]
    for name, desc in abilities:
        story.append(KeepTogether([
            Paragraph(f"● {name}", ST["h3"]),
            Paragraph(desc, ST["body"]),
        ]))

    story.extend(section_title("Tabela de Progressão da Classe Garou"))
    prog_data = [
        ["Nível", "Prof.", "Dons Garou", "Raiva Máx", "Gnose Máx", "Habilidades Especiais"],
        ["1", "T", "2", "6", "4", "Forma Garou, Sentidos de Predador, Pool de Recursos"],
        ["2", "+T", "1", "6", "4", "Feito de Perícia"],
        ["3", "Atq E", "1", "7", "5", "Resistência ao Frenesi +1, Feito de Classe"],
        ["4", "—", "1", "7", "5", "Feito de Perícia, Feito Geral"],
        ["5", "Atq E / Fort M", "2", "8", "6", "Aumento de Atributo (4), Dom Rank 2 disponível"],
        ["6", "—", "1", "8", "6", "Feito de Perícia, Feito de Ancestralidade"],
        ["7", "Atq M", "1", "9", "7", "Resist. Frenesi +2, Garra Aprimorada"],
        ["8", "—", "1", "9", "7", "Feito de Perícia, Feito de Classe"],
        ["9", "Reflex E", "2", "10", "8", "Dom Rank 3 disponível, Feito Geral"],
        ["10", "—", "1", "10", "8", "Aumento de Atributo (4), Feito de Perícia"],
        ["11", "—", "1", "10", "9", "Habilidade Simples de Arma M, Feito de Ancestralidade"],
        ["12", "—", "1", "10", "9", "Dom Rank 4 disponível, Feito de Classe"],
        ["15", "Atq L / Fort L", "2", "10", "10", "Aumento de Atributo (4), Dom Rank 5"],
        ["20", "Vont L", "1", "10", "10", "Forma Garou Lendária, Feito de Ancestralidade"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.07, 0.07, 0.09, 0.09, 0.09, 0.59]]
    story.append(SP(6))
    story.append(styled_table(prog_data[0], prog_data[1:], col_w))
    story.append(SP(4))
    story.append(Paragraph(
        "T = Treinado | E = Especialista | M = Mestre | L = Lendário | "
        "Atq = Ataque | Fort = Fortitude | Vont = Vontade | Reflex = Reflexo",
        ST["body_muted"]))

    return story

def build_ch6():
    story = []
    story.append(chapter_header("Cap. 6 — As 5 Formas Garou",
        "Transformação, modificadores e habilidades especiais de cada forma", C_AMBER))
    story.append(SP(8))
    story.append(Paragraph(
        "Um dos elementos mais icônicos do WtA é a capacidade de assumir múltiplas formas, "
        "cada uma com propósitos e poderes distintos. No PF2e Garou, as formas funcionam como "
        "estados que aplicam modificadores temporários aos atributos físicos e concedem "
        "habilidades especiais. Mudar de forma é uma ação gasta no turno — não é gratuita.",
        ST["body"]))

    forms = [
        ("Homid", "Forma Humana", "#3b82f6", 1,
         {"Força": "—", "Destreza": "—", "Constituição": "—", "Tamanho": "Médio", "Velocidade": "9m"},
         "Forma padrão. O Garou aparece como um humano comum. Todas as perícias sociais "
         "funcionam normalmente. Pode usar equipamentos, veículos e tecnologia sem restrição. "
         "Nenhuma habilidade de Forma ativa.",
         "Nenhuma — a força do Homid está na invisibilidade social e no acesso pleno ao mundo humano."),
        ("Glabro", "Forma Semi-humana", "#6b7280", 1,
         {"Força": "+2", "Destreza": "—", "Constituição": "+1", "Tamanho": "Médio", "Velocidade": "9m"},
         "Musculatura visivelmente aumentada, traços faciais mais rudes, pelos mais densos. "
         "Pode passar como humano em condições de pouca luz ou de longe. Um observador "
         "atento (Percepção CD 14) percebe que algo está errado.",
         "−2 em Diplomacia e Enganação com humanos não familiarizados com Garou. "
         "Pode usar equipamentos normalmente."),
        ("Crinos", "Forma Monstruosa", "#dc2626", 2,
         {"Força": "+4", "Destreza": "+1", "Constituição": "+3", "Tamanho": "Grande (+1 alcance)", "Velocidade": "12m"},
         "O lobisomem clássico das lendas. Bípede, 2,5m de altura, garras e presas que "
         "causam dano agravado. Aparência cai a 0 — falha automática em perícias sociais "
         "com humanos não-iniciados. Causa o efeito Delirium em humanos comuns.",
         "Garras: 2d6 dano cortante Agravado. Mordida: 1d10 dano perfurante Agravado. "
         "Delirium (veja caixa abaixo). Não pode usar equipamentos manufaturados. "
         "Roupas são destruídas na transformação a menos que sejam mágicas."),
        ("Hispo", "Lobo Gigante", "#d97706", 2,
         {"Força": "+3", "Destreza": "+2", "Constituição": "+2", "Tamanho": "Grande", "Velocidade": "18m"},
         "Lobo de tamanho sobrenatural, capaz de intimidar mesmo criaturas grandes. "
         "Quadrúpede — sem mãos, não pode usar equipamentos. Possui o melhor faro "
         "de todas as formas e velocidade superior.",
         "Velocidade 18m. +4 em Percepção baseada em olfato. +2 em Sobrevivência "
         "para rastreamento. Pode ser tomado por um lobo muito grande por observadores "
         "à distância (CD Percepção 18 para identificar como sobrenatural)."),
        ("Lupus", "Lobo Natural", "#059669", 1,
         {"Força": "+1", "Destreza": "+3", "Constituição": "+1", "Tamanho": "Médio", "Velocidade": "15m"},
         "Lobo de tamanho normal. A forma mais discreta e ágil. Passa completamente "
         "como um lobo para observadores humanos. Ideal para infiltração, rastreamento "
         "e exploração de áreas onde a presença humana seria suspeita.",
         "Furtividade com +2 automático. +6 em rastreamento por olfato. "
         "Pode se comunicar com lobos e cães normais. Sem mãos."),
    ]

    for name, subtitle, color_hex, action_cost, mods, desc, special in forms:
        color = colors.HexColor(color_hex)
        # Mods table
        mod_data = [[Paragraph(k, ParagraphStyle("mk", fontName="Helvetica-Bold",
                        fontSize=7.5, leading=10, textColor=C_MUTED, alignment=TA_CENTER)),
                     Paragraph(v, ParagraphStyle("mv", fontName="Helvetica-Bold",
                        fontSize=12, leading=16, textColor=color if v != "—" else C_MUTED,
                        alignment=TA_CENTER))]
                    for k, v in mods.items()]
        # Transpose: 1 row of keys, 1 row of values
        keys_row = [Paragraph(k, ParagraphStyle("mk2", fontName="Helvetica-Bold",
                        fontSize=7, leading=10, textColor=C_MUTED, alignment=TA_CENTER))
                    for k in mods.keys()]
        vals_row = [Paragraph(v, ParagraphStyle("mv2", fontName="Helvetica-Bold",
                        fontSize=13, leading=17,
                        textColor=color if v not in ("—", "Médio", "Grande", "Grande (+1 alcance)") else C_MUTED,
                        alignment=TA_CENTER))
                    for v in mods.values()]
        col_count = len(mods)
        cw = (PAGE_W - MARGIN*2 - 24) / col_count
        mods_table = Table([keys_row, vals_row], colWidths=[cw]*col_count)
        mods_table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#0f172a")),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),
        ]))
        content = [
            Paragraph(name, ParagraphStyle("fn", fontName="Helvetica-Bold",
                fontSize=14, leading=18, textColor=color)),
            Paragraph(f"{subtitle}  ·  Custo: {action_cost} {'ação' if action_cost == 1 else 'ações'}",
                ParagraphStyle("fs", fontName="Helvetica-Oblique",
                fontSize=9, leading=13, textColor=C_MUTED)),
            SP(8),
            mods_table,
            SP(8),
            Paragraph(desc, ST["body"]),
            SP(4),
            Paragraph("Habilidades Especiais:", ParagraphStyle("fh", fontName="Helvetica-Bold",
                fontSize=9, leading=13, textColor=C_AMBER)),
            Paragraph(special, ST["callout"]),
        ]
        card_inner = Table([[p] for p in content], colWidths=[PAGE_W - MARGIN*2 - 24])
        card_inner.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ]))
        bar = Table([[""]], colWidths=[4], rowHeights=[260])
        bar.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),color),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        card = Table([[bar, card_inner]], colWidths=[4, PAGE_W - MARGIN*2 - 4])
        card.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e293b")),
            ("LEFTPADDING",(1,0),(1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
            ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        story.append(SP(8))
        story.append(card)

    story.extend(section_title("Regra do Delirium"))
    story.extend(callout_box("Delirium — Terror Sobrenatural",
        "Humanos que avistam um Garou em forma Crinos ou Hispo devem fazer um save de Vontade "
        "com CD = 10 + Rank do Garou + modificador de Carisma do Garou. "
        "Sucesso Crítico: imune por 24h. Sucesso: o humano age normalmente mas está assustado. "
        "Falha: foge em pânico por 1d4 rodadas e esquece o evento em 10 minutos (memória suprimida). "
        "Falha Crítica: desmaia ou sofre Trauma (condição narrativa persistente por dias). "
        "Garou com a habilidade Veil Mastery podem suprimir o Delirium voluntariamente.",
        C_RED))

    return story

def build_ch7():
    story = []
    story.append(chapter_header("Cap. 7 — Raiva, Gnose e Força de Vontade",
        "Os três recursos que definem o poder e os limites de um Garou", C_RED))
    story.append(SP(8))
    story.append(Paragraph(
        "Os três recursos internos do Garou são o coração mecânico desta conversão. "
        "Diferente de pontos de magia ou pontos de vida, eles existem em camadas "
        "diferentes: Raiva governa o corpo e o combate; Gnose governa o espírito e "
        "a conexão sobrenatural; Força de Vontade governa a mente e o controle. "
        "Gerir os três simultaneamente é o que torna jogar um Garou diferente de "
        "qualquer outra classe do PF2e.",
        ST["body"]))

    resources = [
        ("Raiva (Rage)", C_RED,
         "A fúria de Gaia canalizada através do Garou. É poder bruto, velocidade e destruição. "
         "Alta Raiva torna o Garou devastador em combate — mas aproxima perigosamente o Frenesi. "
         "É o recurso mais fácil de gastar e o mais difícil de controlar.",
         [
             ("1 Raiva", "[A] livre", "Ganhar +1 ação adicional no turno (máximo 2 extras/turno)"),
             ("1 Raiva", "[A]", "Ativar qualquer Dom Físico de Rank 1"),
             ("2 Raiva", "[R] Reação", "Entrar em forma Crinos imediatamente quando atacado"),
             ("2 Raiva", "[A]", "Ativar Dons Físicos de Rank 2"),
             ("3 Raiva", "[A]", "Rerolhar um ataque com vantagem (mantém o melhor resultado)"),
             ("X Raiva", "[A]", "Ativar Dons que especificam custo variável"),
         ],
         "Raiva se recupera 1 ponto quando um inimigo é derrotado pelo Garou ou por sua "
         "matilha em combate. Recupera 1d4 pontos em descanso curto (10 minutos de "
         "contemplação furiosa). Recupera completamente em descanso longo.",
         "Raiva ≥ Vontade Máxima: o Garou deve fazer um save de Resistência ao Frenesi "
         "(CD 15) ao final de cada rodada em combate."),
        ("Gnose (Gnosis)", C_BLUE,
         "A conexão espiritual do Garou com Gaia e a Umbra. É o recurso mais lento de recuperar "
         "e o mais precioso para Theurges. Alta Gnose permite acesso profundo à Umbra, mas "
         "afasta gradualmente o personagem do mundo material — humanos ao redor sentem um "
         "estranhamento crescente.",
         [
             ("1 Gnose", "[A]", "Ativar qualquer Dom Espiritual de Rank 1"),
             ("2 Gnose", "[AA]", "Cruzar o Gauntlet (entrar na Umbra)"),
             ("2 Gnose", "[A]", "Comunicar-se com um espírito disposto"),
             ("3 Gnose", "[AAA]", "Realizar um Ritual Menor (Rank 1–2)"),
             ("3 Gnose", "[AA]", "Ativar Dons Espirituais de Rank 3"),
             ("4+ Gnose", "[AAA]", "Rituais Maiores, Banimento de espíritos poderosos"),
         ],
         "Gnose recupera 1 ponto por descanso longo (8 horas). Pode recuperar pontos extras "
         "meditando em locais de poder (Caerns, florestas virgens, lugares sagrados): +1d4 "
         "Gnose por hora de meditação, máximo 1 vez por local por semana.",
         "Gnose 0: o personagem não consegue perceber a Umbra e falha automaticamente em "
         "todos os testes espirituais. Espíritos ignoram o personagem completamente."),
        ("Força de Vontade (Willpower)", C_ACCENT2,
         "O recurso mais versátil e o mais difícil de ganhar de volta. A Vontade representa "
         "a força mental e emocional do Garou — sua capacidade de permanecer ele mesmo "
         "diante da Raiva, do medo e da corrupção do Wyrm. É o escudo contra o Frenesi.",
         [
             ("1 Vontade", "Antes de rolar", "+2 em qualquer rolagem (declarado antes do dado)"),
             ("1 Vontade", "Reação", "Resistir a um efeito de medo ou controle mental"),
             ("2 Vontade", "[A]", "Suprimir Frenesi ativo por 1 rodada"),
             ("3 Vontade", "Reação", "Negar automaticamente um gatilho de Frenesi"),
             ("1 Vontade", "Fora de combate", "+4 em qualquer teste de perícia social"),
         ],
         "Força de Vontade recupera 1 ponto quando o personagem cumpre um marco narrativo "
         "pessoal (objetivo alinhado com valores da tribo ou auspício, conforme definido "
         "com o Narrador). Recupera completamente em descanso longo após uma cena "
         "de interpretação significativa.",
         "Vontade 0: o personagem está esgotado. Entra em Frenesi automaticamente na "
         "primeira provocação, sem direito a save."),
    ]

    for name, color, desc, uses, recovery, warning in resources:
        story.extend(section_title(name))
        story.append(Paragraph(desc, ST["body"]))
        story.append(SP(6))

        # Uses table
        use_data = [["Custo", "Ação", "Efeito"]] + list(uses)
        col_w = [(PAGE_W - MARGIN*2) * p for p in [0.15, 0.12, 0.73]]
        story.append(styled_table(use_data[0], use_data[1:], col_w))
        story.append(SP(6))
        story.append(Paragraph(f"Recuperação: {recovery}", ParagraphStyle("rr",
            fontName="Helvetica", fontSize=9, leading=14, textColor=C_GREEN)))
        story.extend(callout_box(None, f"⚠ Aviso: {warning}", color))

    return story

def build_ch8():
    story = []
    story.append(chapter_header("Cap. 8 — Dons (Gifts) como Feitos de Classe",
        "Catálogo de Dons organizados por Rank, Tipo e Custo", C_BLUE))
    story.append(SP(8))
    story.append(Paragraph(
        "No WtA original, Dons são poderes sobrenaturais ensinados por espíritos. "
        "No PF2e Garou, funcionam como Feitos de Classe adquiridos ao subir de nível "
        "ou ao avançar de Rank. Cada Dom tem um Tipo (Físico, Espiritual, Social, Passivo), "
        "um Custo em Raiva ou Gnose, e uma ação necessária. Dons de Rank superior "
        "ficam disponíveis apenas quando o personagem atingiu aquele Rank.",
        ST["body"]))

    gifts = [
        # Rank 1
        (1,"Físico","Garra da Fúria","1 Raiva","[A]",
         "Suas garras canalizam a fúria de Gaia. Por uma rodada, seus ataques de garra "
         "causam +1d6 dano Agravado adicional. Em Sucesso Crítico, o alvo também sangra "
         "(1d4 dano Agravado no início de cada turno por 2 rodadas)."),
        (1,"Passivo","Sentidos Aguçados","—","Passivo",
         "Você está permanentemente Treinado em Percepção (ou Especialista se já era Treinado). "
         "Rastrear criaturas por olfato conta como Treinado automaticamente. Detecta "
         "a corrupção do Wyrm em objetos e locais com sucesso em Percepção CD 12."),
        (1,"Físico","Pele de Aço","1 Gnose","[R] Reação",
         "Gatilho: você recebe dano. Você endurece a pele espiritualmente. Reduza o dano "
         "recebido em 3 pontos (5 pontos se estiver em forma Crinos). Pode ser declarado "
         "após ver o resultado do ataque adversário."),
        (1,"Espiritual","Sussurro dos Espíritos","1 Gnose","[A]",
         "Você chama brevemente a atenção de um espírito local. O espírito pode revelar "
         "informações sobre a área (eventos recentes, presença do Wyrm, locais sagrados). "
         "Espíritos hostis resistem — o Narrador pode exigir teste de Diplomacia CD 14."),
        (1,"Social","Cheiro da Fraqueza","1 Raiva","[A]",
         "Você analisa um inimigo com seu olfato sobrenatural. Revela sua condição de HP "
         "(saudável/danificado/crítico), um Save fraco e se está com medo. Funciona apenas "
         "em alvos que você pode ver e cheirar."),
        (1,"Passivo","Cura da Luna","—","Passivo",
         "Você se cura mais rápido durante a noite. Em descanso curto realizado à noite, "
         "cure 1d6 PV extras. Sob luz direta de lua cheia, cure 2d6 extras. Não funciona "
         "em dano Agravado."),
        # Rank 2
        (2,"Social","Uivo da Matilha","2 Raiva","[A]",
         "Você solta um uivo de guerra ritual. Todos os aliados que possam ouvi-lo em "
         "18 metros ganham +2 em ataques e saves de Fortitude por 1 minuto (10 rodadas). "
         "Em Sucesso Crítico, também ganham +1d4 PV temporários."),
        (2,"Espiritual","Passo na Umbra","2 Gnose","[AA]",
         "Você cruza o Gauntlet e entra na Umbra por até 10 minutos, sem teste. "
         "Pode levar consigo um número de aliados tocando você igual ao seu Rank. "
         "Retornar ao mundo físico custa 1 ação adicional."),
        (2,"Físico","Fúria do Wyrm","2 Raiva","[AA]",
         "Você canaliza a fúria de Gaia em um ataque devastador em área. Todos em um "
         "cone de 6m sofrem 3d8 dano Agravado (save de Reflexo CD 10+Rank+mod Força "
         "reduz à metade). Não pode ser usado mais de uma vez por combate."),
        (2,"Espiritual","Purificação","3 Gnose","1 minuto",
         "Você realiza um ritual menor de purificação sobre um alvo tocado. Remove uma "
         "maldição, doença leve ou traço de corrupção do Wyrm. Condições mais graves "
         "podem exigir múltiplos rituais ou Dons de Rank superior."),
        (2,"Passivo","Armadura da Terra","—","Passivo",
         "Sua resistência a dano comum aumenta enquanto você está em contato com terra "
         "natural (não asfalto ou concreto). Reduza qualquer dano contundente, cortante "
         "ou perfurante em 2 pontos. Em solo de floresta, em 4 pontos."),
        # Rank 3
        (3,"Físico","Mordida da Lua","3 Raiva","[A]",
         "Um ataque de mordida carregado de poder lunar. Causa 4d10 dano Agravado. "
         "Em Sucesso Crítico, o alvo sofre sangramento (1d8/rodada por 3 rodadas). "
         "Pode ser usado apenas em forma Crinos, Hispo ou Lupus."),
        (3,"Espiritual","Barreira da Umbra","4 Gnose","[R] Reação",
         "Você cria uma barreira entre o mundo físico e espiritual em raio de 9m por "
         "1 hora. Nenhum espírito pode cruzar a barreira (em nenhuma direção) enquanto "
         "você mantiver concentração. Concentração pode ser quebrada por dano."),
        (3,"Passivo","Forma do Ancestral","—","Passivo",
         "Ao entrar em forma Crinos, você pode invocar brevemente um ancestral Garou. "
         "Escolha um Dom de Rank 1 de qualquer Tribo (não necessariamente a sua). "
         "Você pode usar aquele Dom gratuitamente por 1 hora."),
        (3,"Social","Olhar do Rei","2 Vontade","[A]",
         "Você olha diretamente para um alvo. Ele deve fazer um save de Vontade "
         "(CD 10+Rank+mod Carisma) ou ficar Amedrontado 2 por 1 minuto. Em Falha "
         "Crítica, foge do local pelo caminho mais curto por 1d4 rodadas."),
    ]

    ranks = [1, 2, 3]
    type_colors = {"Físico": C_RED, "Espiritual": C_BLUE, "Social": C_AMBER, "Passivo": C_GREEN}

    for rank in ranks:
        story.extend(section_title(f"Dons de Rank {rank}"))
        rank_gifts = [g for g in gifts if g[0] == rank]
        for _, gtype, gname, gcost, gaction, gdesc in rank_gifts:
            tc = type_colors.get(gtype, C_MUTED)
            inner_content = [
                [Paragraph(gname, ParagraphStyle("gn", fontName="Helvetica-Bold",
                    fontSize=11, leading=15, textColor=C_WHITE)),
                 Paragraph(gtype, ParagraphStyle("gt", fontName="Helvetica-Bold",
                    fontSize=8, leading=12, textColor=tc, alignment=TA_CENTER))],
                [Paragraph(f"Custo: {gcost}  ·  Ação: {gaction}",
                    ParagraphStyle("gi", fontName="Helvetica-Oblique",
                    fontSize=8.5, leading=12, textColor=C_MUTED)), ""],
                [Paragraph(gdesc, ST["body"]), ""],
            ]
            gw = PAGE_W - MARGIN*2
            gift_table = Table(inner_content, colWidths=[gw*0.8, gw*0.2])
            gift_table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e293b")),
                ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LINEAFTER",(0,0),(0,-1), 2, tc),
                ("SPAN",(0,2),(1,2)),
                ("SPAN",(0,1),(1,1)),
            ]))
            story.append(SP(5))
            story.append(gift_table)

    return story

def build_ch9():
    story = []
    story.append(chapter_header("Cap. 9 — Renome e Progressão de Rank",
        "A moeda social dos Garou — Glória, Honra e Sabedoria", C_ACCENT2))
    story.append(SP(8))
    story.append(Paragraph(
        "No WtA, avançar de Rank não é uma questão de experiência acumulada — é uma "
        "questão de reputação. Os Garou não sobem de nível socialmente por matar inimigos; "
        "eles ganham Renome por suas ações, e o Renome é julgado pela própria comunidade Garou. "
        "Esta conversão preserva essa mecânica como camada separada do nível do PF2e.",
        ST["body"]))

    story.extend(section_title("Os Três Eixos do Renome"))
    for name, color, symbol, desc, exemplos in [
        ("Glória", C_RED, "⚔",
         "Conquistada em batalha e feitos de coragem. É o renome mais visível e o mais "
         "fácil de perder. Um Garou que recua sem honra perde Glória tão rápido quanto "
         "a ganhou.",
         ["Derrotar um servo poderoso do Wyrm sozinho",
          "Liderar uma carga vitoriosa contra probabilidades adversas",
          "Sacrificar-se para salvar a matilha (mesmo que sobreviva)",
          "Vencer um desafio de combate ritual perante testemunhas"]),
        ("Honra", C_BLUE, "⚖",
         "Conquistada por conduta ética e respeito às Litanias. A Honra é o renome "
         "dos Philodox — mas qualquer Garou pode perdê-la rapidamente ao violar "
         "as leis da tribo ou trair um aliado.",
         ["Manter a palavra mesmo sob pressão extrema",
          "Julgar um conflito interno com imparcialidade reconhecida",
          "Recusar corrupção, suborno ou vantagem desonesta",
          "Proteger um não-combatente mesmo à custa pessoal"]),
        ("Sabedoria", C_GREEN, "◈",
         "Conquistada por conhecimento espiritual e uso criterioso de Gnose. "
         "É o renome dos Theurges, mas valorizado por todas as tribos. "
         "A Sabedoria não pode ser forçada — é reconhecida por pares.",
         ["Decifrar um enigma ou profecia espiritual",
          "Negociar com sucesso com um espírito hostil",
          "Identificar a presença do Wyrm antes de outros perceberem",
          "Realizar um ritual maior com sucesso em condições adversas"]),
    ]:
        story.append(KeepTogether([
            Paragraph(f"{symbol} {name}", ParagraphStyle("ren", fontName="Helvetica-Bold",
                fontSize=12, leading=16, textColor=color, spaceBefore=12, spaceAfter=4)),
            Paragraph(desc, ST["body"]),
            Paragraph("Exemplos de ações que concedem " + name + ":", ParagraphStyle("re",
                fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=C_MUTED,
                spaceBefore=4, spaceAfter=4)),
        ]))
        for ex in exemplos:
            story.append(Paragraph(f"  + {ex}", ParagraphStyle("rex",
                fontName="Helvetica", fontSize=9, leading=14, textColor=C_TEXT,
                leftIndent=12, spaceAfter=2)))
        story.append(SP(4))

    story.extend(section_title("Tabela de Ranks"))
    rank_data = [
        ["Rank", "Nome", "Glória Mín.", "Honra Mín.", "Sab. Mín.", "Privilégios"],
        ["1", "Cliath", "2", "2", "2", "Dons Rank 1. Voto local apenas."],
        ["2", "Fostern", "5", "5", "5", "Dons Rank 2. +1 Feito de Classe. Pode solicitar julgamento."],
        ["3", "Adren", "10", "10", "10", "Dons Rank 3. +2 Feitos. Pode liderar rituais menores."],
        ["4", "Athro", "20", "20", "20", "Dons Rank 4. Pode treinar Cliathos. Voto pleno."],
        ["5", "Elder", "35", "35", "35", "Dons Rank 5. Autoridade sobre a matilha."],
        ["6", "Elder Lendário", "50", "50", "50", "Poder semidivino. Comunhão direta com Gaia."],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.07, 0.14, 0.11, 0.11, 0.10, 0.47]]
    story.append(SP(6))
    story.append(styled_table(rank_data[0], rank_data[1:], col_w))

    story.extend(section_title("Reivindicar um Rank"))
    story.append(Paragraph(
        "Quando um Garou acumula o Renome mínimo nos três eixos para o próximo Rank, "
        "ele pode <i>reivindicar</i> o avanço. Isso requer: (1) que pelo menos dois Garou "
        "de Rank igual ou superior ao desejado testemunhem e confirmem os feitos; "
        "(2) um Rito de Passagem adequado ao Rank (determinado pelo Narrador); "
        "(3) que nenhuma acusação de desonra esteja pendente contra o personagem.",
        ST["body"]))

    story.extend(section_title("Perda de Renome"))
    story.append(Paragraph(
        "Renome pode ser perdido por ações que contradigam o eixo correspondente: "
        "um ato de covardia retira Glória; trair um aliado retira Honra; agir "
        "impulsivamente em questões espirituais retira Sabedoria. O Narrador anuncia "
        "a perda abertamente — o julgamento da matilha é público, não secreto. "
        "Perder Renome suficiente pode resultar em <i>rebaixamento</i> de Rank, "
        "com todos os privilégios correspondentes perdidos.",
        ST["body"]))
    return story

def build_ch10():
    story = []
    story.append(chapter_header("Cap. 10 — O Frenesi",
        "A mecânica de maior tensão: quando o monstro toma o controle", C_RED))
    story.append(SP(8))
    story.append(Paragraph(
        "O Frenesi é a possibilidade de perda total de controle — o lado animal e "
        "furioso do Garou sobrepondo a consciência. Não é apenas uma ameaça em combate: "
        "é uma ameaça à identidade do personagem, ao tecido social da matilha e à "
        "missão de proteger humanos do Wyrm. Um Garou em Frenesi pode matar aliados, "
        "destruir refúgios e romper o Véu que os protege de serem descobertos.",
        ST["body"]))

    story.extend(section_title("Gatilhos do Frenesi"))
    triggers = [
        ("Dano grave recebido", "CD 12",
         "Receber 15+ pontos de dano em uma única jogada. CD aumenta +2 para cada "
         "instância subsequente no mesmo combate."),
        ("Odor do Wyrm", "CD 14",
         "Detectar a presença de corrupção do Wyrm em alta intensidade — lixo tóxico, "
         "Bane spirits concentrados, objetos rituais corrompidos."),
        ("Ameaça a membro da matilha", "CD 15",
         "Ver um membro da matilha ser gravemente ferido ou ameaçado de morte."),
        ("Insulto à tribo ou ancestrais", "CD 13",
         "Receber um insulto deliberado e público à Tribo, auspício ou ancestrais do Garou."),
        ("Raiva ≥ Vontade Máxima", "CD 15+",
         "Quando os pontos atuais de Raiva igualam ou superam o valor máximo de Vontade. "
         "CD aumenta +1 por ponto excedente."),
        ("Lua Cheia (Ahroun)", "CD 10 na lua cheia",
         "Exclusivo para Ahroun: em noite de lua cheia, qualquer gatilho tem CD −2. "
         "O poder lunar amplifica a Raiva."),
    ]
    t_data = [["Gatilho", "CD Base", "Detalhes"]] + [[g, cd, det] for g, cd, det in triggers]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.28, 0.12, 0.60]]
    story.append(SP(6))
    story.append(styled_table(t_data[0], t_data[1:], col_w))

    story.extend(section_title("O Save de Resistência ao Frenesi"))
    story.append(Paragraph(
        "Quando um gatilho ocorre, o Garou imediatamente faz um save de Resistência "
        "ao Frenesi: d20 + mod Sabedoria + bônus de proficiência em Vontade + bônus de Rank.",
        ST["body"]))
    frenzy_results = [
        ["Resultado", "Consequência"],
        ["Sucesso Crítico", "Imune a esse gatilho específico por 1 hora."],
        ["Sucesso", "Resiste nesta rodada. Deve rerolhar se o gatilho persistir na próxima."],
        ["Falha", "Entra em Frenesi por 1d4 rodadas."],
        ["Falha Crítica", "Entra em Frenesi por 1d4 minutos. O tipo de Frenesi é o mais severo disponível."],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.25, 0.75]]
    story.append(SP(6))
    story.append(styled_table(frenzy_results[0], frenzy_results[1:], col_w))

    story.extend(section_title("Estado de Frenesi"))
    story.append(Paragraph(
        "Durante o Frenesi, o personagem age por instinto puro. O Narrador pode "
        "assumir controle do personagem ou o jogador age com as seguintes restrições:",
        ST["body"]))
    frenzy_rules = [
        "Ataca o inimigo mais próximo em cada turno, sem consideração tática.",
        "Usa ações extras de Raiva sem custo (a Raiva simplesmente flui).",
        "Não pode usar Dons que exijam concentração ou testes de Inteligência.",
        "Ignora aliados como obstáculos — e os ataca se estiverem entre ele e o alvo.",
        "Continua lutando mesmo inconsciente (ativo até −10 PV antes de cair).",
        "Não pode recolher objetos, abrir portas ou realizar ações que exijam planejamento.",
    ]
    for rule in frenzy_rules:
        story.append(Paragraph(f"  ● {rule}", ParagraphStyle("fr",
            fontName="Helvetica", fontSize=9.5, leading=15, textColor=C_TEXT, leftIndent=8)))
    story.append(SP(4))

    story.extend(section_title("Tipos de Frenesi"))
    for name, color, desc in [
        ("Frenesi de Batalha", C_RED,
         "O mais comum. O Garou entra em modo de destruição pura. Ataca o inimigo "
         "mais próximo sem distinção. Continua até não haver mais ameaças visíveis "
         "ou até sua Raiva esgotar. Aliados que fisicamente tentarem contê-lo são "
         "tratados como inimigos."),
        ("Frenesi do Wyrm", C_ACCENT,
         "Causado por exposição extrema à corrupção do Wyrm ou por rituais do inimigo. "
         "O mais devastador: o Garou torna-se temporariamente servo do Wyrm, atacando "
         "aliados preferencialmente sobre inimigos. Requer exorcismo espiritual para "
         "curar os efeitos residuais."),
        ("Frenesi de Caça", C_AMBER,
         "Foco absoluto em um único alvo de fuga. O Garou persegue obsessivamente "
         "uma presa específica, ignorando todos os outros estímulos. Não termina "
         "até capturar o alvo ou perder completamente o rastro."),
    ]:
        story.extend(callout_box(name, desc, color))

    story.extend(section_title("Saindo do Frenesi"))
    story.append(Paragraph(
        "Existem três formas de encerrar um Frenesi ativo:",
        ST["body"]))
    story.append(Paragraph("  1. Gastar 3 Vontade (ação livre, pode ser feito mesmo durante o Frenesi).", ST["callout"]))
    story.append(Paragraph("  2. Um aliado pode tentar acalmar com teste de Empatia ou Adestramento Animal, CD 20.", ST["callout"]))
    story.append(Paragraph("  3. Automaticamente termina quando não há mais estímulos provocadores visíveis e a duração expirou.", ST["callout"]))

    return story

def build_ch11():
    story = []
    story.append(chapter_header("Cap. 11 — A Umbra",
        "O mundo espiritual, o Gauntlet e as regiões além do véu", C_ACCENT2))
    story.append(SP(8))
    story.append(Paragraph(
        "A Umbra é o espelho espiritual do mundo físico — uma realidade paralela onde "
        "tudo que existe no mundo material tem uma contrapartida espiritual. O que está "
        "corrompido espiritualmente aparece primeiro na Umbra antes de manifestar no "
        "mundo físico. Para os Garou, a Umbra é tanto campo de batalha quanto fonte "
        "de poder.",
        ST["body"]))

    story.extend(section_title("Cruzando o Gauntlet"))
    story.append(Paragraph(
        "O Gauntlet é a barreira entre o mundo físico e a Umbra. Cruzá-lo requer "
        "gastar 2 Gnose e fazer um teste de Ocultismo ou Sobrevivência contra a CD "
        "do Gauntlet local. O Dom 'Passo na Umbra' (Rank 2) permite cruzar sem teste.",
        ST["body"]))
    gauntlet_data = [
        ["Tipo de Local", "CD do Gauntlet", "Exemplos"],
        ["Natureza virgem", "10", "Florestas remotas, montanhas, oceano aberto"],
        ["Natureza gerenciada", "13", "Parques, reservas, fazendas orgânicas"],
        ["Subúrbio / periferia", "16", "Bairros residenciais, pequenas cidades"],
        ["Centro urbano", "20", "Cidades grandes, distritos comerciais"],
        ["Área industrial", "23", "Fábricas, refinarias, zonas portuárias"],
        ["Caern (lugar sagrado)", "5", "Locais de poder espiritual Garou"],
        ["Domínio do Wyrm", "25+", "Locais de alta corrupção, Malfeas adjacente"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.30, 0.20, 0.50]]
    story.append(SP(6))
    story.append(styled_table(gauntlet_data[0], gauntlet_data[1:], col_w))

    story.extend(section_title("Regiões da Umbra"))
    regions = [
        ("Penumbra", C_BLUE,
         "A camada mais próxima do mundo físico. Um espelho deformado da realidade — "
         "o que existe lá reflete o estado espiritual do que existe aqui. Uma floresta "
         "saudável tem uma Penumbra exuberante; uma área poluída tem uma Penumbra "
         "doentia e distorcida.",
         "Ações normais. Visão do mundo físico como através de névoa prateada. "
         "Comunicação com o mundo físico é possível mas difícil (CD 15). "
         "Espíritos menores (Gafflings, Jaglings) habitam esta região."),
        ("Umbra Média", C_ACCENT,
         "O reino dos espíritos propriamente dito. Domínios de entidades poderosas, "
         "Totem Spirits e as correntes da luta entre Wyld, Weaver e Wyrm. "
         "Tempo e espaço funcionam diferente aqui — uma hora na Umbra pode ser "
         "minutos ou dias no mundo físico.",
         "−2 em testes físicos. Leis da natureza podem falhar. Navegação requer "
         "teste de Ocultismo CD 16 para não se perder. Comunicação com o mundo "
         "físico é impossível sem rituais específicos."),
        ("Umbra Profunda", C_ACCENT2,
         "O além absoluto. Garou de Rank baixo raramente sobrevivem aqui. "
         "Os Triath — espíritos primordiais de imensa idade e poder — governam "
         "estas regiões. O acesso a relíquias e conhecimentos ancestrais únicos "
         "torna a jornada tentadora apesar dos riscos.",
         "Sem save de Gnose disponível enquanto estiver aqui. Cada hora exige "
         "teste de Vontade CD 20 ou o personagem sofre 1 de Gnose de dano. "
         "Retornar ao mundo físico requer um Portal ou ritual de Rank 4+."),
        ("Domínios do Wyrm / Malfeas", C_RED,
         "Áreas da Umbra completamente consumidas pela corrupção. Malfeas — "
         "a prisão do Wyrm — está aqui. Tudo é tóxico ao espírito Garou. "
         "Destino de campanhas avançadas e missões quase suicidas.",
         "Dano Agravado 1/hora apenas por estar presente. Saves de Frenesi "
         "com CD +4. Gnose se drena à taxa de 1/hora. Espíritos hostis em "
         "abundância. Saída apenas por rituais de Rank 5."),
    ]
    for name, color, desc, rules in regions:
        inner = [
            Paragraph(name, ParagraphStyle("rn", fontName="Helvetica-Bold",
                fontSize=13, leading=17, textColor=color)),
            SP(4),
            Paragraph(desc, ST["body"]),
            SP(4),
            Paragraph(f"Regras: {rules}", ParagraphStyle("rru",
                fontName="Helvetica-Oblique", fontSize=9, leading=14, textColor=C_AMBER)),
        ]
        card = Table([[p] for p in inner], colWidths=[PAGE_W - MARGIN*2])
        card.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e293b")),
            ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
            ("LINEAFTER",(0,0),(-1,-1),0,colors.transparent),
            ("LINEBEFORE",(0,0),(0,-1),4,color),
        ]))
        story.append(SP(8))
        story.append(card)

    story.extend(section_title("Espíritos — Tipos e Interação"))
    spirit_data = [
        ["Tipo", "Poder", "Interação Principal"],
        ["Gafflings", "Menor", "Espíritos menores — mensageiros, elementais simples. Fáceis de contactar."],
        ["Jaglings", "Médio", "Avatares de forças naturais. Podem fazer favores em troca de Gnose."],
        ["Totem Spirits", "Maior", "Espírito protetor da matilha. Fornece Dons e bônus exclusivos."],
        ["Incarna", "Imenso", "Espíritos primordiais que representam forças cósmicas. Raramente interagem."],
        ["Triath", "Divino", "Entidades quase além da compreensão. Aparecem apenas em Umbra Profunda."],
        ["Banes (Wyrm)", "Variável", "Espíritos corrompidos. Hostis. Não negociam — apenas atacam ou manipulam."],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.20, 0.15, 0.65]]
    story.append(SP(6))
    story.append(styled_table(spirit_data[0], spirit_data[1:], col_w))

    return story

def build_ch12():
    story = []
    story.append(chapter_header("Cap. 12 — Dano Agravado e Cura",
        "O tipo de dano que define a mortalidade do combate Garou", C_AMBER))
    story.append(SP(8))
    story.append(Paragraph(
        "No WtA, Dano Agravado é uma categoria especial que não pode ser curada "
        "naturalmente. Esta conversão mantém o conceito com adaptações para o sistema "
        "de PV do PF2e. Dano Agravado representa ferimentos espirituais e físicos "
        "profundos causados por forças sobrenaturais.",
        ST["body"]))

    story.extend(section_title("O que causa Dano Agravado"))
    causes = [
        ("Garras e Presas em Crinos/Hispo", "Ataques físicos de Garou em formas bestiais"),
        ("Prata", "O metal sagrado é veneno para Garou — qualquer dano com prata é Agravado"),
        ("Fogo", "Todo dano de fogo causa Agravado em Garou"),
        ("Magia do Wyrm", "Rituais, Banes e poderes diretamente ligados ao Wyrm"),
        ("Dano espiritual na Umbra", "Espíritos hostis causam Agravado quando atacam na Umbra"),
        ("Certos Dons inimigos", "Dons de Rank 3+ de inimigos Garou ou criaturas sobrenaturais"),
    ]
    for name, desc in causes:
        story.append(Paragraph(f"  ● <b>{name}:</b> {desc}", ParagraphStyle("ca",
            fontName="Helvetica", fontSize=9.5, leading=15, textColor=C_TEXT, leftIndent=8,
            spaceAfter=3)))
    story.append(SP(6))

    story.extend(section_title("Como o Dano Agravado Funciona"))
    story.append(Paragraph(
        "O Dano Agravado é rastreado separadamente dos PV normais. O personagem "
        "possui um Marcador de Dano Agravado (MDA) que começa em 0. Cada ponto de "
        "Dano Agravado recebido adiciona 1 ao MDA e <i>também</i> reduz o máximo "
        "de PV do personagem em 1 enquanto o dano não for curado.",
        ST["body"]))
    story.extend(callout_box("Exemplo",
        "Grimnar tem 40 PV (max 40) e MDA 0. Ele recebe 8 pontos de Dano Agravado. "
        "Seu MDA vai para 8, e seu PV máximo cai para 32. Se seus PV atuais eram 40, "
        "caem automaticamente para 32. Curar Dano Agravado restaura tanto o MDA quanto "
        "o máximo de PV.",
        C_AMBER))

    story.extend(section_title("Cura do Dano Agravado"))
    heal_data = [
        ["Método", "Quantidade Curada", "Requisito"],
        ["Descanso Longo (8h)", "1 ponto de MDA", "Deve estar em local seguro, fora de combate"],
        ["Gastar Gnose", "1 ponto de MDA por 2 Gnose", "Pode ser feito em combate como [AA]"],
        ["Dom: Purificação (Rank 2)", "1d4 pontos de MDA", "Requer 3 Gnose e 1 minuto"],
        ["Ritual de Cura Maior (Rank 4)", "Todo o MDA", "Requer 6 Gnose, 1 hora, local sagrado"],
        ["Prata no corpo", "Não cura", "Enquanto o fragmento estiver no corpo, impossível curar"],
        ["Forma Homid em repouso (1h)", "1 ponto de MDA extra", "Além do descanso longo, forma humana ajuda"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.30, 0.25, 0.45]]
    story.append(SP(6))
    story.append(styled_table(heal_data[0], heal_data[1:], col_w))

    story.extend(section_title("Prata — O Grande Inimigo"))
    story.extend(callout_box("Regra Especial: Prata",
        "Armas de prata causam Dano Agravado automaticamente em Garou. Além disso, "
        "qualquer Garou que receba dano de prata não pode usar a cura natural de "
        "descanso para o MDA causado por prata — apenas Gnose ou rituais funcionam. "
        "Fragmentos de prata embutidos no corpo (por armas perfurantes) causam "
        "1 ponto de Dano Agravado no início de cada turno até serem removidos "
        "(remoção requer 2 ações e um teste de Medicina CD 14).",
        C_RED))
    return story

def build_appendix():
    story = []
    story.append(chapter_header("Apêndice — Tabelas de Referência",
        "Consulta rápida para uso em mesa", C_MUTED))
    story.append(SP(10))

    story.extend(section_title("Resumo de Ações Comuns"))
    actions_ref = [
        ["Ação", "Custo", "Efeito"],
        ["Atacar (Strike)", "[A]", "d20 + ataque vs CA. −5 por ataque adicional."],
        ["Mover (Stride)", "[A]", "Mover até sua Velocidade."],
        ["Mudar forma (menor)", "[A]", "Homid ↔ Glabro ↔ Lupus"],
        ["Mudar forma (maior)", "[AA]", "Qualquer forma → Crinos ou Hispo"],
        ["Dom Rank 1", "[A]", "Custo em Raiva ou Gnose conforme Dom."],
        ["Dom Rank 2", "[AA]", "Custo em Raiva ou Gnose conforme Dom."],
        ["Cruzar Gauntlet", "[AA]", "2 Gnose + teste de Ocultismo vs CD local."],
        ["Suprimir Frenesi", "[A]", "2 Vontade. Dura 1 rodada."],
        ["Reação: Entrada Crinos", "[R]", "2 Raiva. Gatilho: ser atacado."],
        ["Reação: Pele de Aço", "[R]", "1 Gnose. Reduz dano em 3 (ou 5 em Crinos)."],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.35, 0.12, 0.53]]
    story.append(styled_table(actions_ref[0], actions_ref[1:], col_w))

    story.extend(section_title("CDs Comuns"))
    cd_ref = [
        ["Tarefa", "CD"],
        ["Cruzar Gauntlet em natureza virgem", "10"],
        ["Cruzar Gauntlet em cidade", "20"],
        ["Resistir a Delirium (humano)", "10 + Rank + mod Car"],
        ["Detectar presença do Wyrm (Percepção)", "12–20"],
        ["Negociar com espírito menor", "14"],
        ["Resistência ao Frenesi (dano grave)", "12–15"],
        ["Resistência ao Frenesi (prata)", "18"],
        ["Reivindicar Rank (teste social)", "10 + Rank desejado × 3"],
        ["Acompanhar rastro por olfato", "10–20 (condições)"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.70, 0.30]]
    story.append(SP(8))
    story.append(styled_table(cd_ref[0], cd_ref[1:], col_w))

    story.extend(section_title("Modificadores de Forma — Resumo"))
    form_ref = [
        ["Forma", "FOR", "DES", "CON", "Tam.", "Vel.", "Custo", "Especial"],
        ["Homid", "—", "—", "—", "Médio", "9m", "[A]", "Social pleno"],
        ["Glabro", "+2", "—", "+1", "Médio", "9m", "[A]", "−2 social"],
        ["Crinos", "+4", "+1", "+3", "Grande", "12m", "[AA]", "Delirium, Agravado"],
        ["Hispo", "+3", "+2", "+2", "Grande", "18m", "[AA]", "+4 Percepção olfato"],
        ["Lupus", "+1", "+3", "+1", "Médio", "15m", "[A]", "+2 Furtividade"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.13, 0.07, 0.07, 0.07, 0.09, 0.08, 0.08, 0.41]]
    story.append(SP(8))
    story.append(styled_table(form_ref[0], form_ref[1:], col_w))

    story.extend(section_title("Recuperação de Recursos"))
    recov_ref = [
        ["Recurso", "Descanso Curto", "Descanso Longo", "Outros"],
        ["Raiva", "1d4 pontos", "Completo", "+1 por inimigo derrotado"],
        ["Gnose", "Não recupera", "+1 ponto", "+1d4 em Caern ou local sagrado"],
        ["Vontade", "Não recupera", "Completo (com cena interpretativa)", "+1 por marco narrativo"],
        ["PV normais", "Recupera (por dado de cura)", "Completo", "Dom de cura, poções"],
        ["MDA (Dano Agravado)", "Não recupera", "−1 ponto", "2 Gnose = −1 MDA; Rituais"],
    ]
    col_w = [(PAGE_W - MARGIN*2) * p for p in [0.18, 0.20, 0.27, 0.35]]
    story.append(SP(8))
    story.append(styled_table(recov_ref[0], recov_ref[1:], col_w))

    return story

# ─── BUILD ────────────────────────────────────────────────────────────────────

def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=2.8*cm, bottomMargin=1.8*cm,
        title="Garou: The Apocalypse — Conversão PF2e Remaster",
        author="Documento de Regras",
    )

    story = []

    # Cover
    story.extend(build_cover())
    story.append(PageBreak())

    # TOC
    story.extend(build_toc())
    story.append(PageBreak())

    # Chapters
    for builder in [
        build_ch1, build_ch2, build_ch3, build_ch4,
        build_ch5, build_ch6, build_ch7, build_ch8,
        build_ch9, build_ch10, build_ch11, build_ch12,
        build_appendix,
    ]:
        story.extend(builder())
        story.append(PageBreak())

    doc.build(story, onFirstPage=on_cover, onLaterPages=on_page)
    print(f"PDF gerado: {OUTPUT}")

build()
