// Invisible Cloudflare Turnstile check, only used for the demo login button.
// Falls back to Cloudflare's always-pass invisible test key in dev.
const SITE_KEY =
  import.meta.env.VITE_TURNSTILE_SITE_KEY || "1x00000000000000000000BB";

type Turnstile = {
  render: (
    container: HTMLElement,
    options: {
      sitekey: string;
      appearance: string;
      callback: (token: string) => void;
      "error-callback": () => void;
    }
  ) => string;
  remove: (widgetId: string) => void;
};

declare global {
  interface Window {
    turnstile?: Turnstile;
  }
}

let scriptPromise: Promise<void> | null = null;

const loadScript = () => {
  if (!scriptPromise) {
    scriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src =
        "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => {
        scriptPromise = null;
        reject(new Error("Couldn't load Turnstile"));
      };
      document.head.appendChild(script);
    });
  }
  return scriptPromise;
};

export const getTurnstileToken = async (): Promise<string> => {
  await loadScript();
  const turnstile = window.turnstile!;
  const container = document.createElement("div");
  document.body.appendChild(container);

  return new Promise((resolve, reject) => {
    const cleanup = () =>
      setTimeout(() => {
        turnstile.remove(widgetId);
        container.remove();
      });
    const widgetId = turnstile.render(container, {
      sitekey: SITE_KEY,
      appearance: "interaction-only",
      callback: (token) => {
        cleanup();
        resolve(token);
      },
      "error-callback": () => {
        cleanup();
        reject(new Error("Turnstile check failed"));
      },
    });
  });
};
