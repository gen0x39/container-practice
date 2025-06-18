import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router'; // RouterLinkを追加

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink], // RouterLinkを追加
  template: `
    <h1>トップページ</h1>
    <a routerLink="/items">Itemsページへ</a>
    <router-outlet></router-outlet>
  `
})
export class App { }


/*
@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected title = 'frontend';
}*/
