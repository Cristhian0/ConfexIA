import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// Angular Material
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';

// Pipes
import { ColorCodePipe } from './pipes/color-code.pipe';
import { SafeHtmlPipe } from './pipes/safe-html.pipe';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { LoginComponent } from './components/auth/login.component';
import { TokenInterceptor } from './services/token-interceptor.service';
import { AuthGuard } from './guards/auth.guard';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { LotesComponent } from './components/lotes/lotes.component';
import { LoteFormComponent } from './components/lotes/lote-form/lote-form.component';
import { ImportacionExcelComponent } from './components/lotes/importacion-excel/importacion-excel.component';
import { TalleresComponent } from './components/talleres/talleres.component';
import { TallerFormComponent } from './components/talleres/taller-form/taller-form.component';
import { RemisionesComponent } from './components/remisiones/remisiones.component';
import { RemisionFormComponent } from './components/remisiones/remision-form/remision-form.component';
import { ProduccionComponent } from './components/produccion/produccion.component';
import { CatalogoComponent } from './components/catalogo/catalogo.component';
import { InventarioTelaComponent } from './components/inventario-tela/inventario-tela.component';
import { CorteComponent } from './components/corte/corte.component';
import { TallasComponent } from './components/catalogo/tallas/tallas.component';
import { TallaDialogComponent } from './components/catalogo/tallas/talla-dialog.component';
import { ColoresComponent } from './components/catalogo/colores/colores.component';
import { ColorDialogComponent } from './components/catalogo/colores/color-dialog.component';
import { MaterialesComponent } from './components/catalogo/materiales/materiales.component';
import { MaterialDialogComponent } from './components/catalogo/materiales/material-dialog.component';
import { ReferenciasComponent } from './components/catalogo/referencias/referencias.component';
import { ReferenciaDialogComponent } from './components/catalogo/referencias/referencia-dialog.component';
import { TizadoDialogComponent } from './components/corte/tizado-dialog.component';
import { CorteDialogComponent } from './components/corte/corte-dialog.component';
import { SobrantesDialogComponent } from './components/corte/sobrantes-dialog.component';
import { TrazabilidadComponent } from './components/trazabilidad/trazabilidad.component';
import { CalidadComponent } from './components/calidad/calidad.component';
import { ProductoTerminadoComponent } from './components/producto-terminado/producto-terminado.component';
import { BodegaComponent } from './components/bodega/bodega.component';
import { FinancieroComponent } from './components/financiero/financiero.component';
import { ColillasComponent } from './components/colillas/colillas.component';
import { FirmaDialogComponent } from './components/colillas/firma-dialog.component';
import { SignatureDialogComponent } from './components/colillas/signature-dialog.component';
import { IaInsightsComponent } from './components/dashboard/ia-insights/ia-insights.component';
import { ChatIaComponent } from './components/chat-ia/chat-ia.component';
import { ChatIaPageComponent } from './components/chat-ia/chat-ia-page.component';
import { ChatFloatingButtonComponent } from './components/chat-ia/chat-floating-button.component';
import { AssistantComponent } from './components/assistant/assistant.component';
import { DemoComponent } from './components/demo/demo.component';
import { LandingChartComponent } from './components/landing-chart/landing-chart.component';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    LotesComponent,
    LoteFormComponent,
    ImportacionExcelComponent,
    TalleresComponent,
    TallerFormComponent,
    RemisionesComponent,
    RemisionFormComponent,
    ProduccionComponent,
    InventarioTelaComponent,
    CorteComponent,
    CatalogoComponent,
    TallasComponent,
    TallaDialogComponent,
    ColoresComponent,
    ColorDialogComponent,
    MaterialesComponent,
    MaterialDialogComponent,
    ReferenciasComponent,
    ReferenciaDialogComponent,
    TizadoDialogComponent,
    CorteDialogComponent,
    SobrantesDialogComponent,
    FirmaDialogComponent,
    TrazabilidadComponent,
    CalidadComponent,
    ProductoTerminadoComponent,
    BodegaComponent,
    FinancieroComponent,
    ColillasComponent,
    SignatureDialogComponent,
    LoginComponent,
    ColorCodePipe,
    SafeHtmlPipe,
    IaInsightsComponent,
    ChatIaComponent,
    ChatIaPageComponent
    ,AssistantComponent
    ,LandingChartComponent
    ,DemoComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    AppRoutingModule,
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatIconModule,
    MatListModule,
    MatTableModule,
    MatPaginatorModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCardModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    MatTabsModule,
    MatCheckboxModule,
    MatTooltipModule,
    MatExpansionModule,
    MatMenuModule,
    MatDividerModule,
    ChatFloatingButtonComponent
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true },
    AuthGuard
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

