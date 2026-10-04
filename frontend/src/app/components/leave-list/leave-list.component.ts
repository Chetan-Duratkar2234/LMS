import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { LeaveService } from '../../services/leave.service';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-leave-list',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
    MatSnackBarModule,
    RouterModule
  ],
  template: `
    <div class="list-container">
      <div class="header-row">
        <h2 class="mat-h2">My Leave Requests</h2>
        <button mat-raised-button color="primary" routerLink="/leave-request">
          <mat-icon>add</mat-icon> New Request
        </button>
      </div>

      <div class="table-container mat-elevation-z8">
        <table mat-table [dataSource]="myLeaves" matSort>
          <!-- Type Column -->
          <ng-container matColumnDef="leave_type">
            <th mat-header-cell *matHeaderCellDef mat-sort-header> Type </th>
            <td mat-cell *matCellDef="let element"> {{element.leave_type_name}} </td>
          </ng-container>

          <!-- Duration Column -->
          <ng-container matColumnDef="duration">
            <th mat-header-cell *matHeaderCellDef> Duration </th>
            <td mat-cell *matCellDef="let element"> {{element.start_date}} to {{element.end_date}} </td>
          </ng-container>

          <!-- Status Column -->
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef mat-sort-header> Status </th>
            <td mat-cell *matCellDef="let element">
              <mat-chip [color]="getStatusColor(element.status)" selected>{{element.status}}</mat-chip>
            </td>
          </ng-container>

          <!-- Reason Column -->
          <ng-container matColumnDef="reason">
            <th mat-header-cell *matHeaderCellDef> Reason </th>
            <td mat-cell *matCellDef="let element"> {{element.reason}} </td>
          </ng-container>

          <!-- Actions Column -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef> Actions </th>
            <td mat-cell *matCellDef="let element">
              <button mat-icon-button color="warn" *ngIf="element.status === 'PENDING'" (click)="cancelLeave(element.request_id)" title="Cancel Request">
                <mat-icon>cancel</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="myColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: myColumns;"></tr>
        </table>

        <div *ngIf="myLeaves.length === 0" class="empty-state mat-body-1">
          No personal leave requests found.
        </div>
      </div>

      <!-- Team Leaves Section for Managers -->
      <ng-container *ngIf="isManager">
        <br>
        <mat-divider></mat-divider>
        <br>
        <div class="header-row">
          <h2 class="mat-h2">Team Leave Requests (Approvals)</h2>
        </div>

        <div class="table-container mat-elevation-z8">
          <table mat-table [dataSource]="teamLeaves" matSort>
            <!-- Employee Column -->
            <ng-container matColumnDef="employee">
              <th mat-header-cell *matHeaderCellDef mat-sort-header> Employee </th>
              <td mat-cell *matCellDef="let element"> {{element.employee_name}} </td>
            </ng-container>

            <!-- Type Column -->
            <ng-container matColumnDef="leave_type">
              <th mat-header-cell *matHeaderCellDef> Type </th>
              <td mat-cell *matCellDef="let element"> {{element.leave_type_name}} </td>
            </ng-container>

            <!-- Duration Column -->
            <ng-container matColumnDef="duration">
              <th mat-header-cell *matHeaderCellDef> Duration </th>
              <td mat-cell *matCellDef="let element"> {{element.start_date}} to {{element.end_date}} </td>
            </ng-container>

            <!-- Status Column -->
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef mat-sort-header> Status </th>
              <td mat-cell *matCellDef="let element">
                <mat-chip [color]="getStatusColor(element.status)" selected>{{element.status}}</mat-chip>
              </td>
            </ng-container>

            <!-- Reason Column -->
            <ng-container matColumnDef="reason">
              <th mat-header-cell *matHeaderCellDef> Reason </th>
              <td mat-cell *matCellDef="let element"> {{element.reason}} </td>
            </ng-container>

            <!-- Actions Column -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef> Actions </th>
              <td mat-cell *matCellDef="let element">
                <ng-container *ngIf="element.status === 'PENDING'">
                  <button mat-icon-button color="primary" (click)="approveLeave(element.request_id)" title="Approve Request">
                    <mat-icon>check_circle</mat-icon>
                  </button>
                  <button mat-icon-button color="warn" (click)="rejectLeave(element.request_id)" title="Reject Request">
                    <mat-icon>cancel</mat-icon>
                  </button>
                </ng-container>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="teamColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: teamColumns;"></tr>
          </table>

          <div *ngIf="teamLeaves.length === 0" class="empty-state mat-body-1">
            No team leave requests found.
          </div>
        </div>
      </ng-container>
    </div>
  `,
  styles: [`
    .list-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .table-container {
      width: 100%;
      overflow-x: auto;
      background-color: white;
      border-radius: 8px;
    }
    table {
      width: 100%;
    }
    .empty-state {
      padding: 30px;
      text-align: center;
      color: rgba(0, 0, 0, 0.6);
    }
  `]
})
export class LeaveListComponent implements OnInit {
  myColumns: string[] = ['leave_type', 'duration', 'status', 'reason', 'actions'];
  teamColumns: string[] = ['employee', 'leave_type', 'duration', 'status', 'reason', 'actions'];
  
  myLeaves: any[] = [];
  teamLeaves: any[] = [];
  isManager = false;

  constructor(
    private leaveService: LeaveService, 
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    const user = this.authService.currentUserValue;
    if (user && (user.role === 'MANAGER' || user.role === 'HR' || user.role === 'ADMIN')) {
      this.isManager = true;
    }
    this.loadLeaves();
  }

  loadLeaves() {
    const user = this.authService.currentUserValue;
    this.leaveService.getLeaveRequests().subscribe({
      next: (data) => {
        this.myLeaves = data.filter((l: any) => l.employee_id === user.employee_id);
        this.teamLeaves = data.filter((l: any) => l.employee_id !== user.employee_id);
      },
      error: (err) => console.error(err)
    });
  }

  cancelLeave(id: number) {
    if (confirm('Are you sure you want to cancel this leave request?')) {
      this.leaveService.cancelLeave(id).subscribe({
        next: () => this.loadLeaves(),
        error: (err) => console.error(err)
      });
    }
  }

  approveLeave(id: number) {
    if (confirm('Approve this leave request?')) {
      this.leaveService.approveLeave(id, 'Approved by manager').subscribe({
        next: () => {
          this.snackBar.open('Leave approved successfully', 'Close', { duration: 3000 });
          this.loadLeaves();
        },
        error: (err) => this.snackBar.open('Failed to approve leave', 'Close', { duration: 3000 })
      });
    }
  }

  rejectLeave(id: number) {
    const reason = prompt('Reason for rejection:');
    if (reason !== null) {
      this.leaveService.rejectLeave(id, reason || 'Rejected by manager').subscribe({
        next: () => {
          this.snackBar.open('Leave rejected', 'Close', { duration: 3000 });
          this.loadLeaves();
        },
        error: (err) => this.snackBar.open('Failed to reject leave', 'Close', { duration: 3000 })
      });
    }
  }

  getStatusColor(status: string): string {
    switch(status) {
      case 'APPROVED': return 'primary';
      case 'REJECTED': case 'CANCELLED': return 'warn';
      case 'PENDING': return 'accent';
      default: return '';
    }
  }
}
