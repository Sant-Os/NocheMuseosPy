# Informe de aportes — Sant-Os (Grupo 10, Épica 10)

**Corte:** Nov 24, 2026 · **Rama:** `epic/grupo-10-analytics-institucional` · **Autor en Git:** Sant-Os `<santos.c.nnyrd@gmail.com>`

---

## Resumen Ejecutivo de Aportes

Mis aportes en el proyecto abarcan los 3 Sprints de desarrollo dentro del **Grupo 10 (Épica 10: Analítica Institucional)**:

* **Sprint 1 (Reportes y Conexión de Datos):**
  - Conexión del módulo de reportes analíticos e historial con PostgreSQL y Prisma ORM.
  - Inclusión de solicitudes de acceso aprobadas y aislamiento del historial de exportaciones por usuario administrador.
  - Adición de la columna de tipo de usuario en usuarios rechazados y exportación CSV.
  - Adaptación del punto de entrada de NestJS para despliegues serverless.

* **Sprint 2 (Encuestas y Respuestas de Titulados):**
  - Implementación de la vista de analíticas y estadísticas de encuestas junto con la exportación oficial en PDF.
  - Flujo de notificaciones de encuestas para titulados y envío de respuestas (endpoints y frontend).
  - Sustitución de enums de base de datos por tablas catálogo en Prisma y reutilización de componentes compartidos.
  - Pruebas unitarias de respuesta de encuestas y estabilidad ante regresiones.

* **Sprint 3 (Ciclo de Vida, Alertas de Variación y Datos Formales):**
  - Sistema de notificaciones de ciclo de vida (`SURVEY_CLOSING_SOON`, `SURVEY_CLOSED`) y evaluador de variaciones semestrales (`SURVEY_VARIATION_ALERT`).
  - Sincronización e integración de contratos con el módulo centralizado de notificaciones.
  - Corrección de acciones y redirecciones en notificaciones hacia estadísticas (`/backoffice/surveys/statistics/[id]`).
  - Creación del seed formal integral con titulados, encuestas escalonadas, respuestas deterministas y notificaciones asociadas.

---

## Historia de Usuario 1 – Sprint 1

### Reporte de usuarios registrados (aceptados)

**Responsable de la implementación:** Santos Rodrigo Colque Calcina (`Sant-Os`) — Frontend (Trabajo en dúo)  
**Rama:** `epic/grupo-10-analytics-institucional` (trabajo original en `feature/grupo-10-analytics-hu1`, `feature/grupo-10-db-connection` y `fix/grupo-10-hu1-solucion-bugs`)  
**Estimación:** 5 | **Versión:** 1.0  

---

### 1. Descripción general

En este Sprint 1 trabajamos en dúo dentro del equipo QuantumCode (Grupo 10) y me correspondió asumir el desarrollo integral de la parte **Frontend**. La funcionalidad desarrollada permite al Administrador de la plataforma UMSSY consultar de forma centralizada y estructurada el listado de todos los usuarios registrados y aceptados en el sistema (estudiantes, egresados, titulados, mentores, empresas y administradores). 

La interfaz presenta los datos esenciales de cada usuario: nombre de usuario, correo electrónico, tipo de usuario (rol), identificador institucional, documento de respaldo y fecha de registro. Se construyó con un diseño responsivo adaptado tanto a pantallas móviles como a estaciones de escritorio, integrando paginación por servidor (10 registros por página), cabecera descriptiva, navegación fluida desde la barra lateral (sidebar) dentro del módulo de "Reportes Analíticos", amortiguación de tiempos de carga mediante 10 filas de esqueleto animado (Skeletons) para evitar saltos de diseño (*Cumulative Layout Shift - CLS*), y resiliencia ante estados vacíos o desconexión temporal de la red.

---

### 2. Stack tecnológico

| Tecnología | Uso en la funcionalidad |
| :--- | :--- |
| **Next.js 16 (App Router)** | Framework principal; definición de arquitectura de rutas (`/analytics/accepted-users-report` y `/backoffice/reports/accepted-users`), Server Components y Client Components. |
| **React 19** | Biblioteca base para la interfaz de usuario; hooks de estado (`useState`, `useEffect`), memorización y ciclo de vida de los componentes. |
| **TypeScript 5.9** | Lenguaje de desarrollo con tipado estático estricto para entidades (`ReportUser`), contratos de API y propiedades de componentes (`props`). |
| **Tailwind CSS 4** | Sistema de diseño de estilos utilitarios; maquetación responsiva, paleta institucional UMSS, diseño de grillas y control de scroll horizontal en tablas. |
| **shadcn/ui + Lucide React** | Primitivos de interfaz accesibles (Table, Card, Button, Skeleton, Pagination, Badge) e iconografía vectorial (`FileText`, `RefreshCw`, `AlertTriangle`, etc.). |
| **TanStack Query (React Query) + Axios** | Cliente HTTP y gestor de estado asíncrono; peticiones paginadas al backend, control de caché, reintentos y sincronización reactiva de datos. |
| **Vitest + React Testing Library** | Entorno de pruebas unitarias y de integración para vistas, layouts y componentes de navegación. |

---

### 3. Estructura de archivos

