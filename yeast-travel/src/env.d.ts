/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_AMAP_KEY?: string;
  readonly PUBLIC_AMAP_SECURITY_CODE?: string;
  readonly PUBLIC_PLAUSIBLE_DOMAIN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  yeastTrack?: (name: string, props?: Record<string, string>) => void;
  plausible?: (name: string, options?: { props?: Record<string, string> }) => void;
}
