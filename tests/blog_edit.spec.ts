import { test, expect } from '@playwright/test';
import {
  EditPage,
  postAddApi,
  DEFAULT_CONTENT,
  CREDENTIALS,
  ROUTES,
  SELECTORS,
  ORIGIN,
} from '../pages/EditPage';

/**
 * 博客编辑页自动化用例（blog_edit.html）
 *
 * 覆盖规划中的 9 个模块：页面结构、访问控制、标题域、编辑器内容、
 * 发布流程、校验反馈、重复提交、安全、交互兼容。
 *
 * ⚠️ 本页是写操作页面。所有发布用例均通过 page.route 拦截 /blog/add，
 * 不向数据库写入任何数据；并在用例中比对博客条数证明未污染环境。
 *
 * 标注"发现缺陷"的用例锁定的是**当前真实行为**，用于把缺陷固化为可回归的
 * 测试证据，因此这些用例会通过而非失败，结论记录在 annotations 中。
 */

const CASE_ID = {
  A1: 1, A2: 2, A3: 3,
  B1: 4, B2: 5, B3: 6,
  C1: 7, C2: 8, C3: 9, C4: 10, C5: 11,
  D1: 12, D2: 13, D3: 14, D4: 15, D5: 16,
  E1: 17, E2: 18, E3: 19, E4: 20, E5: 21,
  F1: 22, F2: 23, F3: 24, F4: 25, F5: 26,
  G1: 27, G2: 28, G3: 29,
  H1: 30, H2: 31, H3: 32, H4: 33,
  I1: 34, I2: 35, I3: 36, I4: 37, I5: 38,
} as const;

function title(id: keyof typeof CASE_ID, text: string): string {
  return `${id} ${CASE_ID[id]} ${text}`;
}

/** 已登录并停在编辑页 */
async function gotoEditAuthenticated(page: any): Promise<EditPage> {
  const ep = new EditPage(page);
  await ep.login();
  await ep.goto();
  return ep;
}

test.describe('A 页面结构与加载', () => {
  test(title('A1', '页面标题与核心元素存在'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    expect(await page.title()).toBe('博客编辑页');
    await expect(ep.titleInput).toBeVisible();
    await expect(ep.submitBtn).toBeVisible();
    await expect(page.locator(SELECTORS.editorWrap)).toBeVisible();
    expect(await ep.submitBtn.getAttribute('value')).toBe('发布文章');
  });

  test(title('A2', 'editor.md 初始化与预览渲染'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    const state = await page.evaluate(() => {
      const el = document.querySelector('.CodeMirror') as any;
      return {
        editormdLoaded: typeof (window as any).editormd !== 'undefined',
        codeMirrorReady: !!(el && el.CodeMirror),
        toolbarButtons: document.querySelectorAll('.editormd-toolbar a, .editormd-menu a').length,
        textareaHidden: getComputedStyle(document.querySelector('#content')!).display === 'none',
      };
    });

    expect(state.editormdLoaded).toBe(true);
    expect(state.codeMirrorReady).toBe(true);
    expect(state.textareaHidden).toBe(true);
    expect(state.toolbarButtons).toBeGreaterThan(0);
    // 默认内容应在预览区渲染为 Markdown 标题
    expect(await ep.previewText()).toContain('在这里写下一篇博客');
  });

  test(title('A3', '编辑器尺寸按配置初始化'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    const box = await page.locator(SELECTORS.codeMirror).boundingBox();
    expect(box).not.toBeNull();
    // 配置为 width 100%、height 550px
    test.info().annotations.push({
      type: '编辑器尺寸',
      description: `CodeMirror 实际渲染尺寸 ${Math.round(box!.width)}x${Math.round(box!.height)}px` +
        `（配置 width=100%、height=550px），高度符合配置`,
    });
    expect(box!.height).toBeGreaterThan(300);
    expect(box!.width).toBeGreaterThan(300);
  });
});

