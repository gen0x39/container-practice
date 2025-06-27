import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { tap } from 'rxjs/operators';
import { LogService } from '../services/log.service';

export const LoggingInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const logService = inject(LogService);
  const startTime = Date.now();
  const requestId = Math.random().toString(36).substring(2, 15);

  logService.info(
    'http_request_start',
    `HTTP request started: ${request.method} ${request.url}`,
    {
      request_id: requestId,
      method: request.method,
      url: request.url,
      headers: sanitizeHeaders(request.headers),
      body: request.body ? 'present' : 'none'
    }
  );

  return next(request).pipe(
    tap({
      next: (event) => {
        if (event instanceof HttpResponse) {
          const responseTime = Date.now() - startTime;
          
          logService.info(
            'http_request_success',
            `HTTP request completed: ${request.method} ${request.url}`,
            {
              request_id: requestId,
              method: request.method,
              url: request.url,
              status_code: event.status,
              response_time_ms: responseTime,
              response_size_bytes: getResponseSize(event),
              response_type: getResponseType(event)
            }
          );
        }
      },
      error: (error: HttpErrorResponse) => {
        const responseTime = Date.now() - startTime;
        
        logService.error(
          'http_request_error',
          `HTTP request failed: ${request.method} ${request.url}`,
          {
            request_id: requestId,
            method: request.method,
            url: request.url,
            status_code: error.status,
            response_time_ms: responseTime,
            error_message: error.message,
            error_type: error.name
          }
        );
      }
    })
  );
};

function sanitizeHeaders(headers: any): any {
  const sanitized: any = {};
  headers.keys().forEach((key: string) => {
    if (!['authorization', 'cookie'].includes(key.toLowerCase())) {
      sanitized[key] = headers.get(key);
    }
  });
  return sanitized;
}

function getResponseSize(response: HttpResponse<any>): number {
  return response.body ? JSON.stringify(response.body).length : 0;
}

function getResponseType(response: HttpResponse<any>): string {
  if (response.body) {
    return Array.isArray(response.body) ? 'array' : typeof response.body;
  }
  return 'empty';
}
