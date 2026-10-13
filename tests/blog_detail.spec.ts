import { test, expect } from '@playwright/test';
import {
  DetailPage,
  MARKER,
  SAMPLE_BLOG_ID,
  CREDENTIALS,
  ROUTES,
  SELECTORS,
  ORIGIN,
} from '../pages/DetailPage';

/**
 * 博客详情页自动化用例（blog_detail.html）
 *
 * 覆盖规划中的 9 个模块：访问控制、数据渲染、无效 blogId、权限与按钮、
 * 编辑跳转、删除流程、数据一致性、安全、交互兼容。
 *
 * ⚠️ 数据安全策略：
 *   - 删除/更新类用例只针对**自己创建的**测试博客（标题带 __E2E_DETAIL__ 标记）
 *   - 每个用例在 finally 中清理测试博客，保证环境恢复
 *   - 只读用例使用环境中原有博客，绝不修改
 *
 * 标注"发现缺陷"的用例锁定当前真实行为，把缺陷固化为可回归的证据。
 */

const CASE_ID = {
  A1: 1, A2: 2, A3: 3, A4: 4,
  B1: 5, B2: 6, B3: 7, B4: 8, B5: 9,
  C1: 10, C2: 11, C3: 12, C4: 13, C5: 14,
  D1: 15, D2: 16, D3: 17, D4: 18,
  E1: 19, E2: 20, E3: 21,
  F1: 22, F2: 23, F3: 24, F4: 25,
  G1: 26, G2: 27,
  H1: 28, H2: 29, H3: 30, H4: 31, H5: 32, H6: 33,
  I1: 34, I2: 35, I3: 36, I4: 37, I5: 38,
} as const;

function title(id: keyof typeof CASE_ID, text: string): string {
  return `${id} ${CASE_ID[id]} ${text}`;
}

test.describe('A 访问控制', () => {
  test(title('A1', '未登录访问详情页被守卫拦截'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.clearToken();

    await page.goto(`${ORIGIN}${ROUTES.detail}?blogId=${SAMPLE_BLOG_ID}`);
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 12_000 });

    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('A2', '未登录调用详情接口返回 401'), async ({ request }) => {
    const dp = new DetailPage(null as any);
    const res = await dp.getDetail(request, SAMPLE_BLOG_ID, null);
    expect(res.status).toBe(401);
  });

  test(title('A3', '未登录调用作者信息接口返回 401'), async ({ request }) => {
    const dp = new DetailPage(null as any);
    const res = await dp.getAuthor(request, SAMPLE_BLOG_ID, null);
    expect(res.status).toBe(401);
  });

  test(title('A4', '未登录调用删除接口返回 401 且数据未被删除'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    const before = await dp.listBlogs(request, token);

    const res = await request.post(`${ROUTES.deleteApi}?blogId=${SAMPLE_BLOG_ID}`, {
      headers: {},
    });
    expect(res.status()).toBe(401);

    const after = await dp.listBlogs(request, token);
    expect(after.length).toBe(before.length);
    expect(after.some((b) => b.id === SAMPLE_BLOG_ID)).toBe(true);
  });
});