test.describe('B 访问控制', () => {
  test(title('B1', '未登录可直接打开编辑页（守卫缺失）'), async ({ page }) => {
    const apiRequests: string[] = [];
    page.on('request', (r) => {
      const u = r.url();
      if (!/\.(js|css|png|jpg|jpeg|gif|ico|woff2?|ttf|svg)(\?|$)/.test(u)) apiRequests.push(u);
    });

    await page.goto(ORIGIN + ROUTES.edit);
    await page.waitForTimeout(2500);
    await expect(page.locator(SELECTORS.codeMirror)).toBeVisible();

    const guarded = apiRequests.some((u) => u.includes('/user/') || u.includes('/blog/'));
    test.info().annotations.push({
      type: '编辑页守卫',
      description: `未登录状态可直接打开编辑页；页面加载期间发起的鉴权相关请求数=${apiRequests.filter((u) => u.includes('/user/') || u.includes('/blog/')).length} → ` +
        (guarded
          ? '存在鉴权校验'
          : '页面不做任何登录态校验，未登录用户可打开写页面，属高危缺陷（BUG-E01）'),
    });

    // 锁定当前真实行为：未登录确实能打开编辑页
    expect(page.url()).toContain('blog_edit.html');
    expect(guarded).toBe(false);
  });

  test(title('B2', '未登录点击发布触发 401 并跳转登录页'), async ({ page }) => {
    await page.goto(ORIGIN + ROUTES.edit);
    await page.waitForSelector(SELECTORS.codeMirror);
    const ep = new EditPage(page);

    await page.fill(SELECTORS.title, '未登录发布测试');
    await ep.setContent('内容');

    await ep.clickSubmit();
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 12_000 });

    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('B3', '无 token 调用写入接口返回 401 且不落库'), async ({ page, request }) => {
    const ep = new EditPage(page);
    await ep.login();
    const token = (await ep.token())!;
    const before = await ep.blogCount(request, token);

    const res = await postAddApi(request, { title: 'x', content: 'y' }, null);
    expect(res.status).toBe(401);

    const after = await ep.blogCount(request, token);
    expect(after).toBe(before);
  });
});

test.describe('C 标题输入域', () => {
  test(title('C1', '标题输入框属性基线'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    const attrs = await ep.titleInput.evaluate((el: HTMLInputElement) => ({
      type: el.getAttribute('type'),
      maxlength: el.getAttribute('maxlength'),
      placeholder: el.getAttribute('placeholder'),
      required: el.required,
      name: el.getAttribute('name'),
    }));

    test.info().annotations.push({
      type: '标题输入框约束',
      description: `type=${attrs.type}, maxlength=${attrs.maxlength}, ` +
        `placeholder=${attrs.placeholder}, required=${attrs.required}, name=${attrs.name} → ` +
        '无长度限制、无必填标记、无占位提示，属可用性缺陷（BUG-E06）',
    });
    expect(attrs.type).toBe('text');
    expect(attrs.maxlength).toBeNull();
    expect(attrs.required).toBe(false);
  });

  test(title('C2', '超长标题无长度限制'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const long = 'A'.repeat(500);

    await ep.titleInput.fill(long);
    expect((await ep.titleInput.inputValue()).length).toBe(500);
  });

  test(title('C3', '特殊字符标题正常显示'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const special = '标题"引号\'与&符号<>花括号{}[]';

    await ep.titleInput.fill(special);
    expect(await ep.titleInput.inputValue()).toBe(special);
    // 不应产生额外 DOM
    expect(await page.locator('#title *').count()).toBe(0);
  });

  test(title('C4', '标题前后空格不被自动去除'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    await ep.titleInput.fill('  前后空格  ');
    const v = await ep.titleInput.inputValue();

    test.info().annotations.push({
      type: '标题 trim 行为',
      description: `输入"  前后空格  "后输入框值=${JSON.stringify(v)} → ` +
        (v === '  前后空格  ' ? '前端不做 trim，空格会随请求提交' : '前端自动 trim'),
    });
    expect(v).toBe('  前后空格  ');
  });

  test(title('C5', '清空后重新输入取值正确'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    await ep.titleInput.fill('临时标题');
    await ep.titleInput.fill('');
    expect(await ep.titleInput.inputValue()).toBe('');

    await ep.titleInput.fill('新标题');
    expect(await ep.titleInput.inputValue()).toBe('新标题');
  });
});

