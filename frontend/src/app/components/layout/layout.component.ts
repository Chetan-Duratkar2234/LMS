import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule
  ],
  template: `
    <div class="layout-container" [class.is-mobile]="mobileQuery.matches">
      <mat-toolbar color="primary" class="app-toolbar mat-elevation-z4">
        <button mat-icon-button (click)="sidenav.toggle()"><mat-icon>menu</mat-icon></button>
        <h1 class="app-name">LMS Portal</h1>
        <span class="spacer"></span>
        <button mat-button [matMenuTriggerFor]="userMenu">
          <mat-icon>account_circle</mat-icon>
          <span class="user-email">{{ user?.email }}</span>
        </button>
        <mat-menu #userMenu="matMenu">
          <button mat-menu-item (click)="logout()">
            <mat-icon>exit_to_app</mat-icon>
            <span>Logout</span>
          </button>
        </mat-menu>
      </mat-toolbar>

      <mat-sidenav-container class="sidenav-container">
        <mat-sidenav #sidenav [mode]="mobileQuery.matches ? 'over' : 'side'" [opened]="!mobileQuery.matches" class="app-sidenav">
          <mat-nav-list>
            
            <!-- Standard Employee & Manager & HR links -->
            <ng-container *ngIf="user?.role === 'EMPLOYEE' || user?.role === 'MANAGER' || user?.role === 'HR'">
              <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
                <mat-icon matListItemIcon>dashboard</mat-icon>
                <div matListItemTitle>Dashboard</div>
              </a>
              <a mat-list-item routerLink="/leave-request" routerLinkActive="active-link">
                <mat-icon matListItemIcon>post_add</mat-icon>
                <div matListItemTitle>Apply Leave</div>
              </a>
              <a mat-list-item routerLink="/leave-list" routerLinkActive="active-link">
                <mat-icon matListItemIcon>list_alt</mat-icon>
                <div matListItemTitle>My Leaves</div>
              </a>
            </ng-container>

            <!-- HR Only Links -->
            <ng-container *ngIf="user?.role === 'HR'">
              <a mat-list-item routerLink="/reports" routerLinkActive="active-link">
                <mat-icon matListItemIcon>bar_chart</mat-icon>
                <div matListItemTitle>System Reports</div>
              </a>
              <a mat-list-item routerLink="/all-leaves" routerLinkActive="active-link">
                <mat-icon matListItemIcon>event_note</mat-icon>
                <div matListItemTitle>All Employee Leaves</div>
              </a>
              <a mat-list-item routerLink="/manage-balances" routerLinkActive="active-link">
                <mat-icon matListItemIcon>account_balance_wallet</mat-icon>
                <div matListItemTitle>Manage Balances</div>
              </a>
            </ng-container>

            <!-- Admin Only Links -->
            <ng-container *ngIf="user?.role === 'ADMIN'">
              <a mat-list-item routerLink="/audit-logs" routerLinkActive="active-link">
                <mat-icon matListItemIcon>history</mat-icon>
                <div matListItemTitle>Audit Logs</div>
              </a>
              <a mat-list-item routerLink="/users" routerLinkActive="active-link">
                <mat-icon matListItemIcon>people</mat-icon>
                <div matListItemTitle>User Management</div>
              </a>
            </ng-container>

          </mat-nav-list>
        </mat-sidenav>

        <mat-sidenav-content class="main-content">
          <div class="content-wrapper">
            <router-outlet></router-outlet>
          </div>
        </mat-sidenav-content>
      </mat-sidenav-container>
    </div>
  `,
  styles: [`
    .layout-container {
      display: flex;
      flex-direction: column;
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
    }
    .is-mobile .app-toolbar {
      position: fixed;
      z-index: 2;
    }
    .app-toolbar {
      position: relative;
      z-index: 2;
    }
    .app-name {
      margin-left: 8px;
      font-size: 1.2rem;
      font-weight: 500;
    }
    .spacer {
      flex: 1 1 auto;
    }
    .user-email {
      margin-left: 8px;
    }
    .sidenav-container {
      flex: 1;
    }
    .is-mobile .sidenav-container {
      flex: 1 0 auto;
    }
    .app-sidenav {
      width: 250px;
      background-color: #fafafa;
      border-right: 1px solid rgba(0, 0, 0, 0.12);
    }
    .main-content {
      background-color: #f5f5f5;
    }
    .content-wrapper {
      padding: 20px;
      height: calc(100% - 40px);
      box-sizing: border-box;
      overflow: auto;
    }
    .active-link {
      background-color: rgba(25, 118, 210, 0.1) !important;
      color: #1976d2 !important;
      border-left: 4px solid #1976d2;
    }
    .active-link mat-icon {
      color: #1976d2;
    }
  `]
})
export class LayoutComponent {
  mobileQuery: MediaQueryList;
  user: any;

  constructor(private authService: AuthService) {
    this.mobileQuery = window.matchMedia('(max-width: 600px)');
    this.authService.currentUser$.subscribe(u => this.user = u);
  }

  logout() {
    this.authService.logout();
  }
}
