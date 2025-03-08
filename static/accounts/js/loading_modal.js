/**
 * Loading Modal - Um componente para exibir um modal de carregamento com animação
 * durante operações assíncronas como a geração de plano de contas por IA.
 */
window.LoadingModal = (function() {
    // Elemento do modal
    let modalElement = null;
    
    // Criar o HTML do modal
    function createModalHTML(title, message) {
        return `
        <div id="loading-modal" class="fixed inset-0 flex items-center justify-center z-50" style="background-color: rgba(0, 0, 0, 0.5);">
            <div class="bg-white rounded-lg p-8 max-w-md mx-auto shadow-xl transform transition-all">
                <div class="text-center">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">${title}</h3>
                    <p class="text-sm text-gray-500 mb-6">${message}</p>
                    
                    <div class="flex justify-center mb-6">
                        <!-- Animação de carregamento -->
                        <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
                    </div>
                    
                    <div class="flex flex-col items-center">
                        <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                            <div id="progress-bar" class="bg-blue-600 h-2.5 rounded-full" style="width: 0%"></div>
                        </div>
                        <p id="progress-text" class="text-xs text-gray-500">Iniciando...</p>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    // Atualizar a barra de progresso
    function updateProgress(percent, text) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }
        
        if (progressText && text) {
            progressText.textContent = text;
        }
    }
    
    // Simular progresso para dar feedback visual ao usuário
    function simulateProgress() {
        const steps = [
            { percent: 10, text: "Analisando informações do negócio...", delay: 500 },
            { percent: 25, text: "Identificando estrutura contábil ideal...", delay: 1000 },
            { percent: 40, text: "Gerando contas do Ativo...", delay: 1200 },
            { percent: 55, text: "Gerando contas do Passivo...", delay: 1000 },
            { percent: 70, text: "Gerando contas de Patrimônio Líquido...", delay: 800 },
            { percent: 85, text: "Gerando contas de Receitas e Despesas...", delay: 1200 },
            { percent: 95, text: "Finalizando estrutura do plano de contas...", delay: 1000 }
        ];
        
        let currentStep = 0;
        
        function nextStep() {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                updateProgress(step.percent, step.text);
                currentStep++;
                setTimeout(nextStep, step.delay);
            }
        }
        
        nextStep();
    }
    
    return {
        // Mostrar o modal
        show: function(title, message) {
            // Remover qualquer modal existente
            this.hide();
            
            // Criar o novo modal
            const modalHTML = createModalHTML(title, message);
            const modalContainer = document.createElement('div');
            modalContainer.innerHTML = modalHTML;
            modalElement = modalContainer.firstElementChild;
            
            // Adicionar ao body
            document.body.appendChild(modalElement);
            
            // Iniciar a simulação de progresso
            simulateProgress();
            
            // Impedir o scroll da página
            document.body.style.overflow = 'hidden';
        },
        
        // Ocultar o modal
        hide: function() {
            if (modalElement && modalElement.parentNode) {
                modalElement.parentNode.removeChild(modalElement);
                modalElement = null;
                
                // Restaurar o scroll da página
                document.body.style.overflow = '';
            }
        },
        
        // Atualizar o progresso manualmente (se necessário)
        updateProgress: updateProgress
    };
})();
