# 博客系统自动化测试（Playwright）

针对测试环境 `http://127.0.0.1:9090` 的 Playwright 自动化测试，目前覆盖四个页面，
共 **150 条**用例，全部通过。

| 页面 | 用例数 | 脚本 | 一键执行 | 测试用例 | 测试报告 |
|---|---|---|---|---|---|
| 登录页 `blog_login.html` | 40 | `tests/blog_login.spec.ts` | `run-tests.cmd` | [Excel](博客登录页_测试用例.xlsx) | [Word](博客登录页_测试报告.docx) |
| 列表页 `blog_list.html` | 34 | `tests/blog_list.spec.ts` | `run-tests-list.cmd` | [Excel](博客列表页_测试用例.xlsx) | [Word](博客列表页_测试报告.docx) |
| 编辑页 `blog_edit.html` | 38 | `tests/blog_edit.spec.ts` | `run-tests-edit.cmd` | [Excel](博客编辑页_测试用例.xlsx) | [Word](博客编辑页_测试报告.docx) |
| 详情页 `blog_detail.html` | 38 | `tests/blog_detail.spec.ts` | `run-tests-detail.cmd` | [Excel](博客详情页_测试用例.xlsx) | [Word](博客详情页_测试报告.docx) |

> ⚠️ **写操作警告**：
> - 编辑页的发布会真实写入数据库，所有发布用例均拦截 `/blog/add`，不产生数据。
> - 详情页有**删除**操作，破坏性用例只针对**自建测试博客**（标题含 `__E2E_DETAIL__`），
>   并保证在 `finally` 中清理，测试后环境仅剩原有博客。已验证无残留。

## 目录结构

```
playwright.config.ts          配置（baseURL、报告器、login/list/edit/detail 四个 project）
pages/LoginPage.ts            登录页 Page Object
pages/ListPage.ts             列表页 Page Object
pages/EditPage.ts             编辑页 Page Object（封装 editor.md 交互）
pages/DetailPage.ts           详情页 Page Object（含测试数据创建/清理助手）
tests/blog_login.spec.ts      登录页 40 条用例
tests/blog_list.spec.ts       列表页 34 条用例
tests/blog_edit.spec.ts       编辑页 38 条用例
tests/blog_detail.spec.ts     详情页 38 条用例
run-tests*.cmd                四个页面的一键执行脚本
build_*.py                    文档生成脚本（Excel / Word）
blog_*_test_plan.md           四个页面的测试规划
summarize-findings.js         从 JSON 报告提取实测结论
```

## 环境准备

```powershell
# 1. 依赖（使用工作区内 npm 缓存）
npm install --cache .\.npm-cache

# 2. 浏览器缓存目录（关键，否则报 Executable doesn't exist）
$env:PLAYWRIGHT_BROWSERS_PATH = "C:\Users\XDTLXL\AppData\Local\ms-playwright"
```

Playwright 固定为 **1.63.0**，与本地已缓存的 Chromium 1243 精确匹配，无需重新下载浏览器。

## 运行

### 一键脚本（推荐，无需配置）

```cmd
run-tests.cmd            登录页用例
run-tests-list.cmd       列表页用例
run-tests-edit.cmd       编辑页用例
run-tests-detail.cmd     详情页用例
```

四个脚本都会自动探测浏览器目录、检查被测环境、首次运行自动装依赖，
并以正确退出码结束（通过=0，失败=1）。

透传参数给 Playwright：

```cmd
run-tests-detail.cmd --headed          有头模式
run-tests-detail.cmd --ui              交互式 UI，可单条点选
run-tests-detail.cmd -g "F3"           只跑 F3 用例
run-tests-detail.cmd --repeat-each=4   重复 4 轮查不稳定用例
```

### 命令行手动执行

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "C:\Users\XDTLXL\AppData\Local\ms-playwright"

npx playwright test                      # 全部 150 条
npx playwright test --project=login      # 只跑登录页
npx playwright test --project=list       # 只跑列表页
npx playwright test --project=edit       # 只跑编辑页
npx playwright test --project=detail     # 只跑详情页
npx playwright test -g "F3"              # 按用例编号筛选
npm run show-report                      # 打开 HTML 报告
```

## 可覆盖的环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `BASE_URL` | `http://127.0.0.1:9090` | 被测地址前缀 |
| `LOGIN_USERNAME` | `zhangsan` | 有效测试账号 |
| `LOGIN_PASSWORD` | `123456` | 有效测试密码 |
| `PLAYWRIGHT_BROWSERS_PATH` | 系统默认 | 浏览器缓存目录 |

