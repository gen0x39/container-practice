import { Injectable } from '@angular/core';

export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  event_type: string;
  message: string;
  service: string;
  version: string;
  trace_id: string;
  span_id: string;
  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class LogService {
  
  private generateTraceId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  private generateSpanId(): string {
    return Math.random().toString(36).substring(2, 18);
  }

  log(event_type: string, message: string, level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG' = 'INFO', data?: any) {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      event_type,
      message,
      service: 'ascii-twitter-frontend',
      version: '1.0.0',
      trace_id: this.generateTraceId(),
      span_id: this.generateSpanId(),
      ...data
    };
    
    // 標準出力にJSON形式で出力
    console.log(JSON.stringify(logEntry));
  }

  info(event_type: string, message: string, data?: any) {
    this.log(event_type, message, 'INFO', data);
  }

  warn(event_type: string, message: string, data?: any) {
    this.log(event_type, message, 'WARN', data);
  }

  error(event_type: string, message: string, data?: any) {
    this.log(event_type, message, 'ERROR', data);
  }

  debug(event_type: string, message: string, data?: any) {
    this.log(event_type, message, 'DEBUG', data);
  }
}