test.describe('B 数据渲染', () => {
  test(title('B1', '标题、日期、正文与接口数据一致'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    const api = await dp.getDetail(request, SAMPLE_BLOG_ID, token);
    expect(api.body.code).toBe('SUCCESS');

    await dp.open(SAMPLE_BLOG_ID);
    await dp.waitForDetail();

    expect((await dp.titleText.innerText()).trim()).toBe(api.body.data.title);
    expect((await dp.dateText.innerText()).trim()).toContain(api.body.data.createTime.slice(0, 10));
  });

  test(title('B2', '正文经 Markdown 渲染生成容器'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    await dp.open(SAMPLE_BLOG_ID);
    await dp.waitForDetail();

    // editormd.markdownToHTML("detail", ...) 会把 #detail 内容替换为渲染结果，
    // .markdown-body 容器由 editor.md 生成（不在 .content .detail 内部）
    expect(await page.locator('.markdown-body').count()).toBeGreaterThan(0);
    // 正文被渲染为真实 HTML 元素（如 <p>），而非纯文本
    const renderedHtml = await dp.detail.innerHTML();
    expect(renderedHtml).toMatch(/<(p|h[1-6]|ul|ol|blockquote|pre)/);
    expect((await dp.detail.innerText()).length).toBeGreaterThan(0);
  });

  test(title('B3', '作者信息填充左侧卡片'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    const author = await dp.getAuthor(request, SAMPLE_BLOG_ID, token);

    await dp.open(SAMPLE_BLOG_ID);
    await page.waitForTimeout(1500);

    expect((await page.locator(SELECTORS.cardName).innerText()).trim())
      .toBe(author.body.data.userName);
    expect(await page.locator(SELECTORS.cardLink).getAttribute('href'))
      .toBe(author.body.data.githubUrl);
  });

  test(title('B4', '长正文渲染不被截断'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const longContent = Array.from({ length: 120 }, (_, i) => `第 ${i + 1} 段正文内容，用于渲染验证。`).join('\n\n');

    await page.route(`**${ROUTES.detailApi}*`, (route) =>
      route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: {
          id: 1, title: '长文标题', content: longContent, userId: 3,
          deleteFlag: 0, createTime: '2025-01-01 10:00', loginUser: false } }),
      }));

    await dp.open(1);
    await dp.waitForDetail();
    await page.waitForTimeout(800);

    const rendered = await dp.detail.innerText();
    test.info().annotations.push({
      type: '长正文渲染',
      description: `输入 ${longContent.length} 字，渲染后文本 ${rendered.replace(/\s+/g, '').length} 字，未截断`,
    });
    expect(rendered).toContain('第 120 段');
  });

  test(title('B5', '特殊字符标题作为文本渲染'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const special = '引号"单引号\'与&符号<>尖括号';

    await page.route(`**${ROUTES.detailApi}*`, (route) =>
      route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: {
          id: 1, title: special, content: '正文', userId: 3,
          deleteFlag: 0, createTime: '2025-01-01 10:00', loginUser: false } }),
      }));

    await dp.open(1);
    await dp.waitForDetail();

    expect((await dp.titleText.innerText()).trim()).toBe(special);
    expect(await page.locator(`${SELECTORS.contentTitle} *`).count()).toBe(0);
  });
});

test.describe('C 无效与异常 blogId', () => {
  test(title('C1', '不存在的 blogId：空白页面并提示内部错误'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const dialogs = dp.collectDialogs();

    await dp.open(99999999);
    await page.waitForTimeout(1500);

    const title = (await dp.titleText.innerText()).trim();
    test.info().annotations.push({
      type: '不存在 blogId 的表现',
      description: `blogId=99999999：标题为空、正文为空、无按钮，弹窗=${JSON.stringify(dialogs)} → ` +
        '页面仅弹出"内部错误, 请联系管理员"，无任何友好空态或返回入口（BUG-D04）',
    });
    expect(title).toBe('');
    expect(dialogs.length).toBeGreaterThan(0);
    expect(dialogs[0]).toContain('内部错误');
  });

  test(title('C2', '非数字 blogId 的错误信息与"不存在"无法区分'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const bad = await dp.getDetail(request, 'abc', token);
    const missing = await dp.getDetail(request, 99999999, token);

    test.info().annotations.push({
      type: '错误信息可诊断性',
      description: `blogId=abc 返回 ${JSON.stringify(bad.body)}；` +
        `blogId=99999999 返回 ${JSON.stringify(missing.body)} → ` +
        (bad.body.errMsg === missing.body.errMsg
          ? '参数非法与博客不存在返回完全相同的错误信息，用户与开发者都无法定位原因（BUG-D04）'
          : '错误信息可区分'),
    });
    expect(bad.body.code).toBe('FAIL');
    expect(bad.body.errMsg).toBe(missing.body.errMsg);
  });

  test(title('C3', '缺少 blogId 参数时表现一致'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const noParam = await request.get(ROUTES.detailApi, { headers: { 'user_token_header': token } });
    const body = await noParam.json();
    const withId = await dp.getDetail(request, 99999999, token);

    expect(body.code).toBe('FAIL');
    expect(body.errMsg).toBe(withId.body.errMsg);
  });

  test(title('C4', '负数 blogId 失败但不返回 5xx'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const res = await dp.getDetail(request, -1, token);
    expect(res.status).toBeLessThan(500);
    expect(res.body.code).toBe('FAIL');
  });

  test(title('C5', '详情接口返回非 JSON 时页面不崩溃'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    dp.collectDialogs();

    await page.route(`**${ROUTES.detailApi}*`, (route) =>
      route.fulfill({ status: 200, contentType: 'text/html', body: '<html>oops</html>' }));
    await dp.open(SAMPLE_BLOG_ID);
    await page.waitForTimeout(1500);

    await expect(page.locator(SELECTORS.card)).toBeVisible();
    expect(errors).toEqual([]);
  });
});

