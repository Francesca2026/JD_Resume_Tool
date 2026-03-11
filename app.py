# 强制设置UTF-8编码，解决中文/全角字符问题
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

# 导入必备库
import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# 从Streamlit Secrets读取API密钥（加密存储，安全无泄露）
API_KEY = st.secrets["DEEPSEEK_API_KEY"]
BASE_URL = st.secrets["DEEPSEEK_BASE_URL"]

# 定义调用DeepSeek API的通用函数（核心逻辑，适配三大功能）
def call_deepseek(prompt, model="deepseek-chat", temperature=0.3):
    """
    调用DeepSeek API生成内容
    :param prompt: 给AI的指令（比如翻译JD、生成日常）
    :param model: 使用的模型（deepseek-chat足够，免费额度可用）
    :param temperature: 内容严谨度（0.3=精准，适合工作场景）
    :return: AI生成的结果
    """
    # 构造API请求参数
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json; charset=utf-8"  # 明确指定UTF-8编码
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    # 发送请求并获取结果（手动转UTF-8字节）
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            data=json.dumps(data).encode('utf-8')
        )
        response.raise_for_status()  # 捕获HTTP错误
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"调用失败：{str(e)}（检查API Key是否正确，或网络是否正常）"

# ---------------------- 网页界面搭建 ----------------------
st.set_page_config(page_title="JD&简历优化工具", page_icon="📝")
st.title("📝 JD翻译+岗位日常+简历优化工具")
st.subheader("个人自用 | 精准匹配岗位需求")

# 功能选项卡（分3个标签页，界面清晰）
tab1, tab2, tab3 = st.tabs(["🔍 JD翻译（大白话）", "🗓️ 岗位日常描述", "✨ 简历优化"])

# 功能1：JD翻译（优化后Prompt）
with tab1:
    st.subheader("输入JD原文，一键拆解核心信息")
    jd_input = st.text_area(
        label="粘贴JD完整内容（支持长文本）",
        height=300,
        placeholder="请粘贴完整的岗位描述原文..."
    )
    if st.button("开始分析", type="primary"):
        if not jd_input:
            st.warning("⚠️ 请先输入JD内容！")
        else:
            with st.spinner("正在分析中..."):
                translate_prompt = f"""你是一位资深求职顾问，擅长把专业JD翻译成大白话，帮助求职者快速理解岗位核心。请严格基于以下JD原文，**仅使用JD中存在的信息**，按固定顺序输出以下5个板块，不可遗漏、不可调换顺序：

【一句话看懂】
用一句不超过30字的大白话，精准总结该岗位的核心定位与价值。

【要你做的3件事】
提炼该岗位最核心的3项工作职责，每项用一句简洁描述，标号为 1) 2) 3)。若JD信息不足，标注【信息不足】。

【硬门槛 / 可培养 / 加分项】
将JD中的任职要求严格分为三类，每类用 bullet 列出：
- 硬门槛：必须具备的条件，不满足会直接被淘汰
- 可培养：入职后可通过学习掌握的能力/技能
- 加分项：有则更优，不具备不影响基础录用
若某类无对应信息，标注【信息不足】。

【黑话翻译 + 例子】
找出JD中的行业黑话、缩写、模糊表述（如“精细化运营”“用户增长”），逐条翻译为大白话，并附上实际工作场景的例子。若无黑话，标注【无行业黑话/缩写】。

【面试反问3个问题】
基于JD内容，提出3个有深度的面试反问问题（需指向岗位实际工作、团队协作或发展空间，避免泛泛问题）。若JD信息不足，标注【信息不足】。

禁忌规则：
1. 绝对禁止编造JD中不存在的信息
2. 禁止使用鸡汤、空话、套话
3. 若信息不足以判断某项，必须标注【信息不足】
4. 输出仅包含上述5个板块，无额外开场白或总结

JD原文：
{jd_input}"""
                result = call_deepseek(translate_prompt)
                st.subheader("✅ 分析结果")
                st.write(result)

