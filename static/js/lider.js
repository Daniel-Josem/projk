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
