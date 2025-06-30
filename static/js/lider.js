document.getElementById('btnCrearTarea').addEventListener('click', () => {
                    document.getElementById('formEditar').reset();
                    document.getElementById('tareaId').value = '';
                    document.getElementById('nombreArchivoActual').textContent = '';
                    document.getElementById('formEditar').action = '/crear_tarea';
                });

                // Script para cargar datos al editar
                document.querySelectorAll('.btnEditar').forEach(button => {
                    button.addEventListener('click', () => {
                        document.getElementById('formEditar').reset();
                        document.getElementById('tareaId').value = button.getAttribute('data-id');
                        document.getElementById('titulo').value = button.getAttribute('data-titulo');
                        document.getElementById('descripcion').value = button.getAttribute('data-descripcion');
                        document.getElementById('curso_destino').value = button.getAttribute('data-curso');
                        document.getElementById('fecha_vencimiento').value = button.getAttribute('data-fecha');
                        document.getElementById('prioridad').value = button.getAttribute('data-prioridad');
                        document.getElementById('estado').value = button.getAttribute('data-estado');
                        document.getElementById('formEditar').action = '/editar_tarea';
                    });
                });

                document.addEventListener('DOMContentLoaded', function () {
                    const btnProyecto = document.getElementById('proyecto-link');
                    const btnBackToTasksFromProjects = document.getElementById('btnBackToTasksFromProjects');
                    const tasksContainer = document.getElementById('tasksContainer');
                    const studentsContainer = document.getElementById('studentsContainer');
                    const projectsContainer = document.getElementById('projectsContainer');

                    btnProyecto.addEventListener('click', function (e) {
                        e.preventDefault();
                        tasksContainer.style.display = 'none';
                        studentsContainer.style.display = 'none';
                        projectsContainer.style.display = 'block';
                    });

                    btnBackToTasksFromProjects.addEventListener('click', function () {
                        projectsContainer.style.display = 'none';
                        tasksContainer.style.display = 'block';
                    });
                });

                document.addEventListener('DOMContentLoaded', function () {
        const btnDashboard = document.getElementById('dashboard-link');
        const btnProyecto = document.getElementById('proyecto-link');
        const btnBackToTasks = document.getElementById('btnBackToTasks');
        const btnBackToTasksFromProjects = document.getElementById('btnBackToTasksFromProjects');
        const tasksContainer = document.getElementById('tasksContainer');
        const studentsContainer = document.getElementById('studentsContainer');
        const projectsContainer = document.getElementById('projectsContainer');

        // Sidebar navigation for Tareas
        btnDashboard.addEventListener('click', function (e) {
            e.preventDefault();
            tasksContainer.style.display = 'block';
            studentsContainer.style.display = 'none';
            projectsContainer.style.display = 'none';
        });

        // Sidebar navigation for Proyecto
        btnProyecto.addEventListener('click', function (e) {
            e.preventDefault();
            tasksContainer.style.display = 'none';
            studentsContainer.style.display = 'none';
            projectsContainer.style.display = 'block';
        });

        // Back button from Students to Tareas
        btnBackToTasks.addEventListener('click', function () {
            studentsContainer.style.display = 'none';
            tasksContainer.style.display = 'block';
            projectsContainer.style.display = 'none';
        });

        // Back button from Projects to Tareas
        btnBackToTasksFromProjects.addEventListener('click', function () {
            projectsContainer.style.display = 'none';
            tasksContainer.style.display = 'block';
            studentsContainer.style.display = 'none';
        });

        // Navigation for each group
        document.querySelectorAll('.curso-link-sidebar').forEach(function (grupoLink) {
            grupoLink.addEventListener('click', function (e) {
                e.preventDefault();
                const grupoNombre = this.textContent.trim();
                document.getElementById('studentsCourseTitle').querySelector('span').textContent = grupoNombre;
                tasksContainer.style.display = 'none';
                studentsContainer.style.display = 'block';
                projectsContainer.style.display = 'none';
                // Aquí podrías llamar a una función para cargar los estudiantes del grupo seleccionado
            });
        });
    });
    document.getElementById('proyecto-link').addEventListener('click', () => {
    document.getElementById('tasksContainer').style.display = 'none';
    document.getElementById('studentsContainer').style.display = 'none';
    document.getElementById('projectsContainer').style.display = 'block';
});