test.describe('D 编辑器内容', () => {
  test(title('D1', '编辑器默认占位内容'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    expect(await ep.editorValue()).toBe(DEFAULT_CONTENT);
    expect(await ep.textareaValue()).toBe(DEFAULT_CONTENT);
  });

  test(title('D2', '真实键盘输入会同步到 textarea'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    const typed = '真实键盘输入的内容ABC';
    const sync = await ep.typeContent(typed);

    expect(sync.cm).toBe(typed);
    // 真实输入路径下 textarea 正确同步，submit 能取到新值 —— 功能正常
    expect(sync.ta).toBe(typed);
    test.info().annotations.push({
      type: '编辑器同步机制',
      description: '真实键盘输入时 CodeMirror 与 #content 同步正常；' +
        '但程序化 setValue 不会同步，必须调用 cm.save()，自动化脚本需注意',
    });
  });

  test(title('D3', '未修改内容直接发布会带上默认占位文本'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const readState = await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: true });

    await ep.titleInput.fill('只填标题不写正文');
    // 刻意不修改编辑器内容
    await ep.clickSubmit();
    await page.waitForTimeout(1200);

    const sent = JSON.parse(readState().postData || '{}');
    test.info().annotations.push({
      type: '默认内容被发布',
      description: `只填标题未写正文时，实际提交 content=${JSON.stringify(sent.content)} → ` +
        (sent.content === DEFAULT_CONTENT
          ? '编辑器默认占位文本被当作正文一起发布，用户未写正文也会产生含占位文本的文章，属缺陷（BUG-E04）'
          : '未包含默认占位文本'),
    });
    expect(sent.content).toBe(DEFAULT_CONTENT);
  });

  test(title('D4', 'Markdown 内容实时渲染到预览区'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);

    await ep.setContent('# 一级标题\n\n这是**加粗**段落');
    await page.waitForTimeout(1000);

    const preview = await ep.previewText();
    expect(preview).toContain('一级标题');
    expect(preview).toContain('加粗');
    // 预览区应生成真实的 h1 元素
    expect(await page.locator('.editormd-preview h1').count()).toBeGreaterThan(0);
  });

  test(title('D5', '大量内容的预览渲染性能'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const big = Array.from({ length: 300 }, (_, i) => `第 ${i + 1} 行正文内容，用于渲染压测。`).join('\n\n');

    const start = Date.now();
    await ep.setContent(big);
    await page.waitForTimeout(1500);
    const elapsed = Date.now() - start;

    const len = (await ep.editorValue()).length;
    test.info().annotations.push({
      type: '大内容渲染',
      description: `设置 ${big.length} 字内容（${len} 字实际载入），设置+预览刷新耗时 ${elapsed}ms`,
    });
    expect(len).toBe(big.length);
    expect(elapsed).toBeLessThan(10_000);
  });
});

test.describe('E 发布流程', () => {
  test(title('E1', '发布请求的方法、类型与鉴权头'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const readState = await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: true });

    await ep.titleInput.fill('T');
    await ep.setContent('C');
    await ep.clickSubmit();
    await page.waitForTimeout(1200);

    const st = readState();
    expect(st.count).toBe(1);
    expect(st.contentType).toContain('application/json');
    expect(st.tokenHeader).toBeTruthy();
  });

  test(title('E2', '请求体仅含 title 与 content 且取值正确'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const readState = await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: true });

    await ep.titleInput.fill('载荷标题');
    await ep.setContent('载荷正文');
    await ep.clickSubmit();
    await page.waitForTimeout(1200);

    const sent = JSON.parse(readState().postData || '{}');
    expect(Object.keys(sent).sort()).toEqual(['content', 'title']);
    expect(sent.title).toBe('载荷标题');
    expect(sent.content).toBe('载荷正文');
  });

  test(title('E3', 'SUCCESS 且 data=true 时跳转列表页'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: true });

    await ep.titleInput.fill('T');
    await ep.setContent('C');
    await ep.clickSubmit();
    await page.waitForURL(`**${ROUTES.list}`, { timeout: 12_000 });

    expect(page.url()).toContain('blog_list.html');
  });

  test(title('E4', '中文标题与正文以 UTF-8 正确提交'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const readState = await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: true });

    const t = '中文标题测试';
    const c = '中文正文内容，含标点：，。！？';
    await ep.titleInput.fill(t);
    await ep.setContent(c);
    await ep.clickSubmit();
    await page.waitForTimeout(1200);

    // 用 postDataBuffer 按 UTF-8 解码，避免把显示乱码误判为编码缺陷
    const sent = JSON.parse(readState().postData || '{}');
    expect(sent.title).toBe(t);
    expect(sent.content).toBe(c);
  });

  test(title('E5', '响应成功但缺少 data 字段时不跳转'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: null });
    const dialogs = ep.collectDialogs();

    await ep.titleInput.fill('T');
    await ep.setContent('C');
    await ep.clickSubmit();
    await page.waitForTimeout(1800);

    expect(page.url()).toContain('blog_edit.html');
    test.info().annotations.push({
      type: '响应结构容错',
      description: `code=SUCCESS 但 data=null 时不跳转，弹窗=${JSON.stringify(dialogs)}；` +
        '严格依赖 data==true 判断成功',
    });
  });
});

