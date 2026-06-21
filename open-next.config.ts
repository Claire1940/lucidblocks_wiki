import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig({
  // 默认配置：SSR on Workers，静态资源走 assets 绑定。
  // 缓存（ISR）暂不接入 KV/R2，试点先验证基础 SSR 渲染。
});
