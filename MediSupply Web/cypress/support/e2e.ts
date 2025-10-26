// cypress/support/e2e.ts
import './commands'

beforeEach(() => {
  const WRONG = `${Cypress.env('WRONG_AUTH_8001') || 'http://136.112.245.46:8001'}/token`
  const GOOD  = `${Cypress.env('AUTH_8000')       || 'http://136.112.245.46:8000'}/token`

  // 1) Preflight (CORS) → responde 204 y evita que llegue a 8001
  cy.intercept('OPTIONS', WRONG, { statusCode: 204 }).as('preflight_login')

  // 2) POST /token → reescribe a 8000 y continúa
  cy.intercept({ method: 'POST', url: WRONG }, (req) => {
    // Log para que lo veas en el runner
    // eslint-disable-next-line no-console
    console.log('🔁 Rewriting', req.url, '→', GOOD)
    req.url = GOOD
    req.continue()
  }).as('login')
})