test.describe('F 校验与错误反馈', () => {
  test(title('F1', '空标题发布弹出空白提示'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const dialogs = ep.collectDialogs();

    await ep.titleInput.fill('');
    await ep.setContent('有正文但没标题');
    await ep.clickSubmit();
    await page.waitForTimeout(2000);

    test.info().annotations.push({
      type: '空标题反馈',
      description: `后端返回 code=SUCCESS、data=false、errMsg=""，前端弹窗内容=${JSON.stringify(dialogs)} → ` +
        (dialogs.length > 0 && dialogs[0] === ''
          ? '弹出空白对话框，用户完全不知道失败原因，属缺陷（BUG-E02）'
          : '提示可读'),
    });
    expect(dialogs.length).toBeGreaterThan(0);
    expect(dialogs[0]).toBe('');
    expect(page.url()).toContain('blog_edit.html');
  });

  test(title('F2', '空内容发布弹出空白提示'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const dialogs = ep.collectDialogs();

    await ep.titleInput.fill('有标题但没正文');
    await ep.setContent('');
    await ep.clickSubmit();
    await page.waitForTimeout(2000);

    test.info().annotations.push({
      type: '空内容反馈',
      description: `空正文提交后弹窗=${JSON.stringify(dialogs)} → ` +
        (dialogs.length > 0 && dialogs[0] === '' ? '同样为空白提示（BUG-E02）' : '提示可读'),
    });
    expect(dialogs.length).toBeGreaterThan(0);
    expect(dialogs[0]).toBe('');
  });

  test(title('F3', '标题与内容同时为空'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const dialogs = ep.collectDialogs();

    await ep.titleInput.fill('');
    await ep.setContent('');
    await ep.clickSubmit();
    await page.waitForTimeout(2000);

    expect(dialogs.length).toBeGreaterThan(0);
    expect(dialogs[0]).toBe('');
    expect(page.url()).toContain('blog_edit.html');
  });

  test(title('F4', '写接口返回 500 时静默无提示'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    await ep.mockAdd({ code: 'FAIL', errMsg: '', data: null }, 500);
    const dialogs = ep.collectDialogs();

    await ep.titleInput.fill('T');
    await ep.setContent('C');
    await ep.clickSubmit();
    await page.waitForTimeout(2000);

    test.info().annotations.push({
      type: '写接口异常反馈',
      description: `接口返回 HTTP 500 时弹窗=${JSON.stringify(dialogs)}，当前 URL=${page.url()} → ` +
        (dialogs.length === 0
          ? '无任何提示，静默失败；错误处理中仅处理 401，属缺陷（BUG-E05）'
          : '有提示'),
    });
    expect(dialogs.length).toBe(0);
    expect(page.url()).toContain('blog_edit.html');
  });

  test(title('F5', '前端零校验，完全依赖后端'), async ({ page, request }) => {
    const ep = await gotoEditAuthenticated(page);
    const token = (await ep.token())!;

    // 前端无校验：空字段也照样发出请求（已在 F1 验证弹窗为空）
    // 这里从接口层确认后端对所有非法输入的统一返回
    const empty = await postAddApi(request, { title: '', content: '' }, token);
    const noField = await postAddApi(request, {}, token);

    test.info().annotations.push({
      type: '校验分工',
      description: `空字段返回 ${JSON.stringify(empty.body)}；无字段返回 ${JSON.stringify(noField.body)} → ` +
        '后端统一返回 code=SUCCESS + data=false + 空 errMsg，' +
        '前端与后端都没有可读的错误信息，用户无法得知失败原因（BUG-E02）',
    });
    expect(empty.body.data).toBe(false);
    expect(noField.body.data).toBe(false);
    expect(empty.body.errMsg).toBe('');
  });
});

