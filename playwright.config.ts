import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置 —— 博客系统登录页自动化
 *
 * 运行前置条件：被测环境 http://127.0.0.1:9090 已启动。
 * 可通过环境变量覆盖：
 *   BASE_URL        被测地址前缀
 *   LOGIN_USERNAME  有效账号（默认 zhangsan）
 *   LOGIN_PASSWORD  有效密码（默认 123456）
 */
export default defineConfig({
  testDir: './tests',
  // 登录用例会写 localStorage / 触发跳转，用例之间保持隔离串行执行
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: 0,
  timeout: 30_000,
  expect: { timeout: 8_000 },

  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],

  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:9090',
    headless: true,
    actionTimeout: 10_000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'off',
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        locale: 'zh-CN',
        timezoneId: 'Asia/Shanghai',
      },
    },
  ],
});
