import { Page, Locator, APIRequestContext } from '@playwright/test';

export const CREDENTIALS = {
  username: process.env.LOGIN_USERNAME || 'zhangsan',
  password: process.env.LOGIN_PASSWORD || '123456',
};

export const ROUTES = {
  login: '/blog_login.html',
  list: '/blog_list.html',
  edit: '/blog_edit.html',
  addApi: '/blog/add',
  listApi: '/blog/getList',
  loginApi: '/user/login',
};

export const ORIGIN = process.env.BASE_URL || 'http://127.0.0.1:9090';
export const TOKEN_HEADER = 'user_token_header';

export const SELECTORS = {
  navHome: '.nav a[href="blog_list.html"]',
  navEdit: '.nav a[href="blog_edit.html"]',
  navLogout: '.nav a[onclick="logout()"]',
  title: '#title',
  submit: '#submit',
  editorWrap: '#editor',
  content: '#content',
  codeMirror: '.CodeMirror',
  preview: '.editormd-preview',
  toolbar: '.editormd-toolbar a, .editormd-menu a',
};

/** 编辑器默认占位内容（实测） */
export const DEFAULT_CONTENT = '##在这里写下一篇博客';

/** /blog/add 的响应结构 */
export interface AddApiResult {
  status: number;
  body: { code: string; errMsg: string; data: boolean | null };
}

/** 编辑页 Page Object */
export class EditPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  get titleInput(): Locator { return this.page.locator(SELECTORS.title); }
  get submitBtn(): Locator { return this.page.locator(SELECTORS.submit); }
  get preview(): Locator { return this.page.locator(SELECTORS.preview); }
  get logoutLink(): Locator { return this.page.locator(SELECTORS.navLogout); }

  // ---------- 登录态 ----------
  async login(): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.page.fill('#username', CREDENTIALS.username);
    await this.page.fill('#password', CREDENTIALS.password);
    await this.page.click('#submit');
    await this.page.waitForURL(`**${ROUTES.list}`, { timeout: 15_000 });
  }

  async token(): Promise<string | null> {
    return this.page.evaluate(() => localStorage.getItem('user_token'));
  }

  /** 打开编辑页并等待 editor.md 初始化完成 */
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.edit);
    await this.page.waitForSelector(SELECTORS.codeMirror, { timeout: 15_000 });
    // 等 CodeMirror 实例真正可用
    await this.page.waitForFunction(
      () => {
        const el = document.querySelector('.CodeMirror') as any;
        return !!(el && el.CodeMirror && typeof el.CodeMirror.getValue === 'function');
      },
      { timeout: 15_000 },
    );
    await this.page.waitForTimeout(300);
  }

  // ---------- 编辑器交互 ----------

  /**
   * 设置编辑器内容。
   *
   * 关键：editor.md 的 textarea#content 是 display:none 的，
   * CodeMirror.setValue() 只更新编辑器，**不会同步回 textarea**，
   * 而 submit() 读取的是 $("#content").val()。
   * 因此必须调用 cm.save() 同步，否则提交的会是旧值 —— 这曾导致误判为缺陷。
   *
   * 真实键盘输入会自动同步，这里只是为了自动化可控性。
   */
  async setContent(text: string): Promise<void> {
    await this.page.evaluate((t) => {
      const el = document.querySelector('.CodeMirror') as any;
      el.CodeMirror.setValue(t);
      if (typeof el.CodeMirror.save === 'function') el.CodeMirror.save();
    }, text);
  }

  /** 读取编辑器内容（CodeMirror 视图值） */
  async editorValue(): Promise<string> {
    return this.page.evaluate(() => {
      const el = document.querySelector('.CodeMirror') as any;
      return el.CodeMirror.getValue();
    });
  }

  /** 读取隐藏 textarea 的值（即 submit 实际取用的值） */
  async textareaValue(): Promise<string> {
    return this.page.inputValue(SELECTORS.content);
  }

  /** 模拟真实键盘输入并返回输入后的同步状态 */
  async typeContent(text: string): Promise<{ cm: string; ta: string }> {
    await this.setContent('');
    await this.page.click(SELECTORS.codeMirror);
    await this.page.keyboard.type(text, { delay: 15 });
    await this.page.waitForTimeout(300);
    return { cm: await this.editorValue(), ta: await this.textareaValue() };
  }

  /** 读取预览区文本 */
  async previewText(): Promise<string> {
    return (await this.preview.innerText()).replace(/\s+/g, ' ').trim();
  }

  // ---------- 发布 ----------

  /** 拦截 /blog/add，返回指定响应；返回一个可读取最新请求载荷的访问器 */
  async mockAdd(
    response: { code: string; errMsg: string; data: boolean | null },
    status = 200,
  ): Promise<() => { postData: string | null; contentType: string | undefined; tokenHeader: string | undefined; count: number }> {
    const state = {
      postData: null as string | null,
      contentType: undefined as string | undefined,
      tokenHeader: undefined as string | undefined,
      count: 0,
    };
    await this.page.route(`**${ROUTES.addApi}`, async (route) => {
      const req = route.request();
      state.postData = req.postDataBuffer()?.toString('utf8') ?? req.postData();
      state.contentType = req.headers()['content-type'];
      state.tokenHeader = req.headers()[TOKEN_HEADER];
      state.count += 1;
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
    return () => state;
  }

  /** 点击发布（不等待跳转） */
  async clickSubmit(): Promise<void> {
    await this.submitBtn.click();
  }

  /** 注册一次性 alert 监听 */
  expectAlert(): Promise<string> {
    return new Promise<string>((resolve) => {
      this.page.once('dialog', async (d) => {
        const msg = d.message();
        await d.dismiss();
        resolve(msg);
      });
    });
  }

  /** 收集所有弹窗文案 */
  collectDialogs(): string[] {
    const msgs: string[] = [];
    this.page.on('dialog', async (d) => {
      msgs.push(d.message());
      await d.dismiss();
    });
    return msgs;
  }

  /** 页面加载后立即返回博客列表条数（需有效 token） */
  async blogCount(request: APIRequestContext, token: string): Promise<number> {
    const res = await request.get(ROUTES.listApi, { headers: { [TOKEN_HEADER]: token } });
    const body = await res.json();
    return Array.isArray(body.data) ? body.data.length : -1;
  }
}

/** 直接调用 /blog/add（必为失败路径，避免写入数据） */
export async function postAddApi(
  request: APIRequestContext,
  payload: unknown,
  token: string | null,
): Promise<AddApiResult> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token !== null) headers[TOKEN_HEADER] = token;
  const res = await request.post(ROUTES.addApi, {
    headers,
    data: JSON.stringify(payload ?? {}),
  });
  const text = await res.text();
  let body: any;
  try {
    body = JSON.parse(text);
  } catch {
    body = { code: 'PARSE_ERROR', errMsg: text.slice(0, 200), data: null };
  }
  return { status: res.status(), body };
}
