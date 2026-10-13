# 博客编辑页 测试规划（blog_edit.html）

- 被测页面：http://127.0.0.1:9090/blog_edit.html
- 页面标题：博客编辑页
- 核心功能：填写标题 + 使用 editor.md（Markdown）编辑器写正文，点击"发布文章"提交
- 写入接口：`POST /blog/add`（**会真实写入数据库**，测试时须拦截）

> ⚠️ 测试风险提示：本页是**写操作页面**。测试全程通过 `page.route` 拦截 `/blog/add`，
> 只验证「前端发出的载荷」与「前端对响应的处理」，不向数据库写入任何数据，
> 每轮测试前后比对博客条数以证明未污染环境。

## 一、页面结构与功能盘点

| 区域 | 元素 | 关键属性 | 说明 |
|---|---|---|---|
| 导航栏 | logo + 主页 + 写博客 + 注销 | `a[onclick="logout()"]` | 与列表页一致 |
| 发布区 | `input#title` + `input#submit` | `#submit` 为 `type=button`，`value=发布文章` | 标题输入框无 name/placeholder/maxlength |
| 编辑器 | `div#editor` + `textarea#content` | `#content` 被 `display:none` 隐藏 | 由 editor.md 接管，内含 CodeMirror |
| 预览区 | `.editormd-preview` | — | 实时渲染 Markdown |

页面脚本行为（实测确认）：

1. 用 `editormd("editor", {width, height:550px, path})` 初始化编辑器。
2. `submit()` 以 `contentType: application/json` POST `/blog/add`，
   请求体 `{title: $("#title").val(), content: $("#content").val()}`。
3. 成功条件为 `result.code == "SUCCESS" && result.data == true` → 跳转 `blog_list.html`。
4. 否则 `alert(result.errMsg)`。
5. `error` 回调仅处理 `status == 401` → 跳转登录页。

## 二、编辑器交互机制（关键，实测确认）

`#content` 这个 textarea 是 `display:none` 的，实际输入框是 editor.md 内部的 CodeMirror。

| 输入方式 | CodeMirror | `#content` | 是否同步 | 提交是否带对内容 |
|---|---|---|---|---|
| **真实键盘输入** | ✅ 更新 | ✅ 同步 | **是** | **是（正常）** |
| 程序化 `cm.setValue()` | ✅ 更新 | ❌ 不同步 | 否 | 否（submit 读到旧值） |
| `cm.setValue()` + `cm.save()` | ✅ 更新 | ✅ 同步 | 是 | 是 |

> **重要结论**：真实用户通过键盘输入时 textarea 会正常同步，`submit()` 能取到正确内容，
> **功能正常，不是缺陷**。脚本中若用程序化方式设置内容，必须调用 `cm.save()`，
> 否则会误判为缺陷（这是自动化测试的陷阱，已在 Page Object 中封装处理）。

## 三、接口契约（实测）

| 场景 | 请求 | 响应 |
|---|---|---|
| 未携带 token | POST /blog/add | **401**（空响应体） |
| 空标题 + 空内容 | 带 token | 200 `{"code":"SUCCESS","errMsg":"","data":false}` |
| 仅空标题 | 带 token | 200 `{"code":"SUCCESS","errMsg":"","data":false}` |
| 仅空内容 | 带 token | 200 `{"code":"SUCCESS","errMsg":"","data":false}` |
| 请求体无字段 | 带 token | 200 `{"code":"SUCCESS","errMsg":"","data":false}` |

前端实际发送（实测载荷）：

```
POST /blog/add
Content-Type: application/json
user_token_header: <token>          ← 由 common.js 的 ajaxSend 注入
{"title":"中文标题测试","content":"中文正文内容"}
```

> 中文编码正常（已用 `postDataBuffer().toString('utf8')` 核验，并确认库中现有数据
> 中文可读）。注意 Node 环境下打印 `postData()` 可能出现乱码，那是**观察工具的显示问题**，
> 不是接口缺陷 —— 规划阶段曾因此误判，已修正。

## 四、测试模块与用例规划

### 模块 A：页面结构与加载（P1）
| 编号 | 场景 | 预期 |
|---|---|---|
| A1 | 页面标题与核心元素 | 标题"博客编辑页"，`#title`、`#submit`、`#editor` 均存在 |
| A2 | 编辑器初始化 | editor.md 加载，CodeMirror 就绪，预览区渲染 Markdown |
| A3 | 编辑器尺寸配置 | 配置为 width 100%、height 550px |

### 模块 B：访问控制（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| B1 | 未登录直接访问编辑页 | **实测：页面直接打开，不发任何请求 → 守卫缺失（缺陷）** |
| B2 | 未登录点击发布 | 401 → 跳转登录页（接口层鉴权有效） |
| B3 | 未登录调用 /blog/add | 401，不写入数据 |

