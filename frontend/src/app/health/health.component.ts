import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { LogService } from '../services/log.service';
import { environment } from '../../environments/environment';

interface HealthResponse {
  status: string;
  timestamp: string;
  request_id: string;
  response_time_ms: number;
  system: {
    hostname: string;
    pod_name: string;
    node_name: string;
    environment: string;
    python_version: string;
  };
  ascii_art: {
    files_count: number;
    total_size_bytes: number;
    directory_exists: boolean;
  };
  memory: {
    available_mb: number;
  };
}

@Component({
  selector: 'app-health',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="health-container">
      <h2>🏥 ヘルスチェック</h2>
      
      <!-- フロントエンドヘルス -->
      <div class="health-section">
        <h3>フロントエンド</h3>
        <div class="health-status">
          <div class="status-item">
            <span class="status-label">ステータス:</span>
            <span class="status-value healthy">Healthy</span>
          </div>
          <div class="status-item">
            <span class="status-label">タイムスタンプ:</span>
            <span class="status-value">{{ frontendTime }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">バージョン:</span>
            <span class="status-value">1.0.0</span>
          </div>
        </div>
      </div>

      <!-- バックエンドヘルス -->
      <div class="health-section">
        <h3>バックエンド</h3>
        <div class="health-status" *ngIf="!loading && !error">
          <div class="status-item">
            <span class="status-label">ステータス:</span>
            <span class="status-value" [class.healthy]="backendHealth?.status === 'healthy'" [class.unhealthy]="backendHealth?.status !== 'healthy'">
              {{ backendHealth?.status || 'Unknown' }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">レスポンス時間:</span>
            <span class="status-value">{{ backendHealth?.response_time_ms }}ms</span>
          </div>
          <div class="status-item">
            <span class="status-label">ホスト名:</span>
            <span class="status-value">{{ backendHealth?.system?.hostname }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">Pod名:</span>
            <span class="status-value">{{ backendHealth?.system?.pod_name }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">ASCIIファイル数:</span>
            <span class="status-value">{{ backendHealth?.ascii_art?.files_count }}</span>
          </div>
        </div>
        
        <div class="loading" *ngIf="loading">
          <p>バックエンドヘルスチェック中...</p>
        </div>
        
        <div class="error" *ngIf="error">
          <p>エラー: {{ error }}</p>
        </div>
      </div>

      <!-- リクエスト/レスポンス詳細 -->
      <div class="health-section" *ngIf="backendHealth">
        <h3>リクエスト/レスポンス詳細</h3>
        <div class="request-details">
          <div class="detail-item">
            <span class="detail-label">リクエストID:</span>
            <span class="detail-value">{{ backendHealth.request_id }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">リクエストURL:</span>
            <span class="detail-value">{{ requestUrl }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">リクエスト時刻:</span>
            <span class="detail-value">{{ requestTime }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">レスポンス時刻:</span>
            <span class="detail-value">{{ responseTime }}</span>
          </div>
        </div>
        
        <div class="response-json">
          <h4>レスポンスJSON:</h4>
          <pre>{{ responseJson }}</pre>
        </div>
      </div>

      <!-- リフレッシュボタン -->
      <div class="actions">
        <button class="refresh-btn" (click)="checkBackendHealth()" [disabled]="loading">
          {{ loading ? 'チェック中...' : 'バックエンドヘルスチェック' }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .health-container {
      max-width: 800px;
      margin: 30px auto;
      padding: 30px;
      background: white;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    h2 {
      color: #333;
      text-align: center;
      margin-bottom: 30px;
      font-size: 2rem;
    }
    
    .health-section {
      margin-bottom: 40px;
      padding: 20px;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      background: #fafafa;
    }
    
    .health-section h3 {
      color: #555;
      margin-bottom: 20px;
      font-size: 1.3rem;
      border-bottom: 2px solid #007bff;
      padding-bottom: 10px;
    }
    
    .health-status {
      margin-bottom: 20px;
    }
    
    .status-item, .detail-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #eee;
    }
    
    .status-item:last-child, .detail-item:last-child {
      border-bottom: none;
    }
    
    .status-label, .detail-label {
      font-weight: 600;
      color: #555;
      min-width: 150px;
    }
    
    .status-value, .detail-value {
      color: #333;
      font-family: 'Courier New', monospace;
    }
    
    .status-value.healthy {
      color: #28a745;
      font-weight: 600;
    }
    
    .status-value.unhealthy {
      color: #dc3545;
      font-weight: 600;
    }
    
    .loading {
      text-align: center;
      color: #666;
      font-style: italic;
    }
    
    .error {
      color: #dc3545;
      background: #f8d7da;
      padding: 15px;
      border-radius: 5px;
      border: 1px solid #f5c6cb;
    }
    
    .request-details {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
    }
    
    .response-json {
      background: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 5px;
      padding: 15px;
    }
    
    .response-json h4 {
      margin-top: 0;
      color: #495057;
    }
    
    .response-json pre {
      background: #2d3748;
      color: #e2e8f0;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
      font-size: 0.9rem;
      line-height: 1.4;
    }
    
    .actions {
      text-align: center;
      margin-top: 30px;
    }
    
    .refresh-btn {
      background: #007bff;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.3s;
    }
    
    .refresh-btn:hover:not(:disabled) {
      background: #0056b3;
    }
    
    .refresh-btn:disabled {
      background: #6c757d;
      cursor: not-allowed;
    }
  `]
})
export class HealthComponent implements OnInit {
  frontendTime: string = '';
  backendHealth: HealthResponse | null = null;
  loading: boolean = false;
  error: string = '';
  requestUrl: string = '';
  requestTime: string = '';
  responseTime: string = '';
  responseJson: string = '';

  constructor(
    private http: HttpClient,
    private logService: LogService
  ) {}

  ngOnInit() {
    // フロントエンドヘルス情報を設定
    this.frontendTime = new Date().toISOString();
    
    // フロントエンドヘルスログを出力
    this.logService.info(
      'frontend_health_check',
      'Frontend health check page accessed',
      {
        component: 'HealthComponent',
        timestamp: this.frontendTime,
        status: 'healthy',
        version: '1.0.0',
        environment: 'development'
      }
    );
    
    // バックエンドヘルスチェックを実行
    this.checkBackendHealth();
  }

  checkBackendHealth() {
    this.loading = true;
    this.error = '';
    this.requestTime = new Date().toISOString();
    this.requestUrl = `${environment.apiUrl}/health`;

    this.logService.info(
      'backend_health_request_start',
      'Backend health check request started',
      {
        component: 'HealthComponent',
        request_url: this.requestUrl,
        request_time: this.requestTime
      }
    );

    this.http.get<HealthResponse>(this.requestUrl)
      .subscribe({
        next: (response) => {
          this.responseTime = new Date().toISOString();
          this.backendHealth = response;
          this.responseJson = JSON.stringify(response, null, 2);
          
          this.logService.info(
            'backend_health_request_success',
            'Backend health check completed successfully',
            {
              component: 'HealthComponent',
              response_time: this.responseTime,
              response_time_ms: response.response_time_ms,
              status: response.status,
              request_id: response.request_id
            }
          );
          
          this.loading = false;
        },
        error: (err) => {
          this.responseTime = new Date().toISOString();
          this.error = err.message || 'Unknown error';
          this.responseJson = JSON.stringify(err, null, 2);
          
          this.logService.error(
            'backend_health_request_error',
            'Backend health check failed',
            {
              component: 'HealthComponent',
              response_time: this.responseTime,
              error_message: this.error,
              error_status: err.status,
              request_url: this.requestUrl
            }
          );
          
          this.loading = false;
        }
      });
  }
}
