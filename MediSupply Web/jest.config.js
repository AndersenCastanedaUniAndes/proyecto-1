module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  collectCoverage: true,
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  collectCoverageFrom: [
    'src/components/LoginForm.tsx',
    'src/components/ForgotPasswordForm.tsx',
    'src/components/InventarioView.tsx',
    'src/components/figma/**/*.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json', 'node'],
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
  coverageDirectory: 'coverage',
  testMatch: ['<rootDir>/src/tests/**/*.(test|spec).(ts|tsx|js|jsx)'],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
  moduleNameMapper: {
    '^../config/config$': '<rootDir>/src/tests/__mocks__/configMock.ts',
    '^../components/ui/popover$': '<rootDir>/src/tests/__mocks__/popover.tsx',
    '^\./ui/popover$': '<rootDir>/src/tests/__mocks__/popover.tsx',
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};