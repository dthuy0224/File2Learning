/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // 🧩 nếu bạn có thêm env khác, khai báo thêm ở đây
  readonly VITE_SOME_OTHER_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
