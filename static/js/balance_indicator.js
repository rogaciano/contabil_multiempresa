// Script para atualizar o indicador de equilíbrio do balanço
document.addEventListener('DOMContentLoaded', function() {
    // Elementos do indicador
    const balanceIndicator = document.getElementById('balance-indicator');
    const totalAssetsElement = document.getElementById('total-assets');
    const totalLiabilitiesEquityElement = document.getElementById('total-liabilities-equity');
    const balanceStatusElement = document.getElementById('balance-status');
    
    // Função para formatar valores monetários
    function formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }
    
    // Função para atualizar o indicador
    function updateBalanceIndicator() {
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
    if (balanceIndicator) {
        updateBalanceIndicator();
        setInterval(updateBalanceIndicator, 5 * 60 * 1000);
    }
});
