import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router'; // RouterLinkを追加
import { HttpClient } from '@angular/common/http'; // 追加
import { PodInfoComponent } from './pod-info/pod-info.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, PodInfoComponent],
  template: `
    <h1>トップページ</h1>
    <app-pod-info></app-pod-info>

    <div class="navigation">
      <a routerLink="/items" class="nav-link">Itemsページへ</a>
      <a routerLink="/health" class="nav-link">Health Check</a>
    </div>
    <router-outlet></router-outlet>
  `
})
export class App { }
