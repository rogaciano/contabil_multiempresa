/**
 * Loading Modal - Gerencia o modal de carregamento durante operações assíncronas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar o HTML do modal ao documento se ainda não existir
    if (!document.getElementById('loading-modal')) {
        const modalHTML = `
            <div id="loading-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden">
                <div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
                    <div class="flex items-center justify-center mb-4">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                    </div>
                    <h3 id="loading-modal-title" class="text-lg font-medium text-gray-900 text-center">Gerando plano de contas</h3>
                    <p id="loading-modal-message" class="mt-2 text-sm text-gray-500 text-center">
                        Estamos utilizando IA para criar um plano de contas personalizado para o seu negócio. Isso pode levar alguns segundos...
                    </p>
                </div>
            </div>
        `;
        
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer.firstElementChild);
    }
    
    // Funções para manipular o modal
    window.LoadingModal = {
        show: function(title, message) {
            const modal = document.getElementById('loading-modal');
            const modalTitle = document.getElementById('loading-modal-title');
            const modalMessage = document.getElementById('loading-modal-message');
            
            if (title) modalTitle.textContent = title;
            if (message) modalMessage.textContent = message;
            
            modal.classList.remove('hidden');
        },
        
        hide: function() {
            const modal = document.getElementById('loading-modal');
            modal.classList.add('hidden');
        },
        
        updateMessage: function(message) {
            const modalMessage = document.getElementById('loading-modal-message');
            modalMessage.textContent = message;
        }
    };
    
    // Adicionar manipuladores de eventos para formulários que precisam do modal
    const aiAccountForm = document.getElementById('ai-account-form');
    if (aiAccountForm) {
        aiAccountForm.addEventListener('submit', function() {
            LoadingModal.show('Gerando plano de contas', 'Estamos utilizando IA para criar um plano de contas personalizado para o seu negócio. Isso pode levar alguns segundos...');
        });
    }
});