```text
frontend/src/
├── app/(app)/
│   ├── analytics/
│   │   ├── accepted-users-report/
│   │   │   └── page.tsx                        # Página principal de la ruta de usuarios aceptados
│   │   ├── page.tsx                            # Entrada y redirección del módulo de analítica
│   │   ├── layout.tsx                          # Layout contenedor del módulo analytics
│   │   └── pages.test.tsx                      # Pruebas de rutas del módulo
│   └── app-layout.test.tsx                     # Pruebas del layout general
├── modules/analytics/
│   ├── components/
│   │   ├── common/
│   │   │   ├── users-report-header.tsx         # Cabecera con título, breadcrumb y descripción
│   │   │   └── users-report-pagination.tsx     # Control de paginación reactiva (anterior/siguiente/páginas)
│   │   └── users-report/
│   │       ├── users-report-filters.tsx        # Filtros y barra de herramientas superior
│   │       └── users-report-table.tsx          # Tabla principal con columnas reglamentarias
│   ├── types/
│   │   └── analytics.types.ts                  # Interfaces y tipados de usuarios y reportes
│   ├── views/
│   │   ├── accepted-users-report-view.tsx      # Vista integradora del reporte de aceptados
│   │   └── accepted-users-report-view.test.tsx # Suite de pruebas de la vista
│   └── index.ts                                # Exportaciones públicas del módulo
└── shared/
    ├── components/layout/
    │   ├── sidebar.tsx                         # Menú lateral con sección "Reportes Analíticos"
    │   ├── sidebar.test.tsx                    # Pruebas unitarias de navegación y estados del sidebar
    │   ├── shell.tsx                           # Contenedor visual general (Sidebar + Topbar + Content)
    │   └── shell.test.tsx                      # Pruebas del contenedor principal
    └── utils/
        └── is-connection-error.ts              # Detección de fallos de red / conectividad offline
```

---

### 4. Implementación y flujo de datos

#### 4.1 Vista y tabla principal (`AcceptedUsersReportView` y `UsersReportTable`)
Se diseñó la vista principal del reporte garantizando el cumplimiento estricto del orden de columnas definido en los criterios de aceptación:
1. **Usuario:** Nombre completo y correo del usuario.
2. **Identificador:** Código de estudiante, carnet de identidad o identificación institucional correspondiente al rol.
3. **Documento de respaldo:** Tipo de documento presentado (Título académico, Diploma académico, Certificado de egreso, etc.) acompañado de su ícono representativo.
4. **Rol / Tipo de Usuario:** Etiqueta distintiva con el tipo de cuenta (Estudiante, Titulado, Mentor, Empresa o Administrador).
5. **Fecha de registro:** Fecha en formato estandarizado y legible para el usuario (`DD/MM/AAAA`).

#### 4.2 Navegación y Shell de la aplicación (`Sidebar` y `Shell`)
Para permitir un acceso intuitivo y estandarizado, se implementó el componente `Sidebar` dentro del `Shell` del sistema:
- Menú lateral con sección desplegable en acordeón para **"Reportes Analíticos"**.
- Enlace directo a la sub-opción **"Reporte de usuarios registrados"** (más adelante alineada como "Reporte de usuarios registrados aceptados").
- Resaltado activo del elemento según la ruta visitada, soporte de colapso lateral en escritorio y adaptación fluida a pantallas reducidas mediante menú tipo hamburguesa.

#### 4.3 Paginación, cabecera y estados (`UsersReportPagination` y `UsersReportHeader`)
- Se implementó el control de paginación que calcula el total de registros y páginas disponibles, limitando la visualización a 10 usuarios por página.
- Deshabilitación automática de los botones "Anterior" en la primera página y "Siguiente" en la última página.
- Indicador visual del rango actual de registros visualizados (`Mostrando X-Y de N usuarios`).
- Botón interactivo de **"Actualizar"** para refrescar la consulta de datos bajo demanda sin recargar la página.
- Incorporación de esqueletos de carga (`Skeleton`) durante la transición de datos para ofrecer una experiencia fluida.

#### 4.4 Flujo de datos
```text
Administrador inicia sesión con rol Administrador
  → Navega a Inicio > Reportes Analíticos > Reporte de usuarios registrados
  → Se monta la vista AcceptedUsersReportView y se invoca el hook de consulta (TanStack Query / Axios)
  → Durante la petición HTTP: la tabla renderiza 10 filas de Skeleton (evitando Cumulative Layout Shift)
  → Temporizador preventivo: si transcurren >10 s sin respuesta del backend, se dispara notificación Toast de advertencia (Error 408) sin interrumpir la carga
  → En caso de desconexión o fallo 503/504: isConnectionError preserva la última tabla cargada (Offline Shell) y muestra Toast rojo de alerta con role="alert"
  → Cuando el backend responde exitosamente:
      - UsersReportTable renderiza las filas de usuarios ordenadas reglamentariamente
      - UsersReportPagination calcula la cantidad de páginas y habilita la navegación interactiva
```

---

### 5. Bugs encontrados y correcciones (QA)

Durante las dos rondas de pruebas de calidad ejecutadas por el equipo de QA (**QAlified**), registradas en el *Primer Bug Report* y *Segundo Bug Report*, se identificaron y solventaron las siguientes observaciones en el frontend de la funcionalidad:

