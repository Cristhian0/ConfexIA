import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const requiredRole = route.data?.['role'] as string | undefined;
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }
    if (requiredRole) {
      const role = this.auth.getRole();
      if (role !== requiredRole && role !== 'admin') {
        // not allowed
        this.router.navigate(['/inicio']);
        return false;
      }
    }
    return true;
  }
}
