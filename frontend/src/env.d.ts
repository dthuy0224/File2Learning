/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // If you have additional env variables, declare them here
  readonly VITE_SOME_OTHER_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
