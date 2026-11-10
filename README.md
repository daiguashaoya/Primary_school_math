# Primary_school_math

一个持续更新的小学数学教学资料站：从试卷备课出发，逐步积累课堂章节、解题方法与复习资料。

## 网站入口

- 首页：[`index.html`](index.html)
- 备课资料：[`preparation/index.html`](preparation/index.html)
- 课堂章节：[`chapters/index.html`](chapters/index.html)
- 最新备课：[`第一阶段适应性活动：五上数学1109`](preparation/phase-one-1109/index.html)
- 试课备课：[`小数计算与图形应用`](preparation/trial-decimals/index.html)

当前已收录2份备课资料：试课试卷，以及第一阶段适应性活动1109的完整29题。两份均按“答案速查→逐题讲解”组织，包含考点、解题方法、易错点和图解。第一阶段资料可在线阅读并用网页打印按钮打印，原卷PDF单独保存在`试卷/`。课堂章节将按实际教学内容更新。

## 部署到 GitHub Pages

本站是已经生成好的静态网站，没有前端安装步骤。开启 Pages 后即可访问。

1. 打开仓库 **Settings → Pages**。
2. 在 **Build and deployment → Source** 中选择 **Deploy from a branch**。
3. Branch 选择 **main**，目录选择 **/(root)**，点击 **Save**。
4. 等待 GitHub 显示部署完成，使用 Pages 设置页面给出的地址访问。

在默认项目站配置下，预计地址为：

**https://daiguashaoya.github.io/Primary_school_math/**

此地址在 Pages 开启且首次部署成功后才可访问。后续推送到 `main` 会触发站点更新。参见 [GitHub 官方部署说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 本地预览

在仓库根目录运行：

```powershell
python -m http.server 8000
```

浏览器打开 <http://localhost:8000/>。按 `Ctrl+C` 停止服务。

## 修改资料与新增章节

资料内容与导航目录是分开的：

- **内容**：编辑对应的 Markdown 文件。
- **目录**：编辑 [`content/catalog.json`](content/catalog.json)，决定资料属于“备课资料”还是“课堂章节”。
- **生成**：运行下面的命令，刷新首页、栏目页和每篇资料的阅读页。

```powershell
python scripts/build_site.py
```

仅需要 Python 3.10 或以上版本，使用标准库，无需安装第三方包。生成的 HTML 应和源文件一起提交，这样 Pages 可以直接从 `main` 分支发布。

完整流程与新章节示例见 [内容维护指南](docs/内容维护指南.md)。

## 目录结构

```text
Primary_school_math/
├── index.html                  # 总导航首页（自动生成）
├── preparation/                # 备课栏目与阅读页（自动生成）
├── chapters/                   # 课堂章节栏目与阅读页（自动生成）
├── assets/                     # 公共样式、交互与 SVG 插图
├── content/
│   ├── catalog.json            # 统一内容目录
│   └── 章节模板.md             # 新内容起稿参考
├── 备课资料/                    # 现有 Markdown、原卷、PDF 和图解
├── 试卷/                        # 保留的原始试卷
├── scripts/build_site.py        # 站点生成脚本
└── docs/内容维护指南.md
```

`_核对过程/` 和 `.local/` 是本地中间文件目录，已加入 `.gitignore`，不上传。

## 阅读说明

- 支持手机与电脑阅读，资料页包含目录跳转和打印样式。
- 备课栏目支持按考点筛选、按关键词搜索；禁用 JavaScript 时仍可阅读所有内容。
- 网站使用相对路径，兼容 GitHub Pages 项目站的 `/Primary_school_math/` 子路径。
- Markdown 是网页内容的维护来源；原有 HTML 与 PDF 是独立文件，更新网页不会自动重制 PDF。
