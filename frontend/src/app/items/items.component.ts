// src/app/items/items.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';
import { LogService } from '../services/log.service';

interface AsciiArt {
  id: number;
  title: string;
  content: string;
  category: string;
  author: string;
  likes: number;
  timestamp: string;
}

@Component({
  selector: 'app-items',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container">
      <h2>🎨 ASCIIアートギャラリー</h2>
      <ul class="ascii-list">
        <li *ngFor="let art of asciiArts" class="ascii-card">
          <div class="ascii-header">
            <h3 class="ascii-title">{{ art.title }}</h3>
            <span class="ascii-category">{{ art.category }}</span>
          </div>
          
          <div class="ascii-content">
            <pre class="ascii-art">{{ art.content }}</pre>
          </div>
          
          <div class="ascii-footer">
            <div class="ascii-author">
              <span class="author">�� {{ art.author }}</span>
            </div>
            
            <div class="ascii-actions">
              <button class="like-btn" (click)="likeArt(art)">
                ❤️ {{ art.likes }}
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  `,
  styles: [`
    .twitter-container {
      background: #e6ecf0;
      min-height: 100vh;
      font-family: 'Segoe UI', 'Arial', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .header {
      width: 100%;
      background: #1da1f2;
      color: white;
      padding: 32px 0 16px 0;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
      margin-bottom: 16px;
    }
    .header h1 {
      margin: 0;
      font-size: 2.2rem;
      font-weight: bold;
      letter-spacing: 2px;
    }
    .header p {
      margin: 8px 0 0 0;
      font-size: 1.1rem;
      opacity: 0.9;
    }
    .main-content {
      width: 100%;
      max-width: 600px;
      margin: 0 auto;
    }
    .post-form {
      display: flex;
      flex-direction: column;
      margin-bottom: 24px;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
      padding: 16px;
    }
    .post-textarea {
      width: 100%;
      min-height: 80px;
      font-family: 'Courier New', monospace;
      font-size: 1rem;
      margin-bottom: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 8px;
      resize: vertical;
    }
    .post-btn {
      align-self: flex-end;
      background: #1da1f2;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 8px 20px;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    .post-btn:hover {
      background: #0d8ddb;
    }
    .timeline {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .tweet {
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
      padding: 16px;
      display: flex;
      flex-direction: column;
    }
    .tweet-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .user-info {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .username {
      font-weight: bold;
      color: #1da1f2;
    }
    .timestamp {
      color: #888;
      font-size: 0.9rem;
    }
    .category {
      background: #e6ecf0;
      color: #1da1f2;
      border-radius: 12px;
      padding: 2px 10px;
      font-size: 0.85rem;
      font-weight: bold;
    }
    .tweet-content {
      margin-bottom: 8px;
    }
    .ascii-art {
      font-family: 'Courier New', monospace;
      font-size: 1.1rem;
      white-space: pre;
      background: #f7f7f7;
      border-radius: 4px;
      padding: 8px;
      overflow-x: auto;
    }
    .tweet-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
    .like-btn {
      background: none;
      border: none;
      color: #e0245e;
      font-size: 1.1rem;
      cursor: pointer;
      transition: color 0.2s;
    }
    .like-btn:hover {
      color: #ad1457;
    }
  `]
})
export class ItemsComponent implements OnInit {
  asciiArts: AsciiArt[] = [];
  newPost: string = '';

  constructor(
    private http: HttpClient,
    private logService: LogService
  ) { }

  ngOnInit() {
    this.logService.info(
      'component_init',
      'ItemsComponent initialized',
      { component: 'ItemsComponent' }
    );
    this.loadAllAsciiArt();
  }

  private loadAllAsciiArt() {
    const apiUrl = environment.apiUrl || 'http://localhost:8000';

    this.logService.info(
      'ascii_art_request_start',
      'Starting ASCII art request',
      { api_url: `${apiUrl}/ascii-all` }
    );

    this.http.get<AsciiArt[]>(`${apiUrl}/ascii-all`)
      .subscribe({
        next: (arts: AsciiArt[]) => {
          this.logService.info(
            'ascii_art_request_success',
            'ASCII art request completed successfully',
            {
              count: arts.length,
              arts: arts.map(art => ({
                id: art.id,
                title: art.title,
                content_length: art.content.length
              }))
            }
          );

          this.asciiArts = arts.map(art => ({
            ...art,
            timestamp: this.randomPastTime(),
          })).reverse();
        },
        error: (error) => {
          this.logService.error(
            'ascii_art_request_error',
            'ASCII art request failed',
            {
              error_message: error.message,
              error_type: error.name
            }
          );
        }
      });
  }

  likeArt(art: AsciiArt) {
    art.likes++;
  }

  submitPost() {
    if (!this.newPost.trim()) return;
    this.asciiArts.unshift({
      id: Date.now(),
      title: '新規投稿',
      content: this.newPost,
      category: 'ユーザー投稿',
      author: 'あなた',
      likes: 0,
      timestamp: '今'
    });
    this.newPost = '';
  }

  // ダミーの過去時間を生成
  private randomPastTime(): string {
    const mins = Math.floor(Math.random() * 59) + 1;
    return `${mins}分前`;
  }
}
