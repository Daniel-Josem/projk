// Lógica de la pantalla flotante de tareas
// Reemplaza tareasEjemplo por los datos reales inyectados desde Flask
const tareas = window.tareasUsuario || [];

const contenedorTarjetas = document.getElementById('contenedorTarjetasTareas');

function mostrarTarjetasTareas() {
  contenedorTarjetas.innerHTML = '';
  tareas.forEach(tarea => {
    const col = document.createElement('div');
    col.className = 'col-12 col-md-6 col-lg-4';
    const card = document.createElement('div');
    card.className = 'tarea-tarjeta';
    card.innerHTML = `
      <div class="tarea-titulo">${tarea.titulo}</div>
      <div class="tarea-prioridad">
        <span class="badge bg-${tarea.prioridad === 'alta' ? 'danger' : tarea.prioridad === 'media' ? 'warning' : 'secondary'} text-white">${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}</span>
        <span class="tarea-fecha"><i class="bi bi-calendar-event"></i> ${tarea.fecha_vencimiento}</span>
      </div>
      <div class="icono-estado">
        ${tarea.estado === 'completado' ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-hourglass-split text-warning"></i>'}
      </div>
    `;
    // Mostrar detalles de la tarea en un panel flotante a la derecha (moderno)
    card.onclick = (e) => {
      e.stopPropagation();
      mostrarPanelDetalleTareaOverlay(tarea.id);
    };
    col.appendChild(card);
    contenedorTarjetas.appendChild(col);
  });
}

