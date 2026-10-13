# -*- coding: utf-8 -*-
"""生成《博客编辑页测试报告》Word 文档

用例数据从 build_edit_xlsx.py 导入，保证 Word 与 Excel 统计口径一致。
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from build_edit_xlsx import CASES

OUT = r"D:\study\AI\deepseek-day\博客编辑页_测试报告.docx"
EA = "微软雅黑"
doc = Document()

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), EA)
for sec in doc.sections:
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.4)


def set_ea(run, name=EA):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def para(text, size=10.5, bold=False, align=None, space_after=6, color=None, style_name=None):
    p = doc.add_paragraph(style=style_name)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    set_ea(r)
    if color:
        r.font.color.rgb = RGBColor(*color)
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def heading(text, level):
    h = doc.add_heading(level=level)
    r = h.add_run(text)
    set_ea(r)
    if level == 1:
        r.font.size = Pt(15)
        r.font.color.rgb = RGBColor(0x1F, 0x3B, 0x73)
    elif level == 2:
        r.font.size = Pt(12.5)
        r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
    return h


def make_table(headers, rows, widths=None, header_bg="2F5597"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_ea(r)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), header_bg)
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(v))
            r.font.size = Pt(9.5)
            set_ea(r)
            p.paragraph_format.space_after = Pt(2)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    return t


# ==================== 封面 ====================
para("博客系统 编辑页测试报告", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para("Blog Edit Page Test Report", size=11, align=WD_ALIGN_PARAGRAPH.CENTER,
     space_after=18, color=(0x60, 0x60, 0x60))

make_table(
    ["项目", "内容"],
    [
        ("被测系统", "博客系统（我的博客系统）"),
        ("被测页面", "http://127.0.0.1:9090/blog_edit.html"),
        ("页面标题", "博客编辑页"),
        ("核心功能", "填写标题 + editor.md（Markdown）编辑器写正文，点击\"发布文章\"提交"),
        ("写入接口", "POST /blog/add（application/json，需请求头 user_token_header）"),
        ("测试类型", "功能测试、安全测试、健壮性测试、兼容性测试、性能测试"),
        ("测试方式", "Playwright 自动化（Chromium，串行执行）"),
        ("测试工具", "Playwright 1.63.0 + TypeScript"),
        ("测试账号", "zhangsan / 123456"),
        ("测试时间", "2026-10-13"),
        ("报告版本", "V1.0"),
    ],
    widths=[4.0, 12.0],
)
doc.add_paragraph()

# ==================== 一、测试结论 ====================
heading("一、测试结论", 1)
para("本次针对博客编辑页共设计 38 条测试用例（124 个测试步骤），覆盖页面结构、访问控制、"
     "标题输入域、编辑器内容、发布流程、校验反馈、重复提交、安全与交互兼容九个方面。")
para("自动化断言层面 38 次执行全部通过，并经过 5 轮重复执行验证稳定性"
     "（190 次执行零失败、零不稳定）。发布主流程功能正确，请求契约与编码正常，"
     "接口层鉴权有效。")
para("测试过程中确认了 8 个缺陷，其中 1 个为高危：编辑页缺少登录守卫，"
     "未登录用户可直接打开写博客页面。此外还有 4 个中危缺陷，集中在错误反馈缺失、"
     "重复提交与默认内容误发布。", space_after=10)

para("核心结论：", bold=True, space_after=4)
for line in [
    "① 功能层面：标题与正文可正常输入，发布请求契约正确（POST + JSON + 鉴权头），"
    "中文以 UTF-8 正确提交，成功响应能正确跳转列表页。",
    "② 安全层面：存在 1 个高危缺陷（BUG-E01 守卫缺失）；接口层鉴权有效，"
    "未授权写入返回 401 且不落库；标题与编辑器内容中的脚本未被执行。",
    "③ 校验反馈：前后端均无可读错误信息，校验失败弹出空白对话框"
    "（BUG-E02），是本次最影响用户体验的缺陷。",
    "④ 健壮性：无防重复提交机制（连点产生重复文章）、写接口 500 时静默失败。",
    "⑤ 内容质量风险：编辑器默认占位文本会被当作正文发布（BUG-E04）。",
]:
    p = doc.add_paragraph(line)
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
        set_ea(r)

# ==================== 二、测试环境与方法 ====================
heading("二、测试环境与方法", 1)
make_table(
    ["类别", "项目", "说明"],
    [
        ("被测环境", "服务地址", "http://127.0.0.1:9090"),
        ("被测环境", "编辑页", "/blog_edit.html"),
        ("被测环境", "编辑器", "editor.md（内部为 CodeMirror，工具栏 37 个按钮）"),
        ("运行环境", "操作系统", "Windows"),
        ("运行环境", "浏览器内核", "Chromium 1243（headless）"),
        ("运行环境", "自动化框架", "Playwright 1.63.0 + TypeScript"),
        ("测试数据", "有效账号", "zhangsan / 123456"),
        ("测试数据", "构造输入", "空值、超长（500 字标题 / 300 段正文）、特殊字符、"
                                  "HTML 与脚本载荷、中文标点、前后空格"),
    ],
    widths=[3.0, 3.5, 9.5],
)
doc.add_paragraph()

heading("2.1 写操作页面的测试约束", 2)
para("本页是写操作页面，每次成功发布都会真实写入数据库。为在不污染环境的前提下完成测试，"
     "本次采用如下策略：", space_after=6)
for line in [
    "所有发布用例均使用 Playwright 的 page.route 拦截 /blog/add，只验证「前端发出的载荷」"
    "与「前端对响应/异常的处理」，不产生任何真实数据。",
    "通过拦截不同响应（SUCCESS+data:true、SUCCESS+data:false、data:null、HTTP 500）"
    "覆盖成功与各类失败分支。",
    "测试前后调用 /blog/getList 比对博客条数：实测均为 1 条（与测试前基线完全一致），"
    "确认数据库未被污染。",
]:
    p = doc.add_paragraph(line, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
        set_ea(r)

heading("2.2 编辑器内容同步机制（重要发现）", 2)
para("编辑器的可见输入区由 editor.md 的 CodeMirror 承担，而提交时读取的是被隐藏的 "
     "textarea#content。实测两者同步行为如下：", space_after=6)
make_table(
    ["输入方式", "CodeMirror", "#content", "是否同步", "提交内容是否正确"],
    [
        ("真实键盘输入", "更新", "同步", "是", "是（功能正常）"),
        ("程序化 cm.setValue()", "更新", "不同步", "否", "否（提交到旧值）"),
        ("cm.setValue() + cm.save()", "更新", "同步", "是", "是"),
    ],
    widths=[4.2, 2.4, 2.2, 2.0, 3.2],
)
doc.add_paragraph()
para("结论：真实用户通过键盘输入时功能正常，因此「提交内容为默认文本」并**不是**同步缺陷。"
     "本次测试中 BUG-E04 记录的是另一个真实问题：用户只填标题、未触碰编辑器时，"
     "默认占位文本会被当作正文提交。自动化脚本中设置内容必须调用 cm.save()，"
     "否则会误判为缺陷（本报告已按正确方式实现）。", space_after=8)

# ==================== 三、执行统计 ====================
heading("三、测试执行统计", 1)

heading("3.1 总体统计", 2)
defect_cases = [c[0] for c in CASES if c[8].startswith("发现缺陷")]
make_table(
    ["统计项", "数值", "说明"],
    [
        ("用例条数", str(len(CASES)), "Excel 用例文档中的用例条数"),
        ("测试步骤数", str(sum(len(c[7]) for c in CASES)), "每条用例按步骤逐行展开"),
        ("自动化执行次数", str(len(CASES)), "1 条用例 = 1 次执行"),
        ("执行通过", str(len(CASES)), "断言层面全部通过"),
        ("执行失败", "0", "无断言失败"),
        ("通过率", "100%", f"{len(CASES)} / {len(CASES)}"),
        ("稳定性验证", "190 次通过", f"{len(CASES)} 条 × 重复 5 轮，零失败、零不稳定"),
        ("发现缺陷", "8", "1 高 / 4 中 / 3 低"),
        ("结论为\"发现缺陷\"的用例", str(len(defect_cases)), "、".join(defect_cases)),
        ("数据库污染", "无", "测试前后博客条数均为 1 条"),
    ],
    widths=[5.0, 2.5, 8.5],
)
doc.add_paragraph()

heading("3.2 模块分布", 2)
MODULE_ORDER = ["A 页面结构与加载", "B 访问控制", "C 标题输入域", "D 编辑器内容",
                "E 发布流程", "F 校验与错误反馈", "G 重复提交", "H 安全", "I 交互与兼容"]
_mod_rows = []
for _m in MODULE_ORDER:
    _sub = [c for c in CASES if c[1] == _m]
    _mod_rows.append((_m, str(len(_sub)), str(sum(len(c[7]) for c in _sub)),
                      str(len(_sub)), "0", "100%"))
_mod_rows.append(("合计", str(len(CASES)), str(sum(len(c[7]) for c in CASES)),
                  str(len(CASES)), "0", "100%"))
make_table(
    ["模块", "用例数", "步骤数", "通过", "失败", "通过率"],
    _mod_rows,
    widths=[4.2, 2.0, 2.0, 1.8, 1.8, 2.0],
)
doc.add_paragraph()

heading("3.3 缺陷严重级别分布", 2)
make_table(
    ["严重级别", "数量", "占比", "缺陷编号"],
    [
        ("高", "1", "12.5%", "BUG-E01"),
        ("中", "4", "50.0%", "BUG-E02、BUG-E03、BUG-E04、BUG-E05"),
        ("低", "3", "37.5%", "BUG-E06、BUG-E07、BUG-E08"),
        ("合计", "8", "100%", "—"),
    ],
    widths=[3.0, 2.0, 2.5, 8.5],
)
doc.add_paragraph()

# ==================== 四、缺陷明细 ====================
heading("四、缺陷明细", 1)

DEFECTS = [
    dict(no="BUG-E01", sev="高", cat="安全", title="编辑页缺少登录守卫，未登录可打开写页面",
         desc="blog_edit.html 加载时不校验登录态，也不发起任何鉴权请求，未登录用户可"
              "直接打开写博客页面并填写内容（仅在点击发布时才会因 401 被拒）。",
         steps="1）清空 localStorage 登录态；\n2）直接访问 http://127.0.0.1:9090/blog_edit.html；\n"
               "3）观察页面是否打开、加载期间是否发起鉴权请求。",
         actual="页面直接正常打开，编辑器完全可用；加载期间未发起任何 /user/ 或 /blog/ 请求。",
         impact="未授权用户可进入写操作页面，与同一系统 blog_list.html 的守卫行为不一致；"
                "与登录页测试发现的 BUG-01 为同一根因，属越权访问风险。",
         fix="在页面加载时校验 localStorage 中的 token，无效则跳转登录页；"
             "或由后端在渲染页面时做服务端鉴权。",
         ref="B1"),
    dict(no="BUG-E02", sev="中", cat="可用性", title="校验失败返回空 errMsg，前端弹出空白提示",
         desc="/blog/add 对非法输入统一返回 code=SUCCESS、data=false 且 errMsg 为空字符串；"
              "前端在失败分支执行 alert(result.errMsg)，因此弹出空白对话框。"
              "页面源码注释亦自认此问题：\"后端未对错误情况进行分析, 统一返回了false\"。",
         steps="1）登录后打开编辑页；\n2）标题留空、内容填写任意文本；\n"
               "3）点击\"发布文章\"并监听弹窗。",
         actual="弹出对话框但内容为空字符串；标题空、内容空、两者皆空、超长标题四种情况表现一致。",
         impact="用户完全无法得知失败原因（是标题为空、内容为空还是超限），只能反复尝试，"
                "是本次最影响可用性的缺陷，且前后端都没有兜底校验。",
         fix="后端为各类校验失败返回明确 errMsg（如\"标题不能为空\"）；"
             "前端增加必填与长度校验并给出内联提示。",
         ref="F1、F2、F3、F5"),
    dict(no="BUG-E03", sev="中", cat="健壮性", title="无防重复提交机制，连点产生重复文章",
         desc="发布按钮在提交过程中未禁用、无 loading 状态，用户可重复点击，"
              "每次点击都会真实发出一次 /blog/add 写入请求。",
         steps="1）登录后打开编辑页并填写标题与内容；\n2）快速连续点击\"发布文章\"3 次；\n"
               "3）统计实际发出的请求数。",
         actual="实际发出 3 次 /blog/add 请求。由于发布是写操作，会产生 3 篇内容相同的文章。",
         impact="网络较慢时用户容易重复点击，导致数据库出现重复文章；"
                "系统未提供文章删除入口时难以清理。",
         fix="提交期间禁用按钮并显示\"发布中…\"；前端增加请求中的互斥标记。",
         ref="G1、G2、G3"),
    dict(no="BUG-E04", sev="中", cat="功能", title="编辑器默认占位文本会被当作正文发布",
         desc="编辑器初始内容为 \"##在这里写下一篇博客\"，该文本位于真实的 textarea 中。"
              "若用户只填写标题而未修改正文，提交时会把这段占位文本一并发布。",
         steps="1）登录后打开编辑页；\n2）只填写标题，不修改编辑器内容；\n"
               "3）点击\"发布文章\"并拦截请求，检查 content 字段。",
         actual="提交载荷为 {\"title\":\"只填标题不写正文\",\"content\":\"##在这里写下一篇博客\"}。",
         impact="用户不写正文时会产生一篇正文为占位提示文字的文章，污染内容质量，"
                "且用户通常不会察觉。",
         fix="将占位提示改为 placeholder，或让编辑器初始内容为空字符串；"
             "提交前校验正文是否为空并给出提示。",
         ref="D3"),
    dict(no="BUG-E05", sev="中", cat="健壮性", title="写接口 500 时静默失败，用户无感知",
         desc="submit() 的 error 回调只处理 status==401 的情况，其余错误（如 500）"
              "被完全忽略，既不弹窗也不提示。",
         steps="1）登录后打开编辑页并拦截 /blog/add 返回 HTTP 500；\n"
               "2）填写标题与内容并点击发布；\n3）观察页面反馈。",
         actual="无任何弹窗或提示，页面停留在编辑页，用户无法判断是否发布成功。",
         impact="用户可能反复点击发布，既无法得知失败原因，也无法确认内容是否已保存；"
                "与列表页 BUG-L04 为同类问题，说明错误处理缺失是系统性现象。",
         fix="error 回调中为非 401 的情况补充统一错误提示（如\"发布失败，请稍后重试\"）。",
         ref="F4"),
    dict(no="BUG-E06", sev="低", cat="可用性", title="标题输入框无长度限制与必填约束",
         desc="标题输入框未设置 maxlength、required，也没有 placeholder，前端零校验。",
         steps="1）检查 #title 的 maxlength、required、placeholder 属性；\n"
               "2）尝试输入 500 个字符。",
         actual="maxlength=null、required=false、placeholder=null；可输入 500 字符且不被截断。",
         impact="超长标题可提交，可能影响数据库字段长度与列表页展示；"
                "缺少必填约束使空值校验完全依赖后端，而后端又不返回可读错误。",
         fix="为标题设置合理的 maxlength 与必填校验，并补充 placeholder 提示。",
         ref="C1、C2"),
    dict(no="BUG-E07", sev="低", cat="可用性", title="有未保存内容时离开页面无任何提醒",
         desc="页面未注册 beforeunload 或点击拦截，填写内容后直接点击导航链接会丢失内容。",
         steps="1）填写标题与正文；\n2）点击导航栏\"主页\"；\n3）观察是否有未保存提醒。",
         actual="无任何提醒，直接跳转到 blog_list.html，已填写内容全部丢失。",
         impact="用户误点导航会丢失全部写作内容，在长文写作场景下影响较大。",
         fix="注册 beforeunload 事件，内容非空且未提交时提示用户确认离开。",
         ref="I3"),
    dict(no="BUG-E08", sev="低", cat="可用性", title="提交过程中缺少按钮禁用与状态反馈",
         desc="发布过程中按钮保持可用且文案始终为\"发布文章\"，用户无法感知请求正在进行。",
         steps="1）拦截 /blog/add 并延迟响应；\n"
               "2）在请求进行中读取按钮的禁用状态与文案。",
         actual="请求进行中按钮未禁用（isDisabled=false），文案仍为\"发布文章\"。",
         impact="用户无法判断是否已提交，容易重复点击，与 BUG-E03 互为因果。",
         fix="提交期间禁用按钮并将文案改为\"发布中…\"，请求结束后恢复。",
         ref="G2、G3"),
]

SEV_COLOR = {"高": (0xC0, 0x00, 0x00), "中": (0xBF, 0x60, 0x00), "低": (0x40, 0x40, 0x40)}
for i, d in enumerate(DEFECTS, start=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{i}. [{d['no']}] {d['title']}")
    r.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = RGBColor(*SEV_COLOR[d["sev"]])
    set_ea(r)
    make_table(
        ["字段", "内容"],
        [
            ("严重级别", d["sev"]),
            ("缺陷类别", d["cat"]),
            ("缺陷描述", d["desc"]),
            ("复现步骤", d["steps"]),
            ("实际结果", d["actual"]),
            ("影响", d["impact"]),
            ("修复建议", d["fix"]),
            ("关联用例", d["ref"]),
            ("状态", "待修复"),
        ],
        widths=[2.8, 13.2],
    )
    doc.add_paragraph()

doc.add_page_break()

# ==================== 五、测试范围 ====================
heading("五、测试范围与用例执行情况", 1)
para("下表汇总各模块用例的执行情况；完整用例（含前置条件、测试数据、逐步操作、"
     "预期结果与实际结果）详见配套 Excel 文档《博客编辑页_测试用例.xlsx》。", space_after=8)
make_table(
    ["模块", "用例编号", "用例数", "覆盖内容", "执行情况"],
    [
        ("A 页面结构与加载", "A1-A3", "3", "页面元素、editor.md 初始化与预览、编辑器尺寸", "全部通过"),
        ("B 访问控制", "B1-B3", "3", "未登录访问、未登录发布 401、无 token 写入", "确认 1 个高危缺陷"),
        ("C 标题输入域", "C1-C5", "5", "属性约束、超长、特殊字符、空格、清空重输", "确认 1 个缺陷"),
        ("D 编辑器内容", "D1-D5", "5", "默认内容、输入同步、默认文本发布、预览渲染、大内容", "确认 1 个缺陷"),
        ("E 发布流程", "E1-E5", "5", "请求契约、请求体、成功跳转、UTF-8 编码、响应容错", "全部通过"),
        ("F 校验与错误反馈", "F1-F5", "5", "空标题/空内容/全空、接口 500、前后端校验分工", "确认 2 个缺陷"),
        ("G 重复提交", "G1-G3", "3", "连点 3 次、按钮禁用态、按钮文案", "确认 2 个缺陷"),
        ("H 安全", "H1-H4", "4", "标题注入、编辑器注入、超长提交、未授权写入", "全部通过（防护有效）"),
        ("I 交互与兼容", "I1-I5", "5", "导航跳转、注销、未保存提醒、多分辨率、静态资源", "确认 1 个缺陷"),
    ],
    widths=[3.0, 2.2, 1.6, 6.2, 3.0],
)
doc.add_paragraph()

heading("5.1 已验证正常的关键项", 2)
for line in [
    "发布请求契约正确：方法为 POST，Content-Type 为 application/json，"
    "自动携带 user_token_header 鉴权头，请求体仅含 title 与 content 两个字段且取值与页面一致。",
    "中文编码正常：标题与含中文标点的正文以 UTF-8 正确提交，无乱码"
    "（已用 postDataBuffer 按 UTF-8 解码核验，排除了 Node 环境显示乱码的干扰）。",
    "成功流程正确：响应 code=SUCCESS 且 data=true 时正确跳转 blog_list.html；"
    "data 为 null 时不跳转，判定逻辑严谨。",
    "接口层鉴权有效：未登录点击发布会因 401 跳转登录页；无 token 调用 /blog/add 返回 401 "
    "且数据未落库（博客条数前后一致）。",
    "注入防护有效：标题输入框中的 HTML/脚本载荷不被解析（无子元素、无弹窗）；"
    "编辑器内容中的脚本在预览区未被执行。",
    "编辑器内容同步正常：真实键盘输入时 CodeMirror 与隐藏 textarea 完全同步，"
    "submit 能取到用户实际输入的内容。",
    "Markdown 预览正常：输入 # 标题与 **加粗** 语法后，预览区生成真实的 h1 等元素。",
    "注销与导航正常：注销清除 token 并跳转登录页；导航\"主页\"正确跳转列表页。",
    "静态资源正常：本次运行未出现 4xx/5xx 资源。",
]:
    p = doc.add_paragraph(line, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
        set_ea(r)

heading("5.2 测试限制", 2)
para("① 为避免污染数据库，所有发布用例均拦截 /blog/add，未验证「真实写入后数据是否正确落库"
     "（字段截断、时间戳、用户归属等）」。该项需在允许写数据的独立环境中补充。", space_after=3)
para("② 未测试文章长度上限与后端字段长度约束的真实边界（仅验证前端不截断、接口不返回 5xx）。", space_after=3)
para("③ 未测试编辑器工具栏各按钮的功能正确性（工具栏共 37 个按钮），"
     "仅验证了编辑器初始化与 Markdown 渲染。", space_after=3)
para("④ 未测试图片上传等依赖后端存储的功能。", space_after=8)

# ==================== 六、风险评估与建议 ====================
heading("六、风险评估与建议", 1)
para("BUG-E01（守卫缺失）与登录页测试发现的 BUG-01 为同一根因，说明系统的访问控制"
     "只在 blog_list.html 一处实现，未做统一处理。结合列表页的高危 XSS（BUG-L01），"
     "攻击者可未登录进入写页面、发布含脚本的文章，形成完整的攻击链。"
     "建议按以下优先级修复。", space_after=8)
make_table(
    ["优先级", "建议项", "对应缺陷"],
    [
        ("立即修复", "为 blog_edit.html 增加登录守卫（与 blog_list.html 一致），"
                     "并统一封装鉴权逻辑避免遗漏", "BUG-E01"),
        ("立即修复", "后端为各类校验失败返回明确 errMsg；前端补充必填与长度校验，"
                     "消除空白提示", "BUG-E02"),
        ("建议修复", "提交期间禁用发布按钮并显示\"发布中…\"，防止重复文章", "BUG-E03、BUG-E08"),
        ("建议修复", "编辑器初始内容置空或改用 placeholder，避免占位文本被发布", "BUG-E04"),
        ("建议修复", "error 回调补充非 401 的失败提示", "BUG-E05"),
        ("建议修复", "标题增加 maxlength 与必填约束", "BUG-E06"),
        ("可选优化", "注册 beforeunload，未保存内容离开时提醒", "BUG-E07"),
    ],
    widths=[2.6, 10.4, 3.0],
)
doc.add_paragraph()

# ==================== 七、附录 ====================
heading("七、附录：测试资产", 1)
make_table(
    ["资产", "路径", "说明"],
    [
        ("测试用例文档", "博客编辑页_测试用例.xlsx",
         "38 条用例 / 124 步，含用例说明、用例明细、模块划分、缺陷清单、执行统计 5 个工作表"),
        ("测试报告", "博客编辑页_测试报告.docx", "本报告"),
        ("测试规划", "blog_edit_test_plan.md", "测试点、模块与用例规划"),
        ("用例脚本", "tests/blog_edit.spec.ts", "Playwright 用例实现，38 条用例"),
        ("页面对象", "pages/EditPage.ts", "编辑页 Page Object（封装 editor.md 交互）"),
        ("一键执行", "run-tests-edit.cmd", "免配置执行脚本，自动探测浏览器目录"),
        ("HTML 报告", "playwright-report/index.html", "含失败截图与 trace 回放"),
    ],
    widths=[3.0, 5.4, 7.6],
)
doc.add_paragraph()

para("说明：本报告数据来源为 2026-10-13 的自动化执行结果（Playwright，38 条用例全部通过，"
     "并完成 5 轮 190 次重复稳定性验证）。所有缺陷结论均经实际运行验证，非基于代码静态推断。"
     "测试全程未向数据库写入数据。",
     size=9.5, color=(0x60, 0x60, 0x60))

doc.save(OUT)
print("已生成:", OUT)
print("段落数:", len(doc.paragraphs), "表格数:", len(doc.tables))
