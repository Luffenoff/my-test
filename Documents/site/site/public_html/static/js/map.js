let map;

DG.then(function () {
    map = DG.map('map-container', {
        center: [58.123139, 56.391607],
        zoom: 13
    });
    // Добавляем маркер для главного офиса
    let mainOfficeMarker = DG.marker([58.123139, 56.391607]).addTo(map);
    mainOfficeMarker.bindPopup('ООО "МКД-СЕРВИС"<br>ул. Менжинского 53А');

    // Обработчик для кнопок
    const addressButtons = document.querySelectorAll('.address-btn');
    addressButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Удаляем активный класс у всех кнопок
            addressButtons.forEach(btn => btn.classList.remove('active'));
            
            // Добавляем активный класс нажатой кнопке
            this.classList.add('active');
            
            // Получаем координаты из data-атрибута
            const coords = this.dataset.coords.split(',').map(coord => parseFloat(coord.trim()));
            
            // Перемещаем карту к выбранной точке
            map.setView(coords, 16);
            
            // Добавляем маркер
            DG.marker(coords)
                .addTo(map)
                .bindPopup(this.textContent.trim());
        });
    });
}); 