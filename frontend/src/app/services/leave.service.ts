import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class LeaveService {
  private apiUrl = 'http://localhost:8000/api/v1/leaves';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders() {
    const user = this.authService.currentUserValue;
    return new HttpHeaders({
      'Authorization': `Bearer ${user?.token}`
    });
  }

  getLeaveTypes(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/types`, { headers: this.getHeaders() });
  }

  getLeaveBalance(year: number = 2026): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/balance?year=${year}`, { headers: this.getHeaders() });
  }

  applyLeave(data: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}`, data, { headers: this.getHeaders() });
  }

  getLeaveRequests(status?: string): Observable<any[]> {
    const url = status ? `${this.apiUrl}?status=${status}` : this.apiUrl;
    return this.http.get<any[]>(url, { headers: this.getHeaders() });
  }

  approveLeave(requestId: number, comments?: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${requestId}/approve`, { comments }, { headers: this.getHeaders() });
  }

  rejectLeave(requestId: number, comments?: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${requestId}/reject`, { comments }, { headers: this.getHeaders() });
  }

  cancelLeave(requestId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${requestId}/cancel`, {}, { headers: this.getHeaders() });
  }

  getAllBalances(year: number = 2026): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/all-balances?year=${year}`, { headers: this.getHeaders() });
  }

  updateBalance(balanceId: number, availableDays: number): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/balances/${balanceId}`, { available_days: availableDays }, { headers: this.getHeaders() });
  }
}
