import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { LeaveService } from '../../services/leave.service';

@Component({
  selector: 'app-manage-balances',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatButtonModule, MatIconModule],
  template: `
    <div style="padding: 20px;">
      <h2 class="mat-h2">Manage Employee Leave Balances (HR)</h2>
      <mat-card>
        <table mat-table [dataSource]="balancesData" class="mat-elevation-z2" style="width: 100%;">
          <ng-container matColumnDef="employee_name">
            <th mat-header-cell *matHeaderCellDef> Employee </th>
            <td mat-cell *matCellDef="let element"> {{element.employee_name}} </td>
          </ng-container>
          <ng-container matColumnDef="leave_type">
            <th mat-header-cell *matHeaderCellDef> Leave Type </th>
            <td mat-cell *matCellDef="let element"> {{element.leave_type_name}} </td>
          </ng-container>
          <ng-container matColumnDef="available">
            <th mat-header-cell *matHeaderCellDef> Available Days </th>
            <td mat-cell *matCellDef="let element"> {{element.available_days}} </td>
          </ng-container>
          <ng-container matColumnDef="used">
            <th mat-header-cell *matHeaderCellDef> Used Days </th>
            <td mat-cell *matCellDef="let element"> {{element.used_days}} </td>
          </ng-container>
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef> Actions </th>
            <td mat-cell *matCellDef="let element">
              <button mat-icon-button color="primary" (click)="editBalance(element)" title="Edit Balance">
                <mat-icon>edit</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="['employee_name', 'leave_type', 'available', 'used', 'actions']"></tr>
          <tr mat-row *matRowDef="let row; columns: ['employee_name', 'leave_type', 'available', 'used', 'actions'];"></tr>
        </table>
        
        <div *ngIf="balancesData.length === 0" style="padding: 30px; text-align: center; color: #666;">
          No balance records found.
        </div>
      </mat-card>
    </div>
  `
})
export class ManageBalancesComponent implements OnInit {
  balancesData: any[] = [];

  constructor(private leaveService: LeaveService) {}

  ngOnInit() {
    this.loadBalances();
  }

  loadBalances() {
    this.leaveService.getAllBalances().subscribe(data => this.balancesData = data);
  }

  editBalance(record: any) {
    const newAmount = prompt(`Update available days for ${record.employee_name} (${record.leave_type_name}):`, record.available_days);
    if (newAmount !== null && !isNaN(Number(newAmount))) {
      this.leaveService.updateBalance(record.balance_id, Number(newAmount)).subscribe(() => {
        this.loadBalances();
      });
    }
  }
}