## 各页面关键机制（实测确认）

### 通用
1. **鉴权请求头是 `user_token_header`**，由 `common.js` 的 `$(document).ajaxSend` 自动注入；
   头名写成 `user_token` 会返回 401。用 `fetch` 直接调用接口不会触发该注入，需手动带头。
2. **接口失败也返回 HTTP 200**，判定必须看响应体 `code` / `data`，不能看状态码。

### 登录页
3. 登录成功会立即 `location.href` 跳转，跳转后响应体任何时机都读不到 ——
   需用 `page.route` 在路由层取回 JSON，并等 `fulfill` 完成后再解除拦截。
4. 失败提示是同步 `alert()`，必须先注册 dialog 监听再点击提交。

### 列表页
5. `GET /blog/getList` 返回 401 时前端 `error` 回调跳转登录页 —— 这是列表页的守卫实现。
6. 列表用字符串拼接 + `html()` 渲染，`title`/`content`/`createTime` 均未转义。

### 编辑页
7. 编辑器为 editor.md（内部 CodeMirror），`textarea#content` 是 `display:none` 的。
   **真实键盘输入会自动同步**；但程序化 `cm.setValue()` 不会，**必须再调用 `cm.save()`**，
   否则 `submit()` 读到旧值，会误判为缺陷。
8. 中文编码正常。Node 环境打印 `postData()` 可能出现乱码，那是**观察工具的显示问题**，
   应使用 `postDataBuffer().toString('utf8')` 核验，不要据此判缺陷。

### 详情页
9. **详情页有登录守卫**（与列表页一致，未登录会 401 跳转）；但**编辑页没有** —— 同一系统守卫不一致。
10. `loginUser` 字段决定是否渲染"编辑/删除"按钮，但该字段在列表接口与详情接口取值矛盾
    （列表 false / 详情 true）。
11. `editormd.markdownToHTML("detail", ...)` 会替换 `#detail` 内容，生成的 `.markdown-body`
    容器**不在** `.content .detail` 内部，写选择器时要注意。
12. `.container` 为固定宽度 800px，窄屏（≤768px）会出现横向滚动条，三页共用该样式。
13. 设计测试时**先创建带标记的测试博客**（标题含 `__E2E_DETAIL__`），破坏性操作只针对它，
    并在 `finally` 中清理，避免污染环境。

## 已发现缺陷汇总（共 28 个）

**登录页（6 个）**：`blog_edit.html` 缺登录守卫（高）、用户枚举（中）、无暴力破解防护（中）、
AJAX 静默失败、回车不可提交、文案不规范（低）。

**列表页（7 个）**：存储型 XSS（高）、`getUserInfo` 泄露密码哈希（高）、
计数硬编码不一致（中）、FAIL/500 静默无提示（中）、不支持分页（中）、
空态无占位文案（低）、头像硬编码（低）。

**编辑页（8 个）**：编辑页缺登录守卫（高）、校验失败弹空白提示（中）、
无防重复提交（中）、默认占位文本被发布（中）、写接口 500 静默失败（中）、
标题无长度与必填约束（低）、无未保存提醒（低）、无提交中状态（低）。

**详情页（7 个）**：`getAuthorInfo` 泄露密码哈希（高）、`loginUser` 字段矛盾（中）、
更新/删除不存在的 id 误报成功（中）、无效 blogId 错误不可诊断（中）、
计数硬编码（低）、重复陈旧代码（低）、窄屏横向溢出（低）。

### 待确认的高风险项

**跨用户越权**：环境无注册接口，无法创建第二个用户，未能实证"用户 A 能否改删用户 B 的博客"。
但已确认更新/删除接口对不存在的 id 也返回成功（BUG-D03），归属校验很可能缺失。
建议后端补充 `blog.userId` 校验，并提供第二个测试账号以便覆盖多用户权限场景。

详见各页面的测试报告与 Excel 用例表中对应的缺陷清单工作表。

## 测试执行注意事项

1. **不要并发跑多个 Playwright 进程**：共享测试环境不支持并发压测，
   同时运行两个进程会出现偶发超时。请串行执行。
2. **用例串行执行**（`workers: 1`）：登录会写 `localStorage` 并触发跳转，并行会互相干扰。
3. **`-g` 与文件路径冲突**：`playwright test <file> -g "X"` 会把 X 当成文件路径；
   本仓库使用 `--project=login|list|edit` 限定范围，使 `-g` 保持自由。
