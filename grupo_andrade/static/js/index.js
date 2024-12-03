 // Função para atualizar o tema
 function alterarTema() {
    let elemento = document.getElementById('meuElementoBody');
    // Alterna as classes de tema
    if (elemento.classList.contains('bg-black')) {
      elemento.classList.remove('bg-black', 'text-white');
      elemento.classList.add('bg-gray-200', 'text-gray-800');
      localStorage.setItem('tema', 'claro'); // Salva no localStorage
    } else {
      elemento.classList.remove('bg-gray-200', 'text-gray-800');
      elemento.classList.add('bg-black', 'text-white');
      localStorage.setItem('tema', 'escuro'); // Salva no localStorage
    }
  }

  // Função para restaurar o tema ao carregar a página
  function restaurarTema() {
    let elemento = document.getElementById('meuElementoBody');
    const tema = localStorage.getItem('tema');
    if (tema === 'escuro') {
      elemento.classList.add('bg-black', 'text-green-800');
      elemento.classList.remove('bg-gray-200', 'text-gray-800');
    } else {
      elemento.classList.add('bg-gray-200', 'text-gray-800');
      elemento.classList.remove('bg-black', 'text-white');
    }
  }

  document.addEventListener('DOMContentLoaded', restaurarTema);

  // Função para atualizar a placa em tempo real
  function updatePlate() {
    const placaInput = document.getElementById('placa');
    const placaDisplay = document.getElementById('placaDisplay');
    placaDisplay.textContent = placaInput.value.toUpperCase();
  }

  function updatePlate() {
    const placaInput = document.getElementById('placa');
    const placaDisplay = document.getElementById('placaDisplay');
    placaDisplay.textContent = placaInput.value.toUpperCase();
  }