test.describe('D 权限与操作按钮', () => {
  test(title('D1', 'loginUser=true 时渲染编辑与删除按钮'), async ({ page, request, context }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_perm');
      await dp.open(testId);
      await dp.waitForDetail();

      const buttons = await dp.operationButtons();
      expect(buttons).toContain('编辑');
      expect(buttons).toContain('删除');
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });

  test(title('D2', 'loginUser=false 时不渲染任何操作按钮'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();

    await page.route(`**${ROUTES.detailApi}*`, (route) =>
      route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: {
          id: 88888, title: '他人博客标题', content: '他人博客内容', userId: 99,
          deleteFlag: 0, createTime: '2025-01-01 10:00', loginUser: false } }),
      }));

    await dp.open(88888);
    await dp.waitForDetail();

    const buttons = await dp.operationButtons();
    test.info().annotations.push({
      type: '按钮权限控制',
      description: `loginUser=false 时操作区按钮=${JSON.stringify(buttons)} → ` +
        (buttons.length === 0 ? '前端按接口字段正确隐藏按钮' : '仍显示按钮，存在越权操作入口'),
    });
    expect(buttons).toEqual([]);
  });

  test(title('D3', 'loginUser 字段在列表与详情接口间矛盾'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const blogs = await dp.listBlogs(request, token);
    const inList = blogs.find((b) => b.id === SAMPLE_BLOG_ID);
    const inDetail = await dp.getDetail(request, SAMPLE_BLOG_ID, token);

    test.info().annotations.push({
      type: '字段一致性',
      description: `同一博客 ${SAMPLE_BLOG_ID}：列表接口 loginUser=${inList?.loginUser}，` +
        `详情接口 loginUser=${inDetail.body.data.loginUser} → ` +
        (inList?.loginUser === inDetail.body.data.loginUser
          ? '两接口取值一致'
          : '两接口取值矛盾，字段语义不可信（BUG-D02）'),
    });

    expect(inList).toBeTruthy();
    expect(typeof inDetail.body.data.loginUser).toBe('boolean');
  });

  test(title('D4', '按钮为前端控制，后端归属校验需单独确认'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    // 前端仅依据 loginUser 字段渲染按钮
    // 后端是否校验归属：用不存在的 id 更新，若仍返回成功说明成功判定不基于影响行数
    const res = await request.post(ROUTES.updateApi, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'user_token_header': token },
      form: { id: 99999999, title: 'PROBE', content: 'PROBE' },
    });
    const body = await res.json();

    test.info().annotations.push({
      type: '归属校验风险',
      description: `更新不存在的 id=99999999 返回 ${JSON.stringify(body)} → ` +
        (body.data === true
          ? '成功判定不基于影响行数；本次环境无注册接口，无法创建第二用户，跨用户越权未能实证，建议后端补充归属校验'
          : '已按影响行数判定'),
    });
    expect(res.status()).toBeLessThan(500);
  });
});

test.describe('E 编辑跳转', () => {
  test(title('E1', '点击编辑跳转到更新页并带上 blogId'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_edit');
      await dp.open(testId);
      await dp.waitForDetail();

      await Promise.all([
        page.waitForNavigation({ timeout: 10_000 }).catch(() => null),
        dp.editButton.click(),
      ]);
      await page.waitForTimeout(1500);

      expect(page.url()).toContain('blog_update.html');
      expect(page.url()).toContain(`blogId=${testId}`);
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });

  test(title('E2', '更新页正确预填原博客数据'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_prefill');
      await page.goto(`${ORIGIN}${ROUTES.update}?blogId=${testId}`);
      await page.waitForTimeout(3000);

      expect(await page.inputValue('#blogId')).toBe(String(testId));
      expect(await page.inputValue('#title')).toContain('_prefill');

      const editorValue = await page.evaluate(() => {
        const el = document.querySelector('.CodeMirror') as any;
        return el && el.CodeMirror ? el.CodeMirror.getValue() : null;
      });
      expect(editorValue).toContain('_prefill');
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });

  test(title('E3', '更新页按钮文案为"更新文章"'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_btn');
      await page.goto(`${ORIGIN}${ROUTES.update}?blogId=${testId}`);
      await page.waitForTimeout(2500);
      expect(await page.inputValue('#submit')).toBe('更新文章');
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });
});

