import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatGridListModule } from '@angular/material/grid-list';
import { LeaveService } from '../../services/leave.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatProgressBarModule, MatGridListModule],
  template: `
    <div class="dashboard-container">
      <h2 class="mat-h2">Welcome to your Dashboard</h2>
      
      <div class="balance-cards" *ngIf="balance">
        <mat-card class="balance-card mat-elevation-z4">
          <mat-card-header>
            <mat-icon mat-card-avatar color="primary">event_available</mat-icon>
            <mat-card-title>Available Leaves</mat-card-title>
            <mat-card-subtitle>For year {{ balance.year }}</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-value primary-text">{{ balance.total_available }} days</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="balance-card mat-elevation-z4">
          <mat-card-header>
            <mat-icon mat-card-avatar color="accent">event_busy</mat-icon>
            <mat-card-title>Used Leaves</mat-card-title>
            <mat-card-subtitle>For year {{ balance.year }}</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-value accent-text">{{ balance.total_used }} days</div>
          </mat-card-content>
        </mat-card>
      </div>

      <h3 class="mat-h3">Leave Breakdown</h3>
      <div class="breakdown-grid" *ngIf="balance">
        <mat-card *ngFor="let b of balance.detailed" class="breakdown-card mat-elevation-z2">
          <mat-card-header>
            <mat-card-title>{{ b.leave_type_name }}</mat-card-title>
            <mat-card-subtitle>{{ b.leave_type_code }}</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="progress-container">
              <div class="progress-labels">
                <span>Used: {{ b.used_days }}</span>
                <span>Available: {{ b.available_days }}</span>
              </div>
              <mat-progress-bar mode="determinate" [value]="getPercentage(b.used_days, b.available_days + b.used_days)"></mat-progress-bar>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .balance-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
    }
    .stat-value {
      font-size: 2.5rem;
      font-weight: bold;
      text-align: center;
      padding: 20px 0;
    }
    .primary-text {
      color: #1976d2;
    }
    .accent-text {
      color: #ff4081;
    }
    .breakdown-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }
    .progress-container {
      margin-top: 15px;
    }
    .progress-labels {
      display: flex;
      justify-content: space-between;
      margin-bottom: 5px;
      font-size: 0.85rem;
      color: rgba(0,0,0,0.6);
    }
    mat-icon {
      transform: scale(1.2);
    }
  `]
})
export class DashboardComponent implements OnInit {
  balance: any = null;

  constructor(private leaveService: LeaveService) {}

  ngOnInit() {
    this.leaveService.getLeaveBalance(2026).subscribe({
      next: (data) => {
        this.balance = data;
        this.balance.year = 2026;
        this.balance.total_available = data.detailed.reduce((sum: number, b: any) => sum + b.available_days, 0);
        this.balance.total_used = data.detailed.reduce((sum: number, b: any) => sum + b.used_days, 0);
      },
      error: (err) => console.error(err)
    });
  }

  getPercentage(used: number, total: number): number {
    if (total === 0) return 0;
    return (used / total) * 100;
  }
}
