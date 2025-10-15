import '@testing-library/jest-dom';

// Polyfill matchMedia for components relying on media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Polyfill ResizeObserver if missing
if (!(globalThis as any).ResizeObserver) {
  (globalThis as any).ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// Provide a minimal import.meta.env for code that reads Vite envs
// ts-jest doesn't support import.meta by default; components read import.meta.env at runtime.
(globalThis as any).import = { meta: { env: { VITE_API_BASE_URL: 'http://localhost:8000' } } } as any;

// JSDOM doesn't support :has in querySelector; our PopoverContent uses it for positioning.
// In tests, we can no-op the effect by stubbing document.querySelector when called with that selector.
const origQuerySelector = document.querySelector.bind(document);
document.querySelector = ((selectors: string) => {
  if (selectors.includes(':has(.popover-notificaciones)')) {
    return null as any;
  }
  return origQuerySelector(selectors);
}) as any;
