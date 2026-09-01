import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LotesComponent } from './components/lotes/lotes.component';
import { TalleresComponent } from './components/talleres/talleres.component';
import { RemisionesComponent } from './components/remisiones/remisiones.component';
import { ProduccionComponent } from './components/produccion/produccion.component';
import { CatalogoComponent } from './components/catalogo/catalogo.component';
import { InventarioTelaComponent } from './components/inventario-tela/inventario-tela.component';
import { CorteComponent } from './components/corte/corte.component';
import { CalidadComponent } from './components/calidad/calidad.component';
import { ProductoTerminadoComponent } from './components/producto-terminado/producto-terminado.component';
import { BodegaComponent } from './components/bodega/bodega.component';
import { FinancieroComponent } from './components/financiero/financiero.component';
import { ColillasComponent } from './components/colillas/colillas.component';
import { LoginComponent } from './components/auth/login.component';
import { ChatIaPageComponent } from './components/chat-ia/chat-ia-page.component';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  { path: '', redirectTo: '/inicio', pathMatch: 'full' },
  { path: 'inicio', component: DashboardComponent, data: { title: 'Inicio' }, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent, data: { title: 'Login' } },
  { path: 'dashboard', component: DashboardComponent, data: { title: 'Dashboard' } },
  { path: 'chat-ia', component: ChatIaPageComponent, data: { title: 'Asistente IA' } },
  { path: 'tela', component: InventarioTelaComponent, data: { title: 'Tela' } },
  { path: 'bodega', component: BodegaComponent, data: { title: 'Bodega' } },
  { path: 'corte', component: CorteComponent, data: { title: 'Corte' } },
  { path: 'lotes', component: LotesComponent, data: { title: 'Lotes' } },
  { path: 'talleres', component: TalleresComponent, data: { title: 'Talleres' } },
  { path: 'remisiones', component: RemisionesComponent, data: { title: 'Remisiones' } },
  { path: 'colillas', component: ColillasComponent, data: { title: 'Colillas' } },
  { path: 'calidad', component: ProduccionComponent, data: { title: 'Calidad' } },
  { path: 'producto-terminado', component: ProductoTerminadoComponent, data: { title: 'Producto Terminado' } },
  { path: 'financiero', component: FinancieroComponent, data: { title: 'Financiero' } },
  { path: 'catalogo', component: CatalogoComponent, data: { title: 'Catálogo' } }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

