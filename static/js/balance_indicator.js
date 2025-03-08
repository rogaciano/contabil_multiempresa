// Script para atualizar o indicador de equilíbrio do balanço
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o script já foi inicializado para evitar duplicação
    if (window.balanceIndicatorInitialized) {
        return;
    }
    window.balanceIndicatorInitialized = true;
    
    // Elementos do indicador
    const balanceIndicator = document.getElementById('balance-indicator');
    const totalAssetsElement = document.getElementById('total-assets');
    const totalLiabilitiesEquityElement = document.getElementById('total-liabilities-equity');
    const balanceStatusElement = document.getElementById('balance-status');
    
    // Se os elementos não existirem, não continue
    if (!balanceIndicator || !totalAssetsElement || !totalLiabilitiesEquityElement || !balanceStatusElement) {
        return;
    }
    
    // Função para formatar valores monetários
    function formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }
    
    // Variável para controlar o tempo da última atualização
    let lastUpdateTime = 0;
    
    // Função para atualizar o indicador
    function updateBalanceIndicator() {
        // Evitar atualizações muito frequentes (no mínimo 30 segundos entre atualizações)
        const now = Date.now();
        if (now - lastUpdateTime < 30000) {
            return;
        }
        lastUpdateTime = now;
        
        fetch('/reports/balance-status/')
            .then(response => response.json())
            .then(data => {
                // Atualizar valores
                totalAssetsElement.textContent = 'R$ ' + formatCurrency(data.total_assets);
                totalLiabilitiesEquityElement.textContent = 'R$ ' + formatCurrency(data.total_liabilities_equity);
                
                // Atualizar status (cor do indicador)
                if (data.is_balanced) {
                    balanceStatusElement.classList.remove('bg-red-500', 'bg-yellow-500', 'bg-gray-300');
                    balanceStatusElement.classList.add('bg-green-500');
                    balanceStatusElement.title = 'Balanço equilibrado';
                } else if (data.difference < 1) {
                    balanceStatusElement.classList.remove('bg-red-500', 'bg-green-500', 'bg-gray-300');
                    balanceStatusElement.classList.add('bg-yellow-500');
                    balanceStatusElement.title = 'Pequena diferença: R$ ' + formatCurrency(data.difference);
                } else {
                    balanceStatusElement.classList.remove('bg-green-500', 'bg-yellow-500', 'bg-gray-300');
                    balanceStatusElement.classList.add('bg-red-500');
                    balanceStatusElement.title = 'Balanço não equilibrado: R$ ' + formatCurrency(data.difference);
                }
                
                // Mostrar o indicador
                balanceIndicator.classList.remove('hidden');
            })
            .catch(error => {
                console.error('Erro ao atualizar indicador de balanço:', error);
            });
    }
    
    // Atualizar inicialmente e a cada 5 minutos
    updateBalanceIndicator();
    setInterval(updateBalanceIndicator, 5 * 60 * 1000);
});
