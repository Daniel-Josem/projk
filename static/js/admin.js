
document.addEventListener('DOMContentLoaded', function () {
  const mainContent = document.getElementById('mainContent');
  const statsEl = document.getElementById('stats');
  const dashboardLink = document.getElementById('dashboard-link');
  const profesoresLink = document.getElementById('profesores-link');
  const registroLink = document.getElementById('registro-profesor-link');

  document.getElementById('proyectos-count').textContent = '5';

  function ocultarSecciones() {
    if (statsEl) statsEl.style.display = 'none';
    mainContent.innerHTML = '';
  }

  function cargarEstadisticas() {
    if (statsEl) statsEl.style.display = 'flex';
  }

  fetch('/api/trabajadores/count')
    .then(response => response.json())
    .then(data => {
      document.getElementById('trabajadores-count').textContent = data.count;
    })
    .catch(error => console.error('Error al obtener trabajadores:', error));

  fetch('/api/lider/count')
    .then(response => response.json())
    .then(data => {
      document.getElementById('lideres-count').textContent = data.count;
    })
    .catch(error => console.error('Error al obtener líderes:', error));

  if (registroLink) {
    registroLink.addEventListener('click', function (e) {
      e.preventDefault();
      ocultarSecciones();

      const formularioHTML = `
        <div class="container mt-4">
          <h3 class="mb-4">Registrar Nuevo Líder</h3>
          <form id="formRegistroLider">
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">Nombre</label><input type="text" class="form-control" name="nombre" required></div>
              <div class="col-md-6"><label class="form-label">Apellido</label><input type="text" class="form-control" name="apellido" required></div>
              <div class="col-md-6"><label class="form-label">Usuario</label><input type="text" class="form-control" name="usuario" required></div>
              <div class="col-md-6"><label class="form-label">Contraseña</label><input type="password" class="form-control" name="contrasena" required></div>
              <div class="col-md-6"><label class="form-label">Documento</label><input type="text" class="form-control" name="documento" required></div>
              <div class="col-md-6"><label class="form-label">Grupo</label>
                <select class="form-select" name="grupo" required>
                  <option disabled selected value="">Selecciona un grupo</option>
                  <option>Grupo 1</option><option>Grupo 2</option><option>Grupo 3</option><option>Grupo 4</option><option>Grupo 5</option>
                </select>
              </div>
              <div class="col-md-6"><label class="form-label">Proyecto</label>
                <select class="form-select" name="proyecto" required>
                  <option disabled selected value="">Selecciona un proyecto</option>
                  <option>Torre Prado</option><option>Torre Milton</option><option>Fiscalia Medellin</option><option>San velente</option><option>Anay beauty</option>
                </select>
              </div>
              <div class="col-md-6"><label class="form-label">Correo Electrónico</label><input type="email" class="form-control" name="correo" required></div>
              <div class="col-md-6"><label class="form-label">Teléfono</label><input type="text" class="form-control" name="telefono" required></div>
              <div class="col-md-6"><label class="form-label">Dirección</label><input type="text" class="form-control" name="direccion" required></div>
            </div>
            <div class="mt-4">
              <button type="submit" class="btn btn-success">Registrar</button>
            </div>
          </form>
        </div>
      `;
      mainContent.innerHTML = formularioHTML;

      const formRegistro = document.getElementById('formRegistroLider');
      if (formRegistro) {
        formRegistro.addEventListener('submit', function (e) {
          e.preventDefault();
          const formData = new FormData(this);
          const data = Object.fromEntries(formData.entries());

          fetch('/api/lideres/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(res => res.json())
          .then(response => {
            if (response.message) {
              alert("✅ " + response.message);
              formRegistro.reset();

              fetch('/api/lider/count')
                .then(response => response.json())
                .then(data => {
                  document.getElementById('lideres-count').textContent = data.count;
                });

              fetch('/api/lideres')
                .then(res => res.json())
                .then(lideres => {
                  let tablaHTML = `
                    <h3 class="mb-4">Lista de Líderes</h3>
                    <table class="table table-bordered table-hover">
                      <thead class="table-light">
                        <tr>
                          <th>ID</th>
                          <th>Nombre</th>
                          <th>Usuario</th>
                          <th>Documento</th>
                          <th>Grupo</th>
                          <th>Proyecto</th>
                          <th>Correo</th>
                          <th>Teléfono</th>
                          <th>Dirección</th>
                          <th>Estado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>`;
                  lideres.forEach(l => {
                    tablaHTML += `
                      <tr id="fila-lider-${l.id}">
                        <td>${l.id}</td>
                        <td><span class="nombre-lider-clickable" data-id="${l.id}">${l.nombre_completo}</span></td>
                        <td>${l.nombre_usuario}</td>
                        <td>${l.documento}</td>
                        <td>${l.grupo}</td>
                        <td>${l.proyecto}</td>
                        <td>${l.correo}</td>
                        <td>${l.telefono}</td>
                        <td>${l.direccion}</td>
                        <td><span class="badge ${l.estado === 'activo' ? 'bg-success' : 'bg-secondary'}">${l.estado}</span></td>
                        <td>
                          ${l.estado === 'activo'
                            ? `<button class="btn btn-danger btn-sm inactivar-lider" data-id="${l.id}">Inactivar</button>`
                            : `<button class="btn btn-secondary btn-sm" disabled>Inactivado</button>`}
                        </td>
                      </tr>`;
                  });
                  tablaHTML += `</tbody></table>`;
                  mainContent.innerHTML = tablaHTML;
                  cargarEventosLideres();
                });
            } else if (response.error) {
              alert("❌ Error: " + response.error);
            }
          })
          .catch(err => {
            console.error("Error al registrar líder:", err);
            alert("❌ Error al registrar líder.");
          });
        });
      }
    });
  }

  if (profesoresLink) {
    profesoresLink.addEventListener('click', function (e) {
      e.preventDefault();
      ocultarSecciones();

      fetch('/api/lideres')
        .then(res => res.json())
        .then(lideres => {
          let tablaHTML = `
            <h3 class="mb-4">Lista de Líderes</h3>
            <table class="table table-bordered table-hover">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Documento</th>
                  <th>Grupo</th>
                  <th>Proyecto</th>
                  <th>Correo</th>
                  <th>Teléfono</th>
                  <th>Dirección</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>`;
          lideres.forEach(l => {
            tablaHTML += `
              <tr id="fila-lider-${l.id}">
                <td>${l.id}</td>
                <td><span class="nombre-lider-clickable" data-id="${l.id}">${l.nombre_completo}</span></td>
                <td>${l.nombre_usuario}</td>
                <td>${l.documento}</td>
                <td>${l.grupo}</td>
                <td>${l.proyecto}</td>
                <td>${l.correo}</td>
                <td>${l.telefono}</td>
                <td>${l.direccion}</td>
                <td><span class="badge ${l.estado === 'activo' ? 'bg-success' : 'bg-secondary'}">${l.estado}</span></td>
                <td>
                  ${l.estado === 'activo'
                    ? `<button class="btn btn-danger btn-sm inactivar-lider" data-id="${l.id}">Inactivar</button>`
                    : `<button class="btn btn-secondary btn-sm" disabled>Inactivado</button>`}
                </td>
              </tr>`;
          });
          tablaHTML += `</tbody></table>`;
          mainContent.innerHTML = tablaHTML;
          cargarEventosLideres();
        })
        .catch(error => console.error('Error al cargar líderes:', error));
    });
  }
function cargarEventosLideres() {
  // Activar botón "Inactivar"
  document.querySelectorAll('.inactivar-lider').forEach(btn => {
    btn.addEventListener('click', function () {
      const id = this.dataset.id;

      fetch(`/api/lider/inactivar/${id}`, {
        method: 'POST'
      })
        .then(res => res.json())
        .then(data => {
          alert("🚫 " + data.message);

          // ✅ Borrar visualmente la fila
          const fila = document.getElementById(`fila-lider-${id}`);
          if (fila) fila.remove();  // ✅ Esto mantiene el registro en la BD pero lo quita visualmente
        })
        .catch(err => console.error("Error al inactivar líder:", err));
    });
  });

    document.querySelectorAll('.nombre-lider-clickable').forEach(span => {
    span.addEventListener('click', function () {
      const id = this.dataset.id;
      fetch(`/api/lider/${id}`)
        .then(res => res.json())
        .then(l => {
          mainContent.innerHTML = `
            <div class="container mt-4">
              <h3>Editar Líder</h3>
              <form id="formEditarLider">
                <input type="hidden" name="id" value="${l.id}">
                <div class="row g-3">
                  <div class="col-md-6"><label class="form-label">Nombre Completo</label><input type="text" name="nombre_completo" class="form-control" value="${l.nombre_completo}" required></div>
                  <div class="col-md-6"><label class="form-label">Usuario</label><input type="text" name="nombre_usuario" class="form-control" value="${l.nombre_usuario}" required></div>
                  <div class="col-md-6"><label class="form-label">Documento</label><input type="text" name="documento" class="form-control" value="${l.documento}" required></div>
                  <div class="col-md-6"><label class="form-label">Grupo</label><input type="text" name="grupo" class="form-control" value="${l.grupo || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Proyecto</label><input type="text" name="proyecto" class="form-control" value="${l.proyecto || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Correo</label><input type="email" name="correo" class="form-control" value="${l.correo}" required></div>
                  <div class="col-md-6"><label class="form-label">Teléfono</label><input type="text" name="telefono" class="form-control" value="${l.telefono || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Dirección</label><input type="text" name="direccion" class="form-control" value="${l.direccion || ''}"></div>
                </div>
                <div class="mt-3"><button type="submit" class="btn btn-primary">Guardar Cambios</button></div>
              </form>
            </div>
          `;

          const formEditar = document.getElementById('formEditarLider');
          formEditar.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const datos = Object.fromEntries(formData.entries());

            fetch('/api/lider/actualizar', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(datos)
            })
              .then(res => res.json())
              .then(response => {
                alert("✅ " + response.message);
                document.getElementById('profesores-link').click();
              })
              .catch(error => {
                alert("❌ Error al actualizar líder");
                console.error(error);
              });
          });
        });
    });
  });

}

  if (dashboardLink) {
    dashboardLink.addEventListener('click', e => {
      e.preventDefault();
      cargarEstadisticas();
      mainContent.innerHTML = '';
    });
  }
});