document.getElementById('btnBackToTasksFromProjects').addEventListener('click', () => {
    document.getElementById('tasksContainer').style.display = 'block';
    document.getElementById('studentsContainer').style.display = 'none';
    document.getElementById('projectsContainer').style.display = 'none';
});

document.addEventListener('DOMContentLoaded', function () {
    // Notificaciones para el líder
    function cargarNotificaciones() {
        fetch('/notificaciones')
            .then(res => res.json())
            .then(data => {
                const lista = document.getElementById('notificaciones-lista');
                const badge = document.getElementById('notificaciones-count');
                lista.innerHTML = '';
                let noLeidas = 0;
                if (data.notificaciones && data.notificaciones.length > 0) {
                    data.notificaciones.forEach(n => {
                        if (!n.leido) noLeidas++;
                        // Icono según tipo (puedes mejorar esto según tus tipos)
                        let icono = '<i class="bi bi-info-circle text-primary me-2"></i>';
                        if (n.mensaje && n.mensaje.toLowerCase().includes('complet')) {
                            icono = '<i class="bi bi-check-circle-fill text-success me-2"></i>';
                        }
                        // Fecha/hora
                        let fecha = '';
                        if (n.fecha) {
                            const d = new Date(n.fecha);
                            fecha = `<span class='noti-fecha ms-2 text-secondary small'>${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>`;
                        }
                        // Truncar mensaje largo y mostrar tooltip
                        let mensaje = n.mensaje || '';
                        let mensajeCorto = mensaje.length > 48 ? mensaje.slice(0, 48) + '…' : mensaje;
                        let tooltip = mensaje.length > 48 ? `title='${mensaje.replace(/'/g, '&apos;')}'` : '';
                        const li = document.createElement('li');
                        li.className = 'noti-item px-2 py-2' + (n.leido ? ' noti-leida' : ' noti-noleida');
                        li.innerHTML = `
                            <div class="d-flex align-items-center justify-content-between gap-2">
                                <div class="d-flex align-items-center flex-grow-1">
                                    ${icono}
                                    <span class="noti-mensaje${n.leido ? ' text-muted' : ' fw-bold'}" style="max-width: 170px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" ${tooltip}>${mensajeCorto}</span>
                                    ${fecha}
                                </div>
                                ${!n.leido ? `<button class="btn btn-sm btn-link text-success p-0 ms-2 marcar-leida-btn" data-id="${n.id}" title="Marcar como leída"><i class="bi bi-check-circle"></i></button>` : ''}
                            </div>
                        `;
                        lista.appendChild(li);
                    });
                    badge.textContent = noLeidas;
                    lista.innerHTML += '<li><hr class="dropdown-divider"></li>';
                    lista.innerHTML += '<li><a class="dropdown-item text-primary text-center" href="#" id="marcarTodasLeidas">Marcar todas como leídas</a></li>';
                } else {
                    badge.textContent = '0';
                    lista.innerHTML = '<li><a class="dropdown-item text-center text-muted" href="#">No hay notificaciones</a></li>';
                    lista.innerHTML += '<li><hr class="dropdown-divider"></li>';
                    lista.innerHTML += '<li><a class="dropdown-item text-primary text-center" href="#" id="marcarTodasLeidas">Marcar todas como leídas</a></li>';
                }
                // Botón individual
                lista.querySelectorAll('.marcar-leida-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const id = this.getAttribute('data-id');
                        fetch('/notificaciones/marcar_leida', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id })
                        })
                        .then(res => res.json())
                        .then(resp => {
                            if (resp.success) cargarNotificaciones();
                        });
                    });
                });
                // Botón marcar todas
                const btnTodas = lista.querySelector('#marcarTodasLeidas');
                if (btnTodas) {
                    btnTodas.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (data.notificaciones && data.notificaciones.length > 0) {
                            const ids = data.notificaciones.filter(n => !n.leido).map(n => n.id);
                            Promise.all(ids.map(id => fetch('/notificaciones/marcar_leida', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ id })
                            }))).then(() => cargarNotificaciones());
                        }
                    });
                }
            });
    }
    // Cargar notificaciones al abrir el menú
    document.getElementById('navbarDropdownNotificaciones').addEventListener('click', cargarNotificaciones);
    // Polling automático cada 10 segundos
    setInterval(() => {
        // Solo refrescar si el menú está visible (abierto)
        const dropdown = document.getElementById('notificaciones-lista');
        if (dropdown && dropdown.offsetParent !== null) {
            cargarNotificaciones();
        }
    }, 10000); // 10 segundos
});