# 功能2：岗位日常描述（优化后Prompt）
with tab2:
    st.subheader("基于JD，还原岗位真实工作场景")
    jd_daily_input = st.text_area(
        label="粘贴JD完整内容（可复用上面的JD）",
        height=300,
        placeholder="请粘贴完整的岗位描述原文..."
    )
    if st.button("生成日常", type="primary"):
        if not jd_daily_input:
            st.warning("⚠️ 请先输入JD内容！")
        else:
            with st.spinner("正在生成日常..."):
                daily_prompt = f"""你是一位资深职场顾问，擅长基于JD还原岗位真实工作场景。请严格基于以下JD原文，**合理推断并标注【推测】**，按固定顺序输出以下6个板块，不可遗漏、不可调换顺序：

【岗位定位】
用2-3句话，清晰描述该岗位在团队/公司中的角色定位、核心价值与汇报关系（基于JD推断，需标注【推测】）。

【一天时间表】
模拟一个典型工作日的时间安排（从上班到下班），格式严格为：
HH:MM → 具体工作内容 → 产出物/结果
需贴合岗位实际节奏，所有推断内容标注【推测】。

【一周节奏】
描述一周内不同工作日的工作侧重点（如周一：目标对齐；周三：项目评审；周五：数据复盘），基于JD推断，标注【推测】。

【高频任务清单】
按以下5个维度，列出该岗位的高频任务，每项需具体：
- 对齐类：与哪些角色对齐、对齐什么内容
- 分析类：分析什么数据/信息、分析目的
- 产出类：产出什么文档/方案/内容
- 推进类：推进什么项目/流程、推进目标
- 复盘类：复盘什么结果/数据、复盘结论
若某维度无对应信息，标注【信息不足】，所有推断标注【推测】。

【协作对象与配合方式】
列出该岗位日常需要配合的核心角色（如产品经理、运营、开发），并说明具体配合方式（如同步数据、评审方案、联调功能），基于JD推断，标注【推测】。

【一个月交付样例（5个）】
给出入职第一个月可能需要交付的5个具体成果物（如“完成XX竞品分析报告”“搭建XX数据监控表”），需贴合JD职责，基于JD推断，标注【推测】。

禁忌规则：
1. 绝对禁止编造JD中不存在的核心信息
2. 所有推断内容必须标注【推测】
3. 禁止使用鸡汤、空话、套话
4. 输出仅包含上述6个板块，无额外开场白或总结

JD原文：
{jd_daily_input}"""
                result = call_deepseek(daily_prompt)
                st.subheader("✅ 岗位日常")
                st.write(result)

# 功能3：简历优化（优化后Prompt）
with tab3:
    st.subheader("上传简历+JD，一键优化（高亮修改+附理由）")
    resume_input = st.text_area(
        label="粘贴个人简历完整内容",
        height=300,
        placeholder="请粘贴你的完整简历原文..."
    )
    jd_resume_input = st.text_area(
        label="粘贴目标岗位JD",
        height=300,
        placeholder="请粘贴目标岗位的JD原文..."
    )
    if st.button("优化简历", type="primary"):
        if not resume_input or not jd_resume_input:
            st.warning("⚠️ 请同时输入简历和JD！")
        else:
            with st.spinner("正在优化简历..."):
                resume_prompt = f"""你是一位专业简历优化顾问，擅长基于JD精准优化简历，突出匹配度，且绝对不编造经历。请严格基于以下**JD原文**和**用户简历原文**，按固定顺序输出以下两个部分，不可遗漏、不可调换顺序，且输出仅为纯文本，禁止使用任何Markdown格式（如*、**、#、- 等），仅保留{{替换}}和{{新增}}标记：

===最终可投递版本（含高亮标记）===
输出完整的、可直接复制投递的简历纯文本，保留原简历的基本结构（教育背景、工作经历、项目经历、技能等）。
所有改动必须用以下标记包裹：
- 替换内容：{{{{替换|原文内容|改动理由}}}}改动后的文字{{{{/replace}}}}
- 新增内容：{{{{新增|改动理由}}}}新增的文字{{{{/new}}}}
- 删除内容：不出现在此版本中，需在【改动汇总】中说明

标记规则：
1. 标记必须完整包裹改动后的文字
2. “原文内容”为改动前的原始文字
3. “改动理由”需简述：对齐JD中哪项要求，为什么这样改
4. 未改动的文字直接保留，无任何标记

===改动汇总===
逐条列出所有改动（包括删除），格式严格为：
1) 类型：替换/新增/删除 → 内容简述 → 对齐JD：对应JD中的具体要求 → 原因：为什么这样改 →【可填槽位】：若需用户补充具体经历，标注可替换的位置；若无需补充，标注【无】

禁忌规则：
1. 绝对禁止编造用户未提及的经历、技能、数据
2. 若用户简历信息不足以匹配JD某项要求，必须用【可填槽位】标注，引导用户补充
3. 仅可优化措辞、调整优先级，绝对禁止删除用户的真实经历
4. 输出仅包含上述两个部分，无额外开场白或总结
5. 禁止使用任何Markdown格式，仅保留{{替换}}和{{新增}}标记

JD原文：
{jd_resume_input}

用户简历原文：
{resume_input}"""
                result = call_deepseek(resume_prompt)
                st.subheader("✅ 优化后简历")
                st.write(result)