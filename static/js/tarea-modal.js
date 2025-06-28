// Mostrar solo la sección seleccionada
        function mostrarSeccion(id) {
          const secciones = [
            'seccion-inicio',
            'seccion-mis-tareas',
            'contenido-planificacion',
            'contenido-calendario',
            'seccion-estadisticas',
            'seccion-ayuda'
          ];
          secciones.forEach(sec => {
            const el = document.getElementById(sec);
            if (el) el.style.display = 'none';
          });
          const mostrar = document.getElementById(id);
          if (mostrar) mostrar.style.display = 'block';
        }
        // Listeners para el menú lateral
        document.getElementById('btn-inicio').onclick = function() { mostrarSeccion('seccion-inicio'); };
        document.getElementById('btn-mis-tareas').onclick = function() { mostrarSeccion('seccion-mis-tareas'); };
        document.getElementById('btn-planificacion').onclick = function() { mostrarSeccion('contenido-planificacion'); };
        document.getElementById('btn-calendario').onclick = function() { mostrarSeccion('contenido-calendario'); };
        document.getElementById('btn-estadisticas').onclick = function() { mostrarSeccion('seccion-estadisticas'); };
        document.getElementById('btn-ayuda').onclick = function() { mostrarSeccion('seccion-ayuda'); };
        // Al cargar, solo mostrar inicio
        mostrarSeccion('seccion-inicio');
    
      
// --- FILTRO Y ACTUALIZACIÓN DINÁMICA DE TARJETAS Y RESUMEN DE ESTADO ---
const tareasOriginal = window.tareasUsuario || [];
const contenedorTarjetas = document.getElementById('contenedorTarjetasTareas');
const inputBuscar = document.getElementById('buscar-tarea');
const resumenIds = {
  total: 'total-tareas-js',
  completadas: 'tareas-completadas-js',
  progreso: 'tareas-progreso-js',
  atrasadas: 'tareas-atrasadas-js'
};

function normalizarEstado(estado) {
  if (!estado) return '';
  estado = estado.toLowerCase();
  if (estado.includes('completad')) return 'completado';
  if (estado.includes('progreso')) return 'en progreso';
  if (estado.includes('atrasad')) return 'atrasada';
  if (estado.includes('pendiente')) return 'pendiente';
  return estado;
}

function renderTarjetas(tareas) {
  let html = '';
  if (!tareas.length) {
    html = `<div class="col-12"><div class="alert alert-info text-center">No tienes tareas asignadas.</div></div>`;
  } else {
    tareas.forEach(tarea => {
      const estadoNorm = normalizarEstado(tarea.estado);
      html += `
      <div class="col">
        <div class="card h-100 shadow-sm border-0 tarea-card-custom position-relative tarea-borde-${estadoNorm.replace(' ', '-')} animate__animated animate__fadeInUp tarea-interactiva" data-tarea-id="${tarea.id}">
          <div class="card-body d-flex flex-column justify-content-between">
            <div>
              <h5 class="card-title fw-bold mb-2 tarea-titulo">${tarea.titulo}</h5>
              <p class="card-text text-muted mb-3 tarea-desc">${tarea.descripcion}</p>
            </div>
            <ul class="list-group list-group-flush mb-3 tarea-lista">
              <li class="list-group-item px-0 py-1 border-0 d-flex align-items-center">
                <i class="bi bi-flag me-2 text-danger tarea-icon"></i>
                <span class="fw-semibold">Prioridad:</span> <span class="ms-1">${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}</span>
              </li>
              <li class="list-group-item px-0 py-1 border-0 d-flex align-items-center">
                <i class="bi bi-calendar-event me-2 text-primary tarea-icon"></i>
                <span class="fw-semibold">Vence:</span> <span class="ms-1">${tarea.fecha_vencimiento}</span>
              </li>
              <li class="list-group-item px-0 py-1 border-0 d-flex align-items-center">
                <i class="bi bi-clipboard-check me-2 text-success tarea-icon"></i>
                <span class="fw-semibold">Estado:</span> <span class="ms-1">${tarea.estado.charAt(0).toUpperCase() + tarea.estado.slice(1)}</span>
              </li>
            </ul>
            <div class="d-flex justify-content-between align-items-center mt-auto">
              ${tarea.ruta_archivo ? `<a href="/static/archivos_tareas/${tarea.ruta_archivo}" class="btn btn-archivo-tarea" target="_blank"><i class="bi bi-paperclip me-1"></i> Archivo</a>` : ''}
              <span class="badge estado-badge estado-badge-${estadoNorm.replace(' ', '-')}">
                <i class="bi ${estadoNorm==='completado' ? 'bi-check-circle-fill' : estadoNorm==='en progreso' ? 'bi-hourglass-split' : estadoNorm==='atrasada' ? 'bi-exclamation-circle-fill' : 'bi-circle'} me-1"></i>
                ${tarea.estado.charAt(0).toUpperCase() + tarea.estado.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </div>`;
    });
  }
  contenedorTarjetas.innerHTML = html;
}

function actualizarResumen(tareas) {
  const total = tareas.length;
  const completadas = tareas.filter(t => normalizarEstado(t.estado) === 'completado').length;
  const progreso = tareas.filter(t => normalizarEstado(t.estado) === 'en progreso').length;
  const atrasadas = tareas.filter(t => normalizarEstado(t.estado) === 'atrasada').length;
  document.getElementById(resumenIds.total).textContent = total;
  document.getElementById(resumenIds.completadas).textContent = completadas;
  document.getElementById(resumenIds.progreso).textContent = progreso;
  document.getElementById(resumenIds.atrasadas).textContent = atrasadas;
}

