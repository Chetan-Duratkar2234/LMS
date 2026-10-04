import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { AuditService } from '../../services/audit.service';

@Component({
  selector: 'app-audit-logs',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule],
  providers: [DatePipe],
  template: `
    <div style="padding: 20px;">
      <h2 class="mat-h2">System Audit Logs (Admin)</h2>
      <mat-card>
        <table mat-table [dataSource]="logsData" class="mat-elevation-z2" style="width: 100%;">
          <ng-container matColumnDef="timestamp">
            <th mat-header-cell *matHeaderCellDef> Timestamp </th>
            <td mat-cell *matCellDef="let element"> {{element.timestamp | date:'short'}} </td>
          </ng-container>
          <ng-container matColumnDef="event">
            <th mat-header-cell *matHeaderCellDef> Event </th>
            <td mat-cell *matCellDef="let element"> <b>{{element.event}}</b> </td>
          </ng-container>
          <ng-container matColumnDef="performed_by">
            <th mat-header-cell *matHeaderCellDef> Performed By </th>
            <td mat-cell *matCellDef="let element"> {{element.performedBy}} </td>
          </ng-container>
          <ng-container matColumnDef="request_id">
            <th mat-header-cell *matHeaderCellDef> Request ID </th>
            <td mat-cell *matCellDef="let element"> {{element.requestId}} </td>
          </ng-container>
          <ng-container matColumnDef="details">
            <th mat-header-cell *matHeaderCellDef> Details </th>
            <td mat-cell *matCellDef="let element"> {{element.details}} </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="['timestamp', 'event', 'performed_by', 'request_id', 'details']"></tr>
          <tr mat-row *matRowDef="let row; columns: ['timestamp', 'event', 'performed_by', 'request_id', 'details'];"></tr>
        </table>
        
        <div *ngIf="logsData.length === 0" style="padding: 30px; text-align: center; color: #666;">
          No audit logs found.
        </div>
      </mat-card>
    </div>
  `
})
export class AuditLogsComponent implements OnInit {
  logsData: any[] = [];

  constructor(private auditService: AuditService) {}

  ngOnInit() {
    this.auditService.getAuditLogs().subscribe(data => this.logsData = data);
  }
}