| ID Bug | Problema detectado | Causa técnica | Solución aplicada | Commit / Referencia |
| :--- | :--- | :--- | :--- | :--- |
| **BUG-HU1-04** | **Renderizado incompleto de Skeletons (5 en lugar de 10) durante la carga**<br>*(Prioridad: Low, Severidad: Low)* | Al cargar la tabla en condiciones de red lenta, solo se dibujaban 5 filas simuladas, dejando espacio vacío y generando un salto brusco de interfaz (*Cumulative Layout Shift*) cuando llegaban los 10 registros reales. | El componente iteraba sobre un arreglo estático de 5 elementos. Se estandarizó la renderización de exactamente 10 filas de esqueleto (`table-state-rows.tsx`) alineadas con el tamaño de página (`pageSize: 10`), actualizando los tests unitarios. | `ee1363193` *(integrado en PR #925 / `6f1db6cbd`)* |
| **BUG-HU1-24** | **Ausencia de notificación Toast (Error 408) ante latencia extrema (>10s)**<br>*(Prioridad: Medium, Severidad: Low)* | Al simular lentitud extrema en DevTools (Slow 3G o >10 segundos), la aplicación no ofrecía retroalimentación visual al administrador sobre la demora en la solicitud. | No existía un temporizador desacoplado de la promesa HTTP. Se añadió un temporizador de 10 s en `use-paginated-report.ts` que activa un toast de advertencia ("Error 408: La solicitud está tardando demasiado") sin abortar la petición. | `c1cd62332` *(integrado en PR #925 / `6f1db6cbd`)* |
| **BUG-HU1-27** | **Caída total de la interfaz al perder conexión de red en lugar de alerta Toast**<br>*(Prioridad: Medium, Severidad: Medium)* | Al navegar sin conexión a internet (Modo Avión), la tabla y los datos desaparecían, arrojando un texto plano de error en lugar de conservar la estructura visual (Offline Shell) con un toast. | El manejador de errores del hook borraba el caché previo de datos al capturar cualquier fallo de red. Se implementó la utilidad `isConnectionError.ts` para detectar la falta de conexión (503/504 o sin respuesta), conservando la última tabla en pantalla y emitiendo un toast rojo con `role="alert"`. | `c1cd62332` *(integrado en PR #925 / `6f1db6cbd`)* |
| **BUG-H01-11** | **No se visualizaba el identificador de los usuarios en el reporte**<br>*(Prioridad: Medium, Severidad: Medium)* | La columna "Identificador" permanecía vacía para todos los registros mostrados en el reporte. | Inconsistencia en la clave de la propiedad recibida desde el DTO del backend (`studentCode` vs. `identityCard` vs. `identifier`). Se normalizó la lectura del atributo en el componente de fila con fallback seguro. | `ac714cf77` / `fix/grupo-10-hu1-solucion-bugs` |
| **BUG-H01-12** | **No se visualizaba la información del documento de respaldo (mostraba "-")**<br>*(Prioridad: Medium, Severidad: Medium)* | La columna "Documento" mostraba únicamente el símbolo `-` en todos los registros visualizados. | La información del documento de respaldo venía anidada dentro del registro de perfil o solicitud según el rol del usuario. Se ajustó el selector para extraer y formatear el tipo de documento junto a su ícono. | `ac714cf77` / `fix/grupo-10-hu1-solucion-bugs` |
| **BUG-H01-01** | **Visualización temporal del Backoffice antes de redirigir a usuarios no Administradores**<br>*(Prioridad: Medium, Severidad: Medium)* | Al acceder por URL directa a la vista de reportes con un rol distinto a Administrador, se renderizaba brevemente el layout del Backoffice antes de la redirección. | La validación de sesión ocurría en un hook de cliente tras el primer render. Se reforzó el guardia en `layout.tsx` y `shell.tsx`, bloqueando la renderización de la interfaz administrativa hasta confirmar los privilegios del usuario. | `ac714cf77` / `layout.tsx` |
| **BUG-UI-01** | **Inconsistencia de texto en el título respecto al Mockup ("Reporte de usuarios registrados")**<br>*(Prioridad: Low, Severidad: Cosmetic)* | El título principal y el breadcrumb omitían la palabra "aceptados" aprobada en el diseño oficial. | El componente `users-report-header.tsx` contenía el título preliminar. Se corrigió a "Reporte de usuarios registrados aceptados" tanto en la cabecera como en las migas de pan. | `ac714cf77` / `1b850e49b` |
| **BUG-UI-03 / BUG-UI-21** | **Texto truncado e ilegible en opciones del submenú "Reportes Analíticos"**<br>*(Prioridad: Low, Severidad: Low/Cosmetic)* | En el menú lateral los nombres largos se cortaban con puntos suspensivos ("Reporte de usuarios regist..."), haciendo indistinguibles los reportes. | Se utilizaban clases de `truncate` rígidas en el contenedor de los ítems del sidebar. Se reemplazó por diseño flexible con salto de línea automático (`break-words` / `whitespace-normal`) en dos líneas. | `ac714cf77` / `sidebar.tsx` |
| **BUG-UI-04** | **Zoom acumulativo descontrolado al rotar la pantalla en dispositivos móviles**<br>*(Prioridad: Low, Severidad: Low)* | Al cambiar repetidamente la orientación del celular entre vertical y horizontal, la interfaz realizaba un acercamiento desmedido que la volvía gigante e inutilizable. | Ausencia de parámetros de restricción de auto-escalado en la configuración base del viewport. Se definió el meta tag `viewport` con escala base estable (`initial-scale=1.0`) y layout responsivo fluido en Tailwind CSS. | `ac714cf77` / `globals.css` |

---

### 6. Mejoras de experiencia de usuario

1. **Eliminación del salto brusco visual (Cumulative Layout Shift):** La estandarización de 10 filas de esqueleto animado garantiza que el contenedor de la tabla conserve exactamente la misma altura durante la carga y tras recibir los datos finales.
2. **Resiliencia ante degradación o corte de red:** Si la conexión a internet se interrumpe mientras el administrador revisa la lista, la vista no desaparece ni se blanquea; se mantiene visible la última información consultada acompañada de un toast informativo no bloqueante.
3. **Paginación inteligente:** Deshabilitación de botones en los límites inferior y superior, visualización clara del rango consultado (`Mostrando 1-10 de N usuarios`) y reinicio automático a la primera página cuando se actualizan los criterios.
4. **Navegación lateral adaptativa y legible:** Soporte de acordeón en el sidebar con textos completos en dos líneas, eliminando cortes con puntos suspensivos y permitiendo una navegación táctil fluida en dispositivos móviles.

---

### 7. Trabajo que no se pudo fusionar / Dificultades

- **Reestructuración de arquitectura de rutas:** En los primeros días del Sprint 1, el módulo fue maquetado bajo la ruta `/analytics/accepted-users-report` en la rama `feature/grupo-10-analytics-hu1` (commit `ac714cf77`). Posteriormente, en la integración global del Grupo 10 y para mantener la coherencia con el módulo administrativo unificado, la ruta oficial se trasladó a `/backoffice/reports/registered-users`. Esto requirió adaptar rutas, imports y suites de pruebas para que coexistieran con el nuevo enrutador del backoffice.
- **Integración de commits de corrección en ramas grupales:** Ciertas correcciones de bugs de QA realizadas en el frontend (como `c1cd62332` y `ee1363193`) fueron fusionadas a través de commits de integración consolidados (como `6f1db6cbd` y PRs `#925` y `#1109`), por lo que en el historial principal de `develop` parte del código figura bajo autoría de integración del equipo.

---

### 8. Pruebas

Se desarrollaron pruebas unitarias y de integración utilizando **Vitest** y **React Testing Library**:
- `accepted-users-report-view.test.tsx`:
  - Verifica la renderización completa de la cabecera, título y breadcrumb.
  - Comprueba la renderización de las 6 columnas reglamentarias de la tabla.
  - Simula la llamada asíncrona al servicio de reportes y valida que los datos se dibujen en las celdas correspondientes.
  - Verifica que al pulsar el botón "Actualizar" se dispare nuevamente la petición al backend.
- `sidebar.test.tsx`:
  - Valida la existencia del módulo "Reportes Analíticos" y la expansión de sus opciones.
  - Comprueba que el enlace a "Reporte de usuarios registrados" aplique las clases de elemento activo cuando la ruta coincide.
  - Verifica la accesibilidad (atributos `aria-*`) y el colapso del menú en resoluciones móviles.
- `shell.test.tsx`:
  - Verifica el montaje correcto del contenedor principal, la barra superior y la zona de contenido dinámico.
- **Pruebas de estados de carga y error:**
  - Validación de que se muestren exactamente 10 filas de esqueleto durante el estado `isLoading`.
  - Verificación del renderizado del estado vacío cuando no existen registros disponibles.

---

### 9. Resultado final

La Historia de Usuario 1 quedó completada y validada en el frontend con las siguientes capacidades operativas:
- El Administrador puede consultar la totalidad de los usuarios registrados y aceptados en una tabla ordenada y profesional.
- Visualización estandarizada de las columnas: **Usuario**, **Correo**, **Tipo de Usuario**, **Identificador**, **Documento** y **Fecha de Registro**.
- Paginación ágil de 10 registros por página con contador dinámico y actualización asíncrona mediante el botón "Actualizar".
- Sistema de retroalimentación visual compuesto por 10 filas de skeleton, toast de advertencia por demora (408) y toast de protección ante fallos de conectividad (503/504).
- Interfaz 100% responsiva y accesible, cumpliendo con los estándares de diseño institucional de la UMSS.

---

### 10. Commits realizados

| Hash | Fecha | Descripción del Commit | Estado / Destino |
| :--- | :--- | :--- | :--- |
| `ac714cf77` | 30/09/2026 | `feat(frontend): implement analytics module with responsive navigation and tests` | Base fundacional del frontend: rutas de analítica, tabla de usuarios, filtros, paginación, sidebar responsivo, shell y tests unitarios. |
| `1a13a42fa` / `9d75ea73f` | 06/10/2026 | `feat(reports): connect user reports and history with database and prisma` | Fusionado en la épica (PR `#925`). Conexión de reportes e historial con la persistencia real. |
| `0f43c25a1` / `e19ba8425` | 07/10/2026 | `fix(reports): optimize repository synchronization and fix linter warning` | Fusionado en la épica (PR `#925`). Optimización de sincronización y resolución de observaciones de linter. |
| `1d84e14db` / `8b9193313` | 09/10/2026 | `fix(reports): include approved access requests and isolate export history by user` | Fusionado en la épica (PR `#1109`). Inclusión de solicitudes aprobadas y aislamiento de datos por administrador. |
| `08abc2d55` / `dbbe9790a` | 10/10/2026 | `feat(reports): add user type column to rejected users table and csv export` | Fusionado en la épica (PR `#1109` / `#1338`). Incorporación de columna de rol y consistencia en exportaciones. |

---

## Historia de Usuario 5 – Sprint 2

### Encuesta de empleabilidad: Exportar PDF institucional y conexiones a Base de Datos

**Responsable de la implementación:** Santos Rodrigo Colque Calcina (`Sant-Os`) — Fullstack (Historia de Usuario completa: Frontend, Backend y Base de Datos)  
**Rama:** `epic/grupo-10-analytics-institucional` (trabajo original en `feature/grupo-10-sprint-2-surveys` y `feature/grupo-10-sprint-2`)  
**Estimación:** 5 | **Versión:** 1.0  

---

### 1. Descripción general

En este Sprint 2 el equipo QuantumCode (Grupo 10) adoptó la modalidad de desarrollo de **Historias de Usuario completas (Fullstack)**. En esta asignación asumí la responsabilidad de la **Historia de Usuario 5: Home > Reportes Analíticos > Encuesta de empleabilidad > Exportar PDF** de extremo a extremo, junto con el **diseño e integración de la persistencia y conexiones a base de datos** para el módulo de encuestas y respuestas mediante Prisma ORM y PostgreSQL.

La funcionalidad permite al Administrador exportar la vista completa de resultados analíticos y métricas de una encuesta de empleabilidad en un documento oficial en formato PDF estático, limpio y listo para su impresión o distribución institucional ante comisiones de acreditación o autoridades académicas. El documento PDF incorpora la cabecera institucional oficial de la Universidad Mayor de San Simón (UMSS) y la Dirección de Planificación Académica (DPA), código de referencia único (`INF-UMSSY-${id}`), ficha técnica de la encuesta (título, carrera, gestión académica, vigencia, estado, muestra total y preguntas analizadas) y el desglose de resultados por cada pregunta con sus opciones, conteos absolutos, porcentajes calculados y gráficos de barras comparativos.

Adicionalmente, se construyó la arquitectura completa de persistencia en base de datos para encuestas: modelado relacional en Prisma (`Survey`, `SurveyQuestion`, `SurveyQuestionOption`, `SurveyResponse`, `SurveyAnswer`, `Career`), generación de migraciones SQL, eliminación de enums de base de datos para cumplir las directrices de DevOps, integración del registro automático de cada exportación en el historial de reportes administrativos (`admin_export_histories`), y desarrollo de un motor generador de PDF autosuficiente y nativo (`SimplePdfDocument`) sin dependencias externas pesadas para garantizar estabilidad y cumplimiento de estándares en CI/CD.

---

### 2. Stack tecnológico

| Tecnología | Uso en la funcionalidad |
| :--- | :--- |
| **NestJS 12** | Framework backend principal; controladores modulares (`surveys.controller.ts`), inyección de dependencias, endpoints REST (`GET /surveys/:id/report`, `GET /surveys/:id/statistics`) y streaming de archivos con `StreamableFile`. |
| **Prisma 7 + PostgreSQL** | ORM y base de datos relacional; modelado del esquema (`schema.prisma`), ejecución de migraciones SQL, consultas agregadas de estadísticas y transacciones de persistencia. |
| **Next.js 16 (App Router)** | Framework frontend; ruta dinámica `/backoffice/surveys/statistics/[id]`, Server Components y Client Components. |
| **React 19** | Biblioteca base de interfaz; hooks de estado (`useState`, `useEffect`), gestión de diálogos y reactividad en la vista de analíticas. |
| **TypeScript 5.9 / 6** | Lenguaje tipado estricto en frontend y backend para contratos de estadísticas (`SurveyStatisticsResponse`), DTOs y validaciones. |
| **Tailwind CSS 4** | Estilos utilitarios, layout de tarjetas de resultados, barras de progreso y diseño responsivo para analíticas. |
| **shadcn/ui + Lucide React** | Componentes de interfaz (Button, Card, Skeleton, Tooltip, Dialog) e iconografía (`Download`, `RefreshCw`, `BarChart3`, etc.). |
| **TanStack Query + Axios** | Gestión de peticiones asíncronas hacia el backend, mutación de exportación de reporte (`useExportSurveyReport`) y manejo de estados `isPending`. |
| **SimplePdfDocument (Nativo)** | Motor generador de documentos PDF de bajo nivel desarrollado en TypeScript, sin librerías externas foráneas (como `pdfkit`), optimizado para el runtime de NestJS. |
| **sonner** | Sistema de notificaciones toast visuales para confirmación de descarga exitosa ("PDF generado exitosamente") y alertas de error de red. |
| **Vitest + Jest** | Entorno de pruebas unitarias para controladores, servicios de generación PDF (`survey-pdf.service.spec.ts`), repositorios y vistas frontend. |

---

### 3. Estructura de archivos

```text
backend/
├── prisma/
│   ├── schema.prisma                                    # Modelado relacional: Survey, Questions, Options, Responses, Answers
│   └── migrations/
│       ├── 20261022000000_add_surveys/migration.sql     # Migración DDL de tablas base de encuestas
│       └── 20261023000000_survey_questions_and_answers/ # Migración DDL de preguntas, opciones y respuestas
└── src/
    └── modules/
        ├── surveys/
        │   ├── controllers/
        │   │   └── surveys.controller.ts                # Endpoint GET /surveys/:id/report (StreamableFile) y :id/statistics
        │   ├── services/
        │   │   ├── survey-pdf.service.ts                # Generador oficial de PDF institucional con gráficos y membrete DPA
        │   │   └── surveys.service.ts                   # Orquestación de estadísticas, exportación y registro en historial
        │   ├── repositories/
        │   │   └── surveys.repository.ts                # Consultas Prisma: agregación de respuestas, conteos y filtros
        │   ├── constants/
        │   │   ├── survey-pdf.constants.ts              # Colores institucionales (navy, crimson), márgenes y geometría de página
        │   │   └── survey.constants.ts                  # Etiquetas de estado de encuesta y tipos de pregunta
        │   ├── responses/
        │   │   └── survey-statistics.response.ts        # Contrato de datos de analíticas y desglose de preguntas
        │   ├── utils/
        │   │   └── simple-pdf-document.ts               # Motor binario propio para generación de PDFs sin dependencias externas
        │   └── tests/
        │       ├── survey-pdf.service.spec.ts           # Pruebas unitarias de generación de buffer y maquetación de PDF
        │       └── surveys.controller.spec.ts           # Pruebas unitarias del endpoint de exportación
        └── reports/
            ├── reports.module.ts                        # Integración con el módulo central de reportes
            └── services/
                └── report-history.service.ts            # Registro automático en admin_export_histories
frontend/
└── src/
    ├── app/(app)/
    │   └── backoffice/
    │       └── surveys/
    │           └── statistics/[id]/page.tsx             # Ruta dinámica de la vista de analíticas y exportación
    └── modules/
        └── surveys/
            ├── components/
            │   ├── survey-analytics-header.tsx          # Cabecera con título, subtítulo, botón Actualizar y botón Exportar PDF
            │   ├── survey-horizontal-bars.tsx           # Gráficos de barras comparativas por opción de pregunta
            │   ├── survey-question-result-card.tsx      # Tarjeta individual por pregunta con conteo, porcentaje y gráfico
            │   ├── survey-statistics-summary.tsx        # Ficha técnica: muestra total, estado, vigencia y preguntas analizadas
            │   └── survey-statistics-skeleton.tsx       # Esqueletos animados de carga para la vista de estadísticas
            ├── hooks/
            │   ├── use-survey-statistics.ts             # Hook de consulta de métricas globales y desglose
            │   └── use-export-survey-report.ts          # Mutación asíncrona para solicitar y descargar el PDF
            ├── views/
            │   ├── survey-analytics-view.tsx            # Vista integradora de analíticas y control de exportación PDF
            │   └── survey-views.test.tsx                # Suite de pruebas unitarias de vistas y componentes de encuestas
            └── services/
                └── surveys.service.ts                   # Cliente Axios para descarga de blob PDF y consumo de estadísticas
```

---

### 4. Implementación y flujo de datos

#### 4.1 Frontend — Vista de analíticas y acción de exportación (`SurveyAnalyticsView` y componentes)
- **Barra de acciones superior:** Se implementó `SurveyAnalyticsHeader` disponiendo los controles en el orden exacto del mockup: botón **"Actualizar"** a la izquierda y botón **"Exportar PDF"** a la derecha.
- **Protección ante encuestas vacías (Criterio C.A. 14):** Si la encuesta tiene 0 respuestas registradas (`totalResponses === 0`), el botón "Exportar PDF" se inhabilita visual y funcionalmente con un tooltip explicativo para prevenir la emisión de documentos en blanco.
- **Feedback visual no bloqueante:** Al pulsar "Exportar PDF", el botón conmuta a estado de carga (`isGeneratingPdf`), se realiza la petición asíncrona y al completarse se lanza un Toast verde con el mensaje `"PDF generado exitosamente"` (`ExportSuccessToast`), detonando de forma inmediata la descarga del archivo en el navegador del cliente.
- **Gráficos comparativos de barras:** `SurveyHorizontalBars` renderiza proporcionalmente las barras estadísticas de cada opción calculadas sobre el total de respuestas de la pregunta.

#### 4.2 Backend — Motor institucional de PDF (`SurveyPdfService` y `surveys.controller.ts`)
- **Diseño institucional reglamentario:**
  - Franja superior decorativa con colores oficiales UMSS (azul marino y carmesí).
  - Membrete: `"UNIVERSIDAD MAYOR DE SAN SIMÓN"` y `"DIRECCIÓN DE PLANIFICACIÓN ACADÉMICA"`.
  - Código identificador único: `INF-UMSSY-${id.slice(0, 8).toUpperCase()}` y fecha/hora exacta de emisión en formato de Bolivia (`America/La_Paz`).
  - Tarjeta de metadatos (Ficha de la encuesta): Carrera, Gestión, Vigencia, Estado, Muestra Total y Preguntas Analizadas.
  - Resultados detallados: Pregunta enumerada, tipo de pregunta, total de respuestas por pregunta, barras de proporción dibujadas vectorialmente, conteo numérico y porcentaje con un decimal.
  - Paginación automática y salto de página inteligente (`checkPageBreak`) respetando márgenes y límites de pie de página.
- **Exclusión de elementos web:** El documento PDF omite estrictamente la barra lateral (`sidebar`) de navegación y los botones de acción web (`Actualizar`, `Exportar PDF`), ofreciendo un informe ejecutivo limpio.
- **Endpoint seguro:** `@Get(':id/report')` protegido mediante guardia JWT y rol administrativo, retornando un `StreamableFile` con `Content-Type: application/pdf` y cabecera `Content-Disposition: attachment; filename="reporte-encuesta-..."`.

#### 4.3 Persistencia y conexiones en Base de Datos (Prisma + PostgreSQL)
- **Modelado relacional integral:** Se estructuraron las tablas clave del módulo en `schema.prisma`:
  - `Survey`: Registro maestro de encuestas con metadatos de vigencia (`opensAt`, `closesAt`), carrera (`careerId`), gestión (`academicPeriod`) y estado.
  - `SurveyQuestion` y `SurveyQuestionOption`: Preguntas cerradas (opción única y opción múltiple) vinculadas a sus alternativas ordenadas correlativamente (`orderIndex`).
  - `SurveyResponse` y `SurveyAnswer`: Registro transaccional de respuestas completadas por titulados (`respondentId`, `submittedAt`).
- **Eliminación de enums de base de datos:** Se reemplazaron los enums nativos de PostgreSQL por tablas catálogo y validaciones en capa de aplicación para garantizar compatibilidad con migraciones concurrentes y estándares DevOps.
- **Registro en Historial de Reportes (Criterio C.A. 1):** Toda exportación ejecutada por el administrador invoca `reportHistoryService.registerGeneratedReport`, guardando automáticamente una fila en `admin_export_histories` con el nombre del archivo, formato PDF, fecha de generación y tipo de reporte `SURVEY_STATISTICS`.

#### 4.4 Flujo de datos completo
```text
Administrador accede a /backoffice/surveys/statistics/:id
  → Frontend solicita GET /surveys/:id/statistics mediante useSurveyStatistics
  → SurveysRepository ejecuta consultas agregadas en PostgreSQL vía Prisma ORM (conteos, opciones, porcentajes)
  → Se renderizan las métricas en SurveyAnalyticsView y tarjetas de preguntas
  → Administrador presiona el botón "Exportar PDF"
  → Hook useExportSurveyReport ejecuta mutación GET /surveys/:id/report con Axios (responseType: 'blob')
  → Controller valida permisos administrativos y llama a surveysService.exportSurveyPdf
  → SurveysService obtiene los datos estadísticos y llama a SurveyPdfService.generatePdf(stats)
  → SurveyPdfService dibuja el documento con SimplePdfDocument (membrete DPA, tarjetas y barras gráficas)
  → SurveysService invoca ReportHistoryService para registrar la exportación en admin_export_histories
  → Controller devuelve StreamableFile con cabecera Content-Disposition
  → Frontend recibe el Blob, lanza Toast de éxito "PDF generado exitosamente" y detona la descarga automática local
```

---

### 5. Bugs encontrados y correcciones (QA)

A partir de las evaluaciones de calidad del equipo QA (**QAlified**) documentadas en *Copia de Test Case - Epic 10 Segundo Sprint-3* y *Segundo Bug Report*, se resolvieron las siguientes incidencias:

| ID Bug / Caso | Problema detectado | Causa técnica | Solución aplicada | Commit / Referencia |
| :--- | :--- | :--- | :--- | :--- |
| **QA-Nogales-01** | **Disposición invertida de botones en la barra de acciones de analíticas**<br>*(Prioridad: Bajo, Severidad: Cosmético)* | En la vista de analíticas de encuesta, el botón "Generar PDF" aparecía a la izquierda de "Actualizar", contraviniendo el mockup de referencia donde "Actualizar" se ubica a la izquierda. | En el contenedor de botones de `SurveyAnalyticsHeader`, los elementos estaban declarados en orden inverso. Se reordenó el JSX colocando "Actualizar" a la izquierda y "Exportar PDF" a la derecha. | `4f75b8d7f` / `SurveyAnalyticsHeader` |
| **QA-Nogales-02** | **Inconsistencia de dos puntos en el título de la vista de analíticas**<br>*(Prioridad: Bajo, Severidad: Cosmético)* | El encabezado principal mostraba `"Analíticas: [nombre de la encuesta]"` en lugar de la estructura estandarizada `"Analíticas de [nombre de la encuesta]"`. | Cadena literal con dos puntos (`Analíticas: `) en el formateador del encabezado. Se ajustó la plantilla a `"Analíticas de ${statistics.title}"`. | `4f75b8d7f` / `SurveyAnalyticsHeader` |
| **QA-Nogales-03** | **Orden invertido en subtítulo (carrera antes de la cantidad de preguntas)**<br>*(Prioridad: Bajo, Severidad: Cosmético)* | El subtítulo de la vista mostraba la carrera antes de las preguntas (`Licenciatura en Informática · Gestión Todas · 2 preguntas`), alterando el orden del diseño. | Interpolación rígida que anteponía el nombre de carrera. Se reestructuró para mostrar primero la cantidad de preguntas analizadas y luego la carrera (`Resultados de las N preguntas: [Carrera]`). | `4f75b8d7f` / `survey-analytics-header.tsx` |
| **BUG-HU3-02** | **Falta de concordancia gramatical singular en el subtítulo de analíticas**<br>*(Prioridad: Bajo, Severidad: Cosmético)* | Al consultar una encuesta con exactamente una pregunta formulada, el subtítulo mostraba el texto erróneo `"1 preguntas"`. | Concatenación invariable de la palabra `"preguntas"`. Se implementó lógica de pluralización condicional: `"1 pregunta"` cuando `length === 1`, y `"N preguntas"` en cualquier otro caso. | `4f75b8d7f` / `survey-analytics-header.tsx` |
| **BUG-DEVOPS-PDF** | **Dependencia externa de PDF (`pdfkit`) rechazada por estándares de DevOps**<br>*(Prioridad: Alto, Severidad: Crítico)* | La incorporación de paquetes externos de PDF en `backend/package.json` (`pdfkit`) provocaba fallos de pipeline de CI por infracción de antigüedad de dependencias de `pnpm` y dependencias no homologadas. | Se eliminaron completamente las dependencias foráneas de `package.json` y `pnpm-lock.yaml`, y se reimplementó `SurveyPdfService` de forma nativa sobre `SimplePdfDocument`, generando el documento de forma autosuficiente. | `67d52f5c4` (`eliminate package dependency`) |
| **BUG-LAYOUT-TEST** | **Regresión en pruebas unitarias compartidas por espaciado en `app-shell.tsx`**<br>*(Prioridad: Medio, Severidad: Medio)* | Un ajuste en los estilos del layout principal para dar margen a la vista de analíticas rompió las aserciones de pruebas en otros módulos. | Se restauró el padding por defecto en `app-shell.tsx` resolviendo las regresiones de las pruebas compartidas sin alterar la presentación de analíticas. | `67d52f5c4` / `app-shell.tsx` |
| **BUG-PRISMA-ENUMS** | **Incompatibilidad de enums nativos de PostgreSQL en migraciones de base de datos**<br>*(Prioridad: Alto, Severidad: Alto)* | Los enums declarados en `schema.prisma` generaban conflictos con las revisiones de base de datos de DevOps y dificultaban la extensibilidad. | Se removieron los enums nativos de PostgreSQL en `schema.prisma`, sustituyéndolos por tablas catálogo y validaciones en capa TypeScript/Zod. | `e82bbcd7d` (`remove database enums`) |
| **BUG-HU2-01** | **Pérdida de respuestas de encuesta ante corte y recuperación de internet**<br>*(Prioridad: Alto, Severidad: Moderado)* | Al completar parcialmente una encuesta como titulado y sufrir un corte de red temporal, las opciones marcadas se reiniciaban al recuperar la conexión. | El estado de respuestas no mantenía persistencia reactiva en memoria local del cliente. Se sincronizó el estado del formulario (`AnswerSurveyView`) preservando las respuestas del usuario durante fluctuaciones de red. | `3dc8c59a1` / `fe659eef8` |

---

### 6. Mejoras de experiencia de usuario

1. **Documento oficial limpio y profesional:** El PDF generado cuenta con tipografía ejecutiva (Helvetica/Helvetica-Bold), jerarquía visual estandarizada, colores institucionales de la UMSS y exclusión completa de elementos web innecesarios (sidebar y botones).
2. **Prevención de descargas vacías:** Inhabilitación preventiva del botón de exportación cuando la muestra es cero (`n=0`), protegiendo al administrador de descargar reportes carentes de datos estadísticos.
3. **Confirmación visual no invasiva:** Notificación Toast inferior derecha que confirma la finalización exitosa del proceso sin recargar la pantalla ni entorpecer el flujo de trabajo.
4. **Descarga transparente y directa:** El flujo no abre pestañas en blanco innecesarias; utiliza descarga directa por streaming de Blob con nomenclatura descriptiva estandarizada (`reporte-encuesta-[titulo]-[periodo]-[fecha].pdf`).
5. **Autosuficiencia y velocidad:** Al eliminar dependencias pesadas de terceros en Node.js, la compilación del buffer PDF se ejecuta en milisegundos sin sobrecargar el servidor backend.

---

### 7. Trabajo que no se pudo fusionar / Dificultades

- **Bloqueo de dependencias de paquetes en CI:** Inicialmente se evaluó utilizar librerías npm consagradas para generación PDF como `pdfkit`. Sin embargo, las reglas de integración continua (CI) de DevOps imponían restricciones estrictas de *release age* y auditoría de paquetes en `pnpm`. Esto motivó la decisión arquitectónica de descartar dependencias externas en el commit `67d52f5c4` y construir una implementación propia de `SimplePdfDocument` en TypeScript, asegurando la aprobación automática de los pipelines.
- **Sincronización con el módulo centralizado de notificaciones:** Durante el Sprint 2 se implementó inicialmente el flujo de notificaciones para titulados en la ruta `/surveys` (commit `3dc8c59a1`). Posteriormente, la arquitectura general del proyecto decidió centralizar todas las alertas en la bandeja unificada `/notifications?filter=SURVEYS`, lo que requirió adaptar redirecciones y resolvers de enlaces para garantizar la interoperabilidad entre módulos sin romper compatibilidad.

---

### 8. Pruebas

Se diseñó e implementó una suite exhaustiva de pruebas unitarias y de integración tanto en backend como en frontend:
- `survey-pdf.service.spec.ts` (Backend):
  - Verifica que `SurveyPdfService.generatePdf` retorne un `Buffer` válido no vacío con la firma binaria de archivo PDF (`%PDF`).
  - Valida que el documento incluya el membrete institucional de la UMSS y la DPA.
  - Comprueba el formateo correcto de porcentajes, conteos numéricos y ajuste de líneas en enunciados de preguntas largos.
  - Verifica el comportamiento ante encuestas con preguntas de opción única y opción múltiple.
- `surveys.controller.spec.ts` (Backend):
  - Valida que el endpoint `@Get(':id/report')` invoque `exportSurveyPdf` con los parámetros correspondientes y retorne una instancia de `StreamableFile`.
  - Verifica el manejo de excepciones cuando el ID de la encuesta no existe (`SurveyNotFoundException`).
- `survey-views.test.tsx` (Frontend):
  - Valida el renderizado correcto de la vista de analíticas, tarjetas de preguntas y gráficos de barras comparativos.
  - Verifica que el botón "Exportar PDF" se deshabilite cuando `totalResponses === 0`.
  - Simula la ejecución de la mutación de descarga de reporte y verifica la llamada a `downloadFile`.
- `answer-survey-view.test.tsx`:
  - Pruebas del formulario de respuesta de encuestas para titulados y validación de respuestas obligatorias.

---

### 9. Resultado final

La funcionalidad de la Historia de Usuario 5 y las conexiones de base de datos quedaron totalmente operativas y aprobadas:
- El Administrador cuenta con una herramienta confiable para generar y descargar informes estadísticos oficiales en formato PDF con diseño institucional de la UMSS y DPA.
- El PDF contiene la ficha completa de la encuesta, desglose por pregunta, conteos absolutos, porcentajes calculados y gráficos de barras comparativos.
- Cada exportación exitosa queda auditada y registrada automáticamente en el Historial de Reportes (`admin_export_histories`).
- La base de datos relacional PostgreSQL cuenta con el modelo normalizado de encuestas, preguntas, opciones y respuestas, completamente integrado vía Prisma ORM sin enums conflictivos.
- Flujo robusto con retroalimentación mediante Toasts, prevención de descargas vacías y compatibilidad total con los estándares de DevOps y CI/CD.

---

### 10. Commits realizados

| Hash | Fecha | Descripción del Commit | Estado / Destino |
| :--- | :--- | :--- | :--- |
| `4f75b8d7f` / `d45a9cb45` | 23/10/2026 | `feat(surveys): add survey analytics and official PDF report export` | Fusionado en la épica (PR `#1391` / `b2419462f`). Modelado relacional en Prisma (`Survey`, `SurveyQuestion`, `SurveyResponse`, etc.), migraciones SQL, endpoint de exportación PDF, servicio `SurveyPdfService`, vista frontend de analíticas y tests. |
| `67d52f5c4` / `97db8a29e` | 23/10/2026 | `fix(surveys): eliminate package dependency and fix layout test regressions` | Fusionado en la épica (PR `#1391`). Reemplazo de dependencias externas por generador nativo `SimplePdfDocument`, restauración de estilos en `app-shell.tsx` y estabilización de pruebas. |
| `3dc8c59a1` / `814911fb0` | 23/10/2026 | `feat(surveys): implement graduate survey notifications and response submission` | Fusionado en la épica (PR `#1418` / `04654eda6`). Persistencia relacional de respuestas y opciones de titulados en PostgreSQL vía Prisma, endpoints GET/POST y pruebas. |
| `fe659eef8` / `4d40ee7dc` | 24/10/2026 | `test(surveys): fix api response mocks in answer survey test` | Fusionado en la épica (PR `#1418`). Corrección de mocks de respuestas API en pruebas unitarias de encuestas. |
| `e82bbcd7d` | 26/10/2026 | `fix(surveys): remove database enums and reuse shared frontend components` | Fusionado en la épica (PR `#1669` / `4f909348b`). Sustitución de enums de base de datos por tablas catálogo en Prisma y reutilización de componentes compartidos. |
