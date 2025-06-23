import { Routes } from '@angular/router';
import { App } from './app';
import { ItemsComponent } from './items/items.component';
import { HealthComponent } from './health/health.component';

export const routes: Routes = [
  { path: '', component: App },
  { path: 'items', component: ItemsComponent },
  { path: 'health', component: HealthComponent }
];