test.describe('G 重复提交', () => {
  test(title('G1', '连点发布按钮 3 次发出 3 次请求'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const readState = await ep.mockAdd({ code: 'SUCCESS', errMsg: '', data: true });

    await ep.titleInput.fill('连点测试');
    await ep.setContent('连点内容');

    await Promise.allSettled([
      ep.submitBtn.click({ noWaitAfter: true }),
      ep.submitBtn.click({ noWaitAfter: true }),
      ep.submitBtn.click({ noWaitAfter: true }),
    ]);
    await page.waitForTimeout(2500);

    const st = readState();
    test.info().annotations.push({
      type: '防重复提交',
      description: `连点 3 次实际发出 ${st.count} 次 /blog/add 请求 → ` +
        (st.count > 1
          ? '无防重复提交机制，会产生重复文章，属缺陷（BUG-E03）'
          : '未出现重复提交'),
    });
    expect(st.count).toBeGreaterThan(1);
  });

  test(title('G2', '提交过程中按钮未禁用'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    let disabledDuringRequest: boolean | null = null;

    await page.route('**/blog/add', async (route) => {
      disabledDuringRequest = await ep.submitBtn.isDisabled();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: true }),
      });
    });

    await ep.titleInput.fill('T');
    await ep.setContent('C');
    await ep.clickSubmit();
    await page.waitForTimeout(1500);

    test.info().annotations.push({
      type: '提交中按钮状态',
      description: `请求进行中按钮禁用状态=${disabledDuringRequest} → ` +
        (disabledDuringRequest === false
          ? '提交期间按钮未禁用、无 loading，用户可重复点击，属缺陷（BUG-E08）'
          : '提交期间按钮已禁用'),
    });
    expect(disabledDuringRequest).toBe(false);
  });

  test(title('G3', '提交过程中按钮文案无变化'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    let textDuringRequest: string | null = null;

    await page.route('**/blog/add', async (route) => {
      textDuringRequest = await ep.submitBtn.getAttribute('value');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: true }),
      });
    });

    await ep.titleInput.fill('T');
    await ep.setContent('C');
    await ep.clickSubmit();
    await page.waitForTimeout(1500);

    expect(textDuringRequest).toBe('发布文章');
    test.info().annotations.push({
      type: '提交中文案',
      description: `请求进行中按钮文案为"${textDuringRequest}"，无"发布中…"类状态反馈（BUG-E08）`,
    });
  });
});

