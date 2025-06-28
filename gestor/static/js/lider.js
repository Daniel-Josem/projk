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