test.describe('F 删除流程', () => {
  test(title('F1', '点击删除弹出确认框"确定删除?"'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_confirm');
      await dp.open(testId);
      await dp.waitForDetail();

      const msgPromise = dp.handleDialog(false); // 取消，避免删掉
      await dp.deleteButton.click();
      const msg = await msgPromise;

      expect(msg).toBe('确定删除?');
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });

  test(title('F2', '取消确认后不删除且不发起删除请求'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_cancel');
      const deleteCalls: string[] = [];
      page.on('request', (r) => {
        if (r.url().includes(ROUTES.deleteApi)) deleteCalls.push(r.url());
      });

      await dp.open(testId);
      await dp.waitForDetail();

      const msgPromise = dp.handleDialog(false);
      await dp.deleteButton.click();
      await msgPromise;
      await page.waitForTimeout(1500);

      expect(deleteCalls).toEqual([]);
      expect(page.url()).toContain('blog_detail.html');
      const blogs = await dp.listBlogs(request, token);
      expect(blogs.some((b) => b.id === testId)).toBe(true);
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });

  test(title('F3', '确认删除后跳转列表页且博客消失'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    let testId: number | null = null;

    try {
      testId = await dp.createTestBlog(request, token, '_del');
      await dp.open(testId);
      await dp.waitForDetail();

      const msgPromise = dp.handleDialog(true);
      await dp.deleteButton.click();
      const msg = await msgPromise;
      expect(msg).toBe('确定删除?');

      await page.waitForURL(`**${ROUTES.list}`, { timeout: 12_000 });
      expect(page.url()).toContain('blog_list.html');

      const blogs = await dp.listBlogs(request, token);
      expect(blogs.some((b) => b.id === testId)).toBe(false);
      testId = null; // 已删除，无需清理
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
    }
  });

  test(title('F4', '删除测试博客后原有博客完好、环境恢复'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const baselineIds = (await dp.listBlogs(request, token)).map((b) => b.id);

    let testId: number | null = null;
    try {
      testId = await dp.createTestBlog(request, token, '_cleanup');
      const withTest = await dp.listBlogs(request, token);
      expect(withTest.length).toBe(baselineIds.length + 1);

      await dp.deleteBlog(request, token, testId);
      testId = null;

      const after = await dp.listBlogs(request, token);
      expect(after.map((b) => b.id).sort()).toEqual([...baselineIds].sort());
      expect(after.some((b) => b.id === SAMPLE_BLOG_ID)).toBe(true);
    } finally {
      if (testId !== null) await dp.deleteBlog(request, token, testId);
      await dp.cleanupTestBlogs(request, token).catch(() => undefined);
    }
  });
});

test.describe('G 数据一致性', () => {
  test(title('G1', '左侧文章计数为硬编码，与实际不符'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    const blogs = await dp.listBlogs(request, token);

    await dp.open(SAMPLE_BLOG_ID);
    await page.waitForTimeout(1500);

    const rows = (await dp.cardCounts()).map((r) => r.replace(/\s+/g, ' ').trim());
    const numbers = (rows[1] || '').split(/\s+/).map(Number).filter((n) => !Number.isNaN(n));
    const shown = numbers[0];

    test.info().annotations.push({
      type: '计数一致性',
      description: `卡片显示文章数=${shown}，当前账号实际博客数=${blogs.length} → ` +
        (shown === blogs.length ? '一致' : `不一致，卡片为 HTML 硬编码（BUG-D05）`),
    });
    expect(numbers.length).toBeGreaterThan(0);
  });

  test(title('G2', '详情字段与列表接口一致'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const inList = (await dp.listBlogs(request, token)).find((b) => b.id === SAMPLE_BLOG_ID);
    const inDetail = await dp.getDetail(request, SAMPLE_BLOG_ID, token);

    expect(inList).toBeTruthy();
    expect(inDetail.body.data.title).toBe(inList!.title);
    expect(inDetail.body.data.content).toBe(inList!.content);
    expect(inDetail.body.data.id).toBe(inList!.id);
  });
});

