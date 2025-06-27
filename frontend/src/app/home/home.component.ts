import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  template: `
    <h1>トップページ</h1>
    <div class="navigation">
      <a routerLink="/items" class="nav-link">Itemsページへ</a>
      <a routerLink="/health" class="nav-link">Health Check</a>
    </div>
  `
})
export class HomeComponent {}