### 模块 C：标题输入域（P1）
| 编号 | 场景 | 预期 |
|---|---|---|
| C1 | 标题框基础属性 | 记录 type/maxlength/placeholder/required |
| C2 | 超长标题（500 字） | 记录是否截断（**实测无长度限制**） |
| C3 | 特殊字符标题 | 正常显示，不破坏页面 |
| C4 | 标题前后空格 | 记录是否 trim |
| C5 | 清空后重新输入 | 值绑定正确 |

### 模块 D：编辑器内容（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| D1 | 默认占位内容 | 默认值为 `##在这里写下一篇博客` |
| D2 | 真实键盘输入同步 | CodeMirror 与 `#content` 一致（功能正常） |
| D3 | 未修改内容即发布 | 记录载荷是否为默认文本（**实测会带默认文本发布 → 缺陷**） |
| D4 | Markdown 预览渲染 | 输入 `# 标题` 后预览区渲染出对应元素 |
| D5 | 大量内容渲染 | 记录渲染耗时与稳定性 |

### 模块 E：发布流程（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| E1 | 发布请求契约 | method=POST、Content-Type=application/json、带 token 头 |
| E2 | 请求体字段 | 仅含 title 与 content，取值与页面输入一致 |
| E3 | 成功响应跳转 | `code=SUCCESS && data=true` → 跳转 `blog_list.html` |
| E4 | 中文内容编码 | UTF-8 正确，无乱码 |
| E5 | 响应缺少 data 字段 | 按失败处理，不跳转 |

### 模块 F：校验与错误反馈（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| F1 | 空标题发布 | 应给出可读提示 —— **实测弹出空对话框（缺陷）** |
| F2 | 空内容发布 | 同上，**空提示（缺陷）** |
| F3 | 超长标题发布 | **空提示（缺陷）** |
| F4 | 写接口 500 | **无任何提示，静默失败（缺陷）** |
| F5 | 前后端校验分工 | 记录前端零校验，完全依赖后端 |

### 模块 G：重复提交（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| G1 | 连点发布 3 次 | **实测发出 3 次请求 → 会产生重复文章（缺陷）** |
| G2 | 提交期间按钮禁用态 | 无禁用、无 loading（缺陷） |
| G3 | 提交期间按钮文案 | 始终为"发布文章"（缺陷） |

### 模块 H：安全（P0）
| 编号 | 场景 | 预期 |
|---|---|---|
| H1 | 标题注入 HTML/脚本 | 页面不执行，记录是否原样提交 |
| H2 | 注入内容进入库后的下游风险 | 关联列表页 XSS（BUG-L01）说明攻击链 |
| H3 | 超长内容提交 | 接口不 5xx |
| H4 | 无 token 写入被拒 | 401，数据未落库 |

### 模块 I：交互与兼容（P2）
| 编号 | 场景 | 预期 |
|---|---|---|
| I1 | 导航链接跳转 | 主页 → 列表页 |
| I2 | 注销 | 清 token 并跳登录页 |
| I3 | 未保存内容离开 | **实测无任何提醒，内容直接丢失（缺陷）** |
| I4 | 多分辨率布局 | 不溢出 |
| I5 | 静态资源 | 无 4xx/5xx |

**用例合计：31 条**

## 五、已确认缺陷候选（侦察阶段实测确认）

| 编号 | 级别 | 缺陷 | 证据 |
|---|---|---|---|
| BUG-E01 | 高 | 编辑页缺少登录守卫，未登录可打开写页面 | 加载时零鉴权请求 |
| BUG-E02 | 中 | 校验失败返回空 errMsg，前端弹空白提示 | `alert("")` 实测 |
| BUG-E03 | 中 | 无防重复提交，连点产生重复文章 | 连点 3 次发出 3 次请求 |
| BUG-E04 | 中 | 默认占位文本被当正文发布 | 载荷 content=`##在这里写下一篇博客` |
| BUG-E05 | 中 | 写接口 500 时静默无提示 | 无弹窗、无提示 |
| BUG-E06 | 低 | 标题无长度限制与必填约束 | maxlength=null、required=false |
| BUG-E07 | 低 | 无未保存内容离开提醒 | 点主页直接离开，内容丢失 |
| BUG-E08 | 低 | 无提交中状态反馈 | 按钮不禁用、无 loading |

## 六、测试策略

- **绝不真实写入**：所有发布用例拦截 `/blog/add`，返回构造的响应，只校验前端行为与载荷
- **每轮比对博客条数**：测试前后调用 `/blog/getList` 比对，证明环境未被污染
- **内容设置必须走 `cm.save()`**：否则 textarea 不同步，会误判为缺陷
- 鉴权用例使用未登录上下文，避免 token 串扰

## 七、交付物

1. `tests/blog_edit.spec.ts` — 自动化用例
2. `pages/EditPage.ts` — Page Object（封装 editor.md 交互）
3. `博客编辑页_测试用例.xlsx` — 规范测试用例（步骤级）
4. `博客编辑页_测试报告.docx` — 测试报告
5. `run-tests-edit.cmd` — 一键手动执行脚本