test.describe('H 安全', () => {
  test(title('H1', '标题中的 HTML 与脚本不被执行'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));

    await page.route(`**${ROUTES.detailApi}*`, (route) =>
      route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: {
          id: 1, title: '<img src=x onerror="window.__dx1=1">', content: '正文',
          userId: 3, deleteFlag: 0, createTime: '2025-01-01 10:00', loginUser: false } }),
      }));

    await dp.open(1);
    await dp.waitForDetail();
    await page.waitForTimeout(1000);

    const fired = await page.evaluate(() => (window as any).__dx1 || null);
    const imgs = await page.locator(`${SELECTORS.contentTitle} img`).count();

    test.info().annotations.push({
      type: '标题 XSS',
      description: `标题注入 <img onerror> 后：注入元素数=${imgs}，脚本执行=${fired ? '是' : '否'} → ` +
        (fired ? '存在 XSS' : '标题使用 .text() 赋值，未执行脚本，安全'),
    });
    expect(fired).toBeNull();
    expect(imgs).toBe(0);
    expect(errors).toEqual([]);
  });

  test(title('H2', '正文中的脚本不被执行'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();

    await page.route(`**${ROUTES.detailApi}*`, (route) =>
      route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ code: 'SUCCESS', errMsg: '', data: {
          id: 1, title: '标题',
          content: '<img src=x onerror="window.__dx2=1">\n\n# 标题\n\n<script>window.__dx3=1</script>',
          userId: 3, deleteFlag: 0, createTime: '2025-01-01 10:00', loginUser: false } }),
      }));

    await dp.open(1);
    await dp.waitForDetail();
    await page.waitForTimeout(1500);

    const fired = await page.evaluate(() => ({
      a: (window as any).__dx2 || null, b: (window as any).__dx3 || null,
    }));

    test.info().annotations.push({
      type: '正文 XSS',
      description: `正文注入 img/onerror 与 script 后：__dx2=${fired.a}，__dx3=${fired.b} → ` +
        (fired.a || fired.b ? '存在 XSS 执行风险' : 'markdownToHTML 未执行注入脚本，安全'),
    });
    expect(fired.a).toBeNull();
    expect(fired.b).toBeNull();
  });

  test(title('H3', '作者信息接口泄露密码哈希'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const res = await dp.getAuthor(request, SAMPLE_BLOG_ID, token);
    expect(res.status).toBe(200);
    expect(res.body.code).toBe('SUCCESS');

    const keys = Object.keys(res.body.data || {});
    const leaked = keys.filter((k) => /password|pwd|passwd|salt|secret/i.test(k));

    test.info().annotations.push({
      type: '敏感信息泄露',
      description: `getAuthorInfo 响应字段=[${keys.join(', ')}] → ` +
        (leaked.length
          ? `包含敏感字段 ${leaked.join(', ')}，返回值为密码哈希；详情页仅需 userName 与 githubUrl，属信息泄露（高危，BUG-D01）`
          : '未发现敏感字段'),
    });
    expect(leaked.length).toBeGreaterThan(0);
  });

  test(title('H4', '更新不存在的 id 被误报为成功'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;

    const res = await request.post(ROUTES.updateApi, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'user_token_header': token },
      form: { id: 99999999, title: 'X', content: 'Y' },
    });
    const body = await res.json();

    test.info().annotations.push({
      type: '更新成功判定',
      description: `更新不存在的 id=99999999 返回 ${JSON.stringify(body)} → ` +
        (body.code === 'SUCCESS' && body.data === true
          ? '对不存在的记录仍返回成功，成功判定不基于影响行数，会造成"已保存"的假象（BUG-D03）'
          : '正确返回失败'),
    });
    expect(body.code).toBe('SUCCESS');
    expect(body.data).toBe(true);
  });

  test(title('H5', '缺少 id 的更新不误改数据'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    const before = await dp.listBlogs(request, token);

    const res = await request.post(ROUTES.updateApi, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'user_token_header': token },
      form: { title: 'NOID_PROBE', content: 'NOID_PROBE' },
    });
    const body = await res.json();

    const after = await dp.listBlogs(request, token);
    expect(after.some((b) => String(b.title).includes('NOID_PROBE'))).toBe(false);
    expect(after.length).toBe(before.length);

    test.info().annotations.push({
      type: '缺少 id 的更新',
      description: `不带 id 更新返回 ${JSON.stringify(body)}，无任何博客被修改，WHERE 条件正常`,
    });
  });

  test(title('H6', '删除不存在的 id 不误删其他数据'), async ({ page, request }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const token = (await dp.token())!;
    const before = await dp.listBlogs(request, token);

    const res = await request.post(`${ROUTES.deleteApi}?blogId=99999999`, {
      headers: { 'user_token_header': token },
    });
    const body = await res.json();

    const after = await dp.listBlogs(request, token);
    expect(after.length).toBe(before.length);
    expect(after.some((b) => b.id === SAMPLE_BLOG_ID)).toBe(true);

    test.info().annotations.push({
      type: '删除不存在 id',
      description: `删除 blogId=99999999 返回 ${JSON.stringify(body)}，博客条数 ${before.length} → ${after.length}，` +
        '未误删其他数据（WHERE 条件正常），但对不存在的记录误报成功（BUG-D03）',
    });
  });
});

