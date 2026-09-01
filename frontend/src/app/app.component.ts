import { Component, OnDestroy } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import { Subscription } from 'rxjs';
import { AuthService } from './services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { LoginComponent } from './components/auth/login.component';

interface Breadcrumb {
  label: string;
  url: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnDestroy {
  title = 'Sistema de Confección Textil';
  pageTitle = 'Inicio';
  breadcrumbs: Breadcrumb[] = [{ label: 'Inicio', url: '/inicio' }];

  private routerSubscription: Subscription;
  private lastBreadcrumb?: Breadcrumb;

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute
    , public auth: AuthService
    , private dialog: MatDialog
  ) {
    this.routerSubscription = this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      const route = this.getCurrentRoute(this.activatedRoute);
      const title = route.snapshot.data?.['title'] || 'Inicio';
      const url = this.router.url;
      this.pageTitle = title;

      this.breadcrumbs = this.buildBreadcrumbs(title, url);
      if (title !== 'Inicio') {
        this.lastBreadcrumb = { label: title, url };
      }
    });
  }

  openLogin(): void {
    const ref = this.dialog.open(LoginComponent, {
      width: '420px'
    });
    ref.afterClosed().subscribe((result) => {
      if (result) {
        this.router.navigate(['/inicio']);
      }
    });
  }

  

  get role(): string | null {
    return this.auth.getRole();
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  private getCurrentRoute(route: ActivatedRoute): ActivatedRoute {
    while (route.firstChild) {
      route = route.firstChild;
    }
    return route;
  }

  private buildBreadcrumbs(title: string, currentUrl: string): Breadcrumb[] {
    if (title === 'Inicio') {
      return [{ label: 'Inicio', url: '/inicio' }];
    }

    if (this.lastBreadcrumb && this.lastBreadcrumb.label !== 'Inicio' && this.lastBreadcrumb.label !== title) {
      return [
        { label: 'Inicio', url: '/inicio' },
        { label: this.lastBreadcrumb.label, url: this.lastBreadcrumb.url },
        { label: title, url: '' }
      ];
    }

    return [
      { label: 'Inicio', url: '/inicio' },
      { label: title, url: currentUrl }
    ];
  }

  ngOnDestroy(): void {
    this.routerSubscription.unsubscribe();
  }
}

