import { Page, Locator, expect, APIRequestContext, Route } from '@playwright/test';

/** 登录接口响应体结构（实测：失败时 HTTP 状态码同样是 200，必须以 code 判定） */
export interface LoginApiResult {
  status: number;
  body: {
    code: string;
    errMsg: string;
    data: string | null;
  };
}

/** 测试账号，可通过环境变量覆盖，避免把密码硬编码进仓库 */
export const CREDENTIALS = {
  username: process.env.LOGIN_USERNAME || 'zhangsan',
  password: process.env.LOGIN_PASSWORD || '123456',
};

export const ROUTES = {
  login: '/blog_login.html',
  list: '/blog_list.html',
  edit: '/blog_edit.html',
  loginApi: '/user/login',
};

/** 被测环境地址前缀，与 playwright.config.ts 保持一致 */
export const ORIGIN = process.env.BASE_URL || 'http://127.0.0.1:9090';

export const SELECTORS = {
  username: '#username',
  password: '#password',
  submit: '#submit',
  dialogTitle: '.login-dialog h3',
  navHome: 'a[href="blog_list.html"]',
  navEdit: 'a[href="blog_edit.html"]',
};

/**
 * 登录页 Page Object
 *
 * 页面特征（已实测，非假设）：
 *  - 整页没有 <form> 元素，提交只依赖 button#submit 的 onclick="login()"
 *  - 前端零校验、无防重复提交、无 loading 态、无 AJAX error 回调
 *  - 提交后：成功 -> 写 localStorage.user_token 并跳 blog_list.html
 *             失败 -> alert(errMsg)
 */
export class LoginPage {
  readonly page: Page;
  readonly username: Locator;
  readonly password: Locator;
  readonly submit: Locator;
  readonly dialogTitle: Locator;

  constructor(page: Page) {
    this.page = page;
    this.username = page.locator(SELECTORS.username);
    this.password = page.locator(SELECTORS.password);
    this.submit = page.locator(SELECTORS.submit);
    this.dialogTitle = page.locator(SELECTORS.dialogTitle);
  }

  async goto(): Promise<void> {
    await this.page.goto(ROUTES.login);
    await expect(this.submit).toBeVisible();
  }

  /** 只填表单，不提交 */
  async fill(username: string, password: string): Promise<void> {
    await this.username.fill(username);
    await this.password.fill(password);
  }

  /**
   * 通过界面提交并捕获 /user/login 的响应。
   *
   * 实现要点：登录成功时页面会立即 location.href 跳转，
   * 跳转后原响应体在任何时机都读不到（Network.getResponseBody 已失效）。
   * 因此这里用 page.route 在路由层拦截：先由路由自己取回响应体，
   * 再 fulfill 且**去掉跳转脚本执行的时序依赖** —— 路由内拿到的是原始 JSON。
   *
   * 由于 fulfill 后页面仍会跳转，断言所需数据在跳转前已存入 captured。
   */
  async submitAndCapture(): Promise<LoginApiResult> {
    let captured: LoginApiResult | null = null;
    let handlerDone: Promise<void> = Promise.resolve();

    const handler = async (route: Route) => {
      // 已是后续请求则直接放行，只拦截第一次
      if (captured) {
        await route.continue();
        return;
      }
      const response = await route.fetch();
      const text = await response.text();
      let body: LoginApiResult['body'];
      try {
        body = JSON.parse(text);
      } catch {
        body = { code: 'PARSE_ERROR', errMsg: text.slice(0, 200), data: null };
      }
      captured = { status: response.status(), body };
      // 带上原响应 headers（尤其 Content-Type: application/json），
      // 否则 jQuery 收不到 JSON，成功分支不执行，页面就不跳转。
      await route.fulfill({
        status: response.status(),
        headers: response.headers(),
        body: text,
      });
    };

    await this.page.route(`**${ROUTES.loginApi}`, (route) => {
      handlerDone = handler(route);
      return handlerDone;
    });

    await this.submit.click();
    // 等捕获完成（最多 10 秒）
    for (let i = 0; i < 500 && !captured; i++) {
      await this.page.waitForTimeout(20);
    }

    // 关键：必须等 fulfill 真正执行完再解除拦截。
    // 若在 fulfill 尚未完成时就 unroute，请求会悬空，页面永远不跳转，
    // 表现为"接口明明是 SUCCESS 却不跳转"的偶发失败。
    await handlerDone.catch(() => undefined);

    const snapshot: LoginApiResult | null = captured;
    if (!snapshot) throw new Error('未捕获到 /user/login 响应');
    return snapshot;
  }

  /**
   * 注册一次性 alert 监听并返回 Promise<弹窗文案>。
   * alert 是原生阻塞弹窗，会挂起页面 JS，必须先注册监听再点击提交。
   */
  expectAlert(): Promise<string> {
    return new Promise<string>((resolve) => {
      this.page.once('dialog', async (dialog) => {
        const message = dialog.message();
        await dialog.dismiss();
        resolve(message);
      });
    });
  }

  /** 通过界面完成一次成功登录（含跳转等待） */
  async login(username: string, password: string): Promise<void> {
    await this.goto();
    await this.fill(username, password);
    await Promise.all([
      this.page.waitForURL(`**${ROUTES.list}`),
      this.submit.click(),
    ]);
  }

  /** 读取当前 localStorage 中的 token */
  async token(): Promise<string | null> {
    return this.page.evaluate(() => localStorage.getItem('user_token'));
  }

  async clearToken(): Promise<void> {
    await this.page.evaluate(() => localStorage.clear());
  }

  /** 表单输入框是否带必填约束（当前为 false，用于记录体验缺陷） */
  async requiredAttrs(): Promise<{ username: boolean; password: boolean }> {
    return this.page.evaluate(() => ({
      username: (document.querySelector('#username') as HTMLInputElement).required,
      password: (document.querySelector('#password') as HTMLInputElement).required,
    }));
  }

  /** 整页是否存在 <form> 元素 */
  async hasFormElement(): Promise<boolean> {
    return this.page.evaluate(() => document.querySelectorAll('form').length > 0);
  }
}

/**
 * 直接调用登录接口，绕过浏览器交互（用于接口层校验与安全用例）。
 *
 * 使用 Playwright 的 APIRequestContext，而不是 page.evaluate + fetch：
 * 后者依赖页面上下文存活，页面跳转或关闭时会抛 "Failed to fetch"。
 */
export async function postLoginApi(
  request: APIRequestContext,
  username: string,
  password: string,
): Promise<LoginApiResult> {
  const response = await request.post(ROUTES.loginApi, {
    form: { username, password },
  });

  const text = await response.text();
  let body: LoginApiResult['body'];
  try {
    body = JSON.parse(text);
  } catch {
    body = { code: 'PARSE_ERROR', errMsg: text.slice(0, 200), data: null };
  }
  return { status: response.status(), body };
}