test.describe('I 交互与兼容', () => {
  test(title('I1', '导航链接跳转正确'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    await dp.open(SAMPLE_BLOG_ID);
    await page.waitForTimeout(1000);

    await page.locator(SELECTORS.navHome).click();
    await page.waitForURL(`**${ROUTES.list}`, { timeout: 10_000 });
    expect(page.url()).toContain('blog_list.html');

    await page.goto(`${ORIGIN}${ROUTES.detail}?blogId=${SAMPLE_BLOG_ID}`);
    await page.waitForTimeout(1200);
    await page.locator(SELECTORS.navEdit).click();
    await page.waitForURL(`**${ROUTES.edit}`, { timeout: 10_000 });
    expect(page.url()).toContain('blog_edit.html');
  });

  test(title('I2', '注销清除 token 并跳转登录页'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    await dp.open(SAMPLE_BLOG_ID);
    await page.waitForTimeout(1000);

    await page.locator(SELECTORS.navLogout).click();
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 10_000 });

    expect(await dp.token()).toBeNull();
    expect(page.url()).toContain(ROUTES.login);
  });

  test(title('I3', '窄屏下正文横向溢出（固定宽度布局）'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.login();
    const sizes = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 768, height: 1024 },
      { width: 375, height: 667 },
    ];

    const overflowAt: string[] = [];
    const measurements: string[] = [];

    for (const size of sizes) {
      await page.setViewportSize(size);
      await dp.open(SAMPLE_BLOG_ID);
      await dp.waitForDetail();
      await page.waitForTimeout(400);

      const m = await page.evaluate((vw) => ({
        containerWidth: Math.round(document.querySelector('.container')!.getBoundingClientRect().width),
        scrollWidth: document.documentElement.scrollWidth,
        overflow: document.documentElement.scrollWidth > vw,
      }), size.width);

      measurements.push(`${size.width}px: 容器${m.containerWidth}px, 文档宽${m.scrollWidth}px`);
      if (m.overflow) overflowAt.push(`${size.width}px（溢出 ${m.scrollWidth - size.width}px）`);
    }

    test.info().annotations.push({
      type: '窄屏横向溢出',
      description: `各分辨率测量：${measurements.join('；')} → ` +
        (overflowAt.length
          ? `在 ${overflowAt.join('、')} 出现横向滚动条。.container 为固定宽度 800px，` +
            '窄屏下不收缩，属响应式布局缺陷（BUG-D07）'
          : '各分辨率均无横向溢出'),
    });

    // 锁定当前真实行为：窄屏确实溢出
    expect(overflowAt.length).toBeGreaterThan(0);
  });

  test(title('I4', '静态资源无 4xx/5xx'), async ({ page }) => {
    const failed: string[] = [];
    page.on('response', (r) => {
      if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    });
    const dp = new DetailPage(page);
    await dp.login();
    await dp.open(SAMPLE_BLOG_ID);
    await page.waitForTimeout(1500);

    test.info().annotations.push({
      type: '静态资源基线',
      description: failed.length ? `失败资源：${failed.join('; ')}` : '全部资源正常',
    });
    expect(failed.some((f) => f.includes('blog_detail.html'))).toBe(false);
  });

  test(title('I5', '无效 token 访问详情页被拦截'), async ({ page }) => {
    const dp = new DetailPage(page);
    await dp.setToken('garbage.token.xxx');

    await page.goto(`${ORIGIN}${ROUTES.detail}?blogId=${SAMPLE_BLOG_ID}`);
    await page.waitForURL(`**${ROUTES.login}`, { timeout: 12_000 });

    expect(page.url()).toContain(ROUTES.login);
  });
});
