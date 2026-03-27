/**
 * tools/standalone/xml-to-markdown/src/utils/logger.js
 * ======================================================
 * 
 * Purpose:
 *   Logging utilities with environment-aware configuration. Provides
 *   test-mode logging that captures messages for verification.
 * 
 * Exports:
 *   - createLoggerForEnvironment(): Factory for test/production loggers
 *   - log, error, warn, info: Default logger methods
 * 
 * @module logger
 */

/**
 * Creates a logger based on the environment
 * @param {Object} options - Logger options
 * @param {boolean} options.isTestMode - Whether to create a test logger
 * @returns {Object} Logger object
 */
export function createLoggerForEnvironment(options = { isTestMode: false }) {
    if (options.isTestMode) {
        const messages = [];
        return {
            log: (message) => messages.push(message),
            error: (message) => messages.push(`ERROR: ${message}`),
            warn: (message) => messages.push(`WARN: ${message}`),
            info: (message) => messages.push(`INFO: ${message}`),
            getMessages: () => messages,
            clear: () => messages.length = 0
        };
    } else {
        return {
            log: (message) => console.log(message),
            error: (message) => console.error(message),
            warn: (message) => console.warn(message),
            info: (message) => console.info(message)
        };
    }
}

// Create a default logger for non-test environments
const defaultLogger = createLoggerForEnvironment();
export const { log, error, warn, info } = defaultLogger; 