function marcarTareaCompletada(id) {
  const tarea = tareas.find(t => t.id === id);
  if (!tarea || tarea.estado === 'completado') return;
  fetch(`/api/tarea/completar/${id}`, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(resp => resp.json())
    .then(data => {
      if (data.ok) {
        tarea.estado = 'completado';
        mostrarPanelDetalleTareaOverlay(id);
        mostrarTarjetasTareas();
        alert('¡Tarea marcada como completada!');
      } else {
        alert('No se pudo marcar como completada: ' + (data.msg || ''));
      }
    })
    .catch(() => alert('Error de red al marcar como completada.'));
}

// === Overlay Fullscreen para Mis Tareas ===
let overlayTareas = null;

function crearOverlayTareas() {
  if (document.getElementById('overlayMisTareas')) return;
  // Elimina overlays de fondo sobrantes si existen
  document.querySelectorAll('.overlay-fondo').forEach(el => el.remove());
  overlayTareas = document.createElement('div');
  overlayTareas.id = 'overlayMisTareas';
  overlayTareas.innerHTML = `
    <div class="overlay-fondo"></div>
    <div class="overlay-contenido animate__animated animate__fadeInDown">
      <button id="cerrarOverlayTareas" class="btn btn-light btn-close-overlay" title="Cerrar"><i class="bi bi-x-lg"></i></button>
      <h2 class="overlay-titulo mb-4"><i class="bi bi-list-task"></i> Mis Tareas</h2>
      <div class="row g-3" id="contenedorTarjetasTareasOverlay"></div>
    </div>
  `;
  document.body.appendChild(overlayTareas);
  document.getElementById('cerrarOverlayTareas').onclick = cerrarOverlayTareas;
  overlayTareas.querySelector('.overlay-fondo').onclick = cerrarOverlayTareas;
}

function mostrarOverlayTareas() {
  crearOverlayTareas();
  overlayTareas = document.getElementById('overlayMisTareas');
  overlayTareas.style.display = 'flex';
  document.body.classList.add('no-scroll');
  mostrarTarjetasTareasOverlay();
}

function cerrarOverlayTareas() {
  if (overlayTareas) overlayTareas.style.display = 'none';
  document.body.classList.remove('no-scroll');
  // Elimina cualquier overlay de fondo sobrante
  document.querySelectorAll('.overlay-fondo').forEach(el => el.remove());
  // Elimina el overlay del DOM para evitar duplicados
  if (overlayTareas) overlayTareas.remove();
  overlayTareas = null;
}

function mostrarTarjetasTareasOverlay() {
  const contenedor = document.getElementById('contenedorTarjetasTareasOverlay');
  if (!contenedor) return;
  contenedor.innerHTML = '';
  tareas.forEach(tarea => {
    const col = document.createElement('div');
    col.className = 'col-12 col-md-6 col-lg-4';
    const card = document.createElement('div');
    card.className = 'tarea-tarjeta tarea-tarjeta-overlay';
    card.innerHTML = `
      <div class="tarea-titulo">${tarea.titulo}</div>
      <div class="tarea-prioridad">
        <span class="badge bg-${tarea.prioridad === 'alta' ? 'danger' : tarea.prioridad === 'media' ? 'warning' : 'secondary'} text-white">${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}</span>
        <span class="tarea-fecha"><i class="bi bi-calendar-event"></i> ${tarea.fecha_vencimiento}</span>
      </div>
      <div class="icono-estado">
        ${tarea.estado === 'completado' ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-hourglass-split text-warning"></i>'}
      </div>
    `;
    // Mostrar detalles de la tarea en un panel flotante a la derecha del overlay
    card.onclick = (e) => {
      e.stopPropagation();
      mostrarPanelDetalleTareaOverlay(tarea.id);
    };
    col.appendChild(card);
    contenedor.appendChild(col);
  });
}

function mostrarPanelDetalleTareaOverlay(id) {
  fetch(`/api/tarea/${id}`)
    .then(resp => resp.json())
    .then(tarea => {
      if (!tarea || !tarea.id) return;
      // Eliminar panel anterior si existe
      let panel = document.getElementById('panelDetalleTareaOverlay');
      if (panel) {
        panel.remove();
      }
      panel = document.createElement('div');
      panel.id = 'panelDetalleTareaOverlay';
      panel.className = 'panel-detalle-tarea-overlay-visible';
      document.body.appendChild(panel);
      // Avatar: primera letra del título o ícono
      const avatar = `<span class="tarea-avatar"><i class='bi bi-clipboard-check'></i></span>`;
      panel.innerHTML = `
        <button class="btn btn-light btn-close-overlay" style="position:absolute;top:10px;right:10px;z-index:10" id="cerrarPanelDetalleTareaOverlay"><i class="bi bi-x-lg"></i></button>
        <div class="tarea-detalle-titulo mb-2">${avatar} ${tarea.titulo}</div>
        <div class="tarea-detalle-estado mb-2">
          <span class="badge bg-${tarea.estado === 'completado' ? 'success' : 'warning'}">${tarea.estado === 'completado' ? 'Completada' : 'Incompleta'}</span>
          <span class="badge bg-${tarea.prioridad === 'alta' ? 'danger' : tarea.prioridad === 'media' ? 'warning' : 'secondary'} text-white">${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}</span>
          <span class="tarea-fecha"><i class="bi bi-calendar-event"></i> ${tarea.fecha_vencimiento}</span>
        </div>
        <div class="mb-2">${tarea.descripcion}</div>
        <hr />
        <div class="tarea-detalle-archivos mb-2">
          <label class="form-label">Archivos:</label>
          <div>
            ${tarea.archivos && tarea.archivos.length ? tarea.archivos.map(a => `<div class='archivo-item'><i class='bi bi-paperclip'></i> <a href='${a.url}' download>${a.nombre}</a></div>`).join('') : '<span class="text-muted">Sin archivos</span>'}
          </div>
          <form id="formSubirArchivoOverlay${tarea.id}" class="mt-2" enctype="multipart/form-data">
            <input type="file" name="archivo" class="form-control form-control-sm mb-1" accept="*/*">
            <button type="submit" class="btn btn-outline-success btn-sm">Subir archivo</button>
          </form>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-success btn-sm flex-fill" id="btnCompletarTareaOverlay" ${tarea.estado === 'completado' ? 'disabled' : ''}>Marcar como completada</button>
          <button class="btn btn-outline-primary btn-sm flex-fill" id="btnEditarTareaOverlay"><i class="bi bi-pencil"></i> Editar</button>
        </div>
      `;
      panel.style.position = 'fixed';
      panel.style.top = '0';
      panel.style.right = '0';
      panel.style.width = '400px';
      panel.style.height = '100vh';
      panel.style.background = 'rgba(255,255,255,0.98)';
      panel.style.boxShadow = '-4px 0 24px rgba(0,0,0,0.13)';
      panel.style.zIndex = '4000';
      panel.style.padding = '32px 28px 24px 28px';
      panel.style.overflowY = 'auto';

      // Cerrar panel al hacer clic en la X
      document.getElementById('cerrarPanelDetalleTareaOverlay').onclick = function() {
        panel.remove();
      };
      // Cerrar panel al hacer clic fuera de él
      setTimeout(() => {
        document.addEventListener('mousedown', function handler(e) {
          if (panel && !panel.contains(e.target)) {
            panel.remove();
            document.removeEventListener('mousedown', handler);
          }
        });
      }, 100);

      // Subida de archivo
      const form = document.getElementById(`formSubirArchivoOverlay${tarea.id}`);
      form.onsubmit = async function(e) {
        e.preventDefault();
        const archivoInput = form.querySelector('input[name="archivo"]');
        if (!archivoInput.files.length) {
          alert('Selecciona un archivo.');
          return false;
        }
        const formData = new FormData();
        formData.append('archivo', archivoInput.files[0]);
        try {
          const resp = await fetch(`/api/tarea/subir-archivo/${tarea.id}`, {
            method: 'POST',
            body: formData
          });
          const data = await resp.json();
          if (data.ok) {
            mostrarPanelDetalleTareaOverlay(tarea.id);
            alert('Archivo subido correctamente.');
          } else {
            alert('Error al subir archivo: ' + (data.msg || ''));
          }
        } catch (err) {
          alert('Error de red al subir archivo.');
        }
        return false;
      };
      // Marcar como completada
      document.getElementById('btnCompletarTareaOverlay').onclick = function() {
        fetch(`/api/tarea/completar/${tarea.id}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
          .then(resp => resp.json())
          .then(data => {
            if (data.ok) {
              mostrarPanelDetalleTareaOverlay(tarea.id);
              alert('¡Tarea marcada como completada!');
            } else {
              alert('No se pudo marcar como completada: ' + (data.msg || ''));
            }
          })
          .catch(() => alert('Error de red al marcar como completada.'));
      };
      // Botón editar: permite volver a subir archivo aunque la tarea esté completada
      document.getElementById('btnEditarTareaOverlay').onclick = function() {
        // Mostrar el formulario de subida aunque la tarea esté completada
        const form = document.getElementById(`formSubirArchivoOverlay${tarea.id}`);
        if (form) {
          form.style.display = 'block';
          form.scrollIntoView({behavior: 'smooth', block: 'center'});
        }
        // Ocultar el botón de completar para evitar confusión
        const btnCompletar = document.getElementById('btnCompletarTareaOverlay');
        if (btnCompletar) btnCompletar.style.display = 'none';
      };
      // Si la tarea está completada, ocultar el formulario de subida hasta que se pulse editar
      if (tarea.estado === 'completado') {
        const form = document.getElementById(`formSubirArchivoOverlay${tarea.id}`);
        if (form) form.style.display = 'none';
      }
      // Mostrar el panel (asegura que esté visible)
      panel.style.display = 'block';
    });
}

// Esperar a que el DOM esté listo para inicializar listeners
window.addEventListener('DOMContentLoaded', function () {
  const btnMisTareas = document.getElementById('btn-mis-tareas');
  // El overlay no depende de seccionMisTareas ni seccionInicio
  if (btnMisTareas) {
    btnMisTareas.addEventListener('click', function (e) {
      e.preventDefault();
      mostrarOverlayTareas();
    });
  }
  // Forzar recarga de tarjetas al cargar la página
  if (typeof mostrarTarjetasTareas === 'function') {
    console.log('Ejecutando mostrarTarjetasTareas al cargar la página');
    mostrarTarjetasTareas();
  } else {
    console.error('mostrarTarjetasTareas no está definida');
  }
});
