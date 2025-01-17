document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.service-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Убираем активный класс со всех кнопок
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Убираем активный класс со всех секций
            document.querySelectorAll('.service-details').forEach(section => {
                section.classList.remove('active');
            });
            
            // Добавляем активный класс текущей кнопке
            this.classList.add('active');
            
            // Показываем соответствующую секцию
            const serviceId = this.getAttribute('data-service');
            document.getElementById(serviceId).classList.add('active');
        });
    });
});