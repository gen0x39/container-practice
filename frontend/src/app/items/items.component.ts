// src/app/items/items.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';
import { LogService } from '../services/log.service';
import { FormsModule } from '@angular/forms';
import { EventEmitter, Output } from '@angular/core';

interface AsciiArt {
  id: number;
  title: string;
  content: string;
  category: string;
  author: string;
  likes: number;
  timestamp: string;
  tweet: string;
  like: number;
  rt: number;
}

interface Tweet {
  tweet: string;
  like: number;
  rt: number;
  id: string;
  title: string;
  category: string;
  author: string;
  timestamp: string;
  filename: string;
}

interface TweetRequest {
  content: string;
  author: string;
  category: string;
}

@Component({
  selector: 'app-items',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <div class="twitter-container">
    <!-- Twitterライクなヘッダー -->
    <div class="header">
      <h1>🐦 ASCII Twitter</h1>
      <p>ASCIIアートでつぶやこう！</p>
    </div>

    <div class="main-content">
      <!-- 投稿フォーム -->
      <div class="post-form">
        <div class="post-header">
          <div class="user-avatar">👤</div>
          <div class="post-input-container">
            <textarea 
              class="post-textarea" 
              placeholder="ASCIIアートでつぶやいてみよう..."
              [(ngModel)]="newPost"
              maxlength="280"
            ></textarea>
            <div class="post-footer">
              <span class="char-count" [class.char-limit]="newPost.length > 260">
                {{ newPost.length }}/280
              </span>
              <button 
                class="post-btn" 
                [disabled]="!newPost.trim() || newPost.length > 280 || isPosting"
                (click)="submitPost()"
              >
                {{ isPosting ? '投稿中...' : '🐦 ツイート' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="compose-container">
        <h3>画像からアスキーアートを投稿</h3>
        <div class="image-upload-area"
            [class.drag-over]="isDragOver"
            (dragover)="onDragOver($event)"
            (dragleave)="onDragLeave($event)"
            (drop)="onDrop($event)">
          <input type="file" accept="image/*" (change)="onFileSelected($event)" #fileInput hidden />
          <button type="button" (click)="fileInput.click()">画像を選択</button>
          <span *ngIf="selectedImage" class="preview-label">プレビュー:</span>
          <img *ngIf="selectedImage" [src]="selectedImage" class="image-preview" />
          <button *ngIf="selectedImage" type="button" (click)="removeImage()">画像を削除</button>
        </div>
        <button class="upload-btn" [disabled]="!imageFile || isUploading" (click)="uploadImage()">
          {{ isUploading ? 'アップロード中...' : '画像をアスキーアート化して投稿' }}
        </button>
      </div>

      <!-- ツイートタイムライン -->
      <div class="timeline">
        <h2>ツイート</h2>
        <div *ngIf="isLoading" class="loading">読み込み中...</div>
        
        <div *ngFor="let tweet of tweets" class="tweet">
          <div class="tweet-header">
            <div class="user-info">
              <div class="user-avatar">👤</div>
              <div class="user-details">
                <span class="username">{{ tweet.author }}</span>
                <span class="timestamp">· {{ tweet.timestamp | date:'short' }}</span>
              </div>
            </div>
            <span class="category">{{ tweet.category }}</span>
          </div>
          
          <div class="tweet-content">
            <h3 class="tweet-title">{{ tweet.title }}</h3>
            <pre class="ascii-art">{{ tweet.tweet }}</pre>
          </div>
          
          <div class="tweet-actions">
            <button class="action-btn like-btn" (click)="likeTweet(tweet)">
              <span class="action-icon" [class.liked]="tweet.like > 0">❤️</span>
              <span class="action-count">{{ tweet.like }}</span>
            </button>
            <button class="action-btn retweet-btn" (click)="retweetTweet(tweet)">
              <span class="action-icon">🔄</span>
              <span class="action-count">{{ tweet.rt }}</span>
            </button>
            <button class="action-btn reply-btn">
              <span class="action-icon">💬</span>
              <span class="action-count">0</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ASCIIアートタイムライン -->
      <div class="timeline">
        <h2>ASCIIアート</h2>
        <div *ngFor="let art of asciiArts" class="tweet">
          <div class="tweet-header">
            <div class="user-info">
              <div class="user-avatar">👤</div>
              <div class="user-details">
                <span class="username">{{ art.author }}</span>
                <span class="timestamp">· {{ art.timestamp | date:'short' }}</span>
              </div>
            </div>
            <span class="category">{{ art.category }}</span>
          </div>
          
          <div class="tweet-content">
            <h3 class="tweet-title">{{ art.title }}</h3>
            <pre class="ascii-art">{{ art.tweet || art.content }}</pre>
          </div>
          
          <div class="tweet-actions">
            <button class="action-btn like-btn" (click)="likeArt(art)">
              <span class="action-icon" [class.liked]="(art.like || art.likes) > 0">❤️</span>
              <span class="action-count">{{ art.like || art.likes }}</span>
            </button>
            <button class="action-btn retweet-btn">
              <span class="action-icon">🔄</span>
              <span class="action-count">{{ art.rt || 0 }}</span>
            </button>
            <button class="action-btn reply-btn">
              <span class="action-icon">💬</span>
              <span class="action-count">0</span>
            </button>
          </div>
        </div>
      </div>
    </div>
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
      max-width: 900px;  /* 600pxから900pxに変更 */
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
  tweets: Tweet[] = [];
  newPost: string = '';
  isPosting: boolean = false;
  isLoading: boolean = false;

  selectedImage: string | ArrayBuffer | null = null;
  imageFile: File | null = null;
  isUploading: boolean = false;
  isDragOver: boolean = false;
  @Output() asciiArtPosted = new EventEmitter<any>();

  constructor(
    private http: HttpClient,
    private logService: LogService
  ) { }

  /*
ngOnInit() {
  this.logService.info(
    'component_init',
    'ItemsComponent initialized',
    { component: 'ItemsComponent' }
  );
  this.loadAllAsciiArt();
}*/

  ngOnInit() {
    this.loadAllAsciiArt();
    this.loadAllTweets();
  }

  private loadAllTweets() {
    this.isLoading = true;
    this.http.get<Tweet[]>(`${environment.apiUrl}/tweets`)
      .subscribe({
        next: (data) => {
          this.tweets = data;
          this.logService.log('ツイートを読み込みました', String(data.length));
        },
        error: (error) => {
          console.error('ツイートの読み込みに失敗しました:', error);
          this.logService.log('ツイートの読み込みに失敗しました', error);
        },
        complete: () => {
          this.isLoading = false;
        }
      });
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
            timestamp: art.timestamp || this.randomPastTime(),
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
    // いいね機能の実装（実際のアプリではAPIを呼び出してデータベースを更新）
    if (art.like !== undefined) {
      art.like++;
    } else if (art.likes !== undefined) {
      art.likes++;
    }
  }

  likeTweet(tweet: Tweet) {
    // ツイートのいいね機能
    tweet.like++;
  }
  retweetTweet(tweet: Tweet) {
    // リツイート機能
    tweet.rt++;
  }

  submitPost() {
    if (!this.newPost.trim() || this.isPosting) return;

    this.isPosting = true;
    const tweetData = {
      content: this.newPost,
      author: "ユーザー",
      category: "ユーザー投稿"
    };

    this.http.post<Tweet>(`${environment.apiUrl}/tweet`, tweetData)
      .subscribe({
        next: (response) => {
          this.tweets.unshift(response); // 新しいツイートを先頭に追加
          this.newPost = '';
          this.logService.log('ツイートを投稿しました', String(response));
        },
        error: (error) => {
          console.error('ツイートの投稿に失敗しました:', error);
          this.logService.log('ツイートの投稿に失敗しました', error);
        },
        complete: () => {
          this.isPosting = false;
        }
      });
  }

  // ダミーの過去時間を生成
  private randomPastTime(): string {
    const mins = Math.floor(Math.random() * 59) + 1;
    return `${mins}分前`;
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.imageFile = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.selectedImage = e.target?.result || null;
      };
      reader.readAsDataURL(this.imageFile);
    }
  }

  removeImage() {
    this.selectedImage = null;
    this.imageFile = null;
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      this.imageFile = event.dataTransfer.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.selectedImage = e.target?.result || null;
      };
      reader.readAsDataURL(this.imageFile);
    }
  }

  uploadImage() {
    if (!this.imageFile) return;
    this.isUploading = true;
    const apiUrl = environment.apiUrl || 'http://localhost:8000';
    const formData = new FormData();
    formData.append('file', this.imageFile);
    formData.append('author', 'あなた');
    formData.append('category', '画像変換');

    this.http.post<any>(`${apiUrl}/upload-image`, formData)
      .subscribe({
        next: (res) => {
          this.asciiArtPosted.emit({ ...res, timestamp: '今' });
          this.removeImage();
          this.isUploading = false;
        },
        error: (error) => {
          this.isUploading = false;
          alert('画像のアップロードまたは変換に失敗しました');
        }
      });
  }
} 
