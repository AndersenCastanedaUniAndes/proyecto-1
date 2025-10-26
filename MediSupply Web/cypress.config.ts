// cypress.config.ts
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://136.112.245.46',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
    chromeWebSecurity: false,          // ← importante para cross-origin
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 15000,
    pageLoadTimeout: 30000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    env: {
      AUTH_8000: 'http://136.112.245.46:8000',
      WRONG_AUTH_8001: 'http://136.112.245.46:8001',
    },
  },
})
