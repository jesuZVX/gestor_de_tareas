# gestor_de_tareas
Gestor de tareas 

📁 Proyecto: Sistema de Gestión de Tareas
Descripción:
Este proyecto es una aplicación de escritorio desarrollada en Python con PyQt6, utilizando SQLite como base de datos y SQLAlchemy para la conexión backend. Su objetivo principal es permitir a los usuarios (administradores y colaboradores) gestionar proyectos y tareas de forma eficiente, visual y profesional.

Características principales:

🧑‍💼 Autenticación con roles (admin y colaborador).

🗂️ Creación y edición de proyectos por parte del administrador.

✅ Gestión de tareas asignadas a colaboradores.

📊 Visualización moderna en forma de tarjetas (cards) y barra de progreso por proyecto.

📎 Subida de archivos a tareas (PDF, Word, PNG).

📨 Sistema de notificaciones al asignar tareas (por ícono y por correo).

🧩 Interfaz unificada y estética (verde, blanco y gris), tipo dashboard.

🗃️ Eliminación lógica (nada se borra realmente, solo se cambia de "activo" a "inactivo").

🔒 Contraseñas encriptadas con bcrypt para mayor seguridad.

Tecnologías utilizadas:

Python + PyQt6

SQLite + SQLAlchemy

HTML (para algunos correos)

smtplib (para envío de notificaciones por email)

bcrypt (para seguridad de contraseñas)

Este sistema fue desarrollado con enfoque en la práctica, aprendiendo a integrar múltiples tecnologías en una sola aplicación funcional y visualmente agradable.

