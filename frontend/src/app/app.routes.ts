import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { LayoutComponent } from './components/layout/layout.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LeaveRequestComponent } from './components/leave-request/leave-request.component';
import { LeaveListComponent } from './components/leave-list/leave-list.component';
import { ReportsComponent } from './components/reports/reports.component';
import { AuditLogsComponent } from './components/audit-logs/audit-logs.component';
import { UsersComponent } from './components/users/users.component';
import { PlaceholderComponent } from './components/placeholder/placeholder.component';
import { ManageBalancesComponent } from './components/manage-balances/manage-balances.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'leave-request', component: LeaveRequestComponent },
      { path: 'leave-list', component: LeaveListComponent },
      
      // HR Routes
      { path: 'reports', component: ReportsComponent },
      { path: 'all-leaves', component: LeaveListComponent },
      { path: 'manage-balances', component: ManageBalancesComponent },

      // Admin Routes
      { path: 'audit-logs', component: AuditLogsComponent },
      { path: 'users', component: UsersComponent },

      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: '' }
];
