/**
 * Frontend logging utility with environment-aware behavior.
 * Provides structured logging with different log levels.
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  [key: string]: any;
}

class Logger {
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development';
  }

  private shouldLog(level: LogLevel): boolean {
    if (this.isDevelopment) {
      return true; // Log everything in development
    }
    // In production, only log warnings and errors
    return level === 'warn' || level === 'error';
  }

  private formatMessage(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  private log(level: LogLevel, message: string, context?: LogContext, error?: Error): void {
    if (!this.shouldLog(level)) {
      return;
    }

    const formattedMessage = this.formatMessage(level, message, context);

    if (this.isDevelopment) {
      // Use styled console output in development
      const styles: Record<LogLevel, string> = {
        debug: 'color: #6B7280; font-weight: normal',
        info: 'color: #10B981; font-weight: normal',
        warn: 'color: #F59E0B; font-weight: bold',
        error: 'color: #EF4444; font-weight: bold',
      };

      if (context) {
        console.log(`%c${formattedMessage}`, styles[level], context);
      } else {
        console.log(`%c${formattedMessage}`, styles[level]);
      }

      if (error) {
        console.error('Error details:', error);
        if (error.stack) {
          console.error('Stack trace:', error.stack);
        }
      }
    } else {
      // Minimal logging in production
      switch (level) {
        case 'warn':
          console.warn(formattedMessage, context || '');
          break;
        case 'error':
          console.error(formattedMessage, context || '', error || '');
          break;
        default:
          // Should not reach here due to shouldLog check, but just in case
          break;
      }
    }
  }

  debug(message: string, context?: LogContext): void {
    this.log('debug', message, context);
  }

  info(message: string, context?: LogContext): void {
    this.log('info', message, context);
  }

  warn(message: string, context?: LogContext): void {
    this.log('warn', message, context);
  }

  error(message: string, context?: LogContext, error?: Error): void {
    this.log('error', message, context, error);
  }
}

// Export singleton instance
export const logger = new Logger();
