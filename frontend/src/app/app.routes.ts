import { Routes } from '@angular/router';
import { App } from './app';
import { ItemsComponent } from './items/items.component';

export const routes: Routes = [
  { path: '', component: App },
  { path: 'items', component: ItemsComponent }
];

