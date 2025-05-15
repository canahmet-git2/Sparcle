import * as path from 'path';
import * as fs from 'fs';

class ErrorLogger {
  private static instance: ErrorLogger;
  private logFile: string;
  private errors: Array<{
    timestamp: string;
    type: string;
    message: string;
    stack?: string;
    componentName?: string;
  }> = [];

  private constructor() {
    // In development or web environment, log to the project directory
    const logDir = process.cwd();

    try {
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
      this.logFile = path.join(logDir, 'error.log');
    } catch (error) {
      console.warn('Failed to create error log file:', error);
      this.logFile = ''; // Will only log to memory and console
    }
  }

  public static getInstance(): ErrorLogger {
    if (!ErrorLogger.instance) {
      ErrorLogger.instance = new ErrorLogger();
    }
    return ErrorLogger.instance;
  }

  public logError(error: Error, type: string = 'General', componentName?: string) {
    const errorEntry = {
      timestamp: new Date().toISOString(),
      type,
      message: error.message,
      stack: error.stack,
      componentName
    };

    this.errors.push(errorEntry);

    // Always log to console in development
    console.error(`[${type}]${componentName ? ` (${componentName})` : ''}: ${error.message}`);
    if (error.stack) {
      console.error(error.stack);
    }

    // Try to write to file if available
    if (this.logFile) {
      try {
        const logEntry = `[${errorEntry.timestamp}] ${type}${componentName ? ` (${componentName})` : ''}\n${error.message}\n${error.stack || ''}\n\n`;
        fs.appendFileSync(this.logFile, logEntry);
      } catch (error) {
        console.warn('Failed to write to error log file:', error);
      }
    }
  }

  public getRecentErrors(count: number = 10): Array<{
    timestamp: string;
    type: string;
    message: string;
    componentName?: string;
  }> {
    return this.errors.slice(-count);
  }

  public clearErrors() {
    this.errors = [];
    // Try to clear the log file if available
    if (this.logFile) {
      try {
        fs.writeFileSync(this.logFile, '');
      } catch (error) {
        console.warn('Failed to clear error log file:', error);
      }
    }
  }
}

export const errorLogger = ErrorLogger.getInstance();

// Helper function to wrap async functions with error logging
export function withErrorLogging<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  componentName?: string
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      errorLogger.logError(error as Error, 'Async Error', componentName);
      throw error;
    }
  }) as T;
}

// Helper function to wrap component methods with error logging
export function withComponentErrorLogging<T extends (...args: any[]) => any>(
  fn: T,
  componentName: string
): T {
  return ((...args: Parameters<T>) => {
    try {
      return fn(...args);
    } catch (error) {
      errorLogger.logError(error as Error, 'Component Error', componentName);
      throw error;
    }
  }) as T;
} 