function filtrarTareas() {
  let tareas = [...tareasOriginal];
  // Filtros de estado
  const estados = [];
  if (document.getElementById('filter-pendiente')?.checked) estados.push('pendiente');
  if (document.getElementById('filter-progreso')?.checked) estados.push('en progreso');
  if (document.getElementById('filter-completada')?.checked) estados.push('completado');
  // Filtros de prioridad
  const prioridades = [];
  if (document.getElementById('filter-alta')?.checked) prioridades.push('alta');
  if (document.getElementById('filter-media')?.checked) prioridades.push('media');
  if (document.getElementById('filter-baja')?.checked) prioridades.push('baja');
  // Filtros de fecha
  const desde = document.getElementById('filter-date-from')?.value;
  const hasta = document.getElementById('filter-date-to')?.value;
  // Filtro de búsqueda
  const texto = (inputBuscar.value || '').toLowerCase();

  tareas = tareas.filter(t => {
    const estadoNorm = normalizarEstado(t.estado);
    const coincideEstado = !estados.length || estados.includes(estadoNorm);
    const coincidePrioridad = !prioridades.length || prioridades.includes((t.prioridad||'').toLowerCase());
    let coincideFecha = true;
    if (desde && t.fecha_vencimiento < desde) coincideFecha = false;
    if (hasta && t.fecha_vencimiento > hasta) coincideFecha = false;
    const coincideTexto = !texto || (t.titulo && t.titulo.toLowerCase().includes(texto)) || (t.descripcion && t.descripcion.toLowerCase().includes(texto));
    return coincideEstado && coincidePrioridad && coincideFecha && coincideTexto;
  });
  renderTarjetas(tareas);
  actualizarResumen(tareas);
}

// Eventos
inputBuscar?.addEventListener('input', filtrarTareas);
document.getElementById('aplicar-filtros')?.addEventListener('click', function() {
  filtrarTareas();
  const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('tareaFilterModal'));
  modal.hide();
});
// Inicializar al cargar sección
renderTarjetas(tareasOriginal);
actualizarResumen(tareasOriginal);

// tarea-modal.js
// Delegación de eventos para tarjetas de tarea

document.addEventListener('DOMContentLoaded', function() {
  const tareas = window.tareasUsuario || [];
  const contenedor = document.getElementById('contenedorTarjetasTareas');

  if (contenedor) {
    contenedor.addEventListener('click', function(e) {
      // Buscar la tarjeta más cercana al click
      const card = e.target.closest('.tarea-card-custom.tarea-interactiva');
      if (!card) return;
      const tareaId = card.getAttribute('data-tarea-id');
      const tarea = tareas.find(t => String(t.id) === String(tareaId));
      if (!tarea) return;
      // Llenar el modal con los detalles de la tarea
      const cont = document.getElementById('detalle-tarea-contenido');
      cont.innerHTML = `
        <h4 class="fw-bold mb-2">${tarea.titulo}</h4>
        <p class="mb-2 text-muted">${tarea.descripcion}</p>
        <ul class="list-group list-group-flush mb-3">
          <li class="list-group-item px-0 py-1 border-0"><b>Prioridad:</b> ${tarea.prioridad}</li>
          <li class="list-group-item px-0 py-1 border-0"><b>Vence:</b> ${tarea.fecha_vencimiento}</li>
          <li class="list-group-item px-0 py-1 border-0"><b>Estado:</b> ${tarea.estado}</li>
        </ul>
      `;
      // Archivo para descargar
      const archivoDiv = document.getElementById('detalle-tarea-archivo');
      if (tarea.ruta_archivo) {
        archivoDiv.innerHTML = `<a href="/static/archivos_tareas/${tarea.ruta_archivo}" class="btn btn-outline-success" download><i class="bi bi-download"></i> Descargar archivo</a>`;
      } else {
        archivoDiv.innerHTML = `<span class='text-muted'>No hay archivo adjunto.</span>`;
      }
      // Limpiar mensajes de subida
      document.getElementById('mensajeArchivoTarea').innerHTML = '';
      // Guardar el id de la tarea seleccionada para la subida/edición
      document.getElementById('formSubirArchivoTarea').setAttribute('data-tarea-id', tarea.id);
      document.getElementById('btnEditarTareaModal').setAttribute('data-tarea-id', tarea.id);
      // Mostrar el modal
      const modal = new bootstrap.Modal(document.getElementById('modalDetalleTarea'));
      modal.show();
    });
  }

  // Subida de archivo (simulada)
  const formArchivo = document.getElementById('formSubirArchivoTarea');
  if (formArchivo) {
    formArchivo.onsubmit = function(e) {
      e.preventDefault();
      const tareaId = this.getAttribute('data-tarea-id');
      const input = document.getElementById('inputArchivoTarea');
      if (!input.files.length) {
        document.getElementById('mensajeArchivoTarea').innerHTML = '<span class="text-danger">Selecciona un archivo.</span>';
        return;
      }
      // Simulación de subida
      document.getElementById('mensajeArchivoTarea').innerHTML = '<span class="text-success">Archivo subido correctamente (simulado).</span>';
      input.value = '';
    };
  }

  // Botón editar (simulado)
  const btnEditar = document.getElementById('btnEditarTareaModal');
  if (btnEditar) {
    btnEditar.onclick = function() {
      const tareaId = this.getAttribute('data-tarea-id');
      alert('Funcionalidad de edición de tarea (simulada) para tarea ID: ' + tareaId);
    };
  }
});