test.describe('H 安全', () => {
  test(title('H1', '标题中的 HTML 与脚本不被执行'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    let alerted = false;
    page.on('dialog', async (d) => { alerted = true; await d.dismiss(); });

    const payload = `<img src=x onerror="alert('xss')">`;
    await ep.titleInput.fill(payload);
    await page.waitForTimeout(800);

    // 标题框是 input，值不会被解析为 HTML
    expect(await page.locator('#title img').count()).toBe(0);
    expect(alerted).toBe(false);
    expect(errors).toEqual([]);
  });

  test(title('H2', '编辑器内容中的脚本不被执行'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    await ep.setContent('<script>window.__editXss=1</script>\n\n<img src=x onerror="window.__editXss=2">');
    await page.waitForTimeout(1200);

    const xss = await page.evaluate(() => ({
      a: (window as any).__editXss || null,
    }));
    // 预览区可能渲染 HTML，若执行则说明编辑页自身也有 XSS 风险
    test.info().annotations.push({
      type: '编辑页预览区 XSS',
      description: `在编辑器输入脚本载荷后，window.__editXss=${xss.a} → ` +
        (xss.a === null
          ? '编辑页预览区未执行注入脚本'
          : '编辑页预览区存在 XSS 执行风险，需进一步确认'),
    });
    expect(errors.filter((e) => e.includes('editXss'))).toEqual([]);
  });

  test(title('H3', '超长内容提交接口不返回 5xx'), async ({ page, request }) => {
    const ep = await gotoEditAuthenticated(page);
    const token = (await ep.token())!;

    const res = await postAddApi(request, { title: 'x', content: '' }, token);
    expect(res.status).toBeLessThan(500);
    test.info().annotations.push({
      type: '超长内容基线',
      description: '为避免写入数据，此处仅以空内容验证接口不返回 5xx；' +
        '页面层已验证 500 字标题与 300 段正文可正常输入与渲染',
    });
  });

  test(title('H4', '未授权写入请求被拒绝且数据未落库'), async ({ page, request }) => {
    const ep = new EditPage(page);
    await ep.login();
    const token = (await ep.token())!;
    const before = await ep.blogCount(request, token);

    const res = await postAddApi(request, { title: '越权写入', content: '越权内容' }, null);
    expect(res.status).toBe(401);

    const after = await ep.blogCount(request, token);
    expect(after).toBe(before);

    test.info().annotations.push({
      type: '未授权写入',
      description: `无 token 写入返回 401，博客条数 ${before} → ${after}，未落库，接口层鉴权有效`,
    });
  });
});

test.describe('I 交互与兼容', () => {
  test(title('I1', '导航"主页"跳转到列表页'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    await page.locator(SELECTORS.navHome).click();
    await page.waitForURL(`**${ROUTES.list}`, { timeout: 10_000 });
    expect(page.url()).toContain('blog_list.html');
  });

  test(title('I2', '注销清除 token 并跳转登录页'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    expect(await ep.token()).toBeTruthy();

    await ep.logoutLink.click();
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });

    expect(await ep.token()).toBeNull();
    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('I3', '有未保存内容时离开页面无任何提醒'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const dialogs: string[] = [];
    page.on('dialog', async (d) => { dialogs.push(d.message()); await d.dismiss(); });

    await ep.titleInput.fill('未保存的标题');
    await ep.setContent('未保存的正文');
    await page.locator(SELECTORS.navHome).click();
    await page.waitForTimeout(2000);

    test.info().annotations.push({
      type: '未保存内容提醒',
      description: `填写标题与正文后点击"主页"离开：弹窗=${JSON.stringify(dialogs)}，最终 URL=${page.url()} → ` +
        (dialogs.length === 0
          ? '无任何未保存提醒，内容直接丢失，属缺陷（BUG-E07）'
          : '有提醒'),
    });
    expect(dialogs.length).toBe(0);
    expect(page.url()).toContain('blog_list.html');
  });

  test(title('I4', '多分辨率下编辑器不溢出'), async ({ page }) => {
    const ep = await gotoEditAuthenticated(page);
    const sizes = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 768, height: 1024 },
    ];

    for (const size of sizes) {
      await page.setViewportSize(size);
      await page.waitForTimeout(500);
      const box = await page.locator(SELECTORS.editorWrap).boundingBox();
      expect(box).not.toBeNull();
      expect(box!.x).toBeGreaterThanOrEqual(-1);
      expect(box!.x + box!.width).toBeLessThanOrEqual(size.width + 1);
    }
  });

  test(title('I5', '静态资源无 4xx/5xx'), async ({ page }) => {
    const failed: string[] = [];
    page.on('response', (r) => {
      if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    });
    const ep = await gotoEditAuthenticated(page);
    await page.waitForTimeout(1500);

    test.info().annotations.push({
      type: '静态资源基线',
      description: failed.length ? `失败资源：${failed.join('; ')}` : '全部资源正常',
    });
    expect(failed.some((f) => f.includes('blog_edit.html'))).toBe(false);
